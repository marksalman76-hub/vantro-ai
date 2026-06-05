import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";

function adminHeaders(req: NextRequest): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "owner_admin",
    "x-admin-token": req.headers.get("x-admin-token") || process.env.ADMIN_TOKEN || "",
    "authorization": req.headers.get("authorization") || "",
  };
}

function publicHeaders(): Record<string, string> {
  return { "Content-Type": "application/json" };
}

export async function GET(req: NextRequest) {
  const status = req.nextUrl.searchParams.get("status");
  const limit = req.nextUrl.searchParams.get("limit") || "50";
  const qs = new URLSearchParams();
  if (status) qs.set("status", status);
  qs.set("limit", limit);

  const upstream = await fetch(`${BACKEND_URL}/admin/billing/refund-requests?${qs.toString()}`, {
    method: "GET",
    cache: "no-store",
    headers: adminHeaders(req),
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
