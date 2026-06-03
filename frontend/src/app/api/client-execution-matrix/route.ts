import { NextRequest, NextResponse } from "next/server";
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
