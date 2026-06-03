from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row4_client_review_action_scope_fix_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

route = ROOT / "frontend" / "src" / "app" / "api" / "client-review-action" / "route.ts"

if not route.exists():
    raise SystemExit("client-review-action route not found")

shutil.copy2(route, backup / "route.ts")

route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { persistApprovalRevisionEvent } from "@/lib/approvalRevisionHistory";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function mapReviewAction(value: unknown): "approved" | "rejected" | "revision_requested" {
  const lower = String(value || "").toLowerCase();

  if (lower.includes("reject")) return "rejected";
  if (
    lower.includes("revision") ||
    lower.includes("revise") ||
    lower.includes("change")
  ) {
    return "revision_requested";
  }

  return "approved";
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const mappedAction = mapReviewAction(
    body.action ||
    body.review_action ||
    body.status ||
    body.decision
  );

  const tenantKey = resolveTenantKey(req.headers, body);

  const persistedEvent = persistApprovalRevisionEvent(tenantKey, {
    action: mappedAction,
    actor_type: "client",
    comment: String(body.comment || body.feedback || body.revision_notes || ""),
    deliverable_id: body.deliverable_id ? String(body.deliverable_id) : null,
    deliverable_status: mappedAction,
  });

  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  try {
    const response = await fetch(`${backendBaseUrl()}/client-review-action`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        ...body,
        mapped_review_action: mappedAction,
        approval_revision_event_id: persistedEvent.id,
      }),
      cache: "no-store",
    });

    const text = await response.text();

    let backendPayload: Record<string, unknown> = {};
    try {
      backendPayload = JSON.parse(text);
    } catch {
      backendPayload = {
        backend_response_text: text,
      };
    }

    return NextResponse.json(
      {
        ...backendPayload,
        success: backendPayload.success !== false,
        approval_revision_event_saved: true,
        approval_revision_event_id: persistedEvent.id,
        latest_review_action: persistedEvent,
        client_safe_status:
          mappedAction === "approved"
            ? "Approved"
            : mappedAction === "rejected"
              ? "Rejected"
              : "Revision requested",
      },
      {
        status: response.status,
        headers: {
          "cache-control": "no-store, no-cache, must-revalidate",
        },
      }
    );
  } catch {
    return NextResponse.json(
      {
        success: true,
        approval_revision_event_saved: true,
        approval_revision_event_id: persistedEvent.id,
        latest_review_action: persistedEvent,
        client_safe_status:
          mappedAction === "approved"
            ? "Approved"
            : mappedAction === "rejected"
              ? "Rejected"
              : "Revision requested",
        backend_sync_status: "pending",
      },
      {
        status: 200,
        headers: {
          "cache-control": "no-store, no-cache, must-revalidate",
        },
      }
    );
  }
}
''', encoding="utf-8")

print("ROW4_CLIENT_REVIEW_ACTION_SCOPE_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {route}")