import { NextRequest } from 'next/server'

const HIGGSFIELD_BASE = 'https://api.higgsfield.ai/v1'

const VALID_MODELS = new Set([
  'seedream_v4_5',
  'gpt_image_2',
  'dtc_ads',
  'recraft_v4_1',
  'soul_cinematic',
  'marketing_studio_image',
])

const VALID_RATIOS = new Set(['16:9', '1:1', '9:16', '4:3', '3:4'])

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      prompt,
      model = 'seedream_v4_5',
      aspectRatio = '1:1',
      style,
    } = body

    if (!prompt || typeof prompt !== 'string') {
      return Response.json({ error: 'prompt is required' }, { status: 400 })
    }
    if (prompt.length > 2000) {
      return Response.json({ error: 'Prompt too long (max 2000 chars).' }, { status: 400 })
    }

    const HIGGSFIELD_KEY = process.env.HIGGSFIELD_API_KEY || ''
    if (!HIGGSFIELD_KEY) {
      return Response.json({ error: 'Image generation unavailable.' }, { status: 503 })
    }

    const safeModel = VALID_MODELS.has(model) ? model : 'seedream_v4_5'
    const safeRatio = VALID_RATIOS.has(aspectRatio) ? aspectRatio : '1:1'

    const payload: Record<string, unknown> = {
      prompt,
      model: safeModel,
      aspect_ratio: safeRatio,
    }
    if (style) payload.style = style

    const r = await fetch(`${HIGGSFIELD_BASE}/image/generate`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${HIGGSFIELD_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!r.ok) {
      const text = await r.text()
      console.error('[creative/image] higgsfield error:', r.status, text)
      return Response.json({ error: 'Image generation failed. Please try again.' }, { status: r.status })
    }

    const data = await r.json()
    const imageUrl: string | undefined =
      data.url || data.image_url || data.output?.[0] || data.images?.[0]

    return Response.json({
      status: 'complete',
      image_url: imageUrl,
      model: safeModel,
      provider: 'higgsfield',
    })
  } catch (err) {
    console.error('[creative/image] error:', err)
    return Response.json({ error: 'Image generation failed. Please try again.' }, { status: 500 })
  }
}
