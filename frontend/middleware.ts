import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PATHS = ["/admin", "/client"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PATHS.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const portalAccess = request.cookies.get("portal_access")?.value;
  const expected = process.env.PORTAL_ACCESS_CODE;

  if (!expected) {
    return new NextResponse("Portal access is not configured.", { status: 503 });
  }

  if (portalAccess !== expected) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/client/:path*"],
};