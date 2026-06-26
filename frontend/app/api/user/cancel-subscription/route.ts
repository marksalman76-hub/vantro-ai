import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '').trim()
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Stripe cancellation (cancel_at_period_end keeps access until period ends)
    if (process.env.STRIPE_SECRET_KEY) {
      // In production: look up customer's subscription ID from your DB by token/user
      // Then: await stripe.subscriptions.update(subscriptionId, { cancel_at_period_end: true })
      // For now: mock success — wire real lookup when DB is live
    }

    return NextResponse.json({
      message: 'subscription_cancelled',
      cancel_at_period_end: true,
    })
  } catch {
    return NextResponse.json(
      { detail: 'Cancellation failed. Please contact support at billing@vantro.ai.' },
      { status: 500 }
    )
  }
}
