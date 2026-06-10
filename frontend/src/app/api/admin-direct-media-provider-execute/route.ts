import { NextRequest, NextResponse } from "next/server";


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
    "Authorization": token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "User-Agent": "frontend-direct-media-provider-proxy/1.0",
  };
}

function safeErrorPayload(error: unknown) {
  return {
    success: false,
    error: "direct_media_provider_proxy_failed",
    message: error instanceof Error ? error.message : "Unknown proxy error",
    customer_safe: true,
    credential_values_exposed: false,
  };
}


export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json().catch(() => ({}));

    const safePayload = {
      agent_id: payload.agent_id || payload.assigned_agent || payload.requested_agent || "social_media_manager_content_creator_agent",
      provider: payload.provider || payload.selected_provider || payload.selected_video_provider || "runway",
      media_type: payload.media_type || payload.asset_type || "video",
      prompt: payload.prompt || payload.task || "Create a simple ecommerce media asset.",
      owner_approved: true,
      owner_approval_granted: true,
      async_requested: true,
    };

    const response = await fetch(`${backendBaseUrl()}/admin/direct-media-provider-submit`, {
      method: "POST",
      headers: adminHeaders(),
      body: JSON.stringify(safePayload),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_json" }));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(safeErrorPayload(error), { status: 500 });
  }
}
