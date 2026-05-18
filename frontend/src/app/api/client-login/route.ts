import { NextRequest, NextResponse } from "next/server";

const DEMO_EMAIL = "demo@client.local";
const DEMO_PASSWORD = "Demo123!";

export async function POST(request: NextRequest) {
  const form = await request.formData();

  const email = String(form.get("email") || "").trim().toLowerCase();
  const password = String(form.get("password") || "");
  const nextPath = String(form.get("next") || "/client");

  if (email !== DEMO_EMAIL || password !== DEMO_PASSWORD) {
    return NextResponse.redirect(new URL(`/login?next=${encodeURIComponent(nextPath)}&error=invalid_login`, request.url));
  }

  const response = NextResponse.redirect(new URL(nextPath || "/client", request.url));

  response.cookies.set("client_demo_session", "active", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  response.cookies.set("client_session", "demo_client_session", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  return response;
}
