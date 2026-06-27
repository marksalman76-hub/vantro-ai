'use client'

import { useState, useRef, useEffect } from 'react'
import { AGENTS, CATEGORY_COLORS, Agent } from '@/lib/agents'

const CATEGORIES = ['All', 'Sales', 'Operations', 'Engineering', 'Support', 'Executive'] as const

export default function AdminAgentsPage() {
  const [selected, setSelected]             = useState<Agent | null>(null)
  const [prompt, setPrompt]                 = useState('')
  const [output, setOutput]                 = useState('')
  const [running, setRunning]               = useState(false)
  const [error, setError]                   = useState('')
  const [activeCategory, setActiveCategory] = useState<string>('All')
  const [search, setSearch]                 = useState('')
  const outputRef    = useRef<HTMLDivElement>(null)
  const agentAbortRef = useRef<AbortController | null>(null)

  // Abort any in-flight stream on unmount
  useEffect(() => {
    return () => { agentAbortRef.current?.abort() }
  }, [])

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTo({ top: outputRef.current.scrollHeight, behavior: 'smooth' })
    }
  }, [output])

  // Show ALL agents — no plan-tier filtering
  const filtered = AGENTS.filter(a => {
    const matchCat   = activeCategory === 'All' || a.category === activeCategory
    const q          = search.toLowerCase()
    const matchSearch = !q || a.name.toLowerCase().includes(q) || a.role.toLowerCase().includes(q)
    return matchCat && matchSearch
  })

  const accent = selected ? (CATEGORY_COLORS[selected.category] || '#1FFFD6') : '#1FFFD6'

  async function runAgent() {
    if (!selected || !prompt.trim()) return
    setRunning(true)
    setOutput('')
    setError('')

    agentAbortRef.current?.abort()
    const ac = new AbortController()
    agentAbortRef.current = ac

    try {
      // Admin: cookie auth only — no Authorization header
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentId: selected.id, prompt: prompt.trim() }),
        signal: ac.signal,
      })

      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        setError((d as { error?: string }).error || 'Agent unavailable. Please try again.')
        return
      }

      const reader = res.body?.getReader()
      if (!reader) { setError('Agent unavailable. Please try again.'); return }

      const dec = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        setOutput(prev => prev + dec.decode(value, { stream: true }))
      }
    } catch (e) {
      if ((e as Error)?.name === 'AbortError') return
      setError('Agent unavailable. Please try again.')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden', fontFamily: 'system-ui, sans-serif' }}>

      {/* Left panel — agent list */}
      <div style={{
        width: 260, minWidth: 260,
        borderRight: '1px solid rgba(255,255,255,0.07)',
        overflowY: 'auto', padding: '16px 8px',
        background: '#0A0D14',
      }}>

        {/* Header with agent count + admin badge */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '0 8px 10px' }}>
          <p style={{
            color: 'rgba(255,255,255,0.3)', fontSize: 10, fontWeight: 600,
            letterSpacing: '0.1em', textTransform: 'uppercase', margin: 0,
          }}>
            {AGENTS.length} Agents
          </p>
          <span style={{
            fontSize: 9, fontWeight: 700, letterSpacing: '0.08em',
            padding: '2px 7px', borderRadius: 99,
            background: 'rgba(31,255,214,0.12)', color: '#1FFFD6',
            border: '1px solid rgba(31,255,214,0.3)', textTransform: 'uppercase',
          }}>
            ADMIN
          </span>
        </div>

        {/* Search */}
        <input
          type="search"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search agents…"
          style={{
            width: '100%', boxSizing: 'border-box',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.09)',
            borderRadius: 8, padding: '6px 10px',
            color: '#fff', fontSize: 12, outline: 'none', marginBottom: 10,
            fontFamily: 'system-ui, sans-serif',
          }}
        />

        {/* Category filter */}
        <div style={{ display: 'flex', gap: 4, overflowX: 'auto', paddingBottom: 8, marginBottom: 8 }}>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              style={{
                padding: '3px 10px', borderRadius: 99, border: 'none', cursor: 'pointer',
                fontSize: 10, fontWeight: 600, whiteSpace: 'nowrap',
                fontFamily: 'system-ui, sans-serif',
                background: activeCategory === cat ? '#1FFFD6' : 'rgba(255,255,255,0.07)',
                color: activeCategory === cat ? '#0A0D14' : 'rgba(255,255,255,0.45)',
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Agent list */}
        {filtered.map(a => {
          const active = selected?.id === a.id
          const color  = CATEGORY_COLORS[a.category]
          return (
            <button
              key={a.id}
              aria-label={a.name}
              onClick={() => { setSelected(a); setOutput(''); setError('') }}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '7px 10px', borderRadius: 8, border: 'none', cursor: 'pointer',
                background: active ? `${color}14` : 'transparent',
                outline: active ? `1px solid ${color}40` : '1px solid transparent',
                textAlign: 'left', width: '100%',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(255,255,255,0.06)' }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
            >
              <img
                src={a.avatar}
                alt={a.name}
                style={{ width: 28, height: 28, borderRadius: 7, objectFit: 'cover', border: `1px solid ${color}40`, flexShrink: 0 }}
              />
              <div style={{ minWidth: 0 }}>
                <p style={{ color: active ? '#fff' : 'rgba(255,255,255,0.7)', fontSize: 12, fontWeight: 600, margin: 0, fontFamily: 'system-ui, sans-serif' }}>{a.name}</p>
                <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 10, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: 'system-ui, sans-serif' }}>{a.role}</p>
              </div>
            </button>
          )
        })}

        {filtered.length === 0 && (
          <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.25)', padding: '10px 8px' }}>No agents match.</p>
        )}
      </div>

      {/* Right panel — task area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#0A0D14' }}>
        {!selected ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            {/* Admin mode badge */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '6px 16px', borderRadius: 99,
              background: 'rgba(31,255,214,0.08)',
              border: '1px solid rgba(31,255,214,0.25)',
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block' }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: '#1FFFD6', letterSpacing: '0.08em' }}>ADMIN — No Credit Limit</span>
            </div>
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true" style={{ opacity: 0.15 }}>
              <circle cx="16" cy="11" r="5.5" stroke="#fff" strokeWidth="1.5"/>
              <path d="M6 27c0-5.523 4.477-10 10-10s10 4.477 10 10" stroke="#fff" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <p style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13, fontFamily: 'system-ui, sans-serif' }}>
              Select an agent to get started
            </p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div style={{ padding: '18px 24px 14px', borderBottom: '1px solid rgba(255,255,255,0.07)', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
              <img
                src={selected.avatar}
                alt={selected.name}
                style={{ width: 38, height: 38, borderRadius: 10, objectFit: 'cover', border: `2px solid ${accent}60`, flexShrink: 0 }}
              />
              <div>
                <p style={{ color: '#fff', fontSize: 15, fontWeight: 700, margin: 0, fontFamily: 'system-ui, sans-serif' }}>{selected.name}</p>
                <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, margin: '2px 0 4px', fontFamily: 'system-ui, sans-serif' }}>{selected.role}</p>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 99, background: `${accent}18`, color: accent, border: `1px solid ${accent}40`, fontWeight: 600, letterSpacing: '0.04em', fontFamily: 'system-ui, sans-serif' }}>
                  {selected.category}
                </span>
              </div>

              {/* Admin mode badge (right side) */}
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  display: 'inline-flex', alignItems: 'center', gap: 5,
                  fontSize: 10, color: '#1FFFD6',
                  background: 'rgba(31,255,214,0.08)',
                  padding: '3px 10px', borderRadius: 100,
                  fontFamily: 'system-ui, sans-serif', fontWeight: 700,
                  letterSpacing: '0.06em',
                  border: '1px solid rgba(31,255,214,0.25)',
                }}>
                  <span style={{ width: 4, height: 4, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block' }} />
                  ADMIN — No Credit Limit
                </span>
              </div>
            </div>

            {/* Stats strip */}
            <div style={{ padding: '10px 24px', borderBottom: '1px solid rgba(255,255,255,0.07)', display: 'flex', gap: 24, flexShrink: 0 }}>
              {[
                { label: 'Success rate', value: `${selected.stats.successRate}%` },
                { label: 'Response',     value: selected.stats.responseTime },
                { label: 'Languages',   value: String(selected.stats.languages) },
              ].map(({ label, value }) => (
                <div key={label}>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2, fontFamily: 'system-ui, sans-serif' }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: accent, fontFamily: 'system-ui, sans-serif' }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Output area */}
            <div ref={outputRef} style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
              {!output && !running && !error && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 13, lineHeight: 1.65, margin: 0, fontFamily: 'system-ui, sans-serif' }}>
                    {selected.bio}
                  </p>
                  <p style={{ color: 'rgba(255,255,255,0.2)', fontSize: 12, margin: 0, fontFamily: 'system-ui, sans-serif' }}>
                    Describe your task below and press Run.
                  </p>
                </div>
              )}
              {error && (
                <div style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.20)', borderRadius: 10, padding: '12px 16px', color: '#f87171', fontSize: 13, fontFamily: 'system-ui, sans-serif' }}>{error}</div>
              )}
              {output && (
                <div style={{ color: 'rgba(255,255,255,0.82)', fontSize: 13.5, lineHeight: 1.75, whiteSpace: 'pre-wrap', fontFamily: 'system-ui, sans-serif' }}>{output}</div>
              )}
              {running && !output && (
                <>
                  <style>{`@keyframes admDot{0%,80%,100%{opacity:.25;transform:scale(.7)}40%{opacity:1;transform:scale(1)}}`}</style>
                  <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
                    {[0, 1, 2].map(i => (
                      <span key={i} style={{ width: 7, height: 7, borderRadius: '50%', background: accent, display: 'inline-block', animation: `admDot 1.2s ease-in-out ${i * 0.2}s infinite` }} />
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* Prompt input */}
            <div style={{ padding: '14px 24px 20px', borderTop: '1px solid rgba(255,255,255,0.07)', flexShrink: 0 }}>
              <textarea
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runAgent() }}
                placeholder={`Tell ${selected.name} what to do…`}
                rows={3}
                style={{
                  width: '100%', background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10,
                  padding: '11px 14px', color: '#fff', fontSize: 13,
                  fontFamily: 'system-ui, sans-serif', resize: 'vertical',
                  outline: 'none', marginBottom: 10, boxSizing: 'border-box',
                  transition: 'border-color 0.15s',
                }}
                onFocus={e => (e.currentTarget.style.borderColor = `${accent}60`)}
                onBlur={e =>  (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)')}
              />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.18)', fontFamily: 'system-ui, sans-serif' }}>⌘ Enter to run</span>
                <button
                  onClick={runAgent}
                  disabled={running || !prompt.trim()}
                  style={{
                    background: running || !prompt.trim()
                      ? 'rgba(255,255,255,0.06)'
                      : `linear-gradient(135deg, ${accent}, ${accent}99)`,
                    color: running || !prompt.trim() ? 'rgba(255,255,255,0.25)' : '#0A0D14',
                    border: 'none', borderRadius: 8, padding: '9px 22px',
                    fontSize: 13, fontWeight: 700,
                    cursor: running || !prompt.trim() ? 'not-allowed' : 'pointer',
                    fontFamily: 'system-ui, sans-serif',
                    transition: 'all 0.15s',
                  }}
                >
                  {running ? 'Running…' : `Run ${selected.name}`}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
