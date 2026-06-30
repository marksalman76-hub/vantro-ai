import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

function getAuthHeader(request: NextRequest) {
  const cookieToken = request.cookies.get("access_token")?.value;
  return cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");
}

export async function GET(request: NextRequest) {
  const token = getAuthHeader(request);
  try {
    const res = await fetch(`${API_URL}/api/admin/stats`, {
      headers: { Authorization: token },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
