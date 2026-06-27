'use client'

import { useState, useRef, useEffect } from 'react'
import gsap from 'gsap'
import { CREDIT_COSTS, deductCredits, hasCredits, VIDEO_CREDIT_COSTS, PLANS_WITH_4K } from '@/lib/credits'
import type { VideoQuality, VideoDuration } from '@/lib/credits'

interface GenerationJob {
  id: string
  type: 'video' | 'audio'
  provider: string
  job_id: string
  task_id?: string
  poll_endpoint?: string
  prompt: string
  quality?: string
  duration?: number
  status: 'pending' | 'processing' | 'complete' | 'failed'
  result_url?: string
  credits_used: number
  started_at: string
  completed_at?: string
}

const CREATIVE_AGENTS = [
  { id: 'pixel',  name: 'Pixel',  role: 'Design & Creative',   cap: ['video', 'image', 'audio'] as string[], color: '#FF6B35' },
  { id: 'mosaic', name: 'Mosaic', role: 'Social Media Manager', cap: ['video', 'image', 'audio'] as string[], color: '#FF6B35' },
  { id: 'pulse',  name: 'Pulse',  role: 'Marketing Strategist', cap: ['video', 'image', 'audio'] as string[], color: '#FFD700' },
  { id: 'lumen',  name: 'Lumen',  role: 'Brand Strategist',     cap: ['video', 'image', 'audio'] as string[], color: '#FFD700' },
  { id: 'quill',  name: 'Quill',  role: 'Content Writer',       cap: ['video', 'image', 'audio'] as string[], color: '#B084FF' },
  { id: 'aria',   name: 'Aria',   role: 'Voice & Telephony',    cap: ['video', 'image', 'audio'] as string[], color: '#00D9FF' },
]

const VIDEO_STYLES = ['cinematic', 'commercial', 'social', 'documentary']
const DURATIONS = [5, 10, 15, 20, 25, 30] as const

const IMAGE_MODELS = [
  { value: 'seedream_v4_5',          label: 'Photorealistic' },
  { value: 'gpt_image_2',            label: 'Vivid & Creative' },
  { value: 'dtc_ads',                label: 'Product Ads' },
  { value: 'recraft_v4_1',           label: 'Vector & Design' },
  { value: 'soul_cinematic',         label: 'Cinematic' },
  { value: 'marketing_studio_image', label: 'Marketing' },
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

export default function CreativeStudioPage() {
  const [agent, setAgent]     = useState(CREATIVE_AGENTS[0])
  const [mode, setMode]       = useState<Mode>('video')

  // Video
  const [vPrompt, setVPrompt]       = useState('')
  const [vImageData, setVImageData] = useState<string | null>(null)
  const imgInputRef = useRef<HTMLInputElement | null>(null)
  const [quality, setQuality] = useState<VideoQuality>('720p')
  const [duration, setDuration] = useState<VideoDuration>(5)
  const [userPlan, setUserPlan] = useState<string>('starter')
  const [vStyle, setVStyle]       = useState('')
  const [vResult, setVResult]     = useState<VideoResult | null>(null)
  const [vPolling, setVPolling]   = useState(false)
  const pollRef      = useRef<ReturnType<typeof setInterval> | null>(null)
  const pollCountRef = useRef(0)
  const mountedRef   = useRef(true)

  // Audio
  const [aText, setAText]       = useState('')
  const [aResult, setAResult]   = useState<AudioResult | null>(null)
  const [audioSrc, setAudioSrc] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Voice profile
  const [aAge, setAAge]             = useState('30')
  const [aGender, setAGender]       = useState('female')
  const [aEthnicity, setAEthnicity] = useState('western')
  const [aLanguage, setALanguage]   = useState('en')
  const [aSpeech, setASpeech]       = useState('professional')
  const [aMannerism, setAMannerism] = useState('neutral')

  // Image
  const [iPrompt, setIPrompt]   = useState('')
  const [iModel, setIModel]     = useState('seedream_v4_5')
  const [iRatio, setIRatio]     = useState('1:1')
  const [iStyle, setIStyle]     = useState('')
  const [iResult, setIResult]   = useState<ImageResult | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [credits, setCredits] = useState<number>(0)
  const [queue, setQueue]     = useState<GenerationJob[]>([])

  function loadQueue(): GenerationJob[] {
    try {
      return JSON.parse(localStorage.getItem('vantro_generation_queue') || '[]')
    } catch { return [] }
  }

  function saveQueue(jobs: GenerationJob[]) {
    localStorage.setItem('vantro_generation_queue', JSON.stringify(jobs))
    setQueue(jobs)
  }

  function addToQueue(job: GenerationJob) {
    const existing = loadQueue()
    const trimmed = [...existing, job].slice(-20)
    saveQueue(trimmed)
  }

  function updateJobInQueue(id: string, updates: Partial<GenerationJob>) {
    const existing = loadQueue()
    const updated = existing.map(j => j.id === id ? { ...j, ...updates } : j)
    saveQueue(updated)
  }

  // Read credit balance and plan on mount
  useEffect(() => {
    setCredits(parseFloat(localStorage.getItem('vantro_credits') || '0'))
    setUserPlan(localStorage.getItem('vantro_plan') || 'starter')
    setQueue(loadQueue())
  }, [])

  useEffect(() => {
    if (!agent.cap.includes(mode)) setMode(agent.cap[0] as Mode)
  }, [agent, mode])

  // Cleanup on unmount — mounted guard + interval cancel
  useEffect(() => {
    return () => {
      mountedRef.current = false
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Revoke blob URL when audioSrc changes or component unmounts
  useEffect(() => {
    return () => {
      if (audioSrc) URL.revokeObjectURL(audioSrc)
    }
  }, [audioSrc])

  // Poll queue jobs every 8 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      const jobs = loadQueue()
      const active = jobs.filter(j => j.status === 'pending' || j.status === 'processing')
      if (active.length === 0) return

      for (const job of active) {
        if (!job.poll_endpoint) continue
        try {
          const r = await fetch(job.poll_endpoint)
          if (!r.ok) continue
          const data = await r.json()

          const rawStatus = (data.status || data.task_status || '') as string
          const isComplete = rawStatus === 'SUCCEEDED' || rawStatus === 'succeed' || rawStatus === 'completed'
          const isFailed = rawStatus === 'FAILED' || rawStatus === 'failed'
          const videoUrl: string | null = (data.output?.[0] as string | undefined) || data.video_url || data.url || null

          if (isComplete) {
            updateJobInQueue(job.id, {
              status: 'complete',
              result_url: videoUrl ?? undefined,
              completed_at: new Date().toISOString(),
            })
          } else if (isFailed) {
            updateJobInQueue(job.id, { status: 'failed', completed_at: new Date().toISOString() })
          } else {
            updateJobInQueue(job.id, { status: 'processing' })
          }
        } catch { /* ignore poll errors */ }
      }
    }, 8000)
    return () => clearInterval(interval)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function generateVideo() {
    if (!vPrompt.trim()) return
    setLoading(true)
    setError('')
    setVResult(null)
    setVPolling(false)
    if (pollRef.current) clearInterval(pollRef.current)
    pollCountRef.current = 0

    // Check credits before fetch
    const videoCost = VIDEO_CREDIT_COSTS[quality][duration as VideoDuration] ?? 3
    if (!hasCredits(videoCost)) {
      setError('Insufficient credits. Top up to continue.')
      setLoading(false)
      return
    }

    try {
      const res  = await fetch('/api/creative/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: vPrompt.trim(), duration, quality, ratio: '16:9', style: vStyle || undefined, provider: 'auto', imageUrl: vImageData || undefined }),
      })
      const data: VideoResult = await res.json()
      if (!res.ok) { setError(data.error || 'Generation failed'); return }
      // Deduct credits after job accepted
      const newBal = deductCredits(videoCost)
      setCredits(newBal)
      setVResult(data)

      // Add to generation queue
      const jobEntry: GenerationJob = {
        id: crypto.randomUUID(),
        type: 'video',
        provider: data.provider || 'higgsfield',
        job_id: data.job_id || data.task_id || '',
        task_id: data.task_id,
        poll_endpoint: data.poll_endpoint,
        prompt: vPrompt.slice(0, 100),
        quality: quality,
        duration: duration,
        status: 'pending',
        credits_used: videoCost,
        started_at: new Date().toISOString(),
      }
      addToQueue(jobEntry)

      if (data.status === 'pending' && data.poll_endpoint) {
        setVPolling(true)
        const interval = setInterval(async () => {
          // Mounted guard — bail immediately if unmounted
          if (!mountedRef.current) {
            clearInterval(interval)
            return
          }

          // Timeout guard — stop after 120 ticks (~10 min)
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

            // Second mounted guard — check again after the await
            if (!mountedRef.current) return

            setVResult(pData)
            const done   = ['SUCCEEDED', 'succeeded', 'complete', 'completed'].includes(pData.status || '')
            const failed = ['FAILED', 'failed', 'error'].includes(pData.status || '')
            if (done || failed) { setVPolling(false); clearInterval(pollRef.current!) }
          } catch { /* retry next tick */ }
        }, 5000)

        // Only assign to ref if still mounted (avoids TOCTOU leak)
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

    // Check credits before fetch
    if (!hasCredits(CREDIT_COSTS.audio)) {
      setError('Insufficient credits. Top up to continue.')
      setLoading(false)
      return
    }

    try {
      const res  = await fetch('/api/creative/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: aText.trim(), agentId: agent.id, age: Number(aAge), gender: aGender, ethnicity: aEthnicity, language: aLanguage, speechStyle: aSpeech, mannerism: aMannerism }),
      })
      const data: AudioResult = await res.json()
      if (!res.ok) { setError(data.error || 'Audio generation failed'); return }
      // Deduct credits after successful response
      const newBal = deductCredits(CREDIT_COSTS.audio)
      setCredits(newBal)
      setAResult(data)

      // Add to generation queue
      const audioJobEntry: GenerationJob = {
        id: crypto.randomUUID(),
        type: 'audio',
        provider: 'elevenlabs',
        job_id: crypto.randomUUID(),
        prompt: aText.slice(0, 100),
        status: 'complete',
        result_url: (data as AudioResult & { audio_url?: string }).audio_url || undefined,
        credits_used: CREDIT_COSTS.audio,
        started_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      }
      addToQueue(audioJobEntry)

      if (data.audio_base64) {
        const buf  = Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))
        const blob = new Blob([buf], { type: data.content_type || 'audio/mpeg' })
        const url  = URL.createObjectURL(blob)
        setAudioSrc(url)
        // Autoplay is triggered by onLoadedData on the <audio> element — no setTimeout needed
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

    if (!hasCredits(CREDIT_COSTS.image)) {
      setError('Insufficient credits. Top up to continue.')
      setLoading(false)
      return
    }

    try {
      const res  = await fetch('/api/creative/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: iPrompt.trim(), model: iModel, aspectRatio: iRatio, style: iStyle || undefined }),
      })
      const data: ImageResult = await res.json()
      if (!res.ok) { setError(data.error || 'Image generation failed'); return }
      const newBal = deductCredits(CREDIT_COSTS.image)
      setCredits(newBal)
      setIResult(data)

      const imageJobEntry: GenerationJob = {
        id: crypto.randomUUID(),
        type: 'video', // repurpose 'video' type for image (same queue)
        provider: 'higgsfield',
        job_id: crypto.randomUUID(),
        prompt: iPrompt.slice(0, 100),
        quality: iModel,
        status: 'complete',
        result_url: data.image_url,
        credits_used: CREDIT_COSTS.image,
        started_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      }
      addToQueue(imageJobEntry)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const videoUrl = vResult?.video_url || vResult?.output?.[0]
  const isDone   = ['SUCCEEDED', 'succeeded', 'complete', 'completed'].includes(vResult?.status || '')
  const currentVideoCost = VIDEO_CREDIT_COSTS[quality][duration as VideoDuration] ?? 3
  const can4K = PLANS_WITH_4K.has(userPlan)

  return (
    <div style={{ padding: '2rem', maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 4 }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: 0 }}>Creative Studio</h1>
          <div style={{
            fontSize: 11, color: 'rgba(255,255,255,0.4)', fontFamily: "'Space Grotesk', sans-serif",
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <span style={{ color: '#1FFFD6', fontWeight: 700 }}>{credits}</span> credits remaining
            <span style={{ opacity: 0.5 }}>· Video: 3–5 cr · Image: 2 cr · Audio: 1 cr</span>
          </div>
        </div>
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.875rem', margin: 0 }}>
          Generate video, images, and audio using your creative agents.
        </p>
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
                onMouseEnter={(e) => {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { opacity: 0.85, duration: 0.15, ease: 'power2.out' })
                }}
                onMouseLeave={(e) => {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { opacity: 1, duration: 0.15, ease: 'power2.out' })
                }}
                style={{
                  textAlign: 'left', padding: '0.625rem 0.875rem', borderRadius: 10, fontFamily: 'inherit', cursor: 'pointer',
                  background: agent.id === a.id ? `${a.color}18` : 'rgba(255,255,255,0.03)',
                  border: `1px solid ${agent.id === a.id ? `${a.color}60` : 'rgba(255,255,255,0.07)'}`,
                }}
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
                    fontFamily: 'inherit', cursor: avail ? 'pointer' : 'not-allowed',
                    opacity: avail ? 1 : 0.35, textTransform: 'capitalize',
                    background: mode === m && avail ? 'rgba(255,107,53,0.15)' : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${mode === m && avail ? 'rgba(255,107,53,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    color: mode === m && avail ? '#FF6B35' : avail ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.2)',
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
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', resize: 'vertical' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(255,107,53,0.5)' }}
                  onBlur={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
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
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 8px', borderRadius: 8, background: 'rgba(255,107,53,0.08)', border: '1px solid rgba(255,107,53,0.35)' }}>
                    <img src={vImageData} alt="ref" style={{ width: 32, height: 32, borderRadius: 4, objectFit: 'cover' }} />
                    <span style={{ fontSize: '0.72rem', color: '#FF6B35' }}>Image attached</span>
                    <button type="button" onClick={() => setVImageData(null)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', fontSize: '0.85rem', lineHeight: 1, padding: 0 }}>×</button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => imgInputRef.current?.click()}
                    onMouseEnter={e => { gsap.killTweensOf(e.currentTarget); gsap.to(e.currentTarget, { opacity: 0.8, duration: 0.15 }) }}
                    onMouseLeave={e => { gsap.killTweensOf(e.currentTarget); gsap.to(e.currentTarget, { opacity: 1, duration: 0.15 }) }}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '4px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.45)', fontSize: '0.75rem', fontFamily: 'inherit', cursor: 'pointer' }}
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
                      padding: '4px 12px',
                      borderRadius: 99,
                      border: '1px solid rgba(255,255,255,0.12)',
                      background: 'rgba(255,255,255,0.04)',
                      color: 'rgba(255,255,255,0.45)',
                      fontSize: '0.72rem',
                      fontFamily: 'inherit',
                      cursor: 'pointer',
                      textAlign: 'left',
                      lineHeight: 1.3,
                    }}
                    onMouseEnter={e => {
                      gsap.killTweensOf(e.currentTarget)
                      gsap.to(e.currentTarget, { opacity: 0.85, duration: 0.15, ease: 'power2.out' })
                    }}
                    onMouseLeave={e => {
                      gsap.killTweensOf(e.currentTarget)
                      gsap.to(e.currentTarget, { opacity: 1, duration: 0.15, ease: 'power2.out' })
                    }}
                  >
                    {chip.length > 40 ? chip.slice(0, 40) + '…' : chip}
                  </button>
                ))}
              </div>

              {/* Quality selector */}
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6, fontFamily: "'Space Grotesk', sans-serif", textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Quality
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {(['720p', '1080p', '4k'] as VideoQuality[]).map(q => {
                    const locked = q === '4k' && !can4K
                    return (
                      <button
                        key={q}
                        onClick={() => !locked && setQuality(q)}
                        title={locked ? 'Business plan required' : undefined}
                        style={{
                          padding: '5px 14px', borderRadius: 8, cursor: locked ? 'not-allowed' : 'pointer',
                          fontFamily: "'Space Grotesk', sans-serif", fontSize: 12, fontWeight: 600,
                          background: quality === q ? (q === '4k' ? 'rgba(255,107,53,0.15)' : q === '1080p' ? 'rgba(255,179,71,0.12)' : 'rgba(31,255,214,0.12)') : 'rgba(255,255,255,0.05)',
                          border: quality === q
                            ? `1px solid ${q === '4k' ? 'rgba(255,107,53,0.5)' : q === '1080p' ? 'rgba(255,179,71,0.4)' : 'rgba(31,255,214,0.4)'}`
                            : '1px solid rgba(255,255,255,0.08)',
                          color: locked ? 'rgba(255,255,255,0.2)' : quality === q
                            ? (q === '4k' ? '#FF6B35' : q === '1080p' ? '#FFB347' : '#1FFFD6')
                            : 'rgba(255,255,255,0.5)',
                          opacity: locked ? 0.5 : 1,
                        }}
                      >
                        {q.toUpperCase()}{locked ? ' 🔒' : ''}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Duration selector */}
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6, fontFamily: "'Space Grotesk', sans-serif", textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Duration
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {([5, 10, 15, 20, 25, 30] as VideoDuration[]).map(d => (
                    <button
                      key={d}
                      onClick={() => setDuration(d)}
                      style={{
                        padding: '5px 12px', borderRadius: 8, cursor: 'pointer',
                        fontFamily: "'Space Grotesk', sans-serif", fontSize: 12, fontWeight: 600,
                        background: duration === d ? 'rgba(31,255,214,0.12)' : 'rgba(255,255,255,0.05)',
                        border: duration === d ? '1px solid rgba(31,255,214,0.4)' : '1px solid rgba(255,255,255,0.08)',
                        color: duration === d ? '#1FFFD6' : 'rgba(255,255,255,0.5)',
                      }}
                    >
                      {d}s
                    </button>
                  ))}
                </div>
              </div>

              {/* Credit cost preview */}
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', fontFamily: "'Space Grotesk', sans-serif", marginBottom: 12 }}>
                Cost: <span style={{ color: '#1FFFD6', fontWeight: 700 }}>{currentVideoCost} credits</span>
                <span style={{ marginLeft: 8, color: 'rgba(255,255,255,0.2)' }}>· {credits} available</span>
              </div>

              {/* Style selector */}
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                <select value={vStyle} onChange={e => setVStyle(e.target.value)} style={{ width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}>
                  <option value="">Auto</option>
                  {VIDEO_STYLES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                </select>
              </div>

              <button
                onClick={generateVideo}
                disabled={loading || !vPrompt.trim()}
                onMouseEnter={(e) => {
                  if (!loading && vPrompt.trim()) {
                    gsap.killTweensOf(e.currentTarget)
                    gsap.to(e.currentTarget, { opacity: 0.85, duration: 0.15, ease: 'power2.out' })
                  }
                }}
                onMouseLeave={(e) => {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { opacity: loading || !vPrompt.trim() ? 0.5 : 1, duration: 0.15, ease: 'power2.out' })
                }}
                style={{ alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10, fontSize: '0.875rem', fontWeight: 600, color: '#fff', fontFamily: 'inherit', cursor: loading || !vPrompt.trim() ? 'not-allowed' : 'pointer', opacity: loading || !vPrompt.trim() ? 0.5 : 1, background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', border: 'none' }}
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
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', resize: 'vertical' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(255,107,53,0.5)' }}
                  onBlur={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 2 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                  <select
                    value={iModel}
                    onChange={e => setIModel(e.target.value)}
                    style={{ width: '100%', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}
                  >
                    {IMAGE_MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Ratio</label>
                  <select
                    value={iRatio}
                    onChange={e => setIRatio(e.target.value)}
                    style={{ width: '100%', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}
                  >
                    {IMAGE_RATIOS.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                  <select
                    value={iStyle}
                    onChange={e => setIStyle(e.target.value)}
                    style={{ width: '100%', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}
                  >
                    <option value="">Auto</option>
                    {VIDEO_STYLES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
              </div>

              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)' }}>
                Cost: <span style={{ color: '#FF6B35', fontWeight: 700 }}>2 credits</span>
              </div>

              <button
                onClick={generateImage}
                disabled={loading || !iPrompt.trim()}
                onMouseEnter={(e) => {
                  if (!loading && iPrompt.trim()) {
                    gsap.killTweensOf(e.currentTarget)
                    gsap.to(e.currentTarget, { opacity: 0.85, duration: 0.15, ease: 'power2.out' })
                  }
                }}
                onMouseLeave={(e) => {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { opacity: loading || !iPrompt.trim() ? 0.5 : 1, duration: 0.15, ease: 'power2.out' })
                }}
                style={{ alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10, fontSize: '0.875rem', fontWeight: 600, color: '#fff', fontFamily: 'inherit', cursor: loading || !iPrompt.trim() ? 'not-allowed' : 'pointer', opacity: loading || !iPrompt.trim() ? 0.5 : 1, background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', border: 'none' }}
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
                  style={{ width: '100%', boxSizing: 'border-box', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.75rem 1rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', resize: 'vertical' }}
                  onFocus={e => { e.currentTarget.style.borderColor = 'rgba(255,107,53,0.5)' }}
                  onBlur={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.09)' }}
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
                    <select value={val} onChange={e => set(e.target.value)} style={{ width: '100%', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 8, padding: '0.5rem 0.625rem', color: '#fff', fontSize: '0.8rem', fontFamily: 'inherit', cursor: 'pointer' }}>
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
                    <select value={val} onChange={e => set(e.target.value)} style={{ width: '100%', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 8, padding: '0.5rem 0.625rem', color: '#fff', fontSize: '0.8rem', fontFamily: 'inherit', cursor: 'pointer' }}>
                      {opts.map(o => <option key={o.v} value={o.v}>{o.label}</option>)}
                    </select>
                  </div>
                ))}
              </div>

              <button
                onClick={generateAudio}
                disabled={loading || !aText.trim()}
                onMouseEnter={(e) => {
                  if (!loading && aText.trim()) {
                    gsap.killTweensOf(e.currentTarget)
                    gsap.to(e.currentTarget, { opacity: 0.85, duration: 0.15, ease: 'power2.out' })
                  }
                }}
                onMouseLeave={(e) => {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { opacity: loading || !aText.trim() ? 0.5 : 1, duration: 0.15, ease: 'power2.out' })
                }}
                style={{ alignSelf: 'flex-start', padding: '0.75rem 1.5rem', borderRadius: 10, fontSize: '0.875rem', fontWeight: 600, color: '#fff', fontFamily: 'inherit', cursor: loading || !aText.trim() ? 'not-allowed' : 'pointer', opacity: loading || !aText.trim() ? 0.5 : 1, background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', border: 'none' }}
              >
                {loading ? 'Generating…' : '♪ Generate Audio'}
              </button>

            </div>
          )}
          {/* Generation Queue */}
          {queue.length > 0 && (
            <div style={{ marginTop: 32 }}>
              <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @keyframes progress-pulse {
                  0%   { opacity: 0.6; }
                  50%  { opacity: 1; }
                  100% { opacity: 0.6; }
                }
              `}</style>
              <div style={{
                fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.4)',
                fontFamily: "'Space Grotesk', sans-serif", textTransform: 'uppercase',
                letterSpacing: '0.08em', marginBottom: 12,
              }}>
                Generation Queue
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {[...queue].reverse().slice(0, 8).map(job => (
                  <div key={job.id} style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: `1px solid ${job.status === 'complete' ? 'rgba(31,255,214,0.2)' : job.status === 'failed' ? 'rgba(248,113,113,0.2)' : 'rgba(255,255,255,0.07)'}`,
                    borderRadius: 10, padding: '12px 14px',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                          {job.status === 'pending' && (
                            <span style={{ fontSize: 10, fontFamily: "'Space Grotesk', sans-serif", color: '#FFB347', background: 'rgba(255,179,71,0.1)', border: '1px solid rgba(255,179,71,0.3)', borderRadius: 4, padding: '1px 6px' }}>Queued</span>
                          )}
                          {job.status === 'processing' && (
                            <span style={{ fontSize: 10, fontFamily: "'Space Grotesk', sans-serif", color: '#00D9FF', background: 'rgba(0,217,255,0.08)', border: '1px solid rgba(0,217,255,0.25)', borderRadius: 4, padding: '1px 6px' }}>Generating…</span>
                          )}
                          {job.status === 'complete' && (
                            <span style={{ fontSize: 10, fontFamily: "'Space Grotesk', sans-serif", color: '#1FFFD6', background: 'rgba(31,255,214,0.08)', border: '1px solid rgba(31,255,214,0.25)', borderRadius: 4, padding: '1px 6px' }}>✓ Done</span>
                          )}
                          {job.status === 'failed' && (
                            <span style={{ fontSize: 10, fontFamily: "'Space Grotesk', sans-serif", color: '#f87171', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)', borderRadius: 4, padding: '1px 6px' }}>✗ Failed</span>
                          )}
                          <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)', fontFamily: "'Space Grotesk', sans-serif" }}>
                            {job.type === 'video' ? `${job.quality?.toUpperCase() || '720P'} · ${job.duration}s` : 'Audio'} · {job.credits_used} cr
                          </span>
                        </div>
                        <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.55)', fontFamily: "'Space Grotesk', sans-serif", overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {job.prompt}
                        </div>
                      </div>
                      {job.status === 'complete' && job.result_url && (
                        <a
                          href={job.result_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: 11, color: '#1FFFD6', fontFamily: "'Space Grotesk', sans-serif",
                            fontWeight: 600, textDecoration: 'none', whiteSpace: 'nowrap',
                            background: 'rgba(31,255,214,0.08)', border: '1px solid rgba(31,255,214,0.25)',
                            borderRadius: 6, padding: '4px 10px',
                          }}
                        >
                          View ↗
                        </a>
                      )}
                      {(job.status === 'pending' || job.status === 'processing') && (
                        <div style={{
                          width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                          border: '2px solid rgba(0,217,255,0.15)',
                          borderTopColor: '#00D9FF',
                          animation: 'spin 1s linear infinite',
                        }} />
                      )}
                    </div>
                    {(job.status === 'pending' || job.status === 'processing') && (
                      <div style={{ marginTop: 8, height: 2, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{
                          height: '100%', borderRadius: 2,
                          background: 'linear-gradient(90deg, #00D9FF, #1FFFD6)',
                          animation: 'progress-pulse 2s ease-in-out infinite',
                          width: job.status === 'processing' ? '65%' : '25%',
                          transition: 'width 1s ease',
                        }} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {queue.length > 8 && (
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.25)', marginTop: 8, fontFamily: "'Space Grotesk', sans-serif" }}>
                  + {queue.length - 8} older jobs
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Preview Panel ── */}
        <div style={{ position: 'sticky', top: '2rem' }}>
          <p style={{ fontSize: '0.68rem', fontWeight: 700, color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.625rem' }}>Output Preview</p>
          <div style={{ borderRadius: 14, overflow: 'hidden', background: '#0D1017', border: '1px solid rgba(255,255,255,0.07)', minHeight: 300, display: 'flex', flexDirection: 'column' }}>
            <style>{`@keyframes dshCreDot{0%,80%,100%{opacity:.25;transform:scale(.7)}40%{opacity:1;transform:scale(1)}} @keyframes dshVidProg{0%{width:12%}100%{width:88%}}`}</style>

            {/* VIDEO states */}
            {mode === 'video' && !vResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ width: 44, height: 44, borderRadius: 10, border: '2px solid rgba(255,255,255,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.3rem', color: 'rgba(255,255,255,0.6)' }}>▶</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', lineHeight: 1.4 }}>Video output appears here</span>
              </div>
            )}
            {mode === 'video' && loading && !vResult && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#FF6B35', display: 'inline-block', animation: `dshCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)' }}>Generating…</span>
              </div>
            )}
            {mode === 'video' && vResult && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                  <span style={{
                    fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em',
                    background: isDone ? 'rgba(255,107,53,0.15)' : vPolling ? 'rgba(255,215,0,0.12)' : 'rgba(255,255,255,0.06)',
                    color: isDone ? '#FF6B35' : vPolling ? '#FFD700' : 'rgba(255,255,255,0.4)',
                  }}>
                    {isDone ? 'Done' : vPolling ? 'Processing…' : vResult.status}
                  </span>
                </div>
                {videoUrl ? (
                  <div>
                    <video src={videoUrl} controls style={{ width: '100%', borderRadius: 8, marginBottom: 8, maxHeight: 280, background: '#000' }} />
                    <a href={videoUrl} download target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem', color: '#FF6B35', textDecoration: 'none' }}>↓ Download</a>
                  </div>
                ) : vPolling ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: '0.75rem 0' }}>
                    <div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}>
                      {[0,1,2].map(i => <span key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: '#FF6B35', display: 'inline-block', animation: `dshCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                    </div>
                    <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'rgba(255,255,255,0.35)', margin: 0 }}>Processing video — this may take a few minutes</p>
                    <div style={{ height: 3, borderRadius: 99, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
                      <div style={{ height: '100%', background: 'linear-gradient(90deg,#FF6B35,#CC4A18)', borderRadius: 99, animation: 'dshVidProg 3s ease-in-out infinite alternate' }} />
                    </div>
                  </div>
                ) : (
                  vResult.message && <p style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.35)', margin: 0 }}>{vResult.message}</p>
                )}
              </div>
            )}

            {/* AUDIO states */}
            {mode === 'audio' && !aResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ fontSize: '2rem', color: 'rgba(255,255,255,0.5)' }}>♪</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', lineHeight: 1.4 }}>Audio output appears here</span>
              </div>
            )}
            {mode === 'audio' && loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#FF6B35', display: 'inline-block', animation: `dshCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)' }}>Generating audio…</span>
              </div>
            )}
            {mode === 'audio' && aResult && !loading && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ marginBottom: 10 }}>
                  <span style={{ fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', background: aResult.status === 'success' ? 'rgba(255,107,53,0.15)' : 'rgba(239,68,68,0.15)', color: aResult.status === 'success' ? '#FF6B35' : '#ef4444' }}>
                    {aResult.status}
                  </span>
                </div>
                {audioSrc && (
                  <div>
                    <audio ref={audioRef} src={audioSrc} controls style={{ width: '100%', borderRadius: 8, marginBottom: 8 }} onLoadedData={() => void audioRef.current?.play()} />
                    <a href={audioSrc} download="vantro-audio.mp3" style={{ fontSize: '0.75rem', color: '#FF6B35', textDecoration: 'none' }}>↓ Download</a>
                  </div>
                )}
              </div>
            )}

            {/* IMAGE states */}
            {mode === 'image' && !iResult && !loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '2.5rem 1.5rem', opacity: 0.28 }}>
                <div style={{ width: 44, height: 44, borderRadius: 10, border: '2px solid rgba(255,255,255,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.3rem', color: 'rgba(255,255,255,0.6)' }}>⬡</div>
                <span style={{ fontSize: '0.75rem', color: '#fff', textAlign: 'center', lineHeight: 1.4 }}>Image output appears here</span>
              </div>
            )}
            {mode === 'image' && loading && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '2.5rem 1.5rem' }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0,1,2].map(i => <span key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: '#FF6B35', display: 'inline-block', animation: `dshCreDot 1.4s ease-in-out ${i*0.22}s infinite` }} />)}
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)' }}>Generating image…</span>
              </div>
            )}
            {mode === 'image' && iResult && !loading && (
              <div style={{ padding: '0.875rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                  <span style={{ fontSize: '0.65rem', padding: '2px 7px', borderRadius: 5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', background: iResult.image_url ? 'rgba(255,107,53,0.15)' : 'rgba(239,68,68,0.15)', color: iResult.image_url ? '#FF6B35' : '#ef4444' }}>
                    {iResult.image_url ? 'Done' : 'Failed'}
                  </span>
                  {iResult.model && <span style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.3)' }}>{iResult.model}</span>}
                </div>
                {iResult.image_url ? (
                  <div>
                    <img src={iResult.image_url} alt="Generated" style={{ width: '100%', borderRadius: 8, marginBottom: 8, maxHeight: 280, objectFit: 'contain', background: '#000' }} />
                    <a href={iResult.image_url} download target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem', color: '#FF6B35', textDecoration: 'none' }}>↓ Download</a>
                  </div>
                ) : (
                  <p style={{ fontSize: '0.78rem', color: '#ef4444', margin: 0 }}>Generation failed. Please try again.</p>
                )}
              </div>
            )}

            {/* Error */}
            {error && (
              <div style={{ margin: '0.75rem', padding: '0.75rem', borderRadius: 8, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.18)', color: '#f87171', fontSize: '0.78rem' }}>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
