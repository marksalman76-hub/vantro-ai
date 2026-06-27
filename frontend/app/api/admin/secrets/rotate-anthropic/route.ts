import { NextResponse } from 'next/server'
import { Redis } from '@upstash/redis'

const REDIS_KEY = 'secrets:rotation:ANTHROPIC_API_KEY'

function getRedis(): Redis | null {
  if (!process.env.UPSTASH_REDIS_REST_URL || !process.env.UPSTASH_REDIS_REST_TOKEN) return null
  return new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL,
    token: process.env.UPSTASH_REDIS_REST_TOKEN,
  })
}

async function listAnthropicKeys(adminKey: string) {
  const res = await fetch('https://api.anthropic.com/v1/api-keys?limit=100', {
    headers: {
      'x-api-key': adminKey,
      'anthropic-version': '2023-06-01',
    },
  })
  if (!res.ok) throw new Error(`Anthropic list keys failed: ${res.status}`)
  const data = await res.json()
  return data.data as { id: string; name: string; status: string }[]
}

async function createAnthropicKey(adminKey: string, name: string): Promise<{ id: string; secret_key: string }> {
  const res = await fetch('https://api.anthropic.com/v1/api-keys', {
    method: 'POST',
    headers: {
      'x-api-key': adminKey,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })
  if (!res.ok) throw new Error(`Anthropic create key failed: ${res.status}`)
  return res.json()
}

async function deleteAnthropicKey(adminKey: string, keyId: string) {
  const res = await fetch(`https://api.anthropic.com/v1/api-keys/${keyId}`, {
    method: 'DELETE',
    headers: {
      'x-api-key': adminKey,
      'anthropic-version': '2023-06-01',
    },
  })
  if (!res.ok) throw new Error(`Anthropic delete key failed: ${res.status}`)
}

async function updateVercelEnv(name: string, value: string): Promise<boolean> {
  const token = process.env.VERCEL_TOKEN
  const projectId = process.env.VERCEL_PROJECT_ID
  if (!token || !projectId) return false

  const listRes = await fetch(`https://api.vercel.com/v9/projects/${projectId}/env?limit=100`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!listRes.ok) return false
  const { envs } = await listRes.json()
  const existing = (envs as { id: string; key: string; target: string[] }[])
    .find(e => e.key === name && e.target?.includes('production'))
  if (!existing) return false

  const patchRes = await fetch(`https://api.vercel.com/v9/projects/${projectId}/env/${existing.id}`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${token}`, 'content-type': 'application/json' },
    body: JSON.stringify({ value }),
  })
  return patchRes.ok
}

async function rotate(): Promise<Response> {
  const adminKey = process.env.ANTHROPIC_ADMIN_KEY
  if (!adminKey) {
    return NextResponse.json(
      { error: 'ANTHROPIC_ADMIN_KEY not configured. Add it to Vercel env vars.' },
      { status: 503 }
    )
  }

  try {
    const existingKeys = await listAnthropicKeys(adminKey)

    const tag = new Date().toISOString().slice(0, 10)
    const newKey = await createAnthropicKey(adminKey, `vantro-auto-${tag}`)

    const vercelUpdated = await updateVercelEnv('ANTHROPIC_API_KEY', newKey.secret_key)

    // Revoke old vantro-auto-* keys (not the new one)
    const toRevoke = existingKeys.filter(
      k => k.id !== newKey.id && k.status === 'active' && k.name.startsWith('vantro-auto-')
    )
    await Promise.allSettled(toRevoke.map(k => deleteAnthropicKey(adminKey, k.id)))

    const redis = getRedis()
    if (redis) await redis.set(REDIS_KEY, new Date().toISOString())

    return NextResponse.json({
      ok: true,
      newKeyId: newKey.id,
      vercelUpdated,
      revokedCount: toRevoke.length,
    })
  } catch {
    return NextResponse.json(
      { error: 'Rotation failed. Check ANTHROPIC_ADMIN_KEY permissions.' },
      { status: 500 }
    )
  }
}

export async function POST() {
  return rotate()
}

// Called by Vercel Cron on schedule — protected by CRON_SECRET header
export async function GET(req: Request) {
  const cronSecret = process.env.CRON_SECRET
  if (cronSecret && req.headers.get('authorization') !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  return rotate()
}
