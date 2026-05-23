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
    "x-tenant-id": "public_login",
    "x-actor-role": "customer",
    "Origin": "https://ecommerce-ai-agent-platform.vercel.app",
    "Referer": "https://ecommerce-ai-agent-platform.vercel.app/login",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }

  return headers;
}

export async function POST(request: NextRequest) {
  const form = await request.formData();

  const email = String(form.get("email") || "").trim().toLowerCase();
  const password = String(form.get("password") || "");
  const nextPath = String(form.get("next") || "/client");

  const response = await fetch(`${BACKEND_URL}/client/login`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "client_login_backend_response_not_json",
  }));

  if (!response.ok || !result.success || !result.session_token) {
    return NextResponse.redirect(
      new URL(`/login?next=${encodeURIComponent(nextPath)}&error=invalid_login`, request.url),
      { status: 303 }
    );
  }

  const redirect = NextResponse.redirect(new URL(nextPath || "/client", request.url), {
    status: 303,
  });

  redirect.cookies.set("client_session", result.session_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return redirect;
}
