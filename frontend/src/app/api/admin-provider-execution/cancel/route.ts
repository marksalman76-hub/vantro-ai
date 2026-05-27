import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function POST(request: NextRequest) {
  if (!backendUrl || !adminToken) {
    return NextResponse.json(
      {
        ready: false,
        accepted: false,
        credential_values_exposed: false,
        error: "Provider execution admin action is not configured.",
      },
      { status: 503 }
    );
  }

  const body = await request.json().catch(() => ({}));

  const response = await fetch(`${backendUrl}/provider-execution-admin-visibility/actions/cancel`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${adminToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: body.job_id,
      reason: body.reason || "Admin provider execution dashboard action.",
    }),
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    ready: false,
    accepted: false,
    error: "Invalid provider execution action response.",
  }));

  return NextResponse.json(
    {
      ...data,
      credential_values_exposed: false,
    },
    { status: response.status }
  );
}
