import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const publicPaths = [
    "/",
    "/login",
    "/admin-login",
    "/activate",
    "/api/login",
    "/api/logout",
    "/api/admin-login",
    "/api/admin-logout",
    "/api/client-login",
    "/api/client-me",
    "/api/activate",
  ];

  if (
    publicPaths.some((path) => pathname === path || pathname.startsWith(path + "/")) ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon")
  ) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/admin")) {
    const expected = process.env.PORTAL_ACCESS_CODE;
    const cookie = request.cookies.get("portal_access")?.value;

    if (!expected || cookie !== expected) {
      const loginUrl = new URL("/admin-login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
