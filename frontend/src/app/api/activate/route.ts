import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function backendHeaders() {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": "public_activation",
    "x-actor-role": "admin",
    "Origin": "https://ecommerce-ai-agent-platform.vercel.app",
    "Referer": "https://ecommerce-ai-agent-platform.vercel.app/activate",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }

  return headers;
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const clientEmail = String(formData.get("email") || formData.get("client_email") || "");

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/admin/saas-provisioning/validate-one-time-link`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      token,
      client_email: clientEmail,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "activation_backend_response_not_json",
  }));

  if (!response.ok || !result.success || result.valid === false) {
    return NextResponse.json(
      {
        success: false,
        error: result.error || "activation_failed",
        backend_status: response.status,
        backend_result: result,
      },
      { status: 400 }
    );
  }

  return NextResponse.redirect(new URL("/login", request.url), { status: 303 });
}
