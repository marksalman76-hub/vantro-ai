import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(request: NextRequest) {
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken ?? request.headers.get("authorization")?.replace("Bearer ", "");
  if (!token) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });

  try {
    const body = await request.text();
    const res = await fetch(`${API_URL}/api/auth/change-password`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
