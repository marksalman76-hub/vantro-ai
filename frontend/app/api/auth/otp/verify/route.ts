import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";
const IS_PROD = process.env.NODE_ENV === "production";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${API_URL}/api/auth/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: body.email, code: body.code }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = data.detail || data.error || "Verification failed";
      return NextResponse.json({ detail, error: detail }, { status: res.status });
    }

    const token = data.access_token;
    const response = NextResponse.json({ access_token: token, token_type: "bearer", user_id: data.user_id });
    response.cookies.set("access_token", token, {
      httpOnly: true,
      secure: IS_PROD,
      sameSite: "lax",
      maxAge: 86400,
      path: "/",
    });
    return response;
  } catch {
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
