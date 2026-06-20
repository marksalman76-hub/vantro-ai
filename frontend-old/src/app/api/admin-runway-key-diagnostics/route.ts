import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBaseUrl() {
  return (
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminToken() {
  return (
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.ADMIN_BEARER_TOKEN ||
    process.env.ADMIN_TOKEN ||
    process.env.PLATFORM_ADMIN_TOKEN ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  ).trim();
}

function adminHeaders() {
  const token = adminToken();
  return {
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "x-requested-from": "admin_runway_key_diagnostics_proxy",
    "User-Agent": "frontend-admin-runway-key-diagnostics-proxy/1.0",
  };
}

function stripAnyAccidentalSecretFields(data: any) {
  if (!data || typeof data !== "object") return data;
  const clone = { ...data };
  delete clone.value;
  delete clone.secret;
  delete clone.token;
  delete clone.api_key;
  delete clone.starts_with;
  clone.customer_safe = true;
  clone.credential_values_exposed = false;
  return clone;
}

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl()}/admin/runway-key-diagnostics`, {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(stripAnyAccidentalSecretFields(data), { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_runway_key_diagnostics_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
