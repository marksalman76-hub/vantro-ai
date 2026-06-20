import { NextRequest, NextResponse } from "next/server";

function logoutResponse(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", "", {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 0,
  });
  response.cookies.set("admin_session", "", {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 0,
  });

  return response;
}

export async function GET(request: NextRequest) {
  return logoutResponse(request);
}

export async function POST(request: NextRequest) {
  return logoutResponse(request);
}
