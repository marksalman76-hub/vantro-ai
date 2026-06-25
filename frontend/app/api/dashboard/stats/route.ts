import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function GET(request: NextRequest) {
  try {
    const cookieToken = request.cookies.get("access_token")?.value;
    const token = cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");
    const res = await fetch(`${API_URL}/api/dashboard/stats`, {
      method: "GET",
      headers: { "Authorization": token },
    });
    const data = await res.json();
    if (!res.ok) return NextResponse.json({ error: data.detail || "Failed to fetch stats" }, { status: res.status });
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
