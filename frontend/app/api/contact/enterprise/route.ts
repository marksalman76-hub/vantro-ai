import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, email, company, message, plan } = body

    if (!name || !email || !company || !message) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 })
    }

    const RESEND_API_KEY = process.env.RESEND_API_KEY
    if (!RESEND_API_KEY) {
      // Log inquiry server-side if no Resend key configured
      console.log('[enterprise-contact]', { name, email, company, plan, message })
      return NextResponse.json({ success: true })
    }

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Enterprise Inquiry <noreply@vantro.ai>',
        to: ['mark.salman76@gmail.com'],
        subject: `Enterprise Inquiry from ${company}`,
        html: `
          <h2>New Enterprise Inquiry</h2>
          <p><strong>Name:</strong> ${name}</p>
          <p><strong>Email:</strong> ${email}</p>
          <p><strong>Company:</strong> ${company}</p>
          <p><strong>Plan Interest:</strong> ${plan || 'Not specified'}</p>
          <p><strong>Message:</strong></p>
          <p>${message}</p>
        `,
      }),
    })

    if (!res.ok) {
      console.error('[enterprise-contact] Resend error:', res.status)
      return NextResponse.json({ error: 'Failed to send inquiry' }, { status: 502 })
    }

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error('[enterprise-contact] error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
