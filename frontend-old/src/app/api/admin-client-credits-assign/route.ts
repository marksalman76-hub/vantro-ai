import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

export async function POST(req: NextRequest) {
  const adminToken =
    req.headers.get("x-admin-token") ||
    req.headers.get("authorization")?.replace("Bearer ", "") ||
    "";

  const body = await req.text();

  const res = await fetch(`${BACKEND_URL}/admin/client-credits/assign`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": adminToken ? `Bearer ${adminToken}` : "",
      "x-admin-token": adminToken,
      "x-actor-role": "admin",
      "x-tenant-id": req.headers.get("x-tenant-id") || "tenant_unknown",
      "origin": req.headers.get("origin") || "https://app.trance-formation.com.au",
      "referer": req.headers.get("referer") || "https://app.trance-formation.com.au/admin",
    },
    body,
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