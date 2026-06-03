from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row4_approval_revision_history_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

history_lib = ROOT / "frontend" / "src" / "lib" / "approvalRevisionHistory.ts"
review_route = ROOT / "frontend" / "src" / "app" / "api" / "client-review-action" / "route.ts"
deliverable_route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"

for p in [history_lib, review_route, deliverable_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

history_lib.parent.mkdir(parents=True, exist_ok=True)

history_lib.write_text(r'''import fs from "fs";
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
''', encoding="utf-8")

review_text = review_route.read_text(encoding="utf-8")

if 'approvalRevisionHistory' not in review_text:
    review_text = review_text.replace(
        'import { NextRequest, NextResponse } from "next/server";',
        'import { NextRequest, NextResponse } from "next/server";\nimport { persistApprovalRevisionEvent } from "@/lib/approvalRevisionHistory";\nimport { resolveTenantKey } from "@/lib/deliverablePersistence";'
    )

append_block = r'''
    let mappedAction: "approved" | "rejected" | "revision_requested" = "approved";

    const lowerAction = String(
      body?.action ||
      body?.review_action ||
      body?.status ||
      ""
    ).toLowerCase();

    if (lowerAction.includes("reject")) {
      mappedAction = "rejected";
    } else if (
      lowerAction.includes("revision") ||
      lowerAction.includes("revise") ||
      lowerAction.includes("change")
    ) {
      mappedAction = "revision_requested";
    }

    const tenantKey = resolveTenantKey(req.headers, body || {});

    const persistedEvent = persistApprovalRevisionEvent(
      tenantKey,
      {
        action: mappedAction,
        actor_type: "client",
        comment: String(body?.comment || body?.feedback || ""),
        deliverable_id: String(body?.deliverable_id || ""),
        deliverable_status: mappedAction,
      }
    );
'''

if "persistApprovalRevisionEvent" not in review_text:
    if "const body = await req.json();" not in review_text:
        raise SystemExit("ROW4_PATCH_FAILED: could not find request body parsing")

    review_text = review_text.replace(
        "const body = await req.json();",
        "const body = await req.json();" + append_block
    )

response_insert = '''
      approval_revision_event_saved: true,
      approval_revision_event_id: persistedEvent.id,
'''

if response_insert not in review_text:
    review_text = review_text.replace(
        "success: true,",
        "success: true," + response_insert,
        1
    )

review_route.write_text(review_text, encoding="utf-8")

deliverable_text = deliverable_route.read_text(encoding="utf-8")

if 'approvalRevisionHistory' not in deliverable_text:
    deliverable_text = deliverable_text.replace(
        'import { getLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";',
        'import { getLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";\nimport { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";'
    )

inject_target = 'const normalised = normalise(payload as Record<string, unknown>);'

inject_block = '''
  const tenantKey = resolveTenantKey(req.headers, payload as Record<string, unknown>);
  const approvalHistory = getApprovalRevisionHistory(tenantKey);

'''

if inject_block not in deliverable_text:
    deliverable_text = deliverable_text.replace(
        inject_target,
        inject_block + inject_target
    )

replace_block = '''
    ...normalised,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
'''

new_block = '''
    ...normalised,
    approval_revision_history: approvalHistory,
    latest_review_action: approvalHistory[0] || null,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
'''

deliverable_text = deliverable_text.replace(replace_block, new_block)

deliverable_route.write_text(deliverable_text, encoding="utf-8")

test = ROOT / "test_row4_approval_revision_history.py"

test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/approvalRevisionHistory.ts": [
        "persistApprovalRevisionEvent",
        "getApprovalRevisionHistory",
        "approval-history",
        "approval-revision-history.json",
    ],
    "frontend/src/app/api/client-review-action/route.ts": [
        "persistApprovalRevisionEvent",
        "approval_revision_event_saved",
        "approval_revision_event_id",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "approval_revision_history",
        "latest_review_action",
        "getApprovalRevisionHistory",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")

    absent = [needle for needle in needles if needle not in text]

    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(
        f"ROW4_APPROVAL_REVISION_HISTORY_FAILED missing={missing}"
    )

print("ROW4_APPROVAL_REVISION_HISTORY_PASSED")
''', encoding="utf-8")

print("ROW4_APPROVAL_REVISION_HISTORY_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {history_lib}")
print(f"Updated: {review_route}")
print(f"Updated: {deliverable_route}")
print(f"Created: {test}")