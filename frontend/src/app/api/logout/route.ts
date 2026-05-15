import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const next = request.nextUrl.searchParams.get("next") || "/login";

  const response = NextResponse.redirect(
    new URL(next, "https://ecommerce-ai-agent-platform.vercel.app")
  );

  response.cookies.set("portal_access", "", {
    path: "/",
    expires: new Date(0),
  });

  response.cookies.set("client_session", "", {
    path: "/",
    expires: new Date(0),
  });

  return response;
}
