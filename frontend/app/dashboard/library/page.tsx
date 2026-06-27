'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'

gsap.registerPlugin()

// ─── Types ────────────────────────────────────────────────────────────────────

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

// Keep OutputItem for backward-compat with vantro_outputs reads
interface OutputItem {
  id: string
  agentName: string
  prompt: string
  output: string
  timestamp: string
}

// ─── Constants ────────────────────────────────────────────────────────────────

const CARD: React.CSSProperties = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: '1rem',
  padding: '1.25rem',
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getToken() {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null
}

function formatTimestamp(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function truncate(str: string, max: number) {
  if (!str) return ''
  return str.length > max ? str.slice(0, max) + '…' : str
}

// Agent name → accent color (cycles through brand palette)
const AGENT_COLORS = ['#FF6B35', '#00D9FF', '#1FFFD6', '#FF6B35', '#00D9FF']
function agentColor(name: string) {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return AGENT_COLORS[Math.abs(hash) % AGENT_COLORS.length]
}

/** Convert legacy OutputItem → LibraryItem so we can display both sources */
function outputToLibrary(o: OutputItem): LibraryItem {
  return {
    id: o.id,
    agentId: o.id,
    agentName: o.agentName,
    category: '',
    prompt: o.prompt,
    output: o.output,
    savedAt: o.timestamp,
  }
}

// ─── LibraryCard ──────────────────────────────────────────────────────────────

function LibraryCard({
  item,
  onRate,
}: {
  item: LibraryItem
  onRate: (item: LibraryItem, vote: 'approved' | 'rejected') => void
}) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [copied, setCopied] = useState(false)
  const color = agentColor(item.agentName)

  function handleEnter() {
    gsap.to(cardRef.current, {
      y: -4,
      boxShadow: '0 12px 40px rgba(0,217,255,0.10)',
      borderColor: 'rgba(0,217,255,0.20)',
      duration: 0.22,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.to(cardRef.current, {
      y: 0,
      boxShadow: '0 0px 0px rgba(0,0,0,0)',
      borderColor: 'rgba(255,255,255,0.08)',
      duration: 0.32,
      ease: 'power3.out',
    })
  }

  function handleCopy() {
    navigator.clipboard.writeText(item.output).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div
      ref={cardRef}
      data-output-card
      style={{ ...CARD, display: 'flex', flexDirection: 'column', gap: '0.75rem', willChange: 'transform' }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {/* Agent name badge + quality badge + copy */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', minWidth: 0 }}>
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            color,
            background: `${color}18`,
            border: `1px solid ${color}35`,
            borderRadius: 999,
            padding: '0.2rem 0.65rem',
            fontFamily: "'Space Grotesk', sans-serif",
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            maxWidth: '60%',
          }}>
            {item.agentName}
          </span>
          {item.quality && (
            <span style={{
              fontSize: 10,
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: 99,
              background: item.quality === 'approved' ? 'rgba(31,255,214,0.12)' : 'rgba(248,113,113,0.10)',
              color: item.quality === 'approved' ? '#1FFFD6' : '#f87171',
              border: `1px solid ${item.quality === 'approved' ? 'rgba(31,255,214,0.3)' : 'rgba(248,113,113,0.25)'}`,
              fontFamily: "'Space Grotesk', sans-serif",
              whiteSpace: 'nowrap',
            }}>
              {item.quality === 'approved' ? '✓ Approved' : '✗ Rejected'}
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          style={{
            fontSize: '0.72rem',
            fontWeight: 600,
            color: copied ? '#1FFFD6' : 'rgba(255,255,255,0.35)',
            background: copied ? 'rgba(31,255,214,0.08)' : 'rgba(255,255,255,0.05)',
            border: `1px solid ${copied ? 'rgba(31,255,214,0.3)' : 'rgba(255,255,255,0.10)'}`,
            borderRadius: '0.4rem',
            padding: '0.25rem 0.6rem',
            cursor: 'pointer',
            fontFamily: "'Space Grotesk', sans-serif",
            transition: 'all 0.2s ease',
            flexShrink: 0,
          }}
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {/* Prompt */}
      <div>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.28)', marginBottom: '0.3rem', fontFamily: "'Space Grotesk', sans-serif" }}>
          Prompt
        </div>
        <p style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,0.75)', lineHeight: 1.5, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
          {truncate(item.prompt, 80)}
        </p>
      </div>

      {/* Output preview */}
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.28)', marginBottom: '0.3rem', fontFamily: "'Space Grotesk', sans-serif" }}>
          Output
        </div>
        <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)', lineHeight: 1.55, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
          {truncate(item.output, 120)}
        </p>
      </div>

      {/* Timestamp */}
      <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.22)', fontFamily: "'Space Grotesk', sans-serif", marginTop: 'auto', paddingTop: '0.25rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        {formatTimestamp(item.savedAt)}
      </div>

      {/* Approve / Reject row */}
      <div style={{ display: 'flex', gap: 6, marginTop: 10, paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <button
          onClick={(e) => { e.stopPropagation(); onRate(item, 'approved') }}
          style={{
            background: item.quality === 'approved' ? 'rgba(31,255,214,0.12)' : 'rgba(255,255,255,0.05)',
            border: item.quality === 'approved' ? '1px solid rgba(31,255,214,0.3)' : '1px solid rgba(255,255,255,0.08)',
            borderRadius: 6,
            padding: '3px 10px',
            cursor: 'pointer',
            color: item.quality === 'approved' ? '#1FFFD6' : 'rgba(255,255,255,0.45)',
            fontSize: 11,
            fontFamily: "'Space Grotesk', sans-serif",
          }}
        >
          👍 Approve
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onRate(item, 'rejected') }}
          style={{
            background: item.quality === 'rejected' ? 'rgba(248,113,113,0.10)' : 'rgba(255,255,255,0.05)',
            border: item.quality === 'rejected' ? '1px solid rgba(248,113,113,0.3)' : '1px solid rgba(255,255,255,0.08)',
            borderRadius: 6,
            padding: '3px 10px',
            cursor: 'pointer',
            color: item.quality === 'rejected' ? '#f87171' : 'rgba(255,255,255,0.45)',
            fontSize: 11,
            fontFamily: "'Space Grotesk', sans-serif",
          }}
        >
          👎 Reject
        </button>
      </div>
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function LibraryPage() {
  const router = useRouter()
  const [items, setItems] = useState<LibraryItem[]>([])
  const [loaded, setLoaded] = useState(false)
  const [qualityFilter, setQualityFilter] = useState<'all' | 'approved' | 'rejected'>('all')

  const pageRef   = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)
  const gridRef   = useRef<HTMLDivElement>(null)
  const emptyRef  = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!getToken()) { router.replace('/login'); return }
    try {
      // Primary source: vantro_library
      const libraryRaw = localStorage.getItem('vantro_library') || '[]'
      const libraryParsed: LibraryItem[] = JSON.parse(libraryRaw)
      const libraryItems: LibraryItem[] = Array.isArray(libraryParsed) ? libraryParsed : []

      // Fallback/legacy source: vantro_outputs
      const outputsRaw = localStorage.getItem('vantro_outputs') || '[]'
      const outputsParsed: OutputItem[] = JSON.parse(outputsRaw)
      const outputItems: LibraryItem[] = Array.isArray(outputsParsed)
        ? outputsParsed.map(outputToLibrary)
        : []

      // Merge: library items first, then legacy outputs not already present
      const libraryIds = new Set(libraryItems.map(i => i.id))
      const merged = [...libraryItems, ...outputItems.filter(o => !libraryIds.has(o.id))]
      setItems(merged)
    } catch {
      setItems([])
    }
    setLoaded(true)
  }, [router])

  // ── Approve / reject handler ────────────────────────────────────────────────
  function rateItem(item: LibraryItem, vote: 'approved' | 'rejected') {
    const updated = items.map(i => i.id === item.id ? { ...i, quality: vote } : i)
    setItems(updated)

    // Persist only the LibraryItem entries (not the legacy OutputItem ones)
    const libraryOnly = updated.filter(i => i.category !== undefined && i.agentId !== i.id || true)
    localStorage.setItem('vantro_library', JSON.stringify(libraryOnly))

    // Manage approved_examples index
    try {
      const approvedRaw = localStorage.getItem('vantro_approved_examples')
      const allApproved: Record<string, Array<{ prompt: string; output: string }>> =
        approvedRaw ? JSON.parse(approvedRaw) : {}
      const agentExamples = allApproved[item.agentId] || []

      if (vote === 'approved') {
        const already = agentExamples.some(ex => ex.prompt === item.prompt)
        if (!already) {
          const newExamples = [...agentExamples, { prompt: item.prompt, output: item.output }].slice(-5)
          localStorage.setItem('vantro_approved_examples', JSON.stringify({
            ...allApproved,
            [item.agentId]: newExamples,
          }))
        }
      } else {
        const filtered = agentExamples.filter(ex => ex.prompt !== item.prompt)
        localStorage.setItem('vantro_approved_examples', JSON.stringify({
          ...allApproved,
          [item.agentId]: filtered,
        }))
      }
    } catch {
      // ignore
    }
  }

  // ── Filtered view ───────────────────────────────────────────────────────────
  const displayed = items.filter(item =>
    qualityFilter === 'all' || item.quality === qualityFilter
  )

  // ── Page entry animation ────────────────────────────────────────────────────
  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.fromTo(
      headerRef.current,
      { y: -20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5 }
    )
    tl.fromTo(
      gridRef.current,
      { y: 24, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.45 },
      '-=0.25'
    )
  }, { scope: pageRef })

  // ── Cards stagger in once data loads ───────────────────────────────────────
  useGSAP(() => {
    if (!loaded) return
    const cards = gridRef.current?.querySelectorAll<HTMLElement>('[data-output-card]')
    if (cards?.length) {
      gsap.fromTo(
        cards,
        { scale: 0.96, opacity: 0, y: 14 },
        { scale: 1, opacity: 1, y: 0, duration: 0.4, stagger: 0.07, ease: 'back.out(1.4)' }
      )
    }
  }, { scope: pageRef, dependencies: [loaded, displayed.length] })

  // ── Empty state pulse ───────────────────────────────────────────────────────
  useGSAP(() => {
    if (!loaded || displayed.length > 0 || !emptyRef.current) return
    gsap.to(emptyRef.current, {
      boxShadow: '0 0 28px rgba(0,217,255,0.10)',
      borderColor: 'rgba(0,217,255,0.18)',
      repeat: -1,
      yoyo: true,
      duration: 2.2,
      ease: 'sine.inOut',
    })
  }, { scope: pageRef, dependencies: [loaded, displayed.length] })

  return (
    <div ref={pageRef} style={{ flex: 1, minWidth: 0, padding: '2.5rem', background: '#0A0D14', minHeight: '100%' }}>
      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`}</style>

      {/* ── Header ── */}
      <div ref={headerRef} style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.75rem', margin: 0, color: '#fff' }}>
          Library
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.35)', marginTop: '0.375rem', fontSize: '0.9rem', fontFamily: "'Space Grotesk', sans-serif" }}>
          Saved agent outputs
        </p>
      </div>

      {/* ── Quality filter tabs ── */}
      {loaded && items.length > 0 && (
        <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
          {(['all', 'approved', 'rejected'] as const).map(f => (
            <button
              key={f}
              onClick={() => setQualityFilter(f)}
              style={{
                padding: '4px 14px',
                borderRadius: 99,
                cursor: 'pointer',
                fontSize: 11,
                fontWeight: 600,
                textTransform: 'capitalize',
                fontFamily: "'Space Grotesk', sans-serif",
                background: qualityFilter === f
                  ? f === 'approved' ? 'rgba(31,255,214,0.15)'
                  : f === 'rejected' ? 'rgba(248,113,113,0.12)'
                  : 'rgba(255,255,255,0.12)'
                  : 'rgba(255,255,255,0.06)',
                color: qualityFilter === f
                  ? f === 'approved' ? '#1FFFD6'
                  : f === 'rejected' ? '#f87171'
                  : '#fff'
                  : 'rgba(255,255,255,0.4)',
                border: qualityFilter === f
                  ? f === 'approved' ? '1px solid rgba(31,255,214,0.3)'
                  : f === 'rejected' ? '1px solid rgba(248,113,113,0.3)'
                  : '1px solid rgba(255,255,255,0.15)'
                  : '1px solid transparent',
              }}
            >
              {f === 'all' ? 'All' : f === 'approved' ? '✓ Approved' : '✗ Rejected'}
            </button>
          ))}
        </div>
      )}

      {/* ── Grid ── */}
      <div ref={gridRef}>
        {!loaded ? (
          // Loading skeletons
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ ...CARD, height: 200, background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
            ))}
          </div>
        ) : displayed.length === 0 ? (
          // Empty state
          <div
            ref={emptyRef}
            style={{ ...CARD, textAlign: 'center', padding: '3.5rem 1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">
              <rect x="4" y="8" width="32" height="24" rx="3" stroke="rgba(255,255,255,0.18)" strokeWidth="1.8"/>
              <line x1="4" y1="15" x2="36" y2="15" stroke="rgba(255,255,255,0.12)" strokeWidth="1.5"/>
              <line x1="12" y1="8" x2="12" y2="32" stroke="rgba(255,255,255,0.12)" strokeWidth="1.5"/>
              <path d="M18 21h10M18 26h6" stroke="rgba(255,255,255,0.18)" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
            <div>
              <p style={{ fontFamily: "'Space Grotesk', sans-serif", color: 'rgba(255,255,255,0.45)', fontSize: '0.95rem', margin: '0 0 0.5rem', fontWeight: 500 }}>
                {qualityFilter === 'all' ? 'No saved outputs yet' : `No ${qualityFilter} outputs`}
              </p>
              <p style={{ fontFamily: "'Space Grotesk', sans-serif", color: 'rgba(255,255,255,0.25)', fontSize: '0.82rem', margin: 0 }}>
                {qualityFilter === 'all'
                  ? 'Run an agent and your outputs will appear here'
                  : `Approve or reject outputs to see them here`}
              </p>
            </div>
            {qualityFilter === 'all' && (
              <Link href="/dashboard/agents" style={{ textDecoration: 'none' }}>
                <button style={{
                  marginTop: '0.5rem',
                  padding: '0.6rem 1.4rem',
                  background: 'linear-gradient(135deg,#FF6B35,#FF8C42)',
                  border: 'none',
                  borderRadius: '0.625rem',
                  color: '#fff',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  fontFamily: "'Space Grotesk', sans-serif",
                  letterSpacing: '0.02em',
                }}>
                  Run your first agent →
                </button>
              </Link>
            )}
          </div>
        ) : (
          // Items grid
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {displayed.map(item => (
              <LibraryCard key={item.id} item={item} onRate={rateItem} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
