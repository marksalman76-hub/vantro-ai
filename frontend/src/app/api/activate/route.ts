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
    "Content-Type": "application/json",
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const password = String(formData.get("password") || "");
  const confirmPassword = String(formData.get("confirm_password") || "");

  const response = await fetch(`${BACKEND_URL}/client/activate-account`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      token,
      password,
      confirm_password: confirmPassword,
    }),
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "activation_backend_response_not_json",
  }));

  if (!result.success) {
    return new NextResponse(`Activation failed: ${result.error}`, {
      status: 400,
    });
  }

  return NextResponse.redirect(new URL("/login", request.url));
}
