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

export async function GET(req: NextRequest) {
  try {
    const jobId = req.nextUrl.searchParams.get("job_id") || "";
    if (!jobId) {
      return NextResponse.json(
        { success: false, status: "missing_job_id", customer_safe: true, credential_values_exposed: false },
        { status: 400 }
      );
    }

    const token = serverAdminToken();
    const response = await fetch(`${backendBaseUrl()}/admin/direct-media-provider-asset/${encodeURIComponent(jobId)}`, {
      method: "GET",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
        "x-admin-token": token,
        "x-actor-role": "client",
        "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "client_portal",
      },
      cache: "no-store",
    });

    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") || "application/octet-stream",
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_asset_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
