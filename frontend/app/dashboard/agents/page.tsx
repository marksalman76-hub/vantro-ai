'use client'

import { useState, useRef, useEffect } from 'react'
import gsap from 'gsap'
import { AGENTS, CATEGORY_COLORS, Agent } from '@/lib/agents'
import { CREDIT_COSTS, deductCredits, hasCredits } from '@/lib/credits'

const CATEGORIES = ['All', 'Sales', 'Operations', 'Engineering', 'Support', 'Executive'] as const

interface LibraryItem {
  id: string
  agentId: string
  agentName: string
  category: string
  prompt: string
  output: string
  savedAt: string
  quality?: 'approved' | 'rejected'
}

export default function AgentsPage() {
  const [selected, setSelected]       = useState<Agent | null>(null)
  const [prompt, setPrompt]           = useState('')
  const [output, setOutput]           = useState('')
  const [running, setRunning]         = useState(false)
  const [error, setError]             = useState('')
  const [activeCategory, setActiveCategory] = useState<string>('All')
  const [search, setSearch]           = useState('')
  const [rating, setRating]           = useState<'approved' | 'rejected' | null>(null)
  const [credits, setCredits]         = useState<number>(0)
  const outputRef = useRef<HTMLDivElement>(null)
  // R1: AbortController ref for streaming cleanup
  const agentAbortRef = useRef<AbortController | null>(null)
  const lastSavedIdRef = useRef<string | null>(null)

  // R1: Cleanup on unmount — abort any in-flight stream
  useEffect(() => {
    return () => {
      agentAbortRef.current?.abort()
    }
  }, [])

  // Read initial credits from localStorage
  useEffect(() => {
    setCredits(parseFloat(localStorage.getItem('vantro_credits') || '0'))
  }, [])

  // R2: Scroll output container whenever output changes (side-effect moved out of setState)
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTo({ top: outputRef.current.scrollHeight, behavior: 'smooth' })
    }
  }, [output])

  const filtered = AGENTS.filter(a => {
    const matchCat = activeCategory === 'All' || a.category === activeCategory
    const q = search.toLowerCase()
    const matchSearch = !q || a.name.toLowerCase().includes(q) || a.role.toLowerCase().includes(q)
    return matchCat && matchSearch
  })

  const accent = selected ? (CATEGORY_COLORS[selected.category] || '#00D9FF') : '#00D9FF'

  const SONNET_IDS = new Set(['quill','pulse','nova','cipher','lumen','scout','vector','pixel','forge','sentinel','mosaic','ledger','tempo','sage'])

  function creditCostFor(agentId: string): number {
    return SONNET_IDS.has(agentId) ? CREDIT_COSTS.agent_sonnet : CREDIT_COSTS.agent_haiku
  }

  async function runAgent() {
    if (!selected || !prompt.trim()) return

    const cost = creditCostFor(String(selected.id))
    if (!hasCredits(cost)) {
      setError('Insufficient credits. Top up your plan to continue.')
      return
    }
    setRunning(true)
    setOutput('')
    setError('')
    setRating(null)

    // Read context from localStorage — brand profile, library, recent jobs
    let context: Record<string, unknown> = {}
    try {
      const bp  = localStorage.getItem('vantro_brand_profile')
      const lib = localStorage.getItem('vantro_library')
      const jbs = localStorage.getItem('vantro_jobs')
      if (bp) context.brandProfile = JSON.parse(bp)
      if (lib) {
        const items = JSON.parse(lib) as Array<{ output?: string; [k: string]: unknown }>
        context.libraryItems = items.slice(-5).map(item => ({
          ...item,
          output: typeof item.output === 'string' ? item.output.slice(0, 500) : item.output,
        }))
      }
      if (jbs) {
        const parsed = JSON.parse(jbs)
        context.recentJobs = Array.isArray(parsed) ? parsed.slice(-5) : []
      }
    } catch {
      context = {}
    }

    // Read approved examples for the selected agent
    try {
      const approvedRaw = localStorage.getItem('vantro_approved_examples')
      if (approvedRaw && selected) {
        const allApproved = JSON.parse(approvedRaw) as Record<string, Array<{ prompt: string; output: string }>>
        const agentApproved = allApproved[selected.id] || []
        if (agentApproved.length > 0) {
          context.approvedExamples = agentApproved.slice(-2).map(ex => ({
            prompt: ex.prompt.slice(0, 150),
            output: ex.output.slice(0, 800),
          }))
        }
      }
    } catch {
      // ignore
    }

    // R1: Abort any previous stream and create a fresh controller
    agentAbortRef.current?.abort()
    const ac = new AbortController()
    agentAbortRef.current = ac

    let finalOutput = ''

    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentId: selected.id, prompt: prompt.trim(), context }),
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
        const chunk = dec.decode(value, { stream: true })
        finalOutput += chunk
        // R2: No setTimeout side-effect inside setState
        setOutput(prev => prev + chunk)
      }

      // Auto-save completed output to library
      if (finalOutput.trim() && selected) {
        try {
          const existing = JSON.parse(localStorage.getItem('vantro_library') || '[]')
          const newItem: LibraryItem = {
            id: crypto.randomUUID(),
            agentId: String(selected.id),
            agentName: selected.name,
            category: selected.category,
            prompt: prompt.trim().slice(0, 200),
            output: finalOutput,
            savedAt: new Date().toISOString(),
          }
          lastSavedIdRef.current = newItem.id
          localStorage.setItem('vantro_library', JSON.stringify([...existing, newItem]))
        } catch {
          // ignore storage errors
        }
      }

      // Deduct credits for this agent run
      const newBalance = deductCredits(cost)
      setCredits(newBalance)
    } catch (e) {
      // R1: Ignore AbortError (unmount / re-run cancellation)
      if ((e as Error)?.name === 'AbortError') return
      setError('Agent unavailable. Please try again.')
    } finally {
      setRunning(false)
    }
  }

  function handleRating(vote: 'approved' | 'rejected') {
    if (!selected || !lastSavedIdRef.current) return
    setRating(vote)

    // Update the library item quality
    try {
      const lib = JSON.parse(localStorage.getItem('vantro_library') || '[]') as LibraryItem[]
      const updated = lib.map(item =>
        item.id === lastSavedIdRef.current ? { ...item, quality: vote } : item
      )
      localStorage.setItem('vantro_library', JSON.stringify(updated))

      // If approved, add to approved examples index for few-shot injection
      if (vote === 'approved') {
        const approvedRaw = localStorage.getItem('vantro_approved_examples')
        const allApproved = approvedRaw ? JSON.parse(approvedRaw) as Record<string, Array<{ prompt: string; output: string }>> : {}
        const agentExamples = allApproved[selected.id] || []
        const thisItem = lib.find(i => i.id === lastSavedIdRef.current)
        if (thisItem) {
          const newExamples = [
            ...agentExamples,
            { prompt: thisItem.prompt, output: thisItem.output }
          ].slice(-5)
          localStorage.setItem('vantro_approved_examples', JSON.stringify({
            ...allApproved,
            [selected.id]: newExamples,
          }))
        }
      }
    } catch {
      // ignore
    }
  }

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>

      {/* Left panel — agent list */}
      <div style={{ width: 260, minWidth: 260, borderRight: '1px solid var(--t-border)', overflowY: 'auto', padding: '16px 8px' }}>
        {/* D2: fontFamily added */}
        <p style={{ color: 'var(--t-text-3)', fontSize: 10, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', margin: '0 8px 10px', fontFamily: "'Space Grotesk', sans-serif" }}>22 Agents</p>

        {/* Search */}
        <input
          type="search"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search agents…"
          style={{
            width: '100%', boxSizing: 'border-box',
            background: 'var(--t-surface)',
            border: '1px solid var(--t-border)',
            borderRadius: 8, padding: '6px 10px',
            color: 'var(--t-text-1)', fontSize: 12, fontFamily: "'Space Grotesk', sans-serif",
            outline: 'none', marginBottom: 10,
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
                fontSize: 10, fontWeight: 600, whiteSpace: 'nowrap', fontFamily: "'Space Grotesk', sans-serif",
                background: activeCategory === cat ? '#FF6B35' : 'var(--t-surface-2)',
                color: activeCategory === cat ? '#fff' : 'var(--t-text-2)',
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Agent list — D7: CSS transition removed; GSAP hover used instead */}
        {filtered.map(a => {
          const active = selected?.id === a.id
          const color = CATEGORY_COLORS[a.category]
          return (
            <button
              key={a.id}
              aria-label={a.name}
              onClick={() => { setSelected(a); setOutput(''); setError('') }}
              onMouseEnter={(e) => {
                if (!active) {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { background: 'var(--t-border)', duration: 0.15, ease: 'power2.out' })
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  gsap.killTweensOf(e.currentTarget)
                  gsap.to(e.currentTarget, { background: 'transparent', duration: 0.15, ease: 'power2.out' })
                }
              }}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '7px 10px', borderRadius: 8, border: 'none', cursor: 'pointer',
                background: active ? `${color}14` : 'transparent',
                outline: active ? `1px solid ${color}40` : '1px solid transparent',
                textAlign: 'left', width: '100%',
              }}
            >
              <img
                src={a.avatar}
                alt={a.name}
                style={{ width: 28, height: 28, borderRadius: 7, objectFit: 'cover', border: `1px solid ${color}40`, flexShrink: 0 }}
              />
              <div style={{ minWidth: 0 }}>
                {/* D2: fontFamily added */}
                <p style={{ color: active ? 'var(--t-text-1)' : 'var(--t-text-2)', fontSize: 12, fontWeight: 600, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>{a.name}</p>
                <p style={{ color: 'var(--t-text-3)', fontSize: 10, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: "'Space Grotesk', sans-serif" }}>{a.role}</p>
              </div>
            </button>
          )
        })}

        {filtered.length === 0 && (
          <p style={{ fontSize: 12, color: 'var(--t-text-3)', padding: '10px 8px', fontFamily: "'Space Grotesk', sans-serif" }}>No agents match.</p>
        )}
      </div>

      {/* Right panel — task panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {!selected ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true" style={{ opacity: 0.15 }}>
              <circle cx="16" cy="11" r="5.5" stroke="#fff" strokeWidth="1.5"/>
              <path d="M6 27c0-5.523 4.477-10 10-10s10 4.477 10 10" stroke="#fff" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            {/* D2: fontFamily added */}
            <p style={{ color: 'var(--t-text-3)', fontSize: 13, fontFamily: "'Space Grotesk', sans-serif" }}>Select an agent to get started</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div style={{ padding: '18px 24px 14px', borderBottom: '1px solid var(--t-border)', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
              <img
                src={selected.avatar}
                alt={selected.name}
                style={{ width: 38, height: 38, borderRadius: 10, objectFit: 'cover', border: `2px solid ${accent}60`, flexShrink: 0 }}
              />
              <div>
                {/* D2: fontFamily added */}
                <p style={{ color: 'var(--t-text-1)', fontSize: 15, fontWeight: 700, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>{selected.name}</p>
                <p style={{ color: 'var(--t-text-3)', fontSize: 11, margin: '2px 0 4px', fontFamily: "'Space Grotesk', sans-serif" }}>{selected.role}</p>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 99, background: `${accent}18`, color: accent, border: `1px solid ${accent}40`, fontWeight: 600, letterSpacing: '0.04em', fontFamily: "'Space Grotesk', sans-serif" }}>
                  {selected.category}
                </span>
              </div>
              {/* D3: #34d399 → #1FFFD6 */}
              <span style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 10, color: '#1FFFD6', background: 'rgba(31,255,214,0.08)', padding: '3px 10px', borderRadius: 100, fontFamily: "'Space Grotesk', sans-serif" }}>
                <span style={{ width: 4, height: 4, borderRadius: '50%', background: '#1FFFD6', display: 'inline-block' }} /> Online
              </span>
            </div>

            {/* Stats strip */}
            <div style={{ padding: '10px 24px', borderBottom: '1px solid var(--t-border)', display: 'flex', gap: 24, flexShrink: 0 }}>
              {[
                { label: 'Success rate', value: `${selected.stats.successRate}%` },
                { label: 'Response',     value: selected.stats.responseTime },
                { label: 'Languages',    value: String(selected.stats.languages) },
              ].map(({ label, value }) => (
                <div key={label}>
                  {/* D2: fontFamily added */}
                  <div style={{ fontSize: 10, color: 'var(--t-text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2, fontFamily: "'Space Grotesk', sans-serif" }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: accent, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Output */}
            <div ref={outputRef} style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
              {!output && !running && !error && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {/* D2: fontFamily added */}
                  <p style={{ color: 'var(--t-text-2)', fontSize: 13, lineHeight: 1.65, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
                    {selected.bio}
                  </p>
                  <p style={{ color: 'var(--t-text-3)', fontSize: 12, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
                    Describe your task below and press Run.
                  </p>
                </div>
              )}
              {error && (
                <div style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.20)', borderRadius: 10, padding: '12px 16px', color: '#f87171', fontSize: 13, fontFamily: "'Space Grotesk', sans-serif" }}>{error}</div>
              )}
              {output && (
                <div style={{ color: 'var(--t-text-1)', fontSize: 13.5, lineHeight: 1.75, whiteSpace: 'pre-wrap', fontFamily: "'Space Grotesk', sans-serif" }}>{output}</div>
              )}
              {output && !running && !error && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 10, marginTop: 16,
                  paddingTop: 14, borderTop: '1px solid var(--t-border)',
                }}>
                  <span style={{ fontSize: 11, color: 'var(--t-text-3)', fontFamily: "'Space Grotesk', sans-serif" }}>
                    Rate this output:
                  </span>
                  <button
                    onClick={() => handleRating('approved')}
                    disabled={rating !== null}
                    style={{
                      background: rating === 'approved' ? 'rgba(31,255,214,0.15)' : 'var(--t-surface)',
                      border: rating === 'approved' ? '1px solid rgba(31,255,214,0.4)' : '1px solid rgba(255,255,255,0.09)',
                      borderRadius: 8, padding: '5px 14px', cursor: rating !== null ? 'default' : 'pointer',
                      color: rating === 'approved' ? '#1FFFD6' : 'var(--t-text-2)',
                      fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", display: 'flex', alignItems: 'center', gap: 5,
                      transition: 'all 0.15s',
                    }}
                  >
                    👍 {rating === 'approved' ? 'Approved' : 'Approve'}
                  </button>
                  <button
                    onClick={() => handleRating('rejected')}
                    disabled={rating !== null}
                    style={{
                      background: rating === 'rejected' ? 'rgba(248,113,113,0.12)' : 'var(--t-surface)',
                      border: rating === 'rejected' ? '1px solid rgba(248,113,113,0.35)' : '1px solid rgba(255,255,255,0.09)',
                      borderRadius: 8, padding: '5px 14px', cursor: rating !== null ? 'default' : 'pointer',
                      color: rating === 'rejected' ? '#f87171' : 'var(--t-text-2)',
                      fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", display: 'flex', alignItems: 'center', gap: 5,
                      transition: 'all 0.15s',
                    }}
                  >
                    👎 {rating === 'rejected' ? 'Rejected' : 'Reject'}
                  </button>
                  {rating && (
                    <span style={{ fontSize: 11, color: 'var(--t-text-3)', fontFamily: "'Space Grotesk', sans-serif", marginLeft: 4 }}>
                      {rating === 'approved' ? '✓ Saved as example for future runs' : '✓ Logged'}
                    </span>
                  )}
                </div>
              )}
              {running && !output && (
                <style>{`@keyframes dot{0%,80%,100%{opacity:.25;transform:scale(.7)}40%{opacity:1;transform:scale(1)}}`}</style>
              )}
              {running && !output && (
                <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
                  {[0, 1, 2].map(i => (
                    <span key={i} style={{ width: 7, height: 7, borderRadius: '50%', background: accent, display: 'inline-block', animation: `dot 1.2s ease-in-out ${i * 0.2}s infinite` }} />
                  ))}
                </div>
              )}
            </div>

            {/* Input */}
            <div style={{ padding: '14px 24px 20px', borderTop: '1px solid var(--t-border)', flexShrink: 0 }}>
              {selected && (
                <div style={{
                  fontSize: 11, color: 'var(--t-text-3)',
                  fontFamily: "'Space Grotesk', sans-serif",
                  display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8,
                }}>
                  <span style={{ color: '#1FFFD6', fontWeight: 700 }}>{credits}</span>
                  <span>credits ·</span>
                  <span style={{ opacity: 0.7 }}>
                    this run costs {creditCostFor(String(selected.id))} credit{creditCostFor(String(selected.id)) !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
              <textarea
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runAgent() }}
                placeholder={`Tell ${selected.name} what to do…`}
                rows={3}
                style={{
                  width: '100%', background: 'var(--t-surface)', border: '1px solid var(--t-border)', borderRadius: 10,
                  padding: '11px 14px', color: 'var(--t-text-1)', fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", resize: 'vertical',
                  outline: 'none', marginBottom: 10, boxSizing: 'border-box', transition: 'border-color 0.15s',
                }}
                onFocus={e => (e.currentTarget.style.borderColor = `${accent}60`)}
                onBlur={e => (e.currentTarget.style.borderColor = 'var(--t-border)')}
              />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                {/* D2: fontFamily added */}
                <span style={{ fontSize: 11, color: 'var(--t-text-3)', fontFamily: "'Space Grotesk', sans-serif" }}>⌘ Enter to run</span>
                <button
                  onClick={runAgent}
                  disabled={running || !prompt.trim()}
                  style={{
                    background: running || !prompt.trim() ? 'var(--t-surface)' : `linear-gradient(135deg, ${accent}, ${accent}99)`,
                    color: running || !prompt.trim() ? 'var(--t-text-3)' : '#fff',
                    border: 'none', borderRadius: 8, padding: '9px 22px', fontSize: 13, fontWeight: 600,
                    cursor: running || !prompt.trim() ? 'not-allowed' : 'pointer', fontFamily: "'Space Grotesk', sans-serif",
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
