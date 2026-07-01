import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${API_URL}/api/auth/otp/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: body.email, password: body.password }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = data.detail || data.error || "Request failed";
      return NextResponse.json({ detail, error: detail }, { status: res.status });
    }
    return NextResponse.json(data, { status: 200 });
  } catch {
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
