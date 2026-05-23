import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

function backendHeaders() {
  return {
    "Content-Type": "application/json",
    "x-tenant-id": "client_business_profile",
    "x-actor-role": "customer",
    "Origin": "https://ecommerce-ai-agent-platform.vercel.app",
    "Referer": "https://ecommerce-ai-agent-platform.vercel.app/client",
  };
}

export async function GET(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/business-profile?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      headers: backendHeaders(),
      cache: "no-store",
    }
  );

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}

export async function POST(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

  const body = await request.json().catch(() => ({}));
  const profile = body?.profile || {};

  const response = await fetch(`${BACKEND_URL}/client/business-profile`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      session_token: sessionToken,
      profile,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}
