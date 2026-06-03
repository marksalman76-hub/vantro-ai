import fs from "fs";
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


// durable_runtime_storage_enabled
// This module participates in the shared .runtime durable storage layer.
