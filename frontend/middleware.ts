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

  const access = request.nextUrl.searchParams.get("access");
  const expected = process.env.PORTAL_ACCESS_CODE;

  if (!expected) {
    return new NextResponse("Portal access is not configured.", {
      status: 503,
    });
  }

  if (access !== expected) {
    return new NextResponse("Access denied.", {
      status: 401,
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/client/:path*"],
};