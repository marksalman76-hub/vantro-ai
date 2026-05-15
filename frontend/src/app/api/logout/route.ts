import { NextResponse } from "next/server";

export async function GET() {
  const response = NextResponse.redirect(
    "https://ecommerce-ai-agent-platform.vercel.app/login"
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
