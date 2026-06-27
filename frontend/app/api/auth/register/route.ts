import { NextRequest, NextResponse } from 'next/server'
import crypto, { randomInt } from 'crypto'
import { Resend } from 'resend'

function escHtml(s: string): string {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}

function signOtp(payload: object, secret: string): string {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url')
  const sig = crypto.createHmac('sha256', secret).update(data).digest('base64url')
  return `${data}.${sig}`
}

export async function POST(request: NextRequest) {
  const OTP_SECRET = process.env.OTP_SECRET
  if (!OTP_SECRET) {
    return NextResponse.json({ error: 'Server misconfiguration' }, { status: 500 })
  }

  try {
    const body = await request.json()
    const { name, email, password } = body

    if (!name || !email || !password) {
      return NextResponse.json({ detail: 'All fields are required.' }, { status: 400 })
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json({ error: 'Invalid email address' }, { status: 400 })
    }
    if (password.length < 8) {
      return NextResponse.json({ detail: 'Password must be at least 8 characters.' }, { status: 400 })
    }
    if (!/\d/.test(password)) {
      return NextResponse.json({ detail: 'Password must include at least one number.' }, { status: 400 })
    }

    const otp = randomInt(100000, 1000000).toString()
    const token = signOtp({ email, otp, exp: Date.now() + 10 * 60 * 1000, attempts: 0 }, OTP_SECRET)

    // Send OTP email
    if (process.env.RESEND_API_KEY) {
      const resend = new Resend(process.env.RESEND_API_KEY)
      await resend.emails.send({
        from: 'Vantro <noreply@vantro.ai>',
        to: email,
        subject: 'Your Vantro verification code',
        html: `
          <div style="font-family:sans-serif;max-width:480px;margin:0 auto;background:#0A0D14;padding:40px;border-radius:12px">
            <div style="text-align:center;margin-bottom:32px">
              <div style="display:inline-block;width:40px;height:40px;background:linear-gradient(135deg,#FF6B35,#00D9FF);border-radius:10px;line-height:40px;color:#fff;font-weight:900;font-size:18px">V</div>
              <h2 style="color:#fff;margin:12px 0 4px;font-size:20px">Vantro.ai</h2>
            </div>
            <p style="color:rgba(255,255,255,0.60);font-size:15px;margin:0 0 8px">Hi ${escHtml(name)},</p>
            <p style="color:rgba(255,255,255,0.60);font-size:15px;margin:0 0 32px">Enter this code to verify your account:</p>
            <div style="text-align:center;background:rgba(255,107,53,0.10);border:1px solid rgba(255,107,53,0.30);border-radius:12px;padding:28px;margin-bottom:32px">
              <span style="font-size:42px;font-weight:900;letter-spacing:12px;color:#FF6B35">${otp}</span>
            </div>
            <p style="color:rgba(255,255,255,0.35);font-size:13px;text-align:center;margin:0">Code expires in 10 minutes. If you didn't request this, ignore this email.</p>
          </div>
        `,
      })
    }

    const res = NextResponse.json({ message: 'otp_sent', email })
    res.cookies.set('vantro_otp', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 600, // 10 min
      path: '/',
    })
    return res
  } catch {
    return NextResponse.json({ detail: 'Something went wrong. Please try again.' }, { status: 500 })
  }
}
