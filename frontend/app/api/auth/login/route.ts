import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";
const IS_PROD = process.env.NODE_ENV === "production";

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) return NextResponse.json({ error: data.detail || "Login failed" }, { status: res.status });

    const token = data.access_token;
    const response = NextResponse.json({ token, user_id: data.user_id });
    // Set httpOnly cookie — invisible to JS, immune to XSS token theft
    response.cookies.set("access_token", token, {
      httpOnly: true,
      secure: IS_PROD,
      sameSite: "lax",
      maxAge: 86400,
      path: "/",
    });
    return response;
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
