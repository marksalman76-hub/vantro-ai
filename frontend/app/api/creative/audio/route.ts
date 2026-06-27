import { NextRequest } from 'next/server'

const ELEVENLABS_BASE = 'https://api.elevenlabs.io/v1'

// Default voices per agent (ElevenLabs voice IDs)
const AGENT_VOICES: Record<string, string> = {
  aria:   '21m00Tcm4TlvDq8ikWAM', // Rachel — warm female
  quill:  'EXAVITQu4vr4xnSDxMaL', // Bella — soft female
  pixel:  'VR6AewLTigWG4xSOukaG', // Arnold — deep male
  pulse:  'pNInz6obpgDQGcFmaJgB', // Adam — neutral male
  mosaic: 'ThT5KcBeYPX3keUQqHPh', // Dorothy — expressive female
  lumen:  '21m00Tcm4TlvDq8ikWAM', // Rachel
}

// Voice bank indexed by [gender][age_group][ethnicity_group]
// Using publicly available ElevenLabs voices
const VOICE_BANK: Record<string, Record<string, Record<string, string>>> = {
  male: {
    young:  { western: 'TxGEqnHWrfWFTfGW9XjX', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'VR6AewLTigWG4xSOukaG', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'pNInz6obpgDQGcFmaJgB' },
    middle: { western: 'VR6AewLTigWG4xSOukaG', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'VR6AewLTigWG4xSOukaG', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'VR6AewLTigWG4xSOukaG' },
    mature: { western: 'GBv7mTt0atIp3Br8iCZE', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'VR6AewLTigWG4xSOukaG', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'GBv7mTt0atIp3Br8iCZE' },
  },
  female: {
    young:  { western: 'EXAVITQu4vr4xnSDxMaL', south_asian: '21m00Tcm4TlvDq8ikWAM', east_asian: '21m00Tcm4TlvDq8ikWAM', african: 'ThT5KcBeYPX3keUQqHPh', latin: 'EXAVITQu4vr4xnSDxMaL', middle_eastern: '21m00Tcm4TlvDq8ikWAM' },
    middle: { western: '21m00Tcm4TlvDq8ikWAM', south_asian: '21m00Tcm4TlvDq8ikWAM', east_asian: '21m00Tcm4TlvDq8ikWAM', african: 'ThT5KcBeYPX3keUQqHPh', latin: '21m00Tcm4TlvDq8ikWAM', middle_eastern: '21m00Tcm4TlvDq8ikWAM' },
    mature: { western: 'ThT5KcBeYPX3keUQqHPh', south_asian: '21m00Tcm4TlvDq8ikWAM', east_asian: '21m00Tcm4TlvDq8ikWAM', african: 'ThT5KcBeYPX3keUQqHPh', latin: '21m00Tcm4TlvDq8ikWAM', middle_eastern: 'ThT5KcBeYPX3keUQqHPh' },
  },
  neutral: {
    young:  { western: 'pNInz6obpgDQGcFmaJgB', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'pNInz6obpgDQGcFmaJgB', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'pNInz6obpgDQGcFmaJgB' },
    middle: { western: 'pNInz6obpgDQGcFmaJgB', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'pNInz6obpgDQGcFmaJgB', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'pNInz6obpgDQGcFmaJgB' },
    mature: { western: 'GBv7mTt0atIp3Br8iCZE', south_asian: 'pNInz6obpgDQGcFmaJgB', east_asian: 'pNInz6obpgDQGcFmaJgB', african: 'pNInz6obpgDQGcFmaJgB', latin: 'pNInz6obpgDQGcFmaJgB', middle_eastern: 'pNInz6obpgDQGcFmaJgB' },
  },
}

// Speech style → ElevenLabs stability + similarity_boost
const SPEECH_SETTINGS: Record<string, { stability: number; similarity: number; style: number }> = {
  casual:          { stability: 0.30, similarity: 0.65, style: 0.30 },
  conversational:  { stability: 0.45, similarity: 0.72, style: 0.20 },
  professional:    { stability: 0.65, similarity: 0.82, style: 0.10 },
  formal:          { stability: 0.82, similarity: 0.92, style: 0.05 },
  storytelling:    { stability: 0.38, similarity: 0.68, style: 0.55 },
}

// Mannerism → style adjustment added on top of speech base
const MANNERISM_STYLE: Record<string, number> = {
  neutral:      0.00,
  happy:        0.40,
  enthusiastic: 0.65,
  serious:     -0.15,
  calm:        -0.10,
  authoritative: 0.05,
}

// ElevenLabs language codes for multilingual v2
const LANG_CODES: Record<string, string> = {
  en: 'en', es: 'es', fr: 'fr', de: 'de', pt: 'pt',
  hi: 'hi', ja: 'ja', zh: 'zh', ar: 'ar', it: 'it',
  ko: 'ko', nl: 'nl', pl: 'pl', ru: 'ru', tr: 'tr',
}

function ageToGroup(age: number): 'young' | 'middle' | 'mature' {
  if (age <= 30) return 'young'
  if (age <= 50) return 'middle'
  return 'mature'
}

const ETHNICITY_GROUP: Record<string, string> = {
  western: 'western', british: 'western', australian: 'western', american: 'western',
  east_european: 'western',
  hispanic: 'latin', latin: 'latin',
  south_asian: 'south_asian', indian: 'south_asian',
  east_asian: 'east_asian', chinese: 'east_asian', japanese: 'east_asian', korean: 'east_asian',
  southeast_asian: 'east_asian',
  african: 'african', black: 'african', african_american: 'african',
  middle_eastern: 'middle_eastern',
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      text,
      agentId = 'aria',
      voiceId,
      // Voice profile options
      age,
      gender,
      ethnicity,
      language = 'en',
      speechStyle,
      mannerism,
    } = body

    if (!text || typeof text !== 'string') {
      return Response.json({ error: 'text is required' }, { status: 400 })
    }
    if (text.length > 5000) {
      return Response.json({ error: 'Text too long' }, { status: 400 })
    }

    const ELEVEN_KEY = process.env.ELEVENLABS_API_KEY || ''
    if (!ELEVEN_KEY) {
      return Response.json({ error: 'ELEVENLABS_API_KEY not configured' }, { status: 503 })
    }

    // Voice selection: explicit voiceId > demographic bank > agent default
    let voice: string
    if (voiceId && Object.values(AGENT_VOICES).includes(voiceId)) {
      voice = voiceId
    } else if (gender && age) {
      const ageGroup = ageToGroup(Number(age))
      const ethGroup = ETHNICITY_GROUP[ethnicity?.toLowerCase() || ''] || 'western'
      const genderKey = ['male', 'female', 'neutral'].includes(gender) ? gender : 'neutral'
      voice = VOICE_BANK[genderKey]?.[ageGroup]?.[ethGroup] || AGENT_VOICES[agentId] || AGENT_VOICES.aria
    } else {
      voice = AGENT_VOICES[agentId] || AGENT_VOICES.aria
    }

    // Voice settings from speech style + mannerism
    const base = SPEECH_SETTINGS[speechStyle] || SPEECH_SETTINGS.professional
    const mannerismDelta = MANNERISM_STYLE[mannerism] ?? 0
    const finalStyle = Math.min(1, Math.max(0, base.style + mannerismDelta))
    const finalStability = Math.min(1, Math.max(0, base.stability + (mannerism === 'serious' || mannerism === 'authoritative' ? 0.10 : mannerism === 'enthusiastic' ? -0.10 : 0)))

    const langCode = LANG_CODES[language] || 'en'

    const elevenBody: Record<string, unknown> = {
      text,
      model_id: 'eleven_multilingual_v2',
      voice_settings: {
        stability: finalStability,
        similarity_boost: base.similarity,
        style: finalStyle,
        use_speaker_boost: true,
      },
    }
    if (langCode !== 'en') elevenBody.language_code = langCode

    const r = await fetch(`${ELEVENLABS_BASE}/text-to-speech/${voice}`, {
      method: 'POST',
      headers: { 'xi-api-key': ELEVEN_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify(elevenBody),
    })

    if (!r.ok) {
      const txt = await r.text()
      console.error('[creative/audio] elevenlabs error:', r.status, txt)
      return Response.json({ error: 'Generation failed. Please try again.' }, { status: r.status })
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
