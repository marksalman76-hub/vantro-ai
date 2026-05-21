import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function backendHeaders() {
  const headers: Record<string, string> = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token") || "";

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/activation-invite-status?token=${encodeURIComponent(token)}`,
    {
      cache: "no-store",
      headers: backendHeaders(),
    }
  );

  const data = await response.json().catch(() => ({
    success: false,
    error: "activation_status_backend_response_not_json",
  }));

  return NextResponse.json(data, { status: response.status });
}
