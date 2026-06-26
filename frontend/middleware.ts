import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Only protect API routes
  if (!pathname.startsWith('/api/')) return NextResponse.next()

  // Allow auth routes through without auth check
  if (pathname.startsWith('/api/auth/')) return NextResponse.next()

  // Check for httpOnly access_token cookie (primary)
  const cookieToken = request.cookies.get('access_token')?.value

  // Also accept Authorization header for backwards compatibility with localStorage-based auth
  const authHeader = request.headers.get('Authorization')
  const bearerToken = authHeader?.startsWith('Bearer ')
    ? authHeader.slice(7).trim()
    : null

  if (!cookieToken && !bearerToken) {
    return NextResponse.json(
      { error: 'Unauthorized', message: 'Authentication required' },
      { status: 401 }
    )
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/api/:path*'],
}
