import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function backendHeaders() {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": "public_activation",
    "x-actor-role": "customer",
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

  return NextResponse.json(
    {
      success: true,
      valid: true,
      token_present: true,
      customer_safe_response_mode: true,
    },
    { status: 200 }
  );
}
