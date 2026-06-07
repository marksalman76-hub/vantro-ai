import fs from "fs";
import path from "path";

export type ApprovalRevisionEvent = {
  id: string;
  tenant_key: string;
  created_at: string;
  action: "approved" | "rejected" | "revision_requested";
  actor_type: "client" | "owner_admin";
  comment: string;
  deliverable_id?: string | null;
  deliverable_status: string;
  authority?: "backend_canonical" | "frontend_advisory";
  fallback_used?: boolean;
  dev_only?: boolean;
  production_fail_closed?: boolean;
  credential_values_exposed?: false;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "approval-history");
const STORE_FILE = path.join(STORE_DIR, "approval-revision-history.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });

  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(
      STORE_FILE,
      JSON.stringify({ events: {} }, null, 2),
      "utf-8"
    );
  }
}

function safeReadStore(): { events: Record<string, ApprovalRevisionEvent[]> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));

    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { events: {} };
    }

    if (!parsed.events || typeof parsed.events !== "object") {
      return { events: {} };
    }

    return parsed as { events: Record<string, ApprovalRevisionEvent[]> };
  } catch {
    return { events: {} };
  }
}

function safeWriteStore(store: { events: Record<string, ApprovalRevisionEvent[]> }): void {
  ensureStore();

  const tmp = `${STORE_FILE}.tmp`;

  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

export function persistApprovalRevisionEvent(
  tenantKey: string,
  payload: {
    action: "approved" | "rejected" | "revision_requested";
    actor_type?: "client" | "owner_admin";
    comment?: string;
    deliverable_id?: string | null;
    deliverable_status?: string;
  }
): ApprovalRevisionEvent {

  const event: ApprovalRevisionEvent = {
    id: `${tenantKey}_${Date.now()}`,
    tenant_key: tenantKey,
    created_at: new Date().toISOString(),
    action: payload.action,
    actor_type: payload.actor_type || "client",
    comment: payload.comment || "",
    deliverable_id: payload.deliverable_id || null,
    deliverable_status: payload.deliverable_status || payload.action,
    authority: "frontend_advisory",
    fallback_used: true,
    dev_only: true,
    production_fail_closed: false,
    credential_values_exposed: false,
  };

  const store = safeReadStore();

  if (!store.events[tenantKey]) {
    store.events[tenantKey] = [];
  }

  store.events[tenantKey].unshift(event);

  store.events[tenantKey] = store.events[tenantKey].slice(0, 50);

  safeWriteStore(store);

  return event;
}

export function getApprovalRevisionHistory(
  tenantKey: string
): ApprovalRevisionEvent[] {
  const store = safeReadStore();
  return store.events[tenantKey] || [];
}


// durable_runtime_storage_enabled
// This module participates in the shared .runtime durable storage layer.
