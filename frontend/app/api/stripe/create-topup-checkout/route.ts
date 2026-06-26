import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { credits, email } = body

    if (!credits || credits < 1) {
      return NextResponse.json({ error: 'Invalid credits amount' }, { status: 400 })
    }

    const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY
    if (!STRIPE_SECRET_KEY) {
      return NextResponse.json({ error: 'Payment not configured' }, { status: 503 })
    }

    // Map credit amounts to prices (cents)
    const CREDIT_PRICES: Record<number, number> = {
      100: 999,   // $9.99 for 100 credits
      500: 3999,  // $39.99 for 500 credits
      1000: 6999, // $69.99 for 1000 credits
    }

    const amount = CREDIT_PRICES[credits] || credits * 10 // fallback: 10 cents per credit

    const formData = new URLSearchParams()
    formData.append('mode', 'payment')
    formData.append('line_items[0][price_data][currency]', 'usd')
    formData.append('line_items[0][price_data][unit_amount]', String(amount))
    formData.append('line_items[0][price_data][product_data][name]', `${credits} AI Credits`)
    formData.append('line_items[0][quantity]', '1')
    formData.append('success_url', `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/dashboard?topup=success`)
    formData.append('cancel_url', `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/dashboard/settings`)
    if (email) formData.append('customer_email', email)

    const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    })

    const session = await res.json()

    if (!session?.url) {
      console.error('[topup-checkout] No session URL:', session)
      return NextResponse.json({ error: 'Checkout unavailable' }, { status: 502 })
    }

    return NextResponse.json({ url: session.url })
  } catch (err) {
    console.error('[topup-checkout] error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
