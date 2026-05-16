import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function logout(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", "", {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });

  return response;
}

export async function GET(request: NextRequest) {
  return logout(request);
}

export async function POST(request: NextRequest) {
  return logout(request);
}
