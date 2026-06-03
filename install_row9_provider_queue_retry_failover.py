from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row9_provider_queue_retry_failover_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

queue_lib = ROOT / "frontend" / "src" / "lib" / "providerQueueRetryFailover.ts"
provider_lib = ROOT / "frontend" / "src" / "lib" / "realMediaGenerationProviders.ts"
provider_route = ROOT / "frontend" / "src" / "app" / "api" / "real-media-generation-providers" / "route.ts"
admin_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-real-media-generation-providers" / "route.ts"
queue_route = ROOT / "frontend" / "src" / "app" / "api" / "provider-queue-retry-failover" / "route.ts"
delegated_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"

for p in [queue_lib, provider_lib, provider_route, admin_route, queue_route, delegated_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

queue_lib.parent.mkdir(parents=True, exist_ok=True)

queue_lib.write_text(r'''import fs from "fs";
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
''', encoding="utf-8")

# Patch real provider lib to expose queue-safe marker
provider_text = provider_lib.read_text(encoding="utf-8")
if "provider_queue_retry_failover_ready" not in provider_text:
    provider_text = provider_text.replace(
        "real_media_generation_providers_enabled: true,",
        "real_media_generation_providers_enabled: true,\n    provider_queue_retry_failover_ready: true,",
        1
    )
provider_lib.write_text(provider_text, encoding="utf-8")

# Patch delegated route
delegated_text = delegated_route.read_text(encoding="utf-8")

if 'providerQueueRetryFailover' not in delegated_text:
    delegated_text = delegated_text.replace(
        'import { attachRealMediaProviderDecision } from "@/lib/realMediaGenerationProviders";',
        'import { attachRealMediaProviderDecision } from "@/lib/realMediaGenerationProviders";\nimport { attachProviderQueueRetryFailover } from "@/lib/providerQueueRetryFailover";'
    )

delegated_text = delegated_text.replace(
    '''  Object.assign(normalised, attachRealMediaProviderDecision(stateTenantKey, normalised));
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");''',
    '''  Object.assign(normalised, attachRealMediaProviderDecision(stateTenantKey, normalised));
  Object.assign(normalised, attachProviderQueueRetryFailover(stateTenantKey, normalised));
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");'''
)

delegated_route.write_text(delegated_text, encoding="utf-8")

# Create queue route
queue_route.parent.mkdir(parents=True, exist_ok=True)
queue_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import {
  getLatestProviderQueueJob,
  getProviderQueueJobs,
  persistProviderQueueJob,
} from "@/lib/providerQueueRetryFailover";
import { selectRealMediaProvider, inferMediaCapability } from "@/lib/realMediaGenerationProviders";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const jobs = getProviderQueueJobs(tenantKey);
  const latest = getLatestProviderQueueJob(tenantKey);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    provider_queue_retry_failover_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    provider_queue_count: jobs.length,
    latest_provider_queue_job: latest,
    provider_queue_jobs: jobs,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const capability = inferMediaCapability(body);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: capability,
    prompt: String(body.prompt || body.task || ""),
    asset_type: String(body.asset_type || ""),
    owner_approved: Boolean(body.owner_approved || body.owner_approval_granted),
    dry_run: true,
  });

  const job = persistProviderQueueJob(tenantKey, decision, body);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    provider_queue_retry_failover_enabled: true,
    provider_queue_job: job,
    provider_queue_status: job.status,
    provider_failover_available: job.failover_available,
    live_external_call_executed: false,
    external_action_performed: false,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
''', encoding="utf-8")

# Patch provider routes with visibility markers
for route in [provider_route, admin_route]:
    text = route.read_text(encoding="utf-8")
    if "provider_queue_retry_failover_enabled" not in text:
        text = text.replace(
            "real_media_generation_providers_enabled: true,",
            "real_media_generation_providers_enabled: true,\n    provider_queue_retry_failover_enabled: true,",
            1
        )
    route.write_text(text, encoding="utf-8")

test = ROOT / "test_row9_provider_queue_retry_failover.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/providerQueueRetryFailover.ts": [
        "createProviderQueueJob",
        "persistProviderQueueJob",
        "getProviderQueueJobs",
        "getLatestProviderQueueJob",
        "attachProviderQueueRetryFailover",
        "provider-queue.json",
        "retry_scheduled",
        "failover_selected",
        "manual_review_required",
        "live_external_call_executed: false",
        "external_action_performed: false",
    ],
    "frontend/src/app/api/provider-queue-retry-failover/route.ts": [
        "provider_queue_retry_failover_enabled",
        "persistProviderQueueJob",
        "getProviderQueueJobs",
        "provider_failover_available",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachProviderQueueRetryFailover",
        "providerQueueRetryFailover",
    ],
    "frontend/src/app/api/real-media-generation-providers/route.ts": [
        "provider_queue_retry_failover_enabled",
    ],
    "frontend/src/app/api/admin-real-media-generation-providers/route.ts": [
        "provider_queue_retry_failover_enabled",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW9_PROVIDER_QUEUE_RETRY_FAILOVER_FAILED missing={missing}")

print("ROW9_PROVIDER_QUEUE_RETRY_FAILOVER_PASSED")
''', encoding="utf-8")

print("ROW9_PROVIDER_QUEUE_RETRY_FAILOVER_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {queue_lib}")
print(f"Updated: {provider_lib}")
print(f"Created/updated: {queue_route}")
print(f"Updated: {provider_route}")
print(f"Updated: {admin_route}")
print(f"Updated: {delegated_route}")
print(f"Created: {test}")