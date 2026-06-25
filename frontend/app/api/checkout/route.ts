// Called by: AgentSelectModal (src/components/AgentSelectModal.tsx) on vantro.ai
// User instruction: "continue to checkout got not authenticated message" — backend requires auth,
//   so bypass by calling Stripe directly from Next.js server using STRIPE_SECRET_KEY env var.
// Input:  POST { plan: string, agents: string[], email: string }
// Output: { url: string } — Stripe hosted checkout URL
// Env vars needed in Vercel (vantro-app project):
//   STRIPE_SECRET_KEY, STRIPE_PRICE_STARTER, STRIPE_PRICE_GROWTH, STRIPE_PRICE_BUSINESS

import { NextRequest, NextResponse } from 'next/server'

const STRIPE_SECRET = process.env.STRIPE_SECRET_KEY || ''

const PLAN_PRICE_IDS: Record<string, string> = {
  starter:  process.env.STRIPE_PRICE_STARTER  || '',
  growth:   process.env.STRIPE_PRICE_GROWTH   || '',
  business: process.env.STRIPE_PRICE_BUSINESS || '',
}

const SUCCESS_URL = 'https://app.vantro.ai/onboarding?session_id={CHECKOUT_SESSION_ID}'
const CANCEL_URL  = 'https://vantro.ai/#pricing'

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'https://vantro.ai',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS_HEADERS })
}

export async function POST(request: NextRequest) {
  if (!STRIPE_SECRET) {
    return NextResponse.json({ detail: 'Payment system not configured.' }, { status: 503, headers: CORS_HEADERS })
  }

  let body: { plan?: string; agents?: string[]; email?: string }
  try { body = await request.json() } catch {
    return NextResponse.json({ detail: 'Invalid request.' }, { status: 400, headers: CORS_HEADERS })
  }

  const planKey = (body.plan || '').toLowerCase()
  const priceId = PLAN_PRICE_IDS[planKey]

  if (!priceId) {
    return NextResponse.json({ detail: `Plan "${planKey}" not configured.` }, { status: 400, headers: CORS_HEADERS })
  }

  const params = new URLSearchParams()
  params.append('mode', 'subscription')
  params.append('success_url', SUCCESS_URL)
  params.append('cancel_url', CANCEL_URL)
  params.append('line_items[0][price]', priceId)
  params.append('line_items[0][quantity]', '1')
  if (body.email) params.append('customer_email', body.email)
  if (body.agents?.length) {
    params.append('metadata[agents]', body.agents.join(','))
    params.append('metadata[plan]', planKey)
  }

  try {
    const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${STRIPE_SECRET}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    })
    const data = await res.json()
    if (!res.ok) {
      return NextResponse.json({ detail: data.error?.message || 'Stripe error.' }, { status: 502, headers: CORS_HEADERS })
    }
    return NextResponse.json({ url: data.url }, { headers: CORS_HEADERS })
  } catch {
    return NextResponse.json({ detail: 'Payment service unavailable.' }, { status: 502, headers: CORS_HEADERS })
  }
}
