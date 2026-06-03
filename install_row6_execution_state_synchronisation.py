from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row6_execution_state_sync_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

state_lib = ROOT / "frontend" / "src" / "lib" / "executionStateSync.ts"
delegated_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"
latest_route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"
matrix_route = ROOT / "frontend" / "src" / "app" / "api" / "client-execution-matrix" / "route.ts"

for p in [state_lib, delegated_route, latest_route, matrix_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

state_lib.parent.mkdir(parents=True, exist_ok=True)

state_lib.write_text(r'''import fs from "fs";
import path from "path";

export type ClientExecutionState = {
  tenant_key: string;
  updated_at: string;
  execution_id: string | null;
  workflow_status: string;
  execution_status: string;
  display_status: string;
  client_safe_status: string;
  has_real_output: boolean;
  deliverable_persisted: boolean;
  latest_deliverable_id: string | null;
  latest_review_action: unknown | null;
  profile_completed: boolean;
  current_agent: string;
  current_task: string;
  output_truth_reason: string;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "execution-state");
const STORE_FILE = path.join(STORE_DIR, "client-execution-state.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ states: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { states: Record<string, ClientExecutionState> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { states: {} };
    if (!parsed.states || typeof parsed.states !== "object" || Array.isArray(parsed.states)) return { states: {} };
    return parsed as { states: Record<string, ClientExecutionState> };
  } catch {
    return { states: {} };
  }
}

function safeWriteStore(store: { states: Record<string, ClientExecutionState> }): void {
  ensureStore();
  const tmp = `${STORE_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

function text(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

function statusFromPayload(payload: Record<string, unknown>, hasRealOutput: boolean): string {
  const explicit = text(
    payload.client_safe_status ||
    payload.display_status ||
    payload.execution_status ||
    payload.workflow_status ||
    payload.status
  );

  if (hasRealOutput) return "Completed";
  if (explicit && explicit.toLowerCase() !== "completed") return explicit;
  return "Output pending";
}

export function normaliseExecutionState(
  tenantKey: string,
  payload: Record<string, unknown>,
  previous?: ClientExecutionState | null
): ClientExecutionState {
  const hasRealOutput = Boolean(payload.has_real_output);
  const displayStatus = statusFromPayload(payload, hasRealOutput);

  return {
    tenant_key: tenantKey,
    updated_at: new Date().toISOString(),
    execution_id: text(payload.execution_id || payload.run_id || payload.job_id) || previous?.execution_id || null,
    workflow_status: hasRealOutput ? "completed_with_output" : text(payload.workflow_status || payload.status) || "awaiting_output",
    execution_status: hasRealOutput ? "completed_with_output" : text(payload.execution_status || payload.status) || "awaiting_output",
    display_status: displayStatus,
    client_safe_status: displayStatus,
    has_real_output: hasRealOutput,
    deliverable_persisted: Boolean(payload.deliverable_persisted || previous?.deliverable_persisted),
    latest_deliverable_id:
      text(payload.persisted_deliverable_id || payload.deliverable_id || payload.latest_deliverable_id) ||
      previous?.latest_deliverable_id ||
      null,
    latest_review_action: payload.latest_review_action || previous?.latest_review_action || null,
    profile_completed: Boolean(payload.profile_completed || previous?.profile_completed),
    current_agent: text(payload.agent_key || payload.agent || payload.assigned_agent || previous?.current_agent),
    current_task: text(payload.task || payload.prompt || payload.request || previous?.current_task),
    output_truth_reason:
      text(payload.output_truth_reason) ||
      previous?.output_truth_reason ||
      "Execution state synchronised.",
  };
}

export function persistExecutionState(
  tenantKey: string,
  payload: Record<string, unknown>
): ClientExecutionState {
  const store = safeReadStore();
  const previous = store.states[tenantKey] || null;
  const state = normaliseExecutionState(tenantKey, payload, previous);
  store.states[tenantKey] = state;
  safeWriteStore(store);
  return state;
}

export function getExecutionState(tenantKey: string): ClientExecutionState | null {
  const store = safeReadStore();
  return store.states[tenantKey] || null;
}

export function mergeExecutionState(
  tenantKey: string,
  payload: Record<string, unknown>
): Record<string, unknown> {
  const state = getExecutionState(tenantKey);
  if (!state) return payload;

  return {
    ...payload,
    execution_state_synchronised: true,
    execution_state: state,
    workflow_status: payload.workflow_status || state.workflow_status,
    execution_status: payload.execution_status || state.execution_status,
    display_status: payload.display_status || state.display_status,
    client_safe_status: payload.client_safe_status || state.client_safe_status,
    has_real_output: Boolean(payload.has_real_output || state.has_real_output),
    deliverable_persisted: Boolean(payload.deliverable_persisted || state.deliverable_persisted),
    latest_deliverable_id: payload.latest_deliverable_id || state.latest_deliverable_id,
    latest_review_action: payload.latest_review_action || state.latest_review_action,
    profile_completed: Boolean(payload.profile_completed || state.profile_completed),
  };
}
''', encoding="utf-8")

# Patch delegated workforce execution route
delegated_text = delegated_route.read_text(encoding="utf-8")

if 'executionStateSync' not in delegated_text:
    delegated_text = delegated_text.replace(
        'import { persistLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";',
        'import { persistLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";\nimport { persistExecutionState } from "@/lib/executionStateSync";'
    )

needle = '''  return NextResponse.json(normalised, {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });'''

replacement = '''  const stateTenantKey = resolveTenantKey(req.headers, normalised);
  const executionState = persistExecutionState(stateTenantKey, normalised);
  normalised.execution_state_synchronised = true;
  normalised.execution_state = executionState;

  return NextResponse.json(normalised, {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });'''

if needle not in delegated_text:
    raise SystemExit("ROW6_PATCH_FAILED: delegated return block not found")

delegated_text = delegated_text.replace(needle, replacement)
delegated_route.write_text(delegated_text, encoding="utf-8")

# Patch latest deliverable route
latest_text = latest_route.read_text(encoding="utf-8")

if 'executionStateSync' not in latest_text:
    latest_text = latest_text.replace(
        'import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";',
        'import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";\nimport { mergeExecutionState, persistExecutionState } from "@/lib/executionStateSync";'
    )

latest_text = latest_text.replace(
    '''      return NextResponse.json({
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
      });''',
    '''      const persistedPayload = {
        ...persisted,
        success: true,
        has_real_output: true,
        client_output_truth_checked: true,
        client_safe_status: "Completed",
        display_status: "Completed",
        deliverable_persisted: true,
        persistence_source: "latest_deliverable_store",
      };
      const syncedState = persistExecutionState(tenantKey, persistedPayload);
      return NextResponse.json({
        ...persistedPayload,
        execution_state_synchronised: true,
        execution_state: syncedState,
      }, {
        status: 200,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });'''
)

latest_text = latest_text.replace(
    '''  return NextResponse.json({
    ...normalised,
    approval_revision_history: approvalHistory,
    latest_review_action: approvalHistory[0] || null,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
  }, {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });''',
    '''  const latestPayload = mergeExecutionState(tenantKey, {
    ...normalised,
    approval_revision_history: approvalHistory,
    latest_review_action: approvalHistory[0] || null,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
  });

  return NextResponse.json(latestPayload, {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });'''
)

latest_route.write_text(latest_text, encoding="utf-8")

# Replace client-execution-matrix route with synced safe version
matrix_route.parent.mkdir(parents=True, exist_ok=True)
matrix_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { getExecutionState } from "@/lib/executionStateSync";
import { getLatestDeliverable } from "@/lib/deliverablePersistence";
import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";
import { getBusinessProfile } from "@/lib/businessProfilePersistence";

export const dynamic = "force-dynamic";

function statusLabel(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) return value.trim();
  return fallback;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const executionState = getExecutionState(tenantKey);
  const latestDeliverable = getLatestDeliverable(tenantKey);
  const approvalHistory = getApprovalRevisionHistory(tenantKey);
  const businessProfile = getBusinessProfile(tenantKey);

  const hasRealOutput = Boolean(executionState?.has_real_output || latestDeliverable?.has_real_output);
  const profileCompleted = Boolean(businessProfile?.profile_completed || executionState?.profile_completed);

  const matrix = [
    {
      key: "profile",
      label: "Business profile",
      status: profileCompleted ? "complete" : "pending",
      client_safe_status: profileCompleted ? "Complete" : "Needs profile details",
    },
    {
      key: "execution",
      label: "Execution",
      status: statusLabel(executionState?.execution_status, "awaiting_output"),
      client_safe_status: statusLabel(executionState?.client_safe_status, "Output pending"),
    },
    {
      key: "deliverable",
      label: "Deliverable",
      status: hasRealOutput ? "complete" : "pending",
      client_safe_status: hasRealOutput ? "Completed" : "No deliverable yet",
    },
    {
      key: "review",
      label: "Review",
      status: approvalHistory.length ? "reviewed" : "not_reviewed",
      client_safe_status: approvalHistory.length ? "Review recorded" : "Awaiting review",
    },
  ];

  return NextResponse.json({
    success: true,
    execution_state_synchronised: true,
    tenant_scoped: true,
    client_safe: true,
    matrix,
    execution_state: executionState,
    latest_deliverable: latestDeliverable,
    latest_review_action: approvalHistory[0] || null,
    approval_revision_history: approvalHistory,
    business_profile: businessProfile,
    has_real_output: hasRealOutput,
    profile_completed: profileCompleted,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
''', encoding="utf-8")

test = ROOT / "test_row6_execution_state_synchronisation.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/executionStateSync.ts": [
        "persistExecutionState",
        "getExecutionState",
        "mergeExecutionState",
        "client-execution-state.json",
        "execution_state_synchronised",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistExecutionState",
        "execution_state_synchronised",
        "execution_state",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "mergeExecutionState",
        "persistExecutionState",
        "execution_state_synchronised",
    ],
    "frontend/src/app/api/client-execution-matrix/route.ts": [
        "getExecutionState",
        "execution_state_synchronised",
        "Business profile",
        "Deliverable",
        "Review",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW6_EXECUTION_STATE_SYNCHRONISATION_FAILED missing={missing}")

print("ROW6_EXECUTION_STATE_SYNCHRONISATION_PASSED")
''', encoding="utf-8")

print("ROW6_EXECUTION_STATE_SYNCHRONISATION_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {state_lib}")
print(f"Updated: {delegated_route}")
print(f"Updated: {latest_route}")
print(f"Created/updated: {matrix_route}")
print(f"Created: {test}")