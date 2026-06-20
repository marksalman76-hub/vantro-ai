import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";

function serverAdminToken(): string {
  return (
    process.env.ADMIN_TOKEN ||
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  );
}

function adminHeaders(req: NextRequest): Record<string, string> {
  const incomingAuth = req.headers.get("authorization") || "";
  const adminToken = req.headers.get("x-admin-token") || serverAdminToken();
  return {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "owner_admin",
    "x-admin-token": adminToken,
    "authorization": incomingAuth || (adminToken ? `Bearer ${adminToken}` : ""),
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
