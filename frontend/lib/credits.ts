export type VideoQuality = '720p' | '1080p' | '4k'
export type VideoDuration = 5 | 10 | 15 | 20 | 25 | 30

// Credit costs include 30% margin over Higgsfield provider costs
// 720p → Kling 3.0 (~$0.06/s raw)
// 1080p → Sora 2 (~$0.40/s raw)
// 4K → Veo 3.1 (~$0.70/s raw) — Business plan only
export const VIDEO_CREDIT_COSTS: Record<VideoQuality, Record<VideoDuration, number>> = {
  '720p':  { 5: 3,  10: 5,  15: 8,  20: 10, 25: 12, 30: 15  },
  '1080p': { 5: 12, 10: 20, 15: 28, 20: 36, 25: 45, 30: 55  },
  '4k':    { 5: 20, 10: 40, 15: 60, 20: 80, 25: 100, 30: 120 },
}

export const CREDIT_COSTS = {
  agent_haiku:   1,
  agent_sonnet:  2,
  audio:         1,
  image:         2,
  // Video costs are now in VIDEO_CREDIT_COSTS
  // Kept for legacy reference:
  video_5s:      3,
  video_10s:     5,
} as const

export function videoCreditCost(quality: VideoQuality, duration: VideoDuration): number {
  return VIDEO_CREDIT_COSTS[quality][duration] ?? VIDEO_CREDIT_COSTS['720p'][5]
}

// All plans can access 4K
export const PLANS_WITH_4K = new Set(['starter', 'growth', 'business', 'agency', 'enterprise'])

// Provider raw costs (USD) — for reference/reporting
export const PROVIDER_COSTS = {
  higgsfield_5s:           0.30,
  higgsfield_10s:          0.60,
  runway_5s:               0.25,
  runway_10s:              0.50,
  elevenlabs_per_1k_chars: 0.10,
  claude_haiku_per_run:    0.01,
  claude_sonnet_per_run:   0.05,
} as const

export const MARGIN = 0.30 // 30% minimum

// Dollar value per credit (blended across top-up tiers: $18/10, $40/25, $70/50)
export const CREDIT_VALUE_USD = 1.40

// Monthly credit allocations per plan
export const PLAN_CREDITS = {
  starter:    100,
  growth:     300,
  business:   700,
  agency:     2000,
  enterprise: 5000,
} as const

export const PLAN_PRICING = {
  starter:  { monthlyUsd: 99,  annualUsd: 79  },
  growth:   { monthlyUsd: 249, annualUsd: 199 },
  business: { monthlyUsd: 399, annualUsd: 319 },
  agency:   { monthlyUsd: 799, annualUsd: 639 },
} as const

// Max agents per plan
export const PLAN_AGENT_LIMIT = {
  starter:  2,
  growth:   5,
  business: 8,
  agency:   22, // unlimited in practice — contact sales
} as const

// Top-up packs (credits / price USD)
export const TOPUP_PACKS = [
  { credits: 25,  priceUsd: 18,  pricePer: 0.72 },
  { credits: 60,  priceUsd: 40,  pricePer: 0.67 },
  { credits: 130, priceUsd: 70,  pricePer: 0.54 },
] as const

/**
 * Read current credit balance from localStorage.
 * Returns 0 if not set or not in browser.
 */
export function getCredits(): number {
  if (typeof window === 'undefined') return 0
  return parseFloat(localStorage.getItem('vantro_credits') || '0')
}

/**
 * Deduct credits from localStorage balance.
 * Returns new balance. Does NOT check for insufficient credits.
 */
export function deductCredits(amount: number): number {
  const current = getCredits()
  const updated = Math.max(0, current - amount)
  localStorage.setItem('vantro_credits', String(updated))
  return updated
}

/**
 * Add credits (top-up or plan assignment).
 */
export function addCredits(amount: number): number {
  const current = getCredits()
  const updated = current + amount
  localStorage.setItem('vantro_credits', String(updated))
  return updated
}

/**
 * Check if user has enough credits for an operation.
 */
export function hasCredits(required: number): boolean {
  return getCredits() >= required
}

export type CreditOperation = keyof typeof CREDIT_COSTS
