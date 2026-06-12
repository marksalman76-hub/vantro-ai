from pathlib import Path
from datetime import datetime

backup_dir = Path("backups") / f"universal_media_status_fast_timeout_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

files = {
    "frontend/src/app/api/admin-universal-complete-media/route.ts": r'''import { NextRequest, NextResponse } from "next/server";

function backendBaseUrl() {
  return (
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminToken() {
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

function adminHeaders() {
  const token = adminToken();

  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "x-requested-from": "admin_universal_complete_media_proxy",
    "User-Agent": "frontend-admin-universal-complete-media-proxy/1.0",
  };
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

function safeTimeoutResponse(jobId: string, route: string, message: string) {
  return NextResponse.json(
    {
      success: false,
      status: "status_lookup_timeout",
      job_id: jobId || null,
      route,
      message,
      polling_required: true,
      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    },
    { status: 202 }
  );
}

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  const jobId = request.nextUrl.searchParams.get("job_id") || "";
  const qs = jobId ? `?job_id=${encodeURIComponent(jobId)}` : "";

  try {
    const response = await fetchWithTimeout(
      `${backendBaseUrl()}/admin/universal-complete-media-status${qs}`,
      {
        method: "GET",
        headers: adminHeaders(),
        cache: "no-store",
      },
      8000
    );

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      job_id: jobId || null,
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown proxy error";
    if (message.toLowerCase().includes("abort") || message.toLowerCase().includes("timeout")) {
      return safeTimeoutResponse(
        jobId,
        "admin-universal-complete-media",
        "Backend universal complete media status lookup timed out. Returning fast so the popup does not hang."
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: "admin_universal_complete_media_status_proxy_failed",
        message,
        job_id: jobId || null,
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json().catch(() => ({}));

    const safePayload = {
      ...payload,

      prompt:
        payload.prompt ||
        payload.task ||
        payload.creative_brief ||
        payload.user_prompt ||
        payload.complete_media_config?.prompt ||
        "",

      task:
        payload.task ||
        payload.prompt ||
        payload.creative_brief ||
        payload.user_prompt ||
        payload.complete_media_config?.task ||
        "",

      agent_id:
        payload.agent_id ||
        payload.selected_agent ||
        payload.lead_agent_id ||
        payload.complete_media_config?.agent_id ||
        "ugc_creative_agent",

      selected_agent:
        payload.selected_agent ||
        payload.agent_id ||
        payload.lead_agent_id ||
        payload.complete_media_config?.selected_agent ||
        "ugc_creative_agent",

      selected_agents:
        payload.selected_agents ||
        payload.agent_ids ||
        payload.complete_media_config?.selected_agents ||
        [],

      agent_ids:
        payload.agent_ids ||
        payload.selected_agents ||
        payload.complete_media_config?.agent_ids ||
        [],

      output_type:
        payload.output_type ||
        payload.complete_media_config?.output_type ||
        "Complete video with voiceover",

      platform:
        payload.platform ||
        payload.complete_media_config?.platform ||
        "General",

      duration_seconds:
        payload.duration_seconds ||
        payload.complete_media_config?.duration_seconds ||
        5,

      aspect_ratio:
        payload.aspect_ratio ||
        payload.complete_media_config?.aspect_ratio ||
        "16:9",

      language:
        payload.language ||
        payload.complete_media_config?.language ||
        "English",

      accent:
        payload.accent ||
        payload.complete_media_config?.accent ||
        "",

      video_provider:
        payload.video_provider ||
        payload.complete_media_config?.video_provider ||
        "runway",

      audio_provider:
        payload.audio_provider ||
        payload.complete_media_config?.audio_provider ||
        "elevenlabs",

      media_type: "complete_video",
      asset_type: "video",
      provider: "universal_complete_media_workflow",

      source: "admin_universal_complete_media_proxy",
      requested_from:
        payload.requested_from ||
        payload.source ||
        "complete_media_popup",

      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      native_popup_execution: Boolean(payload.native_popup_execution),
      run_direct_from_popup: Boolean(payload.run_direct_from_popup),

      owner_approved: true,
      owner_approval_granted: true,
      owner_admin_unrestricted: true,

      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    };

    const response = await fetchWithTimeout(
      `${backendBaseUrl()}/admin/universal-complete-media`,
      {
        method: "POST",
        headers: adminHeaders(),
        body: JSON.stringify(safePayload),
        cache: "no-store",
      },
      25000
    );

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_universal_complete_media_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
''',

    "frontend/src/app/api/universal-complete-media-status/route.ts": r'''import { NextRequest, NextResponse } from "next/server";

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
    "x-actor-role": "owner_admin",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "owner_admin",
    "x-requested-from": "universal_complete_media_status_proxy",
  };

  const statusUrls = [
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

      return NextResponse.json(decorateMediaAssetUrls(data), { status: response.status });
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
  }

  return NextResponse.json(
    {
      success: false,
      status: "status_lookup_timeout",
      job_id: jobId,
      message: "Universal complete media status lookup timed out before a backend response was available.",
      last_error: lastError,
      polling_required: true,
      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    },
    { status: 202 }
  );
}
''',

    "frontend/src/app/api/admin-media-jobs/route.ts": r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

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

export async function GET() {
  const headers: Record<string, string> = {
    "Cache-Control": "no-store",
    "x-actor-role": "owner_admin",
  };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }

  try {
    const response = await fetchWithTimeout(
      `${backendBaseUrl()}/admin/media-jobs`,
      {
        method: "GET",
        cache: "no-store",
        headers,
      },
      8000
    );

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      jobs: [],
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        status: "media_jobs_lookup_timeout",
        jobs: [],
        message: error instanceof Error ? error.message : String(error),
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 202, headers: { "Cache-Control": "no-store" } }
    );
  }
}
''',

    "frontend/src/app/api/admin-creative-media-assets/route.ts": r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

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

export async function GET() {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
      "x-actor-role": "owner_admin",
    };

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
    }

    const response = await fetchWithTimeout(
      `${backendBaseUrl()}/admin/creative/media-assets`,
      {
        method: "GET",
        cache: "no-store",
        headers,
      },
      8000
    );

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      assets: [],
      media_assets: [],
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        layer: "frontend_admin_creative_media_assets_proxy",
        status: "media_assets_lookup_timeout",
        assets: [],
        media_assets: [],
        error: error instanceof Error ? error.message : String(error),
        credential_values_exposed: false,
      },
      { status: 202, headers: { "Cache-Control": "no-store" } }
    );
  }
}
''',
}

for filename, content in files.items():
  p = Path(filename)
  if p.exists():
    (backup_dir / filename.replace("/", "__")).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(content, encoding="utf-8")

print("UNIVERSAL_MEDIA_STATUS_FAST_TIMEOUT_ROUTES_FIXED")
print(f"Backup: {backup_dir}")
for filename in files:
  print(f"Updated: {filename}")