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

export async function GET(req: NextRequest) {
  const qs = new URLSearchParams();
  const industry = req.nextUrl.searchParams.get("industry");
  const limit = req.nextUrl.searchParams.get("limit") || "100";
  if (industry) qs.set("industry", industry);
  qs.set("limit", limit);

  const upstream = await fetch(`${BACKEND_URL}/admin/industry-agent-store/packs?${qs.toString()}`, {
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

export async function POST(req: NextRequest) {
  const body = await req.text();
  const upstream = await fetch(`${BACKEND_URL}/admin/industry-agent-store/pack`, {
    method: "POST",
    cache: "no-store",
    headers: adminHeaders(req),
    body,
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
