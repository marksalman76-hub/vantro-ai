import { NextRequest } from 'next/server'
import crypto from 'crypto'

const RUNWAY_BASE     = 'https://api.dev.runwayml.com/v1'
const RUNWAY_VERSION  = '2024-11-06'
const HIGGSFIELD_BASE = 'https://api.higgsfield.ai/v1'
const KLING_BASE      = 'https://api.klingai.com/v1'

function klingJwt(ak: string, sk: string): string {
  const header  = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url')
  const now     = Math.floor(Date.now() / 1000)
  const payload = Buffer.from(JSON.stringify({ iss: ak, exp: now + 1800, nbf: now - 5 })).toString('base64url')
  const sig     = crypto.createHmac('sha256', sk).update(`${header}.${payload}`).digest('base64url')
  return `${header}.${payload}.${sig}`
}

// Quality tiers map to Higgsfield model names.
// NOTE: Verify exact model slugs in Higgsfield dashboard — these are the published names.
// Exact model slugs from Higgsfield CLI MODELS.md (github.com/higgsfield-ai/cli)
const HIGGSFIELD_QUALITY_MODEL: Record<string, string> = {
  '720p':  'kling3_0',     // Kling v3.0 — standard, fastest
  '1080p': 'seedance_2_0', // Seedance 2.0 — high quality
  '4k':    'veo3_1',       // Google Veo 3.1 — ultra, Business only
}

const RATIO_MAP: Record<string, string> = {
  '1280:720': '1280:768',
  '720:1280': '768:1280',
  '16:9': '16:9',
  '9:16': '9:16',
  '1:1': '1:1',
  '768:1280': '768:1280',
  '1280:768': '1280:768',
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { prompt, imageUrl, duration = 5, ratio = '16:9', style, provider: reqProvider = 'auto', quality = '720p' } = body

    if (!prompt || typeof prompt !== 'string') {
      return Response.json({ error: 'prompt is required' }, { status: 400 })
    }
    if (prompt.length > 2000) {
      return Response.json({ error: 'Prompt too long (max 2000 chars).' }, { status: 400 })
    }

    // Supported durations: 5, 10, 15, 20, 25, 30
    const SUPPORTED_DURATIONS = [5, 10, 15, 20, 25, 30] as const
    const safeDuration = SUPPORTED_DURATIONS.includes(duration as typeof SUPPORTED_DURATIONS[number])
      ? (duration as number)
      : duration > 20 ? 30 : duration > 15 ? 20 : duration > 10 ? 15 : duration >= 8 ? 10 : 5
    const safeRatio    = RATIO_MAP[ratio] ?? '16:9'

    const RUNWAY_KEY      = process.env.RUNWAY_API_KEY || ''
    const HIGGSFIELD_KEY  = process.env.HIGGSFIELD_API_KEY || ''
    const KLING_AK        = process.env.KLING_ACCESS_KEY || ''
    const KLING_SK        = process.env.KLING_SECRET_KEY || ''

    let provider = reqProvider
    if (reqProvider === 'auto') {
      if (imageUrl && RUNWAY_KEY) provider = 'runway'
      else if (HIGGSFIELD_KEY) provider = 'higgsfield'
      else if (KLING_AK && KLING_SK) provider = 'kling'
      else provider = 'runway'
    }

    // ── Higgsfield ────────────────────────────────────────────────────────────
    if (provider === 'higgsfield') {
      if (!HIGGSFIELD_KEY) return Response.json({ error: 'Video generation unavailable.' }, { status: 503 })
      const payload: Record<string, unknown> = { prompt, duration: safeDuration }
      if (style) payload.style = style
      payload.model = HIGGSFIELD_QUALITY_MODEL[quality as string] ?? HIGGSFIELD_QUALITY_MODEL['720p']
      const r = await fetch(`${HIGGSFIELD_BASE}/generation`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${HIGGSFIELD_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!r.ok) {
        const text = await r.text()
        console.error('[creative/video] higgsfield error:', r.status, text)
        return Response.json({ error: 'Generation failed. Please try again.' }, { status: r.status })
      }
      const data = await r.json()
      const jobId = data.job_id ?? data.id
      return Response.json({
        status: 'pending', provider: 'higgsfield', job_id: jobId,
        quality,
        poll_endpoint: `/api/creative/status?provider=higgsfield&job_id=${jobId}`,
        message: 'Video generation started.',
      })
    }

    // ── Kling ─────────────────────────────────────────────────────────────────
    if (provider === 'kling') {
      if (!KLING_AK || !KLING_SK) return Response.json({ error: 'Video generation unavailable.' }, { status: 503 })
      const jwt = klingJwt(KLING_AK, KLING_SK)
      const klingRatio = safeRatio === '16:9' ? '16:9' : safeRatio === '9:16' ? '9:16' : '1:1'

      const endpoint = imageUrl ? `${KLING_BASE}/videos/image2video` : `${KLING_BASE}/videos/text2video`
      const klingBody: Record<string, unknown> = {
        model_name: 'kling-v1',
        prompt: prompt.slice(0, 2000),
        duration: String(safeDuration),
        aspect_ratio: klingRatio,
        mode: 'std',
      }
      if (imageUrl) klingBody.image = imageUrl

      const r = await fetch(endpoint, {
        method: 'POST',
        headers: { Authorization: `Bearer ${jwt}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(klingBody),
      })
      if (!r.ok) {
        const text = await r.text()
        console.error('[creative/video] kling error:', r.status, text)
        return Response.json({ error: 'Generation failed. Please try again.' }, { status: r.status })
      }
      const data = await r.json()
      if (data.code !== 0) return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
      const taskId = data.data?.task_id
      const klingType = imageUrl ? 'image2video' : 'text2video'
      return Response.json({
        status: 'pending', provider: 'kling', task_id: taskId,
        poll_endpoint: `/api/creative/status?provider=kling&task_id=${taskId}&kling_type=${klingType}`,
        message: 'Video generation started.',
      })
    }

    // ── Runway ────────────────────────────────────────────────────────────────
    if (!RUNWAY_KEY) {
      if (!HIGGSFIELD_KEY) return Response.json({ error: 'Video generation unavailable.' }, { status: 503 })
      const hPayload: Record<string, unknown> = { prompt, duration: safeDuration }
      if (style) hPayload.style = style
      hPayload.model = HIGGSFIELD_QUALITY_MODEL[quality as string] ?? HIGGSFIELD_QUALITY_MODEL['720p']
      const hr = await fetch(`${HIGGSFIELD_BASE}/generation`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${HIGGSFIELD_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(hPayload),
      })
      if (!hr.ok) return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
      const hd = await hr.json()
      const hJobId = hd.job_id ?? hd.id
      return Response.json({
        status: 'pending', provider: 'higgsfield', job_id: hJobId,
        quality,
        poll_endpoint: `/api/creative/status?provider=higgsfield&job_id=${hJobId}`,
        message: 'Video generation started.',
      })
    }

    const runwayBody: Record<string, unknown> = {
      model: 'gen3a_turbo',
      promptText: prompt.slice(0, 1000),
      duration: safeDuration,
      ratio: safeRatio,
    }
    if (imageUrl) runwayBody.promptImage = imageUrl

    const r = await fetch(`${RUNWAY_BASE}/image_to_video`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${RUNWAY_KEY}`,
        'Content-Type': 'application/json',
        'X-Runway-Version': RUNWAY_VERSION,
      },
      body: JSON.stringify(runwayBody),
    })
    if (!r.ok) {
      const text = await r.text()
      console.error('[creative/video] runway error:', r.status, text)
      // On auth/key error try Higgsfield fallback
      if ((r.status === 401 || r.status === 403) && HIGGSFIELD_KEY) {
        console.log('[creative/video] runway auth failed, falling back to higgsfield')
        provider = 'higgsfield'
        const hBody: Record<string, unknown> = { prompt, duration: safeDuration }
        if (style) hBody.style = style
        hBody.model = HIGGSFIELD_QUALITY_MODEL[quality as string] ?? HIGGSFIELD_QUALITY_MODEL['720p']
        const hr = await fetch(`${HIGGSFIELD_BASE}/generation`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${HIGGSFIELD_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify(hBody),
        })
        if (!hr.ok) {
          const ht = await hr.text()
          console.error('[creative/video] higgsfield fallback error:', hr.status, ht)
          return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
        }
        const hd = await hr.json()
        const jobId = hd.job_id ?? hd.id
        return Response.json({
          status: 'pending', provider: 'higgsfield', job_id: jobId,
          quality,
          poll_endpoint: `/api/creative/status?provider=higgsfield&job_id=${jobId}`,
          message: 'Video generation started.',
        })
      }
      return Response.json({ error: 'Generation failed. Please try again.' }, { status: r.status })
    }
    const data = await r.json()
    const taskId = data.id
    return Response.json({
      status: 'pending', provider: 'runway', task_id: taskId,
      poll_endpoint: `/api/creative/status?provider=runway&task_id=${taskId}`,
      message: 'Video generation started.',
    })
  } catch (err) {
    console.error('[creative/video] error:', err)
    return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
  }
}
