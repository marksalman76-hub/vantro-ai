import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { getExecutionState } from "@/lib/executionStateSync";
import { getLatestDeliverable } from "@/lib/deliverablePersistence";
import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";
import { getBusinessProfile } from "@/lib/businessProfilePersistence";
import { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";

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

function forwardHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || tenantKey,
    "x-tenant-key": tenantKey,
  };
  const auth = req.headers.get("authorization");
  const cookie = req.headers.get("cookie");
  const clientToken = req.cookies.get("client_token")?.value;
  if (auth) headers.authorization = auth;
  if (!auth && clientToken) headers.authorization = `Bearer ${clientToken}`;
  if (cookie) headers.cookie = cookie;
  return headers;
}

function statusLabel(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) return value.trim();
  return fallback;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  let executionState = getExecutionState(tenantKey);
  let executionStateAuthority: "backend_canonical" | "frontend_advisory" = "frontend_advisory";
  let executionStateFallbackUsed = true;

  try {
    const response = await fetch(`${backendBaseUrl()}/client-execution-state?tenant_id=${encodeURIComponent(tenantKey)}`, {
      method: "GET",
      headers: forwardHeaders(req, tenantKey),
      cache: "no-store",
    });
    const payload = await response.json().catch(() => ({ success: false }));
    if (response.status < 500 && payload.success !== false) {
      executionState = (payload.execution_state || null) as typeof executionState;
      executionStateAuthority = "backend_canonical";
      executionStateFallbackUsed = false;
    } else if (isProductionRuntime()) {
      return NextResponse.json({
        success: false,
        status: "backend_canonical_unavailable",
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: true,
        credential_values_exposed: false,
      }, {
        status: response.status >= 400 ? response.status : 503,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  } catch {
    if (isProductionRuntime()) {
      return NextResponse.json({
        success: false,
        status: "backend_canonical_unavailable",
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: true,
        credential_values_exposed: false,
      }, {
        status: 503,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  }

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

  const visibilitySync = buildAdminClientExecutionVisibilityPacket(tenantKey, "client");

  return NextResponse.json({
    success: true,
    execution_state_synchronised: true,
    authority: executionStateAuthority,
    fallback_used: executionStateFallbackUsed,
    dev_only: executionStateAuthority === "frontend_advisory",
    production_fail_closed: false,
    admin_client_execution_visibility_sync_enabled: true,
    visibility_sync: visibilitySync,
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
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
