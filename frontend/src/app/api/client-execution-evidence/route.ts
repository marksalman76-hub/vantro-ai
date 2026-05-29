import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const tenantId = searchParams.get("tenant_id") || "client_demo_001";
  const limit = searchParams.get("limit") || "25";

  const url = new URL(`${BACKEND_URL}/client/execution-evidence`);
  url.searchParams.set("tenant_id", tenantId);
  url.searchParams.set("limit", limit);

  const response = await fetch(url.toString(), {
    method: "GET",
    cache: "no-store",
    headers: {
      "x-tenant-id": tenantId,
    },
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  return NextResponse.json(
    {
      success: response.ok && data?.success === true,
      backend_status: response.status,
      data,
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: response.ok ? 200 : response.status }
  );
}
