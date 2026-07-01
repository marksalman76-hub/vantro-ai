import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

/**
 * Proxy handler for the bare GET /api/agents endpoint.
 * The catch-all route at [...path]/route.ts only matches when at least one
 * path segment follows /api/agents/. This file handles the root with no segment.
 */
export async function GET(request: NextRequest) {
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : (request.headers.get("authorization") || "");
  const url = new URL(request.url);
  const query = url.search;

  try {
    const res = await fetch(`${API_URL}/api/agents${query}`, {
      method: "GET",
      headers: { Authorization: token, "Content-Type": "application/json" },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json(
      { error: "Backend unreachable" },
      { status: 502 }
    );
  }
}
