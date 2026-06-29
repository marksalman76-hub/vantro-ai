import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || ''
  const pathname = request.nextUrl.pathname

  // Route admin subdomain to /admin path
  if (hostname.startsWith('admin.')) {
    if (!pathname.startsWith('/admin')) {
      return NextResponse.rewrite(
        new URL(`/admin${pathname}`, request.url)
      )
    }
  } else {
    // Client site: strip /admin prefix if somehow present
    if (pathname.startsWith('/admin')) {
      return NextResponse.redirect(new URL('/', request.url))
    }
  }
}

export const config = {
  matcher: ['/((?!_next|.*\\..*).*)'],
}
