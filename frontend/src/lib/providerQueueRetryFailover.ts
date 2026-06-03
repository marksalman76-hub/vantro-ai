import fs from "fs";
import path from "path";
import {
  MediaGenerationProviderDecision,
  RealMediaProviderKey,
  getRealMediaProviderRegistry,
} from "@/lib/realMediaGenerationProviders";

export type ProviderQueueJobStatus =
  | "queued"
  | "retry_scheduled"
  | "failover_selected"
  | "manual_review_required"
  | "blocked"
  | "completed";

export type ProviderQueueJob = {
  id: string;
  tenant_key: string;
  created_at: string;
  updated_at: string;
  requested_capability: string;
  primary_provider: RealMediaProviderKey | null;
  fallback_provider: RealMediaProviderKey | null;
  status: ProviderQueueJobStatus;
  retry_count: number;
  max_retries: number;
  next_retry_at: string | null;
  failover_available: boolean;
  failover_reason: string;
  owner_approval_required: boolean;
  live_external_call_executed: false;
  external_action_performed: false;
  client_safe_status: string;
  provider_decision: MediaGenerationProviderDecision | null;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "provider-queue");
const STORE_FILE = path.join(STORE_DIR, "provider-queue.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ jobs: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { jobs: Record<string, ProviderQueueJob[]> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { jobs: {} };
    if (!parsed.jobs || typeof parsed.jobs !== "object" || Array.isArray(parsed.jobs)) return { jobs: {} };
    return parsed as { jobs: Record<string, ProviderQueueJob[]> };
  } catch {
    return { jobs: {} };
  }
}

function safeWriteStore(store: { jobs: Record<string, ProviderQueueJob[]> }): void {
  ensureStore();
  const tmp = `${STORE_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

function nextRetryAt(retryCount: number): string {
  const date = new Date();
  const delayMinutes = Math.min(60, Math.max(5, retryCount * 10));
  date.setMinutes(date.getMinutes() + delayMinutes);
  return date.toISOString();
}

function selectFallbackProvider(
  requestedCapability: string,
  primaryProvider: RealMediaProviderKey | null
): RealMediaProviderKey | null {
  const registry = getRealMediaProviderRegistry();

  const fallback = registry.find((provider) =>
    provider.key !== primaryProvider &&
    provider.configured &&
    provider.enabled &&
    provider.supported_capabilities.includes(requestedCapability as any)
  );

  return fallback?.key || null;
}

export function createProviderQueueJob(
  tenantKey: string,
  decision: MediaGenerationProviderDecision | null,
  payload: Record<string, unknown> = {}
): ProviderQueueJob {
  const requestedCapability = String(
    decision?.requested_capability ||
    payload.requested_media_capability ||
    payload.requested_capability ||
    "image_generation"
  );

  const primaryProvider = decision?.provider_selected || null;
  const fallbackProvider = selectFallbackProvider(requestedCapability, primaryProvider);
  const retryCount = Number(payload.retry_count || 0);
  const maxRetries = Number(payload.max_retries || 3);

  let status: ProviderQueueJobStatus = "queued";
  let clientSafeStatus = "Provider job queued safely.";
  let failoverReason = fallbackProvider
    ? "Fallback provider is available if primary provider fails."
    : "No configured fallback provider is currently available.";

  if (!primaryProvider) {
    status = "manual_review_required";
    clientSafeStatus = "Manual provider review required.";
    failoverReason = "No primary provider could be selected.";
  } else if (retryCount > 0 && retryCount < maxRetries) {
    status = "retry_scheduled";
    clientSafeStatus = "Provider retry scheduled.";
  } else if (retryCount >= maxRetries && fallbackProvider) {
    status = "failover_selected";
    clientSafeStatus = "Provider failover selected.";
  } else if (retryCount >= maxRetries && !fallbackProvider) {
    status = "manual_review_required";
    clientSafeStatus = "Manual review required after retry limit.";
  }

  return {
    id: `${tenantKey}_provider_job_${Date.now()}`,
    tenant_key: tenantKey,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    requested_capability: requestedCapability,
    primary_provider: primaryProvider,
    fallback_provider: fallbackProvider,
    status,
    retry_count: retryCount,
    max_retries: maxRetries,
    next_retry_at:
      status === "retry_scheduled" || status === "queued"
        ? nextRetryAt(retryCount + 1)
        : null,
    failover_available: Boolean(fallbackProvider),
    failover_reason: failoverReason,
    owner_approval_required: true,
    live_external_call_executed: false,
    external_action_performed: false,
    client_safe_status: clientSafeStatus,
    provider_decision: decision,
  };
}

export function persistProviderQueueJob(
  tenantKey: string,
  decision: MediaGenerationProviderDecision | null,
  payload: Record<string, unknown> = {}
): ProviderQueueJob {
  const job = createProviderQueueJob(tenantKey, decision, payload);
  const store = safeReadStore();

  if (!store.jobs[tenantKey]) {
    store.jobs[tenantKey] = [];
  }

  store.jobs[tenantKey].unshift(job);
  store.jobs[tenantKey] = store.jobs[tenantKey].slice(0, 100);

  safeWriteStore(store);
  return job;
}

export function getProviderQueueJobs(tenantKey: string): ProviderQueueJob[] {
  const store = safeReadStore();
  return store.jobs[tenantKey] || [];
}

export function getLatestProviderQueueJob(tenantKey: string): ProviderQueueJob | null {
  return getProviderQueueJobs(tenantKey)[0] || null;
}

export function attachProviderQueueRetryFailover(
  tenantKey: string,
  payload: Record<string, unknown>
): Record<string, unknown> {
  const decision = (payload.real_media_provider_decision || null) as MediaGenerationProviderDecision | null;
  const job = persistProviderQueueJob(tenantKey, decision, payload);

  return {
    ...payload,
    provider_queue_retry_failover_enabled: true,
    provider_queue_job: job,
    provider_queue_status: job.status,
    provider_retry_count: job.retry_count,
    provider_max_retries: job.max_retries,
    provider_next_retry_at: job.next_retry_at,
    provider_failover_available: job.failover_available,
    provider_fallback_provider: job.fallback_provider,
    live_external_call_executed: false,
    external_action_performed: false,
  };
}


// durable_runtime_storage_enabled
// This module participates in the shared .runtime durable storage layer.
