
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

export async function POST() {
  const headers: Record<string, string> = {
    "Cache-Control": "no-store",
    "x-actor-role": "owner_admin",
  };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }

  const response = await fetch(`${BACKEND_BASE_URL}/admin/media-jobs/run-next`, {
    method: "POST",
    cache: "no-store",
    headers,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
}
