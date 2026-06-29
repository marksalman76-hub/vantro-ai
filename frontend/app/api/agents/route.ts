import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function GET(request: NextRequest) {
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : (request.headers.get("authorization") || "");
  const query = new URL(request.url).search;

  try {
    const res = await fetch(`${API_URL}/api/agents${query}`, {
      method: "GET",
      headers: { Authorization: token },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(e) },
      { status: 502 }
    );
  }
}
