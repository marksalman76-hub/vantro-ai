import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function GET() {
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
