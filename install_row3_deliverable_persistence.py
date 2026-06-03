from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row3_deliverable_persistence_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

execution_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"
latest_route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"
lib_file = ROOT / "frontend" / "src" / "lib" / "deliverablePersistence.ts"

for p in [execution_route, latest_route, lib_file]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

lib_file.parent.mkdir(parents=True, exist_ok=True)

lib_file.write_text(r'''import fs from "fs";
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
''', encoding="utf-8")

# Patch delegated execution route
execution_text = execution_route.read_text(encoding="utf-8")

if 'deliverablePersistence' not in execution_text:
    execution_text = execution_text.replace(
        'import { NextRequest, NextResponse } from "next/server";',
        'import { NextRequest, NextResponse } from "next/server";\nimport { persistLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";'
    )

old_return = '''  return NextResponse.json(normaliseClientExecutionTruth(payload), {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });'''

new_return = '''  const normalised = normaliseClientExecutionTruth(payload) as Record<string, unknown>;

  if (normalised.has_real_output === true) {
    const tenantKey = resolveTenantKey(req.headers, normalised);
    const persisted = persistLatestDeliverable(tenantKey, normalised, "delegated_workforce_execution");
    normalised.deliverable_persisted = Boolean(persisted);
    normalised.persisted_deliverable_id = persisted?.id || null;
  } else {
    normalised.deliverable_persisted = false;
    normalised.persisted_deliverable_id = null;
  }

  return NextResponse.json(normalised, {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });'''

if old_return not in execution_text:
    raise SystemExit("ROW3_PATCH_FAILED: delegated-workforce-execution return block not found")

execution_text = execution_text.replace(old_return, new_return)
execution_route.write_text(execution_text, encoding="utf-8")

# Patch latest deliverable route
latest_text = latest_route.read_text(encoding="utf-8")

if 'deliverablePersistence' not in latest_text:
    latest_text = latest_text.replace(
        'import { NextRequest, NextResponse } from "next/server";',
        'import { NextRequest, NextResponse } from "next/server";\nimport { getLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";'
    )

fallback_block = '''  return NextResponse.json(normalise(payload as Record<string, unknown>), {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });'''

replacement_block = '''  const normalised = normalise(payload as Record<string, unknown>);

  if (normalised.has_real_output === false) {
    const tenantKey = resolveTenantKey(req.headers, normalised);
    const persisted = getLatestDeliverable(tenantKey);
    if (persisted) {
      return NextResponse.json({
        ...persisted,
        success: true,
        has_real_output: true,
        client_output_truth_checked: true,
        client_safe_status: "Completed",
        display_status: "Completed",
        deliverable_persisted: true,
        persistence_source: "latest_deliverable_store",
      }, {
        status: 200,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  }

  return NextResponse.json({
    ...normalised,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
  }, {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });'''

if fallback_block not in latest_text:
    raise SystemExit("ROW3_PATCH_FAILED: client-latest-deliverable return block not found")

latest_text = latest_text.replace(fallback_block, replacement_block)
latest_route.write_text(latest_text, encoding="utf-8")

test = ROOT / "test_row3_deliverable_persistence.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/deliverablePersistence.ts": [
        "persistLatestDeliverable",
        "getLatestDeliverable",
        "resolveTenantKey",
        "hasRealDeliverableOutput",
        ".runtime",
        "client-deliverables",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistLatestDeliverable",
        "deliverable_persisted",
        "persisted_deliverable_id",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "getLatestDeliverable",
        "latest_deliverable_store",
        "persistence_source",
    ],
}

missing = {}
for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW3_DELIVERABLE_PERSISTENCE_FAILED missing={missing}")

print("ROW3_DELIVERABLE_PERSISTENCE_PASSED")
''', encoding="utf-8")

print("ROW3_DELIVERABLE_PERSISTENCE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {lib_file}")
print(f"Updated: {execution_route}")
print(f"Updated: {latest_route}")
print(f"Created: {test}")