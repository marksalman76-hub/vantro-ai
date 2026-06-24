import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(request: NextRequest) {
  const token = request.headers.get("authorization");
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  try {
    const body = await request.text();
    const res = await fetch(`${API_URL}/api/support/tickets`, {
      method: "POST",
      headers: { Authorization: token, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Backend unavailable" }, { status: 502 });
  }
}
