import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.trance-formation.com.au";

export async function GET() {
  const token =
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.NEXT_PUBLIC_ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    "";

  const response = await fetch(`${API_BASE}/admin/post-deploy-validation/status`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "x-admin-token": token,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
    },
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "invalid_json_response",
  }));

  return NextResponse.json(data, { status: response.status });
}
