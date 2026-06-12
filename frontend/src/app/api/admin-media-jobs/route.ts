import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

export async function GET() {
  const headers: Record<string, string> = {
    "Cache-Control": "no-store",
    "x-actor-role": "owner_admin",
  };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }

  try {
    const response = await fetchWithTimeout(
      `${backendBaseUrl()}/admin/media-jobs`,
      {
        method: "GET",
        cache: "no-store",
        headers,
      },
      8000
    );

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
      jobs: [],
      customer_safe: true,
      credential_values_exposed: false,
    }));

    return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        status: "media_jobs_lookup_timeout",
        jobs: [],
        message: error instanceof Error ? error.message : String(error),
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 202, headers: { "Cache-Control": "no-store" } }
    );
  }
}
