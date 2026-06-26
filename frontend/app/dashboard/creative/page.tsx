'use client'

import { useState, useRef, useEffect } from 'react'
import gsap from 'gsap'

const CREATIVE_AGENTS = [
  { id: 'pixel',  name: 'Pixel',  role: 'Design & Creative',    cap: ['video'] as string[],         color: '#FF6B35' },
  { id: 'mosaic', name: 'Mosaic', role: 'Social Media Manager',  cap: ['video'] as string[],         color: '#FF6B35' },
  { id: 'pulse',  name: 'Pulse',  role: 'Marketing Strategist',  cap: ['video', 'audio'] as string[], color: '#FFD700' },
  { id: 'lumen',  name: 'Lumen',  role: 'Brand Strategist',      cap: ['video', 'audio'] as string[], color: '#FFD700' },
  { id: 'quill',  name: 'Quill',  role: 'Content Writer',        cap: ['audio'] as string[],         color: '#B084FF' },
  { id: 'aria',   name: 'Aria',   role: 'Voice & Telephony',     cap: ['audio'] as string[],         color: '#00D9FF' },
]

const VIDEO_STYLES = ['cinematic', 'commercial', 'social', 'documentary']
const DURATIONS    = [5, 10, 15, 30]

const VIDEO_PROMPT_CHIPS = [
  'Product hero shot on clean white surface, cinematic slow rotation',
  'Aerial city flythrough at golden hour, dramatic depth of field',
  'Abstract logo reveal with particle effects, dark background',
  'Team collaboration montage, modern office, warm color grade',
]

type Mode = 'video' | 'audio'

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

export default function CreativeStudioPage() {
  const [agent, setAgent]     = useState(CREATIVE_AGENTS[0])
  const [mode, setMode]       = useState<Mode>('video')

  // Video
  const [vPrompt, setVPrompt]     = useState('')
  const [vDuration, setVDuration] = useState(5)
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

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

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

  async function generateVideo() {
    if (!vPrompt.trim()) return
    setLoading(true)
    setError('')
    setVResult(null)
    setVPolling(false)
    if (pollRef.current) clearInterval(pollRef.current)
    pollCountRef.current = 0

    try {
      const res  = await fetch('/api/creative/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: vPrompt.trim(), duration: vDuration, style: vStyle || undefined, provider: 'auto' }),
      })
      const data: VideoResult = await res.json()
      if (!res.ok) { setError(data.error || 'Generation failed'); return }
      setVResult(data)

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

    try {
      const res  = await fetch('/api/creative/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: aText.trim(), agentId: agent.id }),
      })
      const data: AudioResult = await res.json()
      if (!res.ok) { setError(data.error || 'Audio generation failed'); return }
      setAResult(data)

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

  const videoUrl = vResult?.video_url || vResult?.output?.[0]
  const isDone   = ['SUCCEEDED', 'succeeded', 'complete', 'completed'].includes(vResult?.status || '')

  return (
    <div style={{ padding: '2rem', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: 4 }}>Creative Studio</h1>
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.875rem' }}>
          Generate video and audio via Runway, Higgsfield.ai, and ElevenLabs — powered by your creative agents.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '1.5rem' }}>

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
            {(['video', 'audio'] as Mode[]).map(m => {
              const avail = agent.cap.includes(m)
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
                  {m === 'video' ? '▶ Video' : '♪ Audio'}
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

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Duration</label>
                  <select value={vDuration} onChange={e => setVDuration(Number(e.target.value))} style={{ width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}>
                    {DURATIONS.map(d => <option key={d} value={d}>{d}s</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Style</label>
                  <select value={vStyle} onChange={e => setVStyle(e.target.value)} style={{ width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, padding: '0.625rem 0.875rem', color: '#fff', fontSize: '0.875rem', fontFamily: 'inherit', cursor: 'pointer' }}>
                    <option value="">Auto</option>
                    {VIDEO_STYLES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
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

              {vResult && (
                <div style={{ borderRadius: 12, padding: '1rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', background: isDone ? 'rgba(31,255,214,0.15)' : vPolling ? 'rgba(255,215,0,0.15)' : 'rgba(255,255,255,0.06)', color: isDone ? '#1FFFD6' : vPolling ? '#FFD700' : 'rgba(255,255,255,0.5)' }}>
                      {isDone ? 'Done' : vPolling ? 'Processing…' : vResult.status}
                    </span>
                    {vResult.provider && <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)' }}>via {vResult.provider}</span>}
                  </div>

                  {videoUrl ? (
                    <div>
                      <video src={videoUrl} controls style={{ width: '100%', borderRadius: 8, marginBottom: 8, maxHeight: 320 }} />
                      <a href={videoUrl} download target="_blank" rel="noreferrer" style={{ fontSize: '0.8rem', color: '#FF6B35', textDecoration: 'none' }}>↓ Download</a>
                    </div>
                  ) : vPolling ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ display: 'flex', gap: 4 }}>
                          {[0, 1, 2].map(i => (
                            <span
                              key={i}
                              style={{
                                width: 6, height: 6, borderRadius: '50%',
                                background: '#FF6B35',
                                display: 'inline-block',
                                animation: `dot 1.4s ease-in-out ${i * 0.22}s infinite`,
                              }}
                            />
                          ))}
                        </div>
                        <span style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,0.55)' }}>
                          Generating video — this may take a few minutes
                        </span>
                      </div>

                      {/* Animated progress bar */}
                      <style>{`
                        @keyframes videoProgress {
                          0%   { width: 15%; }
                          100% { width: 85%; }
                        }
                      `}</style>
                      <div style={{ height: 4, borderRadius: 99, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            background: 'linear-gradient(90deg, #FF6B35, #00D9FF)',
                            borderRadius: 99,
                            animation: 'videoProgress 3s ease-in-out infinite alternate',
                            transformOrigin: 'left center',
                          }}
                        />
                      </div>

                      <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', margin: 0 }}>
                        Polling every 5s · Video will appear here when ready
                      </p>
                    </div>
                  ) : (
                    vResult.message && <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.4)', margin: 0 }}>{vResult.message}</p>
                  )}
                </div>
              )}
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
                <p style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.25)', marginTop: 4, margin: '4px 0 0' }}>
                  {agent.name}&apos;s assigned ElevenLabs voice · eleven_multilingual_v2
                </p>
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

              {aResult && (
                <div style={{ borderRadius: 12, padding: '1rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', background: aResult.status === 'success' ? 'rgba(31,255,214,0.15)' : 'rgba(239,68,68,0.15)', color: aResult.status === 'success' ? '#1FFFD6' : '#ef4444' }}>
                      {aResult.status}
                    </span>
                    {aResult.provider && <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)' }}>via {aResult.provider}</span>}
                  </div>
                  {audioSrc && (
                    <div>
                      <audio
                        ref={audioRef}
                        src={audioSrc}
                        controls
                        style={{ width: '100%', borderRadius: 8, marginBottom: 8 }}
                        onLoadedData={() => void audioRef.current?.play()}
                      />
                      <a href={audioSrc} download="vantro-audio.mp3" style={{ fontSize: '0.8rem', color: '#FF6B35', textDecoration: 'none' }}>↓ Download</a>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {error && (
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: 10, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', color: '#f87171', fontSize: '0.82rem' }}>
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
