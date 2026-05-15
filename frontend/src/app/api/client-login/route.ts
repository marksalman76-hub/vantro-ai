import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const email = String(formData.get("email") || "");
  const password = String(formData.get("password") || "");
  const next = String(formData.get("next") || "/client");

  const response = await fetch(`${BACKEND_URL}/client/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();

  if (!result.success || !result.session_token) {
    return new NextResponse("Client login failed.", { status: 401 });
  }

  const redirectUrl = new URL(next, request.url);
  const nextResponse = NextResponse.redirect(redirectUrl);

  nextResponse.cookies.set("client_session", result.session_token, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return nextResponse;
}
