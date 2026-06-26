import { NextRequest } from 'next/server'

const ELEVENLABS_BASE = 'https://api.elevenlabs.io/v1'

const AGENT_VOICES: Record<string, string> = {
  aria:   '21m00Tcm4TlvDq8ikWAM', // Rachel
  quill:  'EXAVITQu4vr4xnSDxMaL', // Bella
  pixel:  'VR6AewLTigWG4xSOukaG', // Arnold
  pulse:  'pNInz6obpgDQGcFmaJgB', // Adam
  mosaic: 'ThT5KcBeYPX3keUQqHPh', // Dorothy
  lumen:  '21m00Tcm4TlvDq8ikWAM', // Rachel
}

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization')
  const token = authHeader?.replace('Bearer ', '').trim()
  if (!token) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const body = await request.json()
    const {
      text,
      agentId = 'aria',
      voiceId,
      stability = 0.5,
      similarityBoost = 0.75,
    } = body

    if (!text || typeof text !== 'string') {
      return Response.json({ error: 'text is required' }, { status: 400 })
    }

    const ELEVEN_KEY = process.env.ELEVENLABS_API_KEY || ''
    if (!ELEVEN_KEY) {
      return Response.json({ error: 'ELEVENLABS_API_KEY not configured' }, { status: 503 })
    }

    const voice = voiceId || AGENT_VOICES[agentId] || AGENT_VOICES.aria

    const r = await fetch(`${ELEVENLABS_BASE}/text-to-speech/${voice}`, {
      method: 'POST',
      headers: {
        'xi-api-key': ELEVEN_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: { stability, similarity_boost: similarityBoost },
      }),
    })

    if (!r.ok) {
      const txt = await r.text()
      return Response.json({ error: `ElevenLabs ${r.status}: ${txt}` }, { status: r.status })
    }

    const buf = await r.arrayBuffer()
    const b64 = Buffer.from(buf).toString('base64')

    return Response.json({
      status: 'success',
      provider: 'elevenlabs',
      voice_id: voice,
      audio_base64: b64,
      content_type: 'audio/mpeg',
      character_count: text.length,
    })
  } catch (err) {
    console.error('[creative/audio] error:', err)
    return Response.json({ error: 'Generation failed. Please try again.' }, { status: 500 })
  }
}
