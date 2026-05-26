import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function extractToken(payload: any): string {
  return (
    payload?.token ||
    payload?.session_token ||
    payload?.access_token ||
    payload?.client_token ||
    payload?.auth_token ||
    payload?.session?.token ||
    payload?.session?.session_token ||
    payload?.data?.token ||
    payload?.data?.session_token ||
    payload?.data?.access_token ||
    ""
  );
}

function extractTenant(payload: any): string {
  return (
    payload?.tenant_id ||
    payload?.tenantId ||
    payload?.client?.tenant_id ||
    payload?.account?.tenant_id ||
    payload?.data?.tenant_id ||
    payload?.data?.client?.tenant_id ||
    "tenant_unknown"
  );
}

export async function POST(req: NextRequest) {
  const formData = await req.formData();

  const email = String(formData.get("email") || "").trim().toLowerCase();
  const password = String(formData.get("password") || "");
  const nextPath = String(formData.get("next") || "/client");

  const payloadBody = JSON.stringify({ email, password });

  const res = await fetch(`${BACKEND_URL}/client/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-actor-role": "client",
      "x-tenant-id": "tenant_unknown",
      origin: req.headers.get("origin") || "",
      referer: req.headers.get("referer") || "",
    },
    body: payloadBody,
    cache: "no-store",
  });

  const text = await res.text();

  let payload: any = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = {};
  }

  const token = extractToken(payload);
  const tenantId = extractTenant(payload);

  if (!res.ok || !payload?.success || !token) {
    return NextResponse.redirect(new URL("/login?error=1", req.url), {
      status: 302,
    });
  }

  const response = NextResponse.redirect(new URL(nextPath, req.url), {
    status: 302,
  });

  response.cookies.set("client_token", token, {
    httpOnly: false,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  response.cookies.set("tenant_id", tenantId, {
    httpOnly: false,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  return response;
}