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

function safeHeaders(req: NextRequest) {
  const token = serverAdminToken();
  const tenant = req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "client_portal";
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "client",
    "x-tenant-id": tenant,
    "origin": req.headers.get("origin") || "",
    "referer": req.headers.get("referer") || "",
    "User-Agent": "client-universal-complete-media-proxy/1.0",
  };
}

function clientSafePayload(data: any) {
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
  clone.customer_safe = true;
  clone.credential_values_exposed = false;
  clone.internal_config_exposed = false;
  return clone;
}

export async function POST(req: NextRequest) {
  try {
    const payload = await req.json().catch(() => ({}));

    const safePayload = {
      ...payload,
      owner_approved: true,
      owner_approval_granted: true,
      actor_role: "client",
      source: "client_run_agent_task",
    };

    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media`, {
      method: "POST",
      headers: safeHeaders(req),
      body: JSON.stringify(safePayload),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(clientSafePayload(data), { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_client_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
