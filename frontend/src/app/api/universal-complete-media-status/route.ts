import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBaseUrl() {
  return (
    process.env.BACKEND_BASE_URL ||
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function serverAdminToken() {
  return (
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.ADMIN_BEARER_TOKEN ||
    process.env.ADMIN_TOKEN ||
    process.env.PLATFORM_ADMIN_TOKEN ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  ).trim();
}

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}


function isGenericReadinessPayload(data: any, jobId: string) {
  if (!data || typeof data !== "object") return false;
  const returnedJobId = String(data.job_id || data.media_job_id || data.id || "");
  if (returnedJobId && returnedJobId === jobId) return false;

  return Boolean(
    data.universal_complete_media_workflow_ready === true &&
    Array.isArray(data.supported_controls) &&
    !returnedJobId
  );
}

function decorateMediaAssetUrls(data: any) {
  if (data?.composition_job_id) {
    data.preview_url = `/api/universal-complete-media-asset?job_id=${encodeURIComponent(data.composition_job_id)}`;
    data.signed_preview_url = data.preview_url;
    data.download_url = data.preview_url;
  }

  if (data?.job_id && data?.status === "completed" && !data.preview_url) {
    data.preview_url = `/api/universal-complete-media-asset?job_id=${encodeURIComponent(data.job_id)}`;
    data.signed_preview_url = data.preview_url;
    data.download_url = data.preview_url;
  }

  return data;
}

function clientSafeStatusPayload(data: any) {
  if (!data || typeof data !== "object") return data;

  const clone = { ...data };
  delete clone.admin_provider_diagnostics;
  delete clone.safe_provider_diagnostics;
  delete clone.runway_key_diagnostics;
  delete clone.direct_provider_snapshot;
  delete clone.orchestrator_events;
  delete clone.raw_provider_status;
  delete clone.provider_result;
  delete clone.error;
  delete clone.preflight;
  delete clone.failed_preflight_checks;
  delete clone.blocked_provider_calls;
  delete clone.estimated_credit_risk;
  delete clone.executable_visual_providers;
  delete clone.non_executable_visual_providers;
  delete clone.executable_audio_providers;
  delete clone.selected_visual_provider_order;
  delete clone.selected_audio_provider;
  delete clone.media_script_packet;
  delete clone.lead_scripting_agent;
  delete clone.contributing_scripting_agents;
  if (Array.isArray(clone.segment_plan)) {
    clone.segment_plan = clone.segment_plan.map((segment: any) => {
      const { segment_prompt, visual_prompt, provider_prompt, ...safeSegment } = segment || {};
      return safeSegment;
    });
  }
  if (Array.isArray(clone.generated_segments)) {
    clone.generated_segments = clone.generated_segments.map((segment: any) => {
      const { segment_prompt, visual_prompt, provider_result, safe_error_summary, ...safeSegment } = segment || {};
      return safeSegment;
    });
  }

  if (Array.isArray(clone.failed_provider_attempts)) {
    clone.failed_provider_attempts = clone.failed_provider_attempts.map((attempt: any) => ({
      provider: attempt?.provider,
      status: attempt?.status,
      job_id: attempt?.job_id,
      safe_error_summary: attempt?.safe_error_summary,
      customer_safe: true,
      credential_values_exposed: false,
    }));
  }

  clone.customer_safe = true;
  clone.credential_values_exposed = false;
  clone.internal_config_exposed = false;
  return clone;
}

export async function GET(req: NextRequest) {
  const jobId = req.nextUrl.searchParams.get("job_id") || "";

  if (!jobId) {
    return NextResponse.json(
      { success: false, status: "missing_job_id", customer_safe: true, credential_values_exposed: false },
      { status: 400 }
    );
  }

  const token = serverAdminToken();
  const headers: Record<string, string> = {
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "client",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "owner_admin",
    "x-requested-from": "universal_complete_media_status_proxy",
  };

  const isUniversalJob = jobId.startsWith("universal_complete_media_job_");

  const statusUrls = isUniversalJob
    ? [
        `${backendBaseUrl()}/admin/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
      ]
    : [
        `${backendBaseUrl()}/admin/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
        `${backendBaseUrl()}/admin/direct-media-provider-job-status/${encodeURIComponent(jobId)}`,
      ];

  let lastError = "";

  for (const url of statusUrls) {
    try {
      const response = await fetchWithTimeout(
        url,
        {
          method: "GET",
          headers,
          cache: "no-store",
        },
        7000
      );

      const data = await response.json().catch(() => ({
        success: false,
        error: "invalid_backend_json",
        job_id: jobId,
        customer_safe: true,
        credential_values_exposed: false,
      }));

      if (isGenericReadinessPayload(data, jobId)) {
        lastError = "Backend returned generic universal media readiness instead of job status.";
        continue;
      }

      return NextResponse.json(clientSafeStatusPayload(decorateMediaAssetUrls(data)), { status: response.status });
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
  }

  return NextResponse.json(
    {
      success: false,
      status: isUniversalJob ? "job_status_not_returned" : "status_lookup_timeout",
      job_id: jobId,
      message: isUniversalJob
        ? "Backend did not return a per-job status for this universal complete media job."
        : "Universal complete media status lookup timed out before a backend response was available.",
      last_error: lastError,
      polling_required: true,
      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    },
    { status: 202 }
  );
}
