import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const access = String(formData.get("access") || "");
  const next = String(formData.get("next") || "/admin");
  const expected = process.env.PORTAL_ACCESS_CODE;

  if (!expected || access !== expected) {
    return new NextResponse("Access denied.", { status: 401 });
  }

  const response = NextResponse.redirect(new URL(next, request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", expected, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  response.cookies.set("admin_session", expected, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return response;
}
