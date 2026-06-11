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

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const jobId = String(url.searchParams.get("job_id") || "").trim();

    if (!jobId) {
      return NextResponse.json(
        {
          success: false,
          error: "missing_job_id",
          customer_safe: true,
          credential_values_exposed: false,
        },
        { status: 400 }
      );
    }

    const token = adminToken();
    const response = await fetch(`${backendBaseUrl()}/admin/direct-media-provider-asset/${encodeURIComponent(jobId)}`, {
      method: "GET",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
        "x-admin-token": token,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
        "User-Agent": "frontend-direct-media-asset-proxy/1.0",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      return new NextResponse(text || "Direct media asset unavailable", {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("Content-Type") || "text/plain",
        },
      });
    }

    const contentType = response.headers.get("Content-Type") || "application/octet-stream";
    const body = await response.arrayBuffer();

    return new NextResponse(body, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "direct_media_asset_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown asset proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
