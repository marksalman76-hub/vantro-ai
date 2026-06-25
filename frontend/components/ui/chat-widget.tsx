'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'

interface Msg { role: 'user' | 'assistant'; text: string }

async function runAgentChat(message: string, token: string): Promise<string> {
  const res = await fetch('/api/agents/intake_trial_agent/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ input: { task: message } }),
  })
  const job = await res.json() as { id?: string; job_id?: string }
  const jobId = job.id ?? job.job_id
  if (!jobId) throw new Error('No job ID returned')

  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 2000))
    const poll = await fetch(`/api/agents/jobs/${jobId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await poll.json() as { status?: string; output?: string; result?: string }
    if (data.status === 'completed') return data.output ?? data.result ?? 'Done.'
    if (data.status === 'failed') throw new Error('Agent could not complete the request.')
  }
  throw new Error('Request timed out.')
}

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: 'assistant', text: "Hi! I'm your AI assistant. How can I help you today?" },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, open])

  const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    const token = getToken()
    setInput('')
    setMsgs(m => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      if (!token) throw new Error('auth_required')
      const reply = await runAgentChat(text, token)
      setMsgs(m => [...m, { role: 'assistant', text: reply }])
    } catch (e) {
      const msg = e instanceof Error && e.message === 'auth_required' ? '__AUTH__'
        : (e instanceof Error ? e.message : 'Something went wrong.')
      setMsgs(m => [...m, { role: 'assistant', text: msg }])
    }
    setLoading(false)
  }

  return (
    <>
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Open chat"
        style={{
          position: 'fixed', bottom: '1.5rem', right: '1.5rem', zIndex: 9998,
          width: 52, height: 52, borderRadius: '50%', border: 'none', cursor: 'pointer',
          background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
          boxShadow: '0 4px 20px oklch(0.60 0.18 250 / 0.50)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        {open ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )}
      </button>

      {open && (
        <div style={{
          position: 'fixed', bottom: '5.5rem', right: '1.5rem', zIndex: 9997,
          width: 360, height: 480, display: 'flex', flexDirection: 'column',
          background: 'oklch(0.14 0 0)', border: '1px solid oklch(1 0 0 / 0.12)',
          borderRadius: '1.25rem', boxShadow: '0 16px 48px rgba(0,0,0,0.60)',
          fontFamily: "'Inter', sans-serif", overflow: 'hidden',
        }}>
          <div style={{
            padding: '1rem 1.25rem', borderBottom: '1px solid oklch(1 0 0 / 0.08)',
            display: 'flex', alignItems: 'center', gap: '0.75rem',
            background: 'oklch(0.16 0 0)',
          }}>
            <img src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png" style={{ height: 24, width: 'auto' }} alt="" />
            <div>
              <p style={{ color: 'oklch(0.97 0 0)', fontSize: '0.875rem', fontWeight: 600, margin: 0, fontFamily: 'Space Grotesk, sans-serif' }}>Vantro AI</p>
              <p style={{ color: 'oklch(0.55 0 0)', fontSize: '0.72rem', margin: 0 }}>Powered by your AI workforce</p>
            </div>
            <div style={{ marginLeft: 'auto', width: 8, height: 8, borderRadius: '50%', background: 'oklch(0.75 0.22 145)' }} />
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {msgs.map((m, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                {m.text === '__AUTH__' ? (
                  <div style={{
                    background: 'oklch(1 0 0 / 0.04)', border: '1px solid oklch(1 0 0 / 0.10)',
                    borderRadius: '0.875rem', padding: '0.75rem 1rem', maxWidth: '85%',
                    color: 'oklch(0.75 0 0)', fontSize: '0.825rem', lineHeight: 1.5,
                  }}>
                    <p style={{ margin: '0 0 0.5rem' }}>Sign in to chat with your AI workforce.</p>
                    <Link href="https://app.vantro.ai/login" style={{
                      display: 'inline-block',
                      background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
                      color: 'oklch(0.98 0 0)', borderRadius: '9999px', padding: '0.4rem 1rem',
                      fontSize: '0.8rem', fontWeight: 600, textDecoration: 'none',
                    }}>Sign in &rarr;</Link>
                  </div>
                ) : (
                  <div style={{
                    background: m.role === 'user' ? 'oklch(0.60 0.18 250)' : 'oklch(1 0 0 / 0.06)',
                    color: m.role === 'user' ? 'oklch(0.98 0 0)' : 'oklch(0.88 0 0)',
                    border: m.role === 'assistant' ? '1px solid oklch(1 0 0 / 0.09)' : 'none',
                    borderRadius: m.role === 'user' ? '1rem 1rem 0.25rem 1rem' : '1rem 1rem 1rem 0.25rem',
                    padding: '0.625rem 0.875rem', maxWidth: '85%', fontSize: '0.825rem', lineHeight: 1.55,
                  }}>{m.text}</div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{
                background: 'oklch(1 0 0 / 0.06)', border: '1px solid oklch(1 0 0 / 0.09)',
                borderRadius: '1rem 1rem 1rem 0.25rem', padding: '0.625rem 0.875rem',
                display: 'inline-flex', gap: '0.3rem', alignItems: 'center',
              }}>
                {[0,1,2].map(d => (
                  <span key={d} style={{
                    width: 6, height: 6, borderRadius: '50%', background: 'oklch(0.60 0.18 250)',
                    animation: `vantro-pulse 1.2s ease-in-out ${d * 0.2}s infinite`,
                  }} />
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div style={{
            padding: '0.875rem 1rem', borderTop: '1px solid oklch(1 0 0 / 0.08)',
            display: 'flex', gap: '0.5rem', background: 'oklch(0.12 0 0)',
          }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask anything..."
              disabled={loading}
              style={{
                flex: 1, background: 'oklch(1 0 0 / 0.06)', border: '1px solid oklch(1 0 0 / 0.10)',
                borderRadius: '0.625rem', padding: '0.625rem 0.875rem', color: 'oklch(0.97 0 0)',
                fontSize: '0.85rem', outline: 'none',
              }}
            />
            <button
              onClick={send}
              disabled={!input.trim() || loading}
              style={{
                background: input.trim() && !loading ? 'oklch(0.60 0.18 250)' : 'oklch(1 0 0 / 0.06)',
                border: 'none', borderRadius: '0.625rem', width: 38, height: 38,
                cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      )}
      <style>{`@keyframes vantro-pulse { 0%,100%{opacity:0.3;transform:scale(0.8)} 50%{opacity:1;transform:scale(1)} }`}</style>
    </>
  )
}
