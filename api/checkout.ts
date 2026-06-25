import Stripe from 'stripe';
import type { VercelRequest, VercelResponse } from '@vercel/node';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

const PRICE_IDS: Record<string, string | undefined> = {
  starter:  process.env.STRIPE_PRICE_STARTER_MONTHLY,
  growth:   process.env.STRIPE_PRICE_GROWTH_MONTHLY,
  business: process.env.STRIPE_PRICE_PRO_MONTHLY,
};

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { plan, agents } = req.body as { plan: string; agents: string[] };
  const planKey = plan.toLowerCase();

  // Free plan — skip Stripe
  if (planKey === 'starter') {
    return res.status(200).json({
      url: `https://app.vantro.ai/register?plan=starter&agents=${encodeURIComponent(agents.join(','))}`,
    });
  }

  const priceId = PRICE_IDS[planKey];
  if (!priceId) return res.status(400).json({ error: `No price configured for plan: ${plan}` });

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `https://app.vantro.ai/register?session_id={CHECKOUT_SESSION_ID}&plan=${planKey}`,
    cancel_url: 'https://vantro.ai/#pricing',
    metadata: { plan: planKey, agents: agents.join(',') },
  });

  return res.status(200).json({ url: session.url });
}
