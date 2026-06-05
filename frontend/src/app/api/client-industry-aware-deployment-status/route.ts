import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";

export async function GET() {
  const upstream = await fetch(`${BACKEND_URL}/client/industry-aware-deployment/status`, {
    method: "GET",
    cache: "no-store",
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
