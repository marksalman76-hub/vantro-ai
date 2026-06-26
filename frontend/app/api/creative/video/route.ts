import { NextRequest } from 'next/server'

const RUNWAY_BASE     = 'https://api.dev.runwayml.com/v1'
const RUNWAY_VERSION  = '2024-11-06'
const HIGGSFIELD_BASE = 'https://api.higgsfield.ai/v1'

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization')
  const token = authHeader?.replace('Bearer ', '').trim()
  if (!token) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const body = await request.json()
    const { prompt, duration = 5, ratio = '1280:720', style, provider: reqProvider = 'auto' } = body

    if (!prompt || typeof prompt !== 'string') {
      return Response.json({ error: 'prompt is required' }, { status: 400 })
    }

    const RUNWAY_KEY     = process.env.RUNWAY_API_KEY || ''
    const HIGGSFIELD_KEY = process.env.HIGGSFIELD_API_KEY || ''

    const provider = reqProvider === 'auto'
      ? (HIGGSFIELD_KEY ? 'higgsfield' : 'runway')
      : reqProvider

    if (provider === 'higgsfield') {
      if (!HIGGSFIELD_KEY) {
        return Response.json({ error: 'HIGGSFIELD_API_KEY not configured' }, { status: 503 })
      }
      const payload: Record<string, unknown> = { prompt, duration }
      if (style) payload.style = style

      const r = await fetch(`${HIGGSFIELD_BASE}/generation`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${HIGGSFIELD_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!r.ok) {
        const text = await r.text()
        return Response.json({ error: `Higgsfield ${r.status}: ${text}` }, { status: r.status })
      }

      const data = await r.json()
      const jobId = data.job_id ?? data.id
      return Response.json({
        status: 'pending',
        provider: 'higgsfield',
        job_id: jobId,
        poll_endpoint: `/api/creative/status?provider=higgsfield&job_id=${jobId}`,
        message: 'Higgsfield video generation started.',
      })
    }

    // Runway Gen-3
    if (!RUNWAY_KEY) {
      return Response.json({ error: 'RUNWAY_API_KEY not configured' }, { status: 503 })
    }
    const r = await fetch(`${RUNWAY_BASE}/image_to_video`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${RUNWAY_KEY}`,
        'Content-Type': 'application/json',
        'X-Runway-Version': RUNWAY_VERSION,
      },
      body: JSON.stringify({ promptText: prompt, model: 'gen3a_turbo', duration, ratio }),
    })

    if (!r.ok) {
      const text = await r.text()
      return Response.json({ error: `Runway ${r.status}: ${text}` }, { status: r.status })
    }

    const data = await r.json()
    const taskId = data.id
    return Response.json({
      status: 'pending',
      provider: 'runway',
      task_id: taskId,
      poll_endpoint: `/api/creative/status?provider=runway&task_id=${taskId}`,
      message: 'Runway video generation started.',
    })
  } catch (err) {
    console.error('[creative/video] error:', err)
    return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
  }
}
