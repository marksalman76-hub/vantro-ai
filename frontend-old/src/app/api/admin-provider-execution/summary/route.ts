import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";


function isAdminRequest(req: Request): boolean {
  const expected = process.env.ADMIN_PLATFORM_TOKEN || "";
  if (!expected) return false;

  const auth = req.headers.get("authorization") || "";
  const adminHeader = req.headers.get("x-admin-token") || "";

  return auth === `Bearer ${expected}` || adminHeader === expected;
}

function unauthorizedAdminResponse() {
  return NextResponse.json(
    {
      success: false,
      error: "unauthorized",
      message: "Admin access required.",
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: 401 }
  );
}

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function GET(req: Request) {
  if (!isAdminRequest(req)) {
    return unauthorizedAdminResponse();
  }

  if (!backendUrl || !adminToken) {
    return NextResponse.json(
      {
        ready: false,
        jobs: [],
        summary: {},
        delivery_packets: [],
        retry_timeout: {},
        credential_values_exposed: false,
        error: "Provider execution admin summary is not configured.",
      },
      { status: 503 }
    );
  }

  const response = await fetch(`${backendUrl}/provider-execution-admin-visibility/summary`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${adminToken}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    ready: false,
    jobs: [],
    summary: {},
    delivery_packets: [],
    retry_timeout: {},
    error: "Invalid provider execution admin summary response.",
  }));

  return NextResponse.json(
    {
      ...data,
      credential_values_exposed: false,
    },
    { status: response.status }
  );
}
