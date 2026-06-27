import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { checkRate, limiters } from '@/lib/ratelimit'

function getIP(req: NextRequest): string {
  return req.headers.get('x-forwarded-for')?.split(',')[0].trim() ?? 'anonymous'
}

function tooMany(reset?: number): NextResponse {
  const retryAfter = reset ? Math.ceil((reset - Date.now()) / 1000) : 60
  return NextResponse.json(
    { error: 'Too many requests. Please try again later.' },
    { status: 429, headers: { 'Retry-After': String(retryAfter) } }
  )
}

async function timingSafeEqual(a: string, b: string): Promise<boolean> {
  if (a.length !== b.length) return false
  const enc = new TextEncoder()
  const aBytes = enc.encode(a)
  const bBytes = enc.encode(b)
  let diff = 0
  for (let i = 0; i < aBytes.length; i++) diff |= aBytes[i] ^ bBytes[i]
  return diff === 0
}

async function verifyAccessToken(token: string): Promise<boolean> {
  const secret = process.env.OTP_SECRET || ''
  const dotIdx = token.lastIndexOf('.')
  if (dotIdx < 0) return false
  const payload = token.slice(0, dotIdx)
  const sigFromToken = token.slice(dotIdx + 1)
  const enc = new TextEncoder()
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const sigBytes = await crypto.subtle.sign('HMAC', key, enc.encode(payload))
  const expected = btoa(String.fromCharCode(...new Uint8Array(sigBytes)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
  return await timingSafeEqual(sigFromToken, expected)
}

async function verifyAdminToken(token: string): Promise<boolean> {
  const adminPassword = process.env.ADMIN_PASSWORD
  const secret = process.env.OTP_SECRET || ''
  if (!adminPassword || !token) return false
  const enc = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  )
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(adminPassword))
  const expected = Array.from(new Uint8Array(sig))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
  return await timingSafeEqual(token, expected)
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Protect admin sub-pages — /admin itself is the login page, always accessible
  if (pathname.startsWith('/admin/')) {
    const token = request.cookies.get('admin_token')?.value
    const valid = token ? await verifyAdminToken(token) : false
    if (!valid) {
      return NextResponse.redirect(new URL('/admin', request.url))
    }
    return NextResponse.next()
  }

  // Only protect API routes below
  if (!pathname.startsWith('/api/')) return NextResponse.next()

  // Auth routes: rate limit only, no token required
  if (pathname.startsWith('/api/auth/')) {
    const ip = getIP(request)
    if (pathname === '/api/auth/register') {
      const { limited, reset } = await checkRate(limiters.register, ip)
      if (limited) return tooMany(reset)
    }
    if (pathname === '/api/auth/verify-otp') {
      const { limited, reset } = await checkRate(limiters.verifyOtp, ip)
      if (limited) return tooMany(reset)
    }
    return NextResponse.next()
  }

  // Admin API routes: verify admin_token before allowing through
  if (pathname.startsWith('/api/admin/')) {
    const token = request.cookies.get('admin_token')?.value
    const valid = token ? await verifyAdminToken(token) : false
    if (!valid) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    return NextResponse.next()
  }

  // Admin cookie also grants access to regular API routes (admin pages calling /api/agent etc.)
  const adminToken = request.cookies.get('admin_token')?.value
  if (adminToken) {
    const adminValid = await verifyAdminToken(adminToken)
    if (adminValid) return NextResponse.next()
  }

  // User session: HMAC-signed access_token cookie required
  const cookieToken = request.cookies.get('access_token')?.value
  if (!cookieToken) {
    return NextResponse.json(
      { error: 'Unauthorized', message: 'Authentication required' },
      { status: 401 }
    )
  }
  const tokenValid = await verifyAccessToken(cookieToken)
  if (!tokenValid) {
    return NextResponse.json(
      { error: 'Unauthorized', message: 'Session expired. Please sign in again.' },
      { status: 401 }
    )
  }

  // Rate limit expensive authenticated routes
  const ip = getIP(request)
  const identifier = cookieToken ?? ip
  if (pathname === '/api/agent') {
    const { limited, reset } = await checkRate(limiters.agent, identifier)
    if (limited) return tooMany(reset)
  } else if (pathname.startsWith('/api/creative/video')) {
    const { limited, reset } = await checkRate(limiters.video, identifier)
    if (limited) return tooMany(reset)
  } else if (pathname.startsWith('/api/creative/audio')) {
    const { limited, reset } = await checkRate(limiters.audio, identifier)
    if (limited) return tooMany(reset)
  } else if (pathname === '/api/contact/enterprise') {
    const { limited, reset } = await checkRate(limiters.contact, ip)
    if (limited) return tooMany(reset)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/api/:path*', '/admin/:path*'],
}
