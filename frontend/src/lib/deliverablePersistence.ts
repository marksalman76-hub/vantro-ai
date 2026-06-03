import fs from "fs";
import path from "path";

export type PersistedDeliverableRecord = {
  id: string;
  tenant_key: string;
  created_at: string;
  source: string;
  has_real_output: boolean;
  client_output_truth_checked: boolean;
  client_safe_status: string;
  display_status: string;
  output_truth_reason: string;
  output?: unknown;
  deliverable?: unknown;
  latest_deliverable?: unknown;
  generated_output?: unknown;
  final_output?: unknown;
  asset?: unknown;
  assets?: unknown;
  result?: unknown;
  data?: unknown;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "client-deliverables");
const STORE_FILE = path.join(STORE_DIR, "latest-deliverables.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ records: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { records: Record<string, PersistedDeliverableRecord> } {
  ensureStore();
  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { records: {} };
    if (!parsed.records || typeof parsed.records !== "object" || Array.isArray(parsed.records)) return { records: {} };
    return parsed as { records: Record<string, PersistedDeliverableRecord> };
  } catch {
    return { records: {} };
  }
}

function safeWriteStore(store: { records: Record<string, PersistedDeliverableRecord> }): void {
  ensureStore();
  const tmp = `${STORE_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

function readable(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return "";
  }
}

function isMeaningfulValue(value: unknown): boolean {
  const text = readable(value);
  if (!text) return false;
  const marker = text.toLowerCase();
  return ![
    "completed",
    "complete",
    "success",
    "successful",
    "done",
    "pending",
    "awaiting_output",
    "no output",
    "no deliverable",
    "null",
    "undefined",
    "{}",
    "[]",
  ].includes(marker);
}

export function resolveTenantKey(headers: Headers, payload?: Record<string, unknown>): string {
  const fromPayload = readable(
    payload?.tenant_id ||
    payload?.tenant_key ||
    payload?.client_id ||
    payload?.business_id ||
    payload?.workspace_id
  );

  const fromHeaders = readable(
    headers.get("x-tenant-id") ||
    headers.get("x-tenant-key") ||
    headers.get("x-client-id") ||
    headers.get("x-business-id")
  );

  return fromPayload || fromHeaders || "default_client_workspace";
}

export function extractOutputCandidates(payload: Record<string, unknown>): unknown[] {
  const result = (payload.result || {}) as Record<string, unknown>;
  const data = (payload.data || {}) as Record<string, unknown>;
  const asset = (payload.asset || result.asset || data.asset || {}) as Record<string, unknown>;

  return [
    payload.output,
    payload.deliverable,
    payload.deliverables,
    payload.latest_deliverable,
    payload.generated_output,
    payload.final_output,
    payload.asset,
    payload.assets,
    result.output,
    result.deliverable,
    result.deliverables,
    result.latest_deliverable,
    result.generated_output,
    result.final_output,
    result.asset,
    result.assets,
    data.output,
    data.deliverable,
    data.deliverables,
    data.latest_deliverable,
    data.generated_output,
    data.final_output,
    data.asset,
    data.assets,
    asset.preview_url,
    asset.download_url,
    asset.url,
    asset.public_url,
    asset.signed_preview_url,
    asset.signed_download_url,
  ];
}

export function hasRealDeliverableOutput(payload: Record<string, unknown>): boolean {
  return extractOutputCandidates(payload).some(isMeaningfulValue);
}

export function persistLatestDeliverable(
  tenantKey: string,
  payload: Record<string, unknown>,
  source = "delegated_workforce_execution"
): PersistedDeliverableRecord | null {
  const hasRealOutput = Boolean(payload.has_real_output || hasRealDeliverableOutput(payload));
  if (!hasRealOutput) return null;

  const now = new Date().toISOString();
  const record: PersistedDeliverableRecord = {
    id: `${tenantKey}_${Date.now()}`,
    tenant_key: tenantKey,
    created_at: now,
    source,
    has_real_output: true,
    client_output_truth_checked: true,
    client_safe_status: "Completed",
    display_status: "Completed",
    output_truth_reason: "Persisted real deliverable output is available.",
    output: payload.output,
    deliverable: payload.deliverable,
    latest_deliverable: payload.latest_deliverable,
    generated_output: payload.generated_output,
    final_output: payload.final_output,
    asset: payload.asset,
    assets: payload.assets,
    result: payload.result,
    data: payload.data,
  };

  const store = safeReadStore();
  store.records[tenantKey] = record;
  safeWriteStore(store);
  return record;
}

export function getLatestDeliverable(tenantKey: string): PersistedDeliverableRecord | null {
  const store = safeReadStore();
  return store.records[tenantKey] || null;
}
