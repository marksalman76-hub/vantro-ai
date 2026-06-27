import { NextRequest, NextResponse } from 'next/server'
import { Redis } from '@upstash/redis'

const ALLOWED_KEYS = [
  'ANTHROPIC_API_KEY',
  'RUNWAY_API_KEY',
  'ELEVENLABS_API_KEY',
  'RESEND_API_KEY',
  'STRIPE_SECRET_KEY',
  'OTP_SECRET',
]

function getRedis() {
  return new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL!,
    token: process.env.UPSTASH_REDIS_REST_TOKEN!,
  })
}

function computeStatus(lastRotated: string | null): 'ok' | 'warn' | 'stale' | 'unknown' {
  if (!lastRotated) return 'unknown'
  const ageDays = (Date.now() - new Date(lastRotated).getTime()) / (1000 * 60 * 60 * 24)
  if (ageDays < 30) return 'ok'
  if (ageDays <= 60) return 'warn'
  return 'stale'
}

function computeAgeDays(lastRotated: string | null): number | null {
  if (!lastRotated) return null
  return Math.floor((Date.now() - new Date(lastRotated).getTime()) / (1000 * 60 * 60 * 24))
}

export async function GET() {
  const redis = getRedis()
  const redisKeys = ALLOWED_KEYS.map(k => `secrets:rotation:${k}`)
  const values = await redis.mget<(string | null)[]>(...redisKeys)

  const result = ALLOWED_KEYS.map((name, i) => {
    const lastRotated = values[i] ?? null
    return {
      name,
      lastRotated,
      ageDays: computeAgeDays(lastRotated),
      status: computeStatus(lastRotated),
    }
  })

  return NextResponse.json(result)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const { action, keyName, newValue } = body as {
    action: 'update' | 'mark_rotated'
    keyName: string
    newValue?: string
  }

  if (!ALLOWED_KEYS.includes(keyName)) {
    return NextResponse.json({ error: 'Invalid keyName' }, { status: 400 })
  }

  const redis = getRedis()

  if (action === 'mark_rotated') {
    await redis.set(`secrets:rotation:${keyName}`, new Date().toISOString())
    return NextResponse.json({ ok: true })
  }

  if (action === 'update') {
    if (!newValue || typeof newValue !== 'string' || newValue.trim() === '') {
      return NextResponse.json({ error: 'newValue is required' }, { status: 400 })
    }

    const vercelToken = process.env.VERCEL_TOKEN
    const vercelProjectId = process.env.VERCEL_PROJECT_ID

    if (!vercelToken || !vercelProjectId) {
      return NextResponse.json(
        { error: 'Vercel API not configured. Add VERCEL_TOKEN and VERCEL_PROJECT_ID env vars.' },
        { status: 503 }
      )
    }

    try {
      const listRes = await fetch(
        `https://api.vercel.com/v9/projects/${vercelProjectId}/env?limit=100`,
        { headers: { Authorization: `Bearer ${vercelToken}` } }
      )
      if (!listRes.ok) {
        return NextResponse.json({ error: 'Failed to update secret' }, { status: 500 })
      }
      const listData = await listRes.json()
      const envVar = (listData.envs as Array<{ id: string; key: string; target: string[] }>).find(
        e => e.key === keyName && Array.isArray(e.target) && e.target.includes('production')
      )
      if (!envVar) {
        return NextResponse.json({ error: 'Env var not found in Vercel project' }, { status: 404 })
      }

      const patchRes = await fetch(
        `https://api.vercel.com/v9/projects/${vercelProjectId}/env/${envVar.id}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${vercelToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ value: newValue }),
        }
      )
      if (!patchRes.ok) {
        return NextResponse.json({ error: 'Failed to update secret' }, { status: 500 })
      }

      await redis.set(`secrets:rotation:${keyName}`, new Date().toISOString())
      return NextResponse.json({ ok: true, vercelUpdated: true })
    } catch {
      return NextResponse.json({ error: 'Failed to update secret' }, { status: 500 })
    }
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
}
