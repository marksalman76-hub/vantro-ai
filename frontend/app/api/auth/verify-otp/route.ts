import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

interface OtpPayload {
  email: string
  otp: string
  exp: number
  attempts: number
}

function verifyToken(token: string, secret: string): OtpPayload | null {
  try {
    const [data, sig] = token.split('.')
    const expected = crypto.createHmac('sha256', secret).update(data).digest('base64url')
    if (sig !== expected) return null
    return JSON.parse(Buffer.from(data, 'base64url').toString())
  } catch {
    return null
  }
}

function signPayload(payload: OtpPayload, secret: string): string {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url')
  const sig = crypto.createHmac('sha256', secret).update(data).digest('base64url')
  return `${data}.${sig}`
}

function signAccessToken(email: string, secret: string): string {
  const payload = Buffer.from(email).toString('base64url')
  const sig = crypto.createHmac('sha256', secret).update(payload).digest('base64url')
  return `${payload}.${sig}`
}

export async function POST(request: NextRequest) {
  const OTP_SECRET = process.env.OTP_SECRET
  if (!OTP_SECRET) {
    return NextResponse.json({ error: 'Server misconfiguration' }, { status: 500 })
  }

  try {
    const { email, otp } = await request.json()
    if (!email || !otp) {
      return NextResponse.json({ detail: 'Email and code are required.' }, { status: 400 })
    }

    const token = request.cookies.get('vantro_otp')?.value
    if (!token) {
      return NextResponse.json({ detail: 'Session expired. Please register again.' }, { status: 400 })
    }

    const payload = verifyToken(token, OTP_SECRET)
    if (!payload) {
      return NextResponse.json({ detail: 'Invalid session. Please register again.' }, { status: 400 })
    }
    if (Date.now() > payload.exp) {
      return NextResponse.json({ detail: 'Code expired. Please register again.' }, { status: 400 })
    }

    // Increment attempt counter before checking OTP
    const attempts = (payload.attempts ?? 0) + 1

    // Brute-force guard: block after 5 failed attempts
    if (attempts > 5) {
      const response = NextResponse.json(
        { error: 'Too many attempts. Request a new code.' },
        { status: 429 }
      )
      response.cookies.delete('vantro_otp')
      return response
    }

    if (payload.email !== email || payload.otp !== otp.toString()) {
      // Wrong code — persist incremented attempt count back into the cookie
      const updatedPayload: OtpPayload = { ...payload, attempts }
      const updatedToken = signPayload(updatedPayload, OTP_SECRET)
      const failResponse = NextResponse.json({ detail: 'Incorrect code. Try again.' }, { status: 400 })
      failResponse.cookies.set('vantro_otp', updatedToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: Math.max(0, Math.floor((payload.exp - Date.now()) / 1000)),
        path: '/',
      })
      return failResponse
    }

    // OTP verified successfully — clear OTP cookie and set session cookie
    const successResponse = NextResponse.json({ message: 'verified', email })
    successResponse.cookies.set('vantro_otp', '', { maxAge: 0, path: '/' })
    // Set httpOnly session cookie (30 day expiry)
    successResponse.cookies.set('access_token', signAccessToken(email, OTP_SECRET), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 30,
      path: '/',
    })
    return successResponse
  } catch {
    return NextResponse.json({ detail: 'Verification failed. Please try again.' }, { status: 500 })
  }
}
