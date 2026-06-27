import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const hasConfig = !!(
  process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN
)

let redis: Redis | null = null
if (hasConfig) {
  try {
    redis = new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL!,
      token: process.env.UPSTASH_REDIS_REST_TOKEN!,
    })
  } catch {
    redis = null
  }
}

function make(tokens: number, window: Parameters<typeof Ratelimit.slidingWindow>[1], prefix: string): Ratelimit | null {
  if (!redis) return null
  try {
    return new Ratelimit({ redis, limiter: Ratelimit.slidingWindow(tokens, window), prefix })
  } catch {
    return null
  }
}

export const limiters = {
  register:  make(5,  '15 m', 'rl:register'),
  verifyOtp: make(10, '10 m', 'rl:verify-otp'),
  agent:     make(10, '1 m',  'rl:agent'),
  video:     make(5,  '1 h',  'rl:video'),
  audio:     make(20, '1 h',  'rl:audio'),
  contact:   make(3,  '1 d',  'rl:contact'),
}

export async function checkRate(
  limiter: Ratelimit | null,
  identifier: string
): Promise<{ limited: boolean; reset?: number }> {
  if (!limiter) return { limited: false }
  try {
    const { success, reset } = await limiter.limit(identifier)
    return { limited: !success, reset }
  } catch {
    return { limited: false }
  }
}
