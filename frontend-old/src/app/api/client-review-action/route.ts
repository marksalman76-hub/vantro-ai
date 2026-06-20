import { NextRequest, NextResponse } from "next/server";
import { persistApprovalRevisionEvent, getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";
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

function isProductionRuntime(): boolean {
  return process.env.NODE_ENV === "production";
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

function buildForwardHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || tenantKey,
    "x-tenant-key": req.headers.get("x-tenant-key") || tenantKey,
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");
  const clientToken = req.cookies.get("client_token")?.value;

  if (auth) headers.authorization = auth;
  if (!auth && clientToken) headers.authorization = `Bearer ${clientToken}`;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

function clientSafeStatus(action: "approved" | "rejected" | "revision_requested"): string {
  if (action === "approved") return "Approved";
  if (action === "rejected") return "Rejected";
  return "Revision requested";
}

function productionFailClosed(message: string, status = 503): NextResponse {
  return NextResponse.json({
    success: false,
    status: "backend_canonical_unavailable",
    error: message,
    authority: "backend_canonical",
    fallback_used: false,
    dev_only: false,
    production_fail_closed: true,
    approval_revision_event_saved: false,
    latest_review_action: null,
    credential_values_exposed: false,
  }, {
    status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  try {
    const response = await fetch(`${backendBaseUrl()}/client-review-action?tenant_id=${encodeURIComponent(tenantKey)}`, {
      method: "GET",
      headers: buildForwardHeaders(req, tenantKey),
      cache: "no-store",
    });
    const payload = await response.json().catch(() => ({ success: false, error: "invalid_backend_response" }));

    if (response.status < 500 && payload.success !== false) {
      return NextResponse.json({
        ...payload,
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: false,
        credential_values_exposed: false,
      }, {
        status: response.status,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }

    if (isProductionRuntime()) {
      return productionFailClosed(String(payload.error || payload.status || "backend_review_history_unavailable"), response.status >= 400 ? response.status : 503);
    }
  } catch (error) {
    if (isProductionRuntime()) {
      return productionFailClosed(error instanceof Error ? error.message : String(error));
    }
  }

  const history = getApprovalRevisionHistory(tenantKey);
  return NextResponse.json({
    success: true,
    authority: "frontend_advisory",
    fallback_used: true,
    dev_only: true,
    production_fail_closed: false,
    approval_revision_history: history,
    latest_review_action: history[0] || null,
    count: history.length,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
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

  try {
    const response = await fetch(`${backendBaseUrl()}/client-review-action`, {
      method: "POST",
      headers: buildForwardHeaders(req, tenantKey),
      body: JSON.stringify({
        ...body,
        tenant_id: String(body.tenant_id || body.tenant_key || tenantKey),
        mapped_review_action: mappedAction,
      }),
      cache: "no-store",
    });

    const text = await response.text();
    let backendPayload: Record<string, unknown> = {};
    try {
      backendPayload = text ? JSON.parse(text) : {};
    } catch {
      backendPayload = { backend_response_text: text };
    }

    if (response.status < 500 && backendPayload.success !== false) {
      let advisoryEvent = null;
      if (!isProductionRuntime()) {
        advisoryEvent = persistApprovalRevisionEvent(tenantKey, {
          action: mappedAction,
          actor_type: "client",
          comment: String(body.comment || body.feedback || body.revision_notes || ""),
          deliverable_id: body.deliverable_id ? String(body.deliverable_id) : null,
          deliverable_status: mappedAction,
        });
      }

      return NextResponse.json(
        {
          ...backendPayload,
          success: true,
          authority: "backend_canonical",
          fallback_used: false,
          dev_only: false,
          production_fail_closed: false,
          frontend_advisory_review_cached: Boolean(advisoryEvent),
          client_safe_status: clientSafeStatus(mappedAction),
          credential_values_exposed: false,
        },
        {
          status: response.status,
          headers: {
            "cache-control": "no-store, no-cache, must-revalidate",
          },
        }
      );
    }

    if (isProductionRuntime()) {
      return productionFailClosed(String(backendPayload.error || backendPayload.status || "backend_review_action_unavailable"), response.status >= 400 ? response.status : 503);
    }
  } catch (error) {
    if (isProductionRuntime()) {
      return productionFailClosed(error instanceof Error ? error.message : String(error));
    }
  }

  const persistedEvent = persistApprovalRevisionEvent(tenantKey, {
    action: mappedAction,
    actor_type: "client",
    comment: String(body.comment || body.feedback || body.revision_notes || ""),
    deliverable_id: body.deliverable_id ? String(body.deliverable_id) : null,
    deliverable_status: mappedAction,
  });

  return NextResponse.json(
    {
      success: true,
      authority: "frontend_advisory",
      fallback_used: true,
      dev_only: true,
      production_fail_closed: false,
      approval_revision_event_saved: true,
      approval_revision_event_id: persistedEvent.id,
      latest_review_action: persistedEvent,
      client_safe_status: clientSafeStatus(mappedAction),
      backend_sync_status: "pending",
      credential_values_exposed: false,
    },
    {
      status: 200,
      headers: {
        "cache-control": "no-store, no-cache, must-revalidate",
      },
    }
  );
}
