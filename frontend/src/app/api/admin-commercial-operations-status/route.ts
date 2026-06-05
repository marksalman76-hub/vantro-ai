import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";

export async function GET(req: NextRequest) {
  const upstream = await fetch(`${BACKEND_URL}/admin/commercial-operations/status`, {
    method: "GET",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "x-actor-role": req.headers.get("x-actor-role") || "owner_admin",
      "x-admin-token": req.headers.get("x-admin-token") || process.env.ADMIN_TOKEN || "",
      "authorization": req.headers.get("authorization") || "",
    },
  });

  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
