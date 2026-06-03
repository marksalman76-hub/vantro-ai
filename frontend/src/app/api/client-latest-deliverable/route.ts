import { NextRequest, NextResponse } from "next/server";
import { getLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";
import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";
import { mergeExecutionState, persistExecutionState } from "@/lib/executionStateSync";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function isMeaningfulValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return false;
    return !["completed", "complete", "success", "successful", "done", "pending", "null", "undefined"].includes(trimmed.toLowerCase());
  }
  if (Array.isArray(value)) return value.some(isMeaningfulValue);
  if (typeof value === "object") return Object.values(value as Record<string, unknown>).some(isMeaningfulValue);
  return true;
}

function normalise(payload: Record<string, unknown>): Record<string, unknown> {
  const result = (payload.result || {}) as Record<string, unknown>;
  const data = (payload.data || {}) as Record<string, unknown>;
  const asset = (payload.asset || result.asset || data.asset || {}) as Record<string, unknown>;

  const candidates = [
    payload.output, payload.deliverable, payload.latest_deliverable, payload.generated_output, payload.final_output,
    result.output, result.deliverable, result.latest_deliverable, result.generated_output, result.final_output,
    data.output, data.deliverable, data.latest_deliverable, data.generated_output, data.final_output,
    payload.asset, payload.assets, result.asset, result.assets, data.asset, data.assets,
    asset.preview_url, asset.download_url, asset.url, asset.public_url, asset.signed_preview_url, asset.signed_download_url,
  ];

  const hasRealOutput = candidates.some(isMeaningfulValue);

  return {
    ...payload,
    has_real_output: hasRealOutput,
    client_output_truth_checked: true,
    client_safe_status: hasRealOutput ? "Completed" : "Output pending",
    display_status: hasRealOutput ? "Completed" : "Output pending",
    output_truth_reason: hasRealOutput
      ? "A real deliverable, output, or generated asset was returned."
      : "No real deliverable, output, or generated asset was returned.",
  };
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const headers: Record<string, string> = {};
  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  const response = await fetch(`${backendBaseUrl()}/client-latest-deliverable`, {
    method: "GET",
    headers,
    cache: "no-store",
  });

  const text = await response.text();

  let payload: unknown;
  try {
    payload = JSON.parse(text);
  } catch {
    return NextResponse.json({
      success: false,
      has_real_output: false,
      client_output_truth_checked: true,
      client_safe_status: "Output pending",
      display_status: "Output pending",
      output_truth_reason: "Latest deliverable route did not return JSON.",
    }, { status: response.status });
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return NextResponse.json({
      success: false,
      has_real_output: false,
      client_output_truth_checked: true,
      client_safe_status: "Output pending",
      display_status: "Output pending",
      output_truth_reason: "Latest deliverable response was empty.",
    }, { status: response.status });
  }

  
  const tenantKey = resolveTenantKey(req.headers, payload as Record<string, unknown>);
  const approvalHistory = getApprovalRevisionHistory(tenantKey);

const normalised = normalise(payload as Record<string, unknown>);

  if (normalised.has_real_output === false) {
    const tenantKey = resolveTenantKey(req.headers, normalised);
    const persisted = getLatestDeliverable(tenantKey);
    if (persisted) {
      const persistedPayload = {
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
      });
    }
  }

  const latestPayload = mergeExecutionState(tenantKey, {
    ...normalised,
    approval_revision_history: approvalHistory,
    latest_review_action: approvalHistory[0] || null,
    deliverable_persisted: false,
    persistence_source: "backend_latest_deliverable_route",
  });

  return NextResponse.json(latestPayload, {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
