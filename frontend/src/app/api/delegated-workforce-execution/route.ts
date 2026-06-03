import { NextRequest, NextResponse } from "next/server";
import { persistLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";
import { persistExecutionState } from "@/lib/executionStateSync";
import { persistMediaAssets, attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";
import { attachRealMediaProviderDecision } from "@/lib/realMediaGenerationProviders";
import { attachProviderQueueRetryFailover } from "@/lib/providerQueueRetryFailover";
import { attachAgentOutputContract } from "@/lib/allAgentOutputContracts";
import { attachPackageCreditEnforcement } from "@/lib/packageCreditEnforcement";

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
    const emptyMarkers = new Set([
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
    ]);
    return !emptyMarkers.has(trimmed.toLowerCase());
  }
  if (Array.isArray(value)) return value.some(isMeaningfulValue);
  if (typeof value === "object") return Object.values(value as Record<string, unknown>).some(isMeaningfulValue);
  return true;
}

function pickOutputCandidates(payload: Record<string, unknown>): unknown[] {
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

function hasRealClientOutput(payload: Record<string, unknown>): boolean {
  return pickOutputCandidates(payload).some(isMeaningfulValue);
}

function normaliseClientExecutionTruth(raw: unknown): unknown {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return raw;

  const payload = { ...(raw as Record<string, unknown>) };
  const hasRealOutput = hasRealClientOutput(payload);

  payload.has_real_output = hasRealOutput;
  payload.client_output_truth_checked = true;

  if (!hasRealOutput) {
    payload.completed = false;
    payload.is_completed = false;
    payload.workflow_status = "awaiting_output";
    payload.execution_status = "awaiting_output";
    payload.status = "awaiting_output";
    payload.client_safe_status = "Output pending";
    payload.display_status = "Output pending";
    payload.output_truth_reason = "No real deliverable, output, or generated asset was returned.";
  } else {
    payload.client_safe_status = "Completed";
    payload.display_status = "Completed";
    payload.output_truth_reason = "A real deliverable, output, or generated asset was returned.";
  }

  return payload;
}

async function proxyToBackend(req: NextRequest): Promise<NextResponse> {
  const body = await req.text();
  const headers: Record<string, string> = {
    "content-type": req.headers.get("content-type") || "application/json",
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  const response = await fetch(`${backendBaseUrl()}/delegated-workforce-execution`, {
    method: "POST",
    headers,
    body,
    cache: "no-store",
  });

  const text = await response.text();

  let payload: unknown;
  try {
    payload = JSON.parse(text);
  } catch {
    return new NextResponse(text, { status: response.status });
  }

  const normalised = normaliseClientExecutionTruth(payload) as Record<string, unknown>;

  if (normalised.has_real_output === true) {
    const tenantKey = resolveTenantKey(req.headers, normalised);
    const persisted = persistLatestDeliverable(tenantKey, normalised, "delegated_workforce_execution");
    normalised.deliverable_persisted = Boolean(persisted);
    normalised.persisted_deliverable_id = persisted?.id || null;
  } else {
    normalised.deliverable_persisted = false;
    normalised.persisted_deliverable_id = null;
  }

  const stateTenantKey = resolveTenantKey(req.headers, normalised);
  Object.assign(normalised, attachPackageCreditEnforcement(stateTenantKey, req.headers, normalised, true));
  Object.assign(normalised, attachAgentOutputContract(normalised));
  Object.assign(normalised, attachRealMediaProviderDecision(stateTenantKey, normalised));
  Object.assign(normalised, attachProviderQueueRetryFailover(stateTenantKey, normalised));
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");
  normalised.media_asset_lifecycle_enabled = true;
  normalised.media_assets_persisted = persistedMediaAssets.length;
  const lifecyclePayload = attachMediaAssetLifecycle(stateTenantKey, normalised);
  Object.assign(normalised, lifecyclePayload);
  const executionState = persistExecutionState(stateTenantKey, normalised);
  normalised.execution_state_synchronised = true;
  normalised.execution_state = executionState;

  return NextResponse.json(normalised, {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  return proxyToBackend(req);
}
