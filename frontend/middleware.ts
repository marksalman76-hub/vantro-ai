import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isAdminPath = pathname === "/admin" || pathname.startsWith("/admin/");
  const isClientPath = pathname === "/client" || pathname.startsWith("/client/");

  if (!isAdminPath && !isClientPath) {
    return NextResponse.next();
  }

  const expectedOwnerCode = process.env.PORTAL_ACCESS_CODE;
  const ownerAccess = request.cookies.get("portal_access")?.value;
  const clientSession = request.cookies.get("client_session")?.value;

  if (isAdminPath) {
    if (!expectedOwnerCode) {
      return new NextResponse("Portal access is not configured.", { status: 503 });
    }

    if (ownerAccess !== expectedOwnerCode) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  if (isClientPath) {
    if (clientSession || ownerAccess === expectedOwnerCode) {
      return NextResponse.next();
    }

    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/client/:path*"],
};
