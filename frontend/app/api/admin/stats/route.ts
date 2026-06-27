import { NextRequest, NextResponse } from 'next/server'
import { createHmac, timingSafeEqual } from 'crypto'
import Stripe from 'stripe'

function verifyAdminToken(token: string): boolean {
  const adminPassword = process.env.ADMIN_PASSWORD
  const secret = process.env.OTP_SECRET || ''
  if (!adminPassword || !token) return false
  const expected = createHmac('sha256', secret).update(adminPassword).digest('hex')
  if (token.length !== expected.length) return false
  return timingSafeEqual(Buffer.from(token), Buffer.from(expected))
}

export async function GET(request: NextRequest) {
  const adminToken = request.cookies.get('admin_token')?.value
  if (!verifyAdminToken(adminToken || '')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const stripeKey = process.env.STRIPE_SECRET_KEY
  if (!stripeKey) {
    return NextResponse.json({ error: 'Stripe not configured' }, { status: 503 })
  }

  const stripe = new Stripe(stripeKey)

  const [balance, charges, subscriptions, customers] = await Promise.all([
    stripe.balance.retrieve(),
    stripe.charges.list({ limit: 10 }),
    stripe.subscriptions.list({ limit: 100, status: 'active' }),
    stripe.customers.list({ limit: 5 }),
  ])

  const availableUSD = balance.available.find(b => b.currency === 'usd')?.amount ?? 0
  const pendingUSD   = balance.pending.find(b => b.currency === 'usd')?.amount ?? 0

  const mrr = subscriptions.data.reduce((sum, sub) => {
    const item = sub.items.data[0]
    if (!item?.price?.unit_amount) return sum
    const unitAmount = item.price.unit_amount
    const interval   = item.price.recurring?.interval
    const monthly    = interval === 'year' ? unitAmount / 12 : unitAmount
    return sum + monthly
  }, 0)

  return NextResponse.json({
    balance: { available: availableUSD, pending: pendingUSD },
    mrr,
    activeSubscriptions: subscriptions.data.length,
    recentCharges: charges.data.map(c => ({
      id: c.id,
      amount: c.amount,
      currency: c.currency,
      status: c.status,
      description: c.description,
      email: c.billing_details?.email ?? null,
      created: c.created,
    })),
    recentCustomers: customers.data.map(c => ({
      id: c.id,
      email: c.email,
      created: c.created,
    })),
  })
}
