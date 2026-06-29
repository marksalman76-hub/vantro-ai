import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || ''
  const pathname = request.nextUrl.pathname
  const isAdminHost = hostname.startsWith('admin.')
  const isAdminPage =
    pathname === '/admin' ||
    pathname.startsWith('/admin/') ||
    pathname === '/admin-login'
  const isAdminApi = pathname === '/api/admin' || pathname.startsWith('/api/admin/')

  if (isAdminHost) {
    if (pathname.startsWith('/api/')) {
      return NextResponse.next()
    }

    if (!isAdminPage) {
      return NextResponse.rewrite(
        new URL(`/admin${pathname}`, request.url)
      )
    }

    return NextResponse.next()
  }

  if (isAdminApi) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  if (isAdminPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next|.*\\..*).*)'],
}
