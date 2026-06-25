import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";
const IS_PROD = process.env.NODE_ENV === "production";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = res.status === 409 ? "Account already exists" :
                  res.status === 422 ? "Invalid input" :
                  "Request failed";
      return NextResponse.json({ error: msg }, { status: res.status });
    }

    const response = NextResponse.json(data);
    if (data.access_token) {
      response.cookies.set("access_token", data.access_token, {
        httpOnly: true,
        secure: IS_PROD,
        sameSite: "lax",
        maxAge: 86400,
        path: "/",
      });
    }
    return response;
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
