'use client'

import { useState, useRef, useEffect } from 'react'

const CREATIVE_AGENTS = [
  { id: 'pixel',  name: 'Pixel',  role: 'Design & Creative',    cap: ['video', 'image'] as string[],          color: '#FF6B35' },
  { id: 'mosaic', name: 'Mosaic', role: 'Social Media Manager',  cap: ['video', 'image'] as string[],          color: '#FF6B35' },
  { id: 'pulse',  name: 'Pulse',  role: 'Marketing Strategist',  cap: ['video', 'audio', 'image'] as string[], color: '#FFD700' },
  { id: 'lumen',  name: 'Lumen',  role: 'Brand Strategist',      cap: ['video', 'audio', 'image'] as string[], color: '#FFD700' },
  { id: 'quill',  name: 'Quill',  role: 'Content Writer',        cap: ['audio', 'image'] as string[],          color: '#B084FF' },
  { id: 'aria',   name: 'Aria',   role: 'Voice & Telephony',     cap: ['audio', 'image'] as string[],          color: '#1FFFD6' },
]

const VIDEO_STYLES   = ['cinematic', 'commercial', 'social', 'documentary']
const DURATIONS      = [5, 10, 15, 20, 25, 30]
const QUALITIES      = ['720p', '1080p', '4k'] as const
type VideoQuality    = typeof QUALITIES[number]

const IMAGE_MODELS = [
  { value: 'seedream_v4_5',         label: 'Seedream 4.5' },
  { value: 'gpt_image_2',           label: 'GPT Image 2' },
  { value: 'dtc_ads',               label: 'DTC Ads' },
  { value: 'recraft_v4_1',          label: 'Recraft V4.1' },
  { value: 'soul_cinematic',        label: 'Soul Cinematic' },
  { value: 'marketing_studio_image', label: 'Marketing Studio' },
]
const IMAGE_RATIOS = ['16:9', '1:1', '9:16', '4:3', '3:4']

const VOICE_AGES      = [{ v:'20',label:'18–25'},{ v:'30',label:'26–35'},{ v:'40',label:'36–45'},{ v:'50',label:'46–55'},{ v:'62',label:'56–65'}]
const VOICE_GENDERS   = [{ v:'male',label:'Male'},{ v:'female',label:'Female'},{ v:'neutral',label:'Neutral'}]
const VOICE_ETHNICITIES = [{ v:'western',label:'Western'},{ v:'hispanic',label:'Hispanic'},{ v:'south_asian',label:'South Asian'},{ v:'east_asian',label:'East Asian'},{ v:'african',label:'African'}]
const VOICE_LANGUAGES = [{ v:'en',label:'English'},{ v:'es',label:'Spanish'},{ v:'fr',label:'French'},{ v:'de',label:'German'},{ v:'pt',label:'Portuguese'},{ v:'hi',label:'Hindi'},{ v:'ja',label:'Japanese'},{ v:'zh',label:'Chinese'},{ v:'ar',label:'Arabic'},{ v:'it',label:'Italian'},{ v:'ko',label:'Korean'},{ v:'ru',label:'Russian'},{ v:'tr',label:'Turkish'}]
const VOICE_SPEECHES  = [{ v:'casual',label:'Casual'},{ v:'conversational',label:'Conversational'},{ v:'professional',label:'Professional'},{ v:'formal',label:'Formal'},{ v:'storytelling',label:'Storytelling'}]
const VOICE_MANNERISMS = [{ v:'neutral',label:'Neutral'},{ v:'happy',label:'Happy'},{ v:'enthusiastic',label:'Enthusiastic'},{ v:'serious',label:'Serious'},{ v:'calm',label:'Calm'},{ v:'authoritative',label:'Authoritative'}]

const VIDEO_PROMPT_CHIPS = [
  'Product hero shot on clean white surface, cinematic slow rotation',
  'Aerial city flythrough at golden hour, dramatic depth of field',
  'Abstract logo reveal with particle effects, dark background',
  'Team collaboration montage, modern office, warm color grade',
]

type Mode = 'video' | 'audio' | 'image'

interface ImageResult {
  status?: string
  image_url?: string
  model?: string
  provider?: string
  error?: string
}

interface VideoResult {
  status?: string
  provider?: string
  task_id?: string
  job_id?: string
  poll_endpoint?: string
  video_url?: string
  output?: string[]
  message?: string
  error?: string
}

interface AudioResult {
  status?: string
  provider?: string
  audio_base64?: string
  content_type?: string
  voice_id?: string
  error?: string
}

function compressImage(file: File, maxPx = 1280, quality = 0.82): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(url)
      const scale = Math.min(1, maxPx / Math.max(img.width, img.height))
      const w = Math.round(img.width * scale)
      const h = Math.round(img.height * scale)
      const canvas = document.createElement('canvas')
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext('2d')
      if (!ctx) { reject(new Error('no ctx')); return }
      ctx.drawImage(img, 0, 0, w, h)
      resolve(canvas.toDataURL('image/jpeg', quality))
    }
    img.onerror = reject
    img.src = url
  })
}

export default function AdminCreativePage() {
  const [agent, setAgent] = useState(CREATIVE_AGENTS[0])
  const [mode, setMode]   = useState<Mode>('video')

  // Video state
  const [vPrompt, setVPrompt]     = useState('')
  const [vImageData, setVImageData] = useState<string | null>(null)
  const imgInputRef = useRef<HTMLInputElement | null>(null)
  const [vDuration, setVDuration] = useState(5)
  const [vQuality, setVQuality]   = useState<VideoQuality>('720p')
  const [vStyle, setVStyle]       = useState('')
  const [vResult, setVResult]     = useState<VideoResult | null>(null)
  const [vPolling, setVPolling]   = useState(false)
  const pollRef      = useRef<ReturnType<typeof setInterval> | null>(null)
  const pollCountRef = useRef(0)
  const mountedRef   = useRef(true)

  // Audio state
  const [aText, setAText]       = useState('')
  const [aResult, setAResult]   = useState<AudioResult | null>(null)
  const [audioSrc, setAudioSrc] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Voice profile
  const [aAge, setAAge]           = useState('30')
  const [aGender, setAGender]     = useState('female')
  const [aEthnicity, setAEthnicity] = useState('western')
  const [aLanguage, setALanguage] = useState('en')
  const [aSpeech, setASpeech]     = useState('professional')
  const [aMannerism, setAMannerism] = useState('neutral')

  // Image state
  const [iPrompt, setIPrompt]   = useState('')
  const [iModel, setIModel]     = useState('seedream_v4_5')
  const [iRatio, setIRatio]     = useState('1:1')
  const [iStyle, setIStyle]     = useState('')
  const [iResult, setIResult]   = useState<ImageResult | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  // Switch mode when agent changes and current mode isn't supported
  useEffect(() => {
    if (!agent.cap.includes(mode)) setMode(agent.cap[0] as Mode)
  }, [agent, mode])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Revoke blob URL on audioSrc change
  useEffect(() => {
    return () => { if (audioSrc) URL.revokeObjectURL(audioSrc) }
  }, [audioSrc])

  async function generateVideo() {
    if (!vPrompt.trim()) return
    setLoading(true)
    setError('')
    setVResult(null)
    setVPolling(false)
    if (pollRef.current) clearInterval(pollRef.current)
    pollCountRef.current = 0

    try {
      // Admin: cookie auth only — no Authorization header
      const res  = await fetch('/api/creative/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: vPrompt.trim(), duration: vDuration, quality: vQuality, style: vStyle || undefined, provider: 'auto', imageUrl: vImageData || undefined }),
      })
      const data: VideoResult = await res.json()
      if (!res.ok) { setError(data.error || 'Generation failed'); return }
      setVResult(data)

      if (data.status === 'pending' && data.poll_endpoint) {
        setVPolling(true)
        const interval = setInterval(async () => {
          if (!mountedRef.current) { clearInterval(interval); return }

          pollCountRef.current++
          if (pollCountRef.current > 120) {
            clearInterval(pollRef.current!)
            pollRef.current = null
            if (!mountedRef.current) return
            setVPolling(false)
            setError('Video generation is taking longer than expected. Please try again.')
            return
          }

          try {
            const poll  = await fetch(data.poll_endpoint!)
            const pData: VideoResult = await poll.json()
            if (!mountedRef.current) return
            setVResult(pData)
            const done   = ['SUCCEEDED', 'succeeded', 'complete', 'completed'].includes(pData.status || '')
            const failed = ['FAILED', 'failed', 'error'].includes(pData.status || '')
            if (done || failed) { setVPolling(false); clearInterval(pollRef.current!) }
          } catch { /* retry next tick */ }
        }, 5000)

        if (mountedRef.current) {
          pollRef.current = interval
        } else {
          clearInterval(interval)
        }
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  async function generateAudio() {
    if (!aText.trim()) return
    setLoading(true)
    setError('')
    setAResult(null)
    setAudioSrc(null)

    try {
      // Admin: cookie auth only — no Authorization header
      const res  = await fetch('/api/creative/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: aText.trim(), agentId: agent.id, age: Number(aAge), gender: aGender, ethnicity: aEthnicity, language: aLanguage, speechStyle: aSpeech, mannerism: aMannerism }),
      })
      const data: AudioResult = await res.json()
      if (!res.ok) { setError(data.error || 'Audio generation failed'); return }
      setAResult(data)

      if (data.audio_base64) {
        const buf  = Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))
        const blob = new Blob([buf], { type: data.content_type || 'audio/mpeg' })
        const url  = URL.createObjectURL(blob)
        setAudioSrc(url)
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  async function generateImage() {
    if (!iPrompt.trim()) return
    setLoading(true)
    setError('')
    setIResult(null)
    try {
      const res  = await fetch('/api/creative/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: iPrompt.trim(), model: iModel, aspectRatio: iRatio, style: iStyle || undefined }),
      })
      const data: ImageResult = await res.json()
      if (!res.ok) { setError(data.error || 'Image generation failed'); return }
      setIResult(data)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const videoUrl = vResult?.video_url || vResult?.output?.[0]
  const isDone   = ['SUCCEEDED', 'succeeded', 'complete', 'completed'].includes(vResult?.status || '')

  return (
    <div style={{ padding: '2rem', maxWidth: 1100, margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>

      {/* Page header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: 4, fontFamily: 'system-ui, sans-serif' }}>
            Creative Studio
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.875rem', margin: 0 }}>
            Generate video and audio using your creative agents.
          </p>
        </div>

        {/* ADMIN MODE badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 7,
          padding: '6px 14px', borderRadius: 99,
          background: 'rgba(31,255,214,0.08)',
          border: '1px solid rgba(31,255,214,0.3)',
          flexShrink: 0,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block' }} />
          <span style={{ fontSize: 11, fontWeight: 700, color: '#1FFFD6', letterSpacing: '0.08em' }}>ADMIN MODE</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr 300px', gap: '1.25rem', alignItems: 'start' }}>

        {/* Agent picker */}
        <div>
          <p style={{ fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.75rem' }}>Agent</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {CREATIVE_AGENTS.map(a => (
              <button
                key={a.id}
                onClick={() => setAgent(a)}
                style={{
                  textAlign: 'left', padding: '0.625rem 0.875rem', borderRadius: 10,
                  fontFamily: 'system-ui, sans-serif', cursor: 'pointer',
                  background: agent.id === a.id ? `${a.color}18` : 'rgba(255,255,255,0.03)',
                  border: `1px solid ${agent.id === a.id ? `${a.color}60` : 'rgba(255,255,255,0.07)'}`,
                  transition: 'opacity 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.opacity = '0.85' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = '1' }}
              >
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: agent.id === a.id ? a.color : '#fff' }}>{a.name}</div>
                <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', marginTop: 1 }}>{a.role}</div>
                <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                  {a.cap.map(c => (
                    <span key={c} style={{ fontSize: '0.6rem', padding: '1px 5px', borderRadius: 4, background: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{c}</span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Work area */}
        <div>
          {/* Mode tabs */}
          <div style={{ display: 'flex', gap: 6, marginBottom: '1.25rem' }}>
            {(['video', 'image', 'audio'] as Mode[]).map(m => {
              const avail = agent.cap.includes(m)
              const label = m === 'video' ? '▶ Video' : m === 'image' ? '⬡ Image' : '♪ Audio'
              return (
                <button
                  key={m}
                  onClick={() => avail && setMode(m)}
                  disabled={!avail}
                  style={{
                    padding: '0.4rem 1rem', borderRadius: 8, fontSize: '0.82rem', fontWeight: 500,
                    fontFamily: 'system-ui, sans-serif', cursor: avail ? 'pointer' : 'not-allowed',
                    opacity: avail ? 1 : 0.35, textTransform: 'capitalize',
                    background: mode === m && avail ? 'rgba(31,255,214,0.12)' : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${mode === m && avail ? 'rgba(31,255,214,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    color: mode === m && avail ? '#1FFFD6' : avail ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.2)',
                  }}
                >
                  {label}
                </button>
              )
            })}
          </div>

          {/* VIDEO */}
          {mode === 'video' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Prompt</label>
                <textarea
                  value={vPrompt}
                  onChange={e => setVPrompt(e.target.value)}
                  placeholder="A product hero shot of sneakers on a clean white surface, cinematic lighting, slow rotation…"
                  rows={3}
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', resize: 'vertical', outline: 'none' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(31,255,214,0.45)' }}
                  onBlur={e =>  { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
                />
              </div>

              {/* Image attach */}
              <div style={{ marginTop: -4 }}>
                <input
                  ref={imgInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={e => {
                    const file = e.target.files?.[0]
                    if (!file) return
                    e.target.value = ''
                    compressImage(file).then(setVImageData).catch(() => {
                      const reader = new FileReader()
                      reader.onload = ev => setVImageData(ev.target?.result as string)
                      reader.readAsDataURL(file)
                    })
                  }}
                />
                {vImageData ? (
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 8px', borderRadius: 8, background: 'rgba(31,255,214,0.08)', border: '1px solid rgba(31,255,214,0.3)' }}>
                    <img src={vImageData} alt="ref" style={{ width: 32, height: 32, borderRadius: 4, objectFit: 'cover' }} />
                    <span style={{ fontSize: '0.72rem', color: '#1FFFD6' }}>Image attached</span>
                    <button type="button" onClick={() => setVImageData(null)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', fontSize: '0.85rem', lineHeight: 1, padding: 0 }}>×</button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => imgInputRef.current?.click()}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '4px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.45)', fontSize: '0.75rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    <span style={{ fontSize: '1rem', lineHeight: 1 }}>+</span> Add reference image
                  </button>
                )}
              </div>

              {/* Prompt chips */}
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: -4 }}>
                {VIDEO_PROMPT_CHIPS.map(chip => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setVPrompt(chip)}
                    style={{
                      padding: '4px 12px', borderRadius: 99,
                      border: '1px solid rgba(255,255,255,0.12)',
                      background: 'rgba(255,255,255,0.04)',
                      color: 'rgba(255,255,255,0.45)',
                      fontSize: '0.72rem', fontFamily: 'system-ui, sans-serif',
                      cursor: 'pointer', textAlign: 'left', lineHeight: 1.3,
                      transition: 'opacity 0.15s',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.opacity = '0.75' }}
                    onMouseLeave={e => { e.currentTarget.style.opacity = '1' }}
                  >
                    {chip.length > 40 ? chip.slice(0, 40) + '…' : chip}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Quality</label>
                  <select
                    value={vQuality}
                    onChange={e => setVQuality(e.target.value as VideoQuality)}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    {QUALITIES.map(q => <option key={q} value={q}>{q.toUpperCase()}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Duration</label>
                  <select
                    value={vDuration}
                    onChange={e => setVDuration(Number(e.target.value))}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    {DURATIONS.map(d => <option key={d} value={d}>{d}s</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                  <select
                    value={vStyle}
                    onChange={e => setVStyle(e.target.value)}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    <option value="">Auto</option>
                    {VIDEO_STYLES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
              </div>

              <button
                onClick={generateVideo}
                disabled={loading || !vPrompt.trim()}
                style={{
                  alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10,
                  fontSize: '0.875rem', fontWeight: 700, color: loading || !vPrompt.trim() ? 'rgba(255,255,255,0.3)' : '#0A0D14',
                  fontFamily: 'system-ui, sans-serif',
                  cursor: loading || !vPrompt.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !vPrompt.trim() ? 0.5 : 1,
                  background: loading || !vPrompt.trim() ? 'rgba(255,255,255,0.06)' : 'linear-gradient(135deg,#1FFFD6,#00B8A0)',
                  border: 'none', transition: 'opacity 0.15s',
                }}
                onMouseEnter={e => { if (!loading && vPrompt.trim()) e.currentTarget.style.opacity = '0.85' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = loading || !vPrompt.trim() ? '0.5' : '1' }}
              >
                {loading ? 'Generating…' : '▶ Generate Video'}
              </button>

            </div>
          )}

          {/* IMAGE */}
          {mode === 'image' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Prompt</label>
                <textarea
                  value={iPrompt}
                  onChange={e => setIPrompt(e.target.value)}
                  placeholder="A product hero shot of sneakers on a clean white surface, studio lighting, photorealistic…"
                  rows={3}
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', resize: 'vertical', outline: 'none' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(31,255,214,0.45)' }}
                  onBlur={e =>  { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 2 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Model</label>
                  <select
                    value={iModel}
                    onChange={e => setIModel(e.target.value)}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    {IMAGE_MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Ratio</label>
                  <select
                    value={iRatio}
                    onChange={e => setIRatio(e.target.value)}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    {IMAGE_RATIOS.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                  <select
                    value={iStyle}
                    onChange={e => setIStyle(e.target.value)}
                    style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}
                  >
                    <option value="">Auto</option>
                    {VIDEO_STYLES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
              </div>

              <button
                onClick={generateImage}
                disabled={loading || !iPrompt.trim()}
                style={{
                  alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10,
                  fontSize: '0.875rem', fontWeight: 700, color: loading || !iPrompt.trim() ? 'rgba(255,255,255,0.3)' : '#0A0D14',
                  fontFamily: 'system-ui, sans-serif',
                  cursor: loading || !iPrompt.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !iPrompt.trim() ? 0.5 : 1,
                  background: loading || !iPrompt.trim() ? 'rgba(255,255,255,0.06)' : 'linear-gradient(135deg,#1FFFD6,#00B8A0)',
                  border: 'none', transition: 'opacity 0.15s',
                }}
                onMouseEnter={e => { if (!loading && iPrompt.trim()) e.currentTarget.style.opacity = '0.85' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = loading || !iPrompt.trim() ? '0.5' : '1' }}
              >
                {loading ? 'Generating…' : '⬡ Generate Image'}
              </button>
            </div>
          )}

          {/* AUDIO */}
          {mode === 'audio' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Script</label>
                <textarea
                  value={aText}
                  onChange={e => setAText(e.target.value)}
                  placeholder="Welcome to Vantro — where AI agents handle the work so you can focus on growth."
                  rows={4}
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'system-ui, sans-serif', resize: 'vertical', outline: 'none' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(31,255,214,0.45)' }}
                  onBlur={e =>  { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
                />
              </div>

              {/* Voice Profile — row 1 */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                {([
                  { label: 'Age', val: aAge, set: setAAge, opts: VOICE_AGES },
                  { label: 'Gender', val: aGender, set: setAGender, opts: VOICE_GENDERS },
                  { label: 'Language', val: aLanguage, set: setALanguage, opts: VOICE_LANGUAGES },
                ] as { label: string; val: string; set: (v: string) => void; opts: { v: string; label: string }[] }[]).map(({ label, val, set, opts }) => (
                  <div key={label}>
                    <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 600, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>{label}</label>
                    <select value={val} onChange={e => set(e.target.value)} style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 8, padding: '0.5rem 0.625rem', color: '#fff', fontSize: '0.8rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}>
                      {opts.map(o => <option key={o.v} value={o.v}>{o.label}</option>)}
                    </select>
                  </div>
                ))}
              </div>

              {/* Voice Profile — row 2 */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                {([
                  { label: 'Ethnicity', val: aEthnicity, set: setAEthnicity, opts: VOICE_ETHNICITIES },
                  { label: 'Speech', val: aSpeech, set: setASpeech, opts: VOICE_SPEECHES },
                  { label: 'Mannerism', val: aMannerism, set: setAMannerism, opts: VOICE_MANNERISMS },
                ] as { label: string; val: string; set: (v: string) => void; opts: { v: string; label: string }[] }[]).map(({ label, val, set, opts }) => (
                  <div key={label}>
                    <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 600, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>{label}</label>
                    <select value={val} onChange={e => set(e.target.value)} style={{ width: '100%', background: '#12151E', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 8, padding: '0.5rem 0.625rem', color: '#fff', fontSize: '0.8rem', fontFamily: 'system-ui, sans-serif', cursor: 'pointer' }}>
                      {opts.map(o => <option key={o.v} value={o.v}>{o.label}</option>)}
                    </select>
                  </div>
                ))}
              </div>

              <button
                onClick={generateAudio}
                disabled={loading || !aText.trim()}
                style={{
                  alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10,
                  fontSize: '0.875rem', fontWeight: 700,
                  color: loading || !aText.trim() ? 'rgba(255,255,255,0.3)' : '#0A0D14',
                  fontFamily: 'system-ui, sans-serif',
                  cursor: loading || !aText.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !aText.trim() ? 0.5 : 1,
                  background: loading || !aText.trim() ? 'rgba(255,255,255,0.06)' : 'linear-gradient(135deg,#1FFFD6,#00B8A0)',
                  border: 'none', transition: 'opacity 0.15s',
                }}
                onMouseEnter={e => { if (!loading && aText.trim()) e.currentTarget.style.opacity = '0.85' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = loading || !aText.trim() ? '0.5' : '1' }}
              >
                {loading ? 'Generating…' : '♪ Generate Audio'}
              </button>

            </div>
          )}
        </div>

        {/* ── Preview Panel ── */}
        <div style={{ position: 'sticky', top: '2rem' }}>
          <p style={{ fontSize: '0.68rem', fontWeight: 700, color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.625rem', fontFamily: 'system-ui, sans-serif' }}>Output Preview</p>
          <div style={{ borderRadius: 14, overflow: 'hidden', background: '#0D1017', border: '1px solid rgba(255,255,255,0.07)', minHeight: 300, display: 'flex', flexDirection: 'column' }}>
            <style>{`@keyframes admCreDot{0%,80%,100%{opacity:.25;transform:scale(.7)}40%{opacity:1;transform:scale(1)}} @keyframes admVidProg{0%{width:12%}100%{width:88%}}`}</style>

            {/* VIDEO states */}
            {mode === 'video' && !vResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ width: 44, height: 44, borderRadius: 10, border: '2px solid rgba(255,255,255,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.3rem', color: 'rgba(255,255,255,0.6)' }}>▶</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', fontFamily: 'system-ui, sans-serif', lineHeight: 1.4 }}>Video output appears here</span>
              </div>
            )}
            {mode === 'video' && loading && !vResult && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block', animation: `admCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)', fontFamily: 'system-ui, sans-serif' }}>Generating…</span>
              </div>
            )}
            {mode === 'video' && vResult && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                  <span style={{
                    fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'system-ui, sans-serif',
                    background: isDone ? 'rgba(31,255,214,0.15)' : vPolling ? 'rgba(255,215,0,0.12)' : 'rgba(255,255,255,0.06)',
                    color: isDone ? '#1FFFD6' : vPolling ? '#FFD700' : 'rgba(255,255,255,0.4)',
                  }}>
                    {isDone ? 'Done' : vPolling ? 'Processing…' : vResult.status}
                  </span>
                </div>
                {videoUrl ? (
                  <div>
                    <video src={videoUrl} controls style={{ width: '100%', borderRadius: 8, marginBottom: 8, maxHeight: 280, background: '#000' }} />
                    <a href={videoUrl} download target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem', color: '#1FFFD6', textDecoration: 'none', fontFamily: 'system-ui, sans-serif' }}>↓ Download</a>
                  </div>
                ) : vPolling ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: '0.75rem 0' }}>
                    <div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}>
                      {[0,1,2].map(i => <span key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block', animation: `admCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                    </div>
                    <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'rgba(255,255,255,0.35)', margin: 0, fontFamily: 'system-ui, sans-serif' }}>Processing video — this may take a few minutes</p>
                    <div style={{ height: 3, borderRadius: 99, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
                      <div style={{ height: '100%', background: 'linear-gradient(90deg,#1FFFD6,#00D9FF)', borderRadius: 99, animation: 'admVidProg 3s ease-in-out infinite alternate' }} />
                    </div>
                  </div>
                ) : (
                  vResult.message && <p style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.35)', margin: 0, fontFamily: 'system-ui, sans-serif' }}>{vResult.message}</p>
                )}
              </div>
            )}

            {/* IMAGE states */}
            {mode === 'image' && !iResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ width: 44, height: 44, borderRadius: 10, border: '2px solid rgba(255,255,255,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.3rem', color: 'rgba(255,255,255,0.6)' }}>⬡</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', fontFamily: 'system-ui, sans-serif', lineHeight: 1.4 }}>Image output appears here</span>
              </div>
            )}
            {mode === 'image' && loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block', animation: `admCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)', fontFamily: 'system-ui, sans-serif' }}>Generating image…</span>
              </div>
            )}
            {mode === 'image' && iResult && !loading && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                  <span style={{ fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'system-ui, sans-serif', background: iResult.image_url ? 'rgba(31,255,214,0.15)' : 'rgba(239,68,68,0.15)', color: iResult.image_url ? '#1FFFD6' : '#ef4444' }}>
                    {iResult.image_url ? 'Done' : 'Failed'}
                  </span>
                  {iResult.model && <span style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.3)', fontFamily: 'system-ui, sans-serif' }}>{iResult.model}</span>}
                </div>
                {iResult.image_url ? (
                  <div>
                    <img src={iResult.image_url} alt="Generated" style={{ width: '100%', borderRadius: 8, marginBottom: 8, maxHeight: 280, objectFit: 'contain', background: '#000' }} />
                    <a href={iResult.image_url} download target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem', color: '#1FFFD6', textDecoration: 'none', fontFamily: 'system-ui, sans-serif' }}>↓ Download</a>
                  </div>
                ) : (
                  <p style={{ fontSize: '0.78rem', color: '#ef4444', margin: 0, fontFamily: 'system-ui, sans-serif' }}>Generation failed. Please try again.</p>
                )}
              </div>
            )}

            {/* AUDIO states */}
            {mode === 'audio' && !aResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ fontSize: '2rem', color: 'rgba(255,255,255,0.5)' }}>♪</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', fontFamily: 'system-ui, sans-serif', lineHeight: 1.4 }}>Audio output appears here</span>
              </div>
            )}
            {mode === 'audio' && loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block', animation: `admCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)', fontFamily: 'system-ui, sans-serif' }}>Generating audio…</span>
              </div>
            )}
            {mode === 'audio' && aResult && !loading && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ marginBottom: 10 }}>
                  <span style={{ fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'system-ui, sans-serif', background: aResult.status === 'success' ? 'rgba(31,255,214,0.15)' : 'rgba(239,68,68,0.15)', color: aResult.status === 'success' ? '#1FFFD6' : '#ef4444' }}>
                    {aResult.status}
                  </span>
                </div>
                {audioSrc && (
                  <div>
                    <audio ref={audioRef} src={audioSrc} controls style={{ width: '100%', borderRadius: 8, marginBottom: 8 }} onLoadedData={() => void audioRef.current?.play()} />
                    <a href={audioSrc} download="vantro-audio.mp3" style={{ fontSize: '0.75rem', color: '#1FFFD6', textDecoration: 'none', fontFamily: 'system-ui, sans-serif' }}>↓ Download</a>
                  </div>
                )}
              </div>
            )}

            {/* Error */}
            {error && (
              <div style={{ margin: '0.75rem', padding: '0.75rem', borderRadius: 8, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.18)', color: '#f87171', fontSize: '0.78rem', fontFamily: 'system-ui, sans-serif' }}>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
