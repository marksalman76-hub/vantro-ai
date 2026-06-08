import { NextRequest, NextResponse } from "next/server";
import { persistLatestDeliverable, resolveTenantKey } from "@/lib/deliverablePersistence";
import { persistExecutionState } from "@/lib/executionStateSync";
import { persistMediaAssets, attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";
import { attachRealMediaProviderDecision } from "@/lib/realMediaGenerationProviders";
import { attachAgentOutputContract } from "@/lib/allAgentOutputContracts";
import { attachPackageCreditEnforcement } from "@/lib/packageCreditEnforcement";
import { extractLiveActionDeliverableText } from "@/lib/liveActionResultExtraction";

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

function serverAdminToken(): string {
  return (
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.ADMIN_TOKEN ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  );
}

function trustedFrontendOrigin(req: NextRequest): string {
  return (
    req.headers.get("origin") ||
    process.env.FRONTEND_URL ||
    process.env.NEXT_PUBLIC_APP_URL ||
    "https://app.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminPortalAuthorised(req: NextRequest): boolean {
  const suppliedAdminToken = req.headers.get("x-admin-token") || req.headers.get("authorization");
  const expectedPortalAccess = process.env.PORTAL_ACCESS_CODE || "";
  const portalAccess = req.cookies.get("portal_access")?.value || "";
  const adminSession = req.cookies.get("admin_session")?.value || "";
  return Boolean(
    suppliedAdminToken ||
    (expectedPortalAccess && portalAccess === expectedPortalAccess) ||
    (expectedPortalAccess && adminSession === expectedPortalAccess)
  );
}

function backendProviderQueueHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    "x-tenant-key": tenantKey,
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token") || process.env.ADMIN_PLATFORM_TOKEN || "";
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

function backendCanonicalHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    "x-tenant-id": String(req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || tenantKey),
    "x-tenant-key": tenantKey,
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

function backendAdminMediaJobHeaders(req: NextRequest): Record<string, string> {
  const origin = trustedFrontendOrigin(req);
  const headers: Record<string, string> = {
    "content-type": "application/json",
    "cache-control": "no-store",
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "origin": origin,
    "referer": req.headers.get("referer") || `${origin}/admin`,
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token") || serverAdminToken();
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
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
  const extractedLiveDeliverable = extractLiveActionDeliverableText(payload, { customerSafe: true });

  return [
    extractedLiveDeliverable,
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
  const extractedLiveDeliverable = extractLiveActionDeliverableText(payload, { customerSafe: true });
  if (extractedLiveDeliverable) {
    payload.live_action_deliverable = extractedLiveDeliverable;
    payload.output = payload.output || extractedLiveDeliverable;
    payload.generated_output = payload.generated_output || extractedLiveDeliverable;
    payload.deliverable = payload.deliverable || {
      title: "Client deliverable",
      summary: "Live provider result ready for review.",
      output: extractedLiveDeliverable,
      generated_output: extractedLiveDeliverable,
      credential_values_exposed: false,
      customer_safe: true,
    };
  }
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

async function attachDurableProviderQueueRetryFailover(
  req: NextRequest,
  tenantKey: string,
  payload: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const decision = (payload.real_media_provider_decision || {}) as Record<string, unknown>;
  const provider = decision.provider_selected || payload.provider_selected || payload.provider || "unknown";
  const requestedCapability =
    payload.requested_media_capability ||
    decision.requested_capability ||
    payload.requested_capability ||
    payload.asset_type ||
    "provider_execution";

  try {
    const response = await fetch(`${backendBaseUrl()}/provider-queue-retry-failover`, {
      method: "POST",
      headers: backendProviderQueueHeaders(req, tenantKey),
      body: JSON.stringify({
        ...payload,
        tenant_id: String(payload.tenant_id || payload.tenant_key || tenantKey),
        tenant_key: tenantKey,
        provider,
        primary_provider: provider,
        requested_capability: requestedCapability,
        action_type: String(payload.action_type || requestedCapability),
        live_external_call_executed: false,
        external_action_performed: false,
      }),
      cache: "no-store",
    });
    const text = await response.text();
    const result = text ? JSON.parse(text) as Record<string, unknown> : {};
    const { success, ...providerQueueResult } = result;

    return {
      ...providerQueueResult,
      provider_queue_success: Boolean(success),
      provider_queue_retry_failover_enabled: Boolean(result.provider_queue_retry_failover_enabled ?? result.success),
      durable_provider_ledger_authority: "backend",
      live_external_call_executed: false,
      external_action_performed: false,
      credential_values_exposed: false,
    };
  } catch {
    return {
      provider_queue_success: false,
      provider_queue_retry_failover_enabled: false,
      durable_provider_ledger_available: false,
      durable_provider_ledger_authority: "backend",
      provider_queue_status: "provider_queue_backend_unavailable",
      client_safe: true,
      credential_values_exposed: false,
      live_external_call_executed: false,
      external_action_performed: false,
    };
  }
}

async function syncBackendCanonicalExecutionState(
  req: NextRequest,
  tenantKey: string,
  payload: Record<string, unknown>
): Promise<Record<string, unknown>> {
  try {
    const response = await fetch(`${backendBaseUrl()}/client-execution-state`, {
      method: "POST",
      headers: backendCanonicalHeaders(req, tenantKey),
      body: JSON.stringify({
        ...payload,
        tenant_id: String(payload.tenant_id || payload.tenant_key || tenantKey),
        tenant_key: tenantKey,
      }),
      cache: "no-store",
    });

    const text = await response.text();
    const result = text ? JSON.parse(text) as Record<string, unknown> : {};

    if (response.status < 500 && result.success !== false) {
      return {
        ...result,
        execution_state_authority: "backend_canonical",
        execution_state_backend_status: response.status,
        fallback_used: false,
        dev_only: false,
        production_fail_closed: false,
        credential_values_exposed: false,
      };
    }

    return {
      success: false,
      status: result.status || "backend_execution_state_unavailable",
      error: result.error || "backend_execution_state_unavailable",
      execution_state_backend_status: response.status,
      authority: "backend_canonical",
      fallback_used: false,
      dev_only: false,
      production_fail_closed: isProductionRuntime(),
      credential_values_exposed: false,
    };
  } catch (error) {
    return {
      success: false,
      status: "backend_execution_state_unavailable",
      error: error instanceof Error ? error.message : String(error),
      authority: "backend_canonical",
      fallback_used: false,
      dev_only: false,
      production_fail_closed: isProductionRuntime(),
      credential_values_exposed: false,
    };
  }
}

async function runBackendMediaJobsForDelegatedWorkforce(req: NextRequest): Promise<Record<string, unknown>> {
  if (!adminPortalAuthorised(req)) {
    return {
      success: false,
      authorised: false,
      processor_invoked: false,
      media_job_runner_triggered: false,
      media_job_runner_status: "admin_authorisation_required",
      processed_job_count: 0,
      processed_count: 0,
      final_status_counts: {},
      security_profile: "priority5_security_audit_enforcement_v1",
      auth_sources_checked: [
        "cookie:portal_access",
        "cookie:admin_session",
        "header:x-admin-token",
        "header:authorization",
      ],
      cookies_present: req.cookies.getAll().map((cookie) => cookie.name).filter(Boolean).sort(),
      reason: "missing_expected_admin_session_cookie",
      customer_safe: true,
      credential_values_exposed: false,
    };
  }

  try {
    const response = await fetch(`${backendBaseUrl()}/admin/media-jobs/run-all`, {
      method: "POST",
      headers: backendAdminMediaJobHeaders(req),
      cache: "no-store",
    });
    const text = await response.text();
    const result = text ? JSON.parse(text) as Record<string, unknown> : {};

    return {
      ...result,
      media_job_runner_triggered: response.status < 500 && result.success !== false,
      media_job_runner_status: response.status,
      credential_values_exposed: false,
    };
  } catch (error) {
    return {
      success: false,
      media_job_runner_triggered: false,
      media_job_runner_status: "unavailable",
      error: error instanceof Error ? error.message : String(error),
      customer_safe: true,
      credential_values_exposed: false,
    };
  }
}

async function proxyToBackend(req: NextRequest): Promise<NextResponse> {
  const body = await req.text();
  const headers: Record<string, string> = {
    "content-type": req.headers.get("content-type") || "application/json",
  };

  const auth = req.headers.get("authorization");
  const portalAdminAuthorised = adminPortalAuthorised(req);
  const adminToken = portalAdminAuthorised ? (req.headers.get("x-admin-token") || serverAdminToken()) : req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");
  const origin = trustedFrontendOrigin(req);

  if (auth) headers.authorization = auth;
  if (!auth && portalAdminAuthorised && adminToken) headers.authorization = `Bearer ${adminToken}`;
  if (portalAdminAuthorised && adminToken) headers["x-admin-token"] = adminToken;
  if (portalAdminAuthorised) {
    headers["x-actor-role"] = "owner_admin";
    headers["x-tenant-id"] = "owner_admin";
    headers.origin = origin;
    headers.referer = req.headers.get("referer") || `${origin}/admin`;
  }
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
  const backendExecutionAllowed = normalised.execution_allowed;
  const backendExecutionStatus = normalised.execution_status;
  Object.assign(normalised, attachPackageCreditEnforcement(stateTenantKey, req.headers, normalised, false));
  normalised.execution_allowed = backendExecutionAllowed;
  normalised.execution_status = backendExecutionStatus;
  normalised.package_credit_enforcement_authority = "frontend_advisory_only";
  Object.assign(normalised, attachAgentOutputContract(normalised));
  Object.assign(normalised, attachRealMediaProviderDecision(stateTenantKey, normalised));
  Object.assign(normalised, await attachDurableProviderQueueRetryFailover(req, stateTenantKey, normalised));
  const mediaJobRunner: Record<string, unknown> = {
    success: true,
    media_job_runner_triggered: false,
    media_job_runner_status: "explicit_admin_processor_route_required",
    authorised: portalAdminAuthorised,
    processor_invoked: false,
    processed_job_count: 0,
    processed_count: 0,
    final_status_counts: {},
    security_profile: "priority5_security_audit_enforcement_v1",
    customer_safe: true,
    credential_values_exposed: false,
  };
  normalised.media_job_runner_triggered = Boolean(mediaJobRunner.media_job_runner_triggered);
  normalised.media_job_runner_status = mediaJobRunner.status || mediaJobRunner.media_job_runner_status || "unknown";
  normalised.media_job_processed_count = Number(mediaJobRunner.processed_count || 0);
  normalised.media_job_runner_results = Array.isArray(mediaJobRunner.results) ? mediaJobRunner.results : [];
  normalised.credential_values_exposed = false;
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");
  normalised.media_asset_lifecycle_enabled = true;
  normalised.media_assets_persisted = persistedMediaAssets.length;
  const lifecyclePayload = attachMediaAssetLifecycle(stateTenantKey, normalised);
  Object.assign(normalised, lifecyclePayload);
  const backendExecutionState = await syncBackendCanonicalExecutionState(req, stateTenantKey, normalised);
  if (backendExecutionState.success !== false) {
    normalised.execution_state_synchronised = true;
    normalised.execution_state = backendExecutionState.execution_state;
    normalised.execution_state_authority = "backend_canonical";
    normalised.execution_state_backend_status = backendExecutionState.execution_state_backend_status;
    normalised.execution_state_fallback_used = false;
    normalised.execution_state_dev_only = false;
    normalised.execution_state_production_fail_closed = false;
  } else if (isProductionRuntime()) {
    normalised.execution_state_synchronised = false;
    normalised.execution_state = null;
    normalised.execution_state_authority = "backend_canonical";
    normalised.execution_state_status = backendExecutionState.status;
    normalised.execution_state_error = backendExecutionState.error;
    normalised.execution_state_fallback_used = false;
    normalised.execution_state_dev_only = false;
    normalised.execution_state_production_fail_closed = true;
  } else {
    const executionState = persistExecutionState(stateTenantKey, {
      ...normalised,
      authority: "frontend_advisory",
      fallback_used: true,
      dev_only: true,
    });
    normalised.execution_state_synchronised = true;
    normalised.execution_state = executionState;
    normalised.execution_state_authority = "frontend_advisory";
    normalised.execution_state_status = backendExecutionState.status;
    normalised.execution_state_fallback_used = true;
    normalised.execution_state_dev_only = true;
    normalised.execution_state_production_fail_closed = false;
  }

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
