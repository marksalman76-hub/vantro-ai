import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

export async function GET(req: NextRequest) {
  const adminToken =
    req.headers.get("x-admin-token") ||
    req.headers.get("authorization")?.replace("Bearer ", "") ||
    "";

  const res = await fetch(`${BACKEND_URL}/admin/global-provider/readiness`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": adminToken ? `Bearer ${adminToken}` : "",
      "x-admin-token": adminToken,
      "x-actor-role": "admin",
      "x-tenant-id": req.headers.get("x-tenant-id") || "admin_global_provider_readiness",
      "origin": req.headers.get("origin") || "https://app.trance-formation.com.au",
      "referer": req.headers.get("referer") || "https://app.trance-formation.com.au/admin",
    },
    cache: "no-store",
  });

  const text = await res.text();

  return new NextResponse(text, {
    status: res.status,
    headers: {
      "Content-Type": res.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    },
  });
}