'use client'

import { useState, useRef } from 'react'

const AGENTS = [
  { id: 'atlas',    name: 'Atlas',    role: 'Operations Orchestrator' },
  { id: 'echo',     name: 'Echo',     role: 'Customer Support' },
  { id: 'ledger',   name: 'Ledger',   role: 'Finance & Accounting' },
  { id: 'quill',    name: 'Quill',    role: 'Content Writer' },
  { id: 'pixel',    name: 'Pixel',    role: 'Design & Creative' },
  { id: 'forge',    name: 'Forge',    role: 'Code & Engineering' },
  { id: 'sentinel', name: 'Sentinel', role: 'Security & Compliance' },
  { id: 'pulse',    name: 'Pulse',    role: 'Marketing Strategist' },
  { id: 'harbor',   name: 'Harbor',   role: 'Recruiting & HR' },
  { id: 'vector',   name: 'Vector',   role: 'Data Analyst' },
  { id: 'scout',    name: 'Scout',    role: 'Research Agent' },
  { id: 'relay',    name: 'Relay',    role: 'Email & Comms' },
  { id: 'nova',     name: 'Nova',     role: 'Sales Closer' },
  { id: 'cipher',   name: 'Cipher',   role: 'Legal Reviewer' },
  { id: 'tempo',    name: 'Tempo',    role: 'Project Manager' },
  { id: 'mosaic',   name: 'Mosaic',   role: 'Social Media Manager' },
  { id: 'lumen',    name: 'Lumen',    role: 'Brand Strategist' },
  { id: 'drift',    name: 'Drift',    role: 'Logistics & Supply' },
  { id: 'sage',     name: 'Sage',     role: 'Knowledge Base' },
  { id: 'bolt',     name: 'Bolt',     role: 'Automation Engineer' },
  { id: 'aria',     name: 'Aria',     role: 'Voice & Telephony' },
  { id: 'onyx',     name: 'Onyx',     role: 'Executive Assistant' },
]

const AVATARS: Record<string, string> = {
  atlas: '◈', echo: '◉', ledger: '◎', quill: '◌', pixel: '◆',
  forge: '⬡', sentinel: '▣', pulse: '◐', harbor: '◑', vector: '◒',
  scout: '◓', relay: '⬢', nova: '◇', cipher: '⬟', tempo: '◈',
  mosaic: '⬠', lumen: '◉', drift: '◎', sage: '◆', bolt: '⚡',
  aria: '◌', onyx: '▲',
}

const COLORS: Record<string, string> = {
  atlas: '#00D9FF', echo: '#34d399', ledger: '#a78bfa', quill: '#f472b6',
  pixel: '#fb923c', forge: '#60a5fa', sentinel: '#f87171', pulse: '#fbbf24',
  harbor: '#34d399', vector: '#818cf8', scout: '#22d3ee', relay: '#f472b6',
  nova: '#ff6b35', cipher: '#a78bfa', tempo: '#34d399', mosaic: '#fb923c',
  lumen: '#fbbf24', drift: '#60a5fa', sage: '#34d399', bolt: '#fbbf24',
  aria: '#22d3ee', onyx: '#818cf8',
}

type Agent = typeof AGENTS[0]

export default function AgentsPage() {
  const [selected, setSelected] = useState<Agent | null>(null)
  const [prompt, setPrompt]     = useState('')
  const [output, setOutput]     = useState('')
  const [running, setRunning]   = useState(false)
  const [error, setError]       = useState('')
  const outputRef = useRef<HTMLDivElement>(null)

  async function runAgent() {
    if (!selected || !prompt.trim()) return
    setRunning(true)
    setOutput('')
    setError('')

    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentId: selected.id, prompt: prompt.trim() }),
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
        setOutput(prev => {
          const next = prev + dec.decode(value, { stream: true })
          setTimeout(() => outputRef.current?.scrollTo({ top: outputRef.current.scrollHeight, behavior: 'smooth' }), 0)
          return next
        })
      }
    } catch {
      setError('Agent unavailable. Please try again.')
    } finally {
      setRunning(false)
    }
  }

  const accent = selected ? (COLORS[selected.id] || '#00D9FF') : '#00D9FF'

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>

      {/* Agent list */}
      <div style={{ width: 260, minWidth: 260, borderRight: '1px solid rgba(255,255,255,0.07)', overflowY: 'auto', padding: '16px 8px' }}>
        <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 10, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', margin: '0 8px 10px' }}>22 Agents</p>
        {AGENTS.map(a => {
          const active = selected?.id === a.id
          const color = COLORS[a.id] || '#00D9FF'
          return (
            <button
              key={a.id}
              onClick={() => { setSelected(a); setOutput(''); setError('') }}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '7px 10px', borderRadius: 8, border: 'none', cursor: 'pointer',
                background: active ? `${color}14` : 'transparent',
                outline: active ? `1px solid ${color}40` : '1px solid transparent',
                textAlign: 'left', width: '100%', transition: 'all 0.12s',
              }}
            >
              <span style={{ width: 28, height: 28, borderRadius: 7, background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, color, flexShrink: 0 }}>
                {AVATARS[a.id] || '◈'}
              </span>
              <div style={{ minWidth: 0 }}>
                <p style={{ color: active ? '#fff' : 'rgba(255,255,255,0.7)', fontSize: 12, fontWeight: 600, margin: 0 }}>{a.name}</p>
                <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 10, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.role}</p>
              </div>
            </button>
          )
        })}
      </div>

      {/* Task panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {!selected ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
            <div style={{ fontSize: 32, opacity: 0.15 }}>◈</div>
            <p style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>Select an agent to get started</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div style={{ padding: '18px 24px 14px', borderBottom: '1px solid rgba(255,255,255,0.07)', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
              <span style={{ width: 38, height: 38, borderRadius: 10, background: `${accent}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, color: accent }}>
                {AVATARS[selected.id] || '◈'}
              </span>
              <div>
                <p style={{ color: '#fff', fontSize: 15, fontWeight: 700, margin: 0 }}>{selected.name}</p>
                <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, margin: 0 }}>{selected.role}</p>
              </div>
              <span style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 10, color: '#34d399', background: 'rgba(52,211,153,0.08)', padding: '3px 10px', borderRadius: 100 }}>
                <span style={{ width: 4, height: 4, borderRadius: '50%', background: '#34d399', display: 'inline-block' }} /> Online
              </span>
            </div>

            {/* Output */}
            <div ref={outputRef} style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
              {!output && !running && !error && (
                <p style={{ color: 'rgba(255,255,255,0.18)', fontSize: 13 }}>Describe your task below and press Run.</p>
              )}
              {error && (
                <div style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.20)', borderRadius: 10, padding: '12px 16px', color: '#f87171', fontSize: 13 }}>{error}</div>
              )}
              {output && (
                <div style={{ color: 'rgba(255,255,255,0.82)', fontSize: 13.5, lineHeight: 1.75, whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{output}</div>
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
            <div style={{ padding: '14px 24px 20px', borderTop: '1px solid rgba(255,255,255,0.07)', flexShrink: 0 }}>
              <textarea
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runAgent() }}
                placeholder={`Tell ${selected.name} what to do…`}
                rows={3}
                style={{
                  width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10,
                  padding: '11px 14px', color: '#fff', fontSize: 13, fontFamily: 'inherit', resize: 'vertical',
                  outline: 'none', marginBottom: 10, boxSizing: 'border-box', transition: 'border-color 0.15s',
                }}
                onFocus={e => (e.currentTarget.style.borderColor = `${accent}60`)}
                onBlur={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)')}
              />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.18)' }}>⌘ Enter to run</span>
                <button
                  onClick={runAgent}
                  disabled={running || !prompt.trim()}
                  style={{
                    background: running || !prompt.trim() ? 'rgba(255,255,255,0.06)' : `linear-gradient(135deg, ${accent}, ${accent}99)`,
                    color: running || !prompt.trim() ? 'rgba(255,255,255,0.25)' : '#fff',
                    border: 'none', borderRadius: 8, padding: '9px 22px', fontSize: 13, fontWeight: 600,
                    cursor: running || !prompt.trim() ? 'not-allowed' : 'pointer', fontFamily: 'inherit',
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
