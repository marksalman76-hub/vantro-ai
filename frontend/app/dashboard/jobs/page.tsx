'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'

gsap.registerPlugin()

// ─── Types ────────────────────────────────────────────────────────────────────

interface Job {
  id: string
  agent_id?: string
  agent_name?: string
  status: string
  created_at: string
  completed_at?: string | null
  output?: string
  credits_used?: number
}

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

interface JobRun {
  id: string
  agentId: string
  agentName: string
  prompt: string
  status: string
  createdAt?: string
  savedAt?: string
  quality?: 'approved' | 'rejected'
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

function formatDate(iso: string) {
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
  if (!str) return '—'
  return str.length > max ? str.slice(0, max) + '…' : str
}

function normalizeStatus(s: string) {
  const v = s?.toLowerCase() ?? ''
  if (v === 'completed' || v === 'done') return 'completed'
  if (v === 'running' || v === 'processing' || v === 'approved') return 'running'
  if (v === 'failed') return 'failed'
  if (v === 'pending' || v === 'queued') return 'queued'
  if (v === 'cancelled') return 'cancelled'
  return v
}

function humanStatus(s: string) {
  const n = normalizeStatus(s)
  if (n === 'completed') return 'Completed'
  if (n === 'running') return 'Running'
  if (n === 'failed') return 'Failed'
  if (n === 'queued') return 'Queued'
  if (n === 'cancelled') return 'Cancelled'
  return s
}

function statusColor(s: string) {
  const n = normalizeStatus(s)
  if (n === 'completed') return '#1FFFD6'
  if (n === 'running') return '#FF6B35'
  if (n === 'failed') return '#f87171'
  if (n === 'queued') return '#00D9FF'
  return 'rgba(255,255,255,0.35)'
}

// ─── Quality helpers ──────────────────────────────────────────────────────────

function computeAgentStats(libraryItems: LibraryItem[]) {
  const stats: Record<string, { total: number; approved: number; rejected: number; rate: number }> = {}
  for (const item of libraryItems) {
    if (!stats[item.agentId]) {
      stats[item.agentId] = { total: 0, approved: 0, rejected: 0, rate: 0 }
    }
    stats[item.agentId].total++
    if (item.quality === 'approved') stats[item.agentId].approved++
    if (item.quality === 'rejected') stats[item.agentId].rejected++
  }
  for (const key of Object.keys(stats)) {
    const s = stats[key]
    const rated = s.approved + s.rejected
    s.rate = rated > 0 ? Math.round((s.approved / rated) * 100) : -1
  }
  return stats
}

function getJobQuality(job: Job, libraryItems: LibraryItem[]): 'approved' | 'rejected' | null {
  const agentId = job.agent_id || ''
  const match = libraryItems.find(
    item =>
      item.agentId === agentId &&
      item.prompt.slice(0, 100) === (job.output || '').slice(0, 100)
  )
  return match?.quality ?? null
}

// ─── StatusBadge ──────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const color = statusColor(status)
  return (
    <span style={{
      fontSize: '0.72rem',
      fontWeight: 700,
      letterSpacing: '0.04em',
      color,
      background: `${color}18`,
      border: `1px solid ${color}40`,
      borderRadius: 999,
      padding: '0.2rem 0.65rem',
      whiteSpace: 'nowrap',
      fontFamily: "'Space Grotesk', sans-serif",
    }}>
      {humanStatus(status)}
    </span>
  )
}

// ─── Skeleton rows ─────────────────────────────────────────────────────────────

function SkeletonRows() {
  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '1rem', overflow: 'hidden' }}>
      {[1, 2, 3, 4, 5].map((i, idx) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            padding: '0.85rem 1.25rem',
            borderBottom: idx < 4 ? '1px solid rgba(255,255,255,0.05)' : 'none',
            animation: 'pulse 1.5s ease-in-out infinite',
            animationDelay: `${idx * 0.08}s`,
          }}
        >
          <div style={{ flex: 2, height: 14, borderRadius: 4, background: 'rgba(255,255,255,0.07)' }} />
          <div style={{ flex: 1, height: 22, borderRadius: 999, background: 'rgba(255,255,255,0.05)' }} />
          <div style={{ flex: 1.5, height: 12, borderRadius: 4, background: 'rgba(255,255,255,0.05)' }} />
          <div style={{ flex: 2, height: 12, borderRadius: 4, background: 'rgba(255,255,255,0.04)' }} />
          <div style={{ width: 48, height: 28, borderRadius: 6, background: 'rgba(255,255,255,0.05)' }} />
        </div>
      ))}
    </div>
  )
}

// ─── DetailPanel ─────────────────────────────────────────────────────────────

function DetailPanel({ job, onClose }: { job: Job; onClose: () => void }) {
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (panelRef.current) {
      gsap.fromTo(
        panelRef.current,
        { opacity: 0, y: 12 },
        { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }
      )
    }
  }, [])

  return (
    <div
      ref={panelRef}
      style={{
        ...CARD,
        marginTop: '1rem',
        position: 'relative',
      }}
    >
      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          background: 'rgba(255,255,255,0.07)',
          border: '1px solid rgba(255,255,255,0.10)',
          borderRadius: '0.4rem',
          color: 'rgba(255,255,255,0.5)',
          fontSize: '0.75rem',
          fontWeight: 600,
          padding: '0.2rem 0.6rem',
          cursor: 'pointer',
          fontFamily: "'Space Grotesk', sans-serif",
        }}
      >
        Close
      </button>

      <div style={{ marginBottom: '1rem', paddingRight: '3rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1rem', color: '#fff', margin: 0 }}>
            {job.agent_name || job.agent_id || 'Unknown Agent'}
          </h3>
          <StatusBadge status={job.status} />
        </div>
        <p style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '0.78rem', color: 'rgba(255,255,255,0.3)', margin: '0.3rem 0 0' }}>
          Started: {formatDate(job.created_at)}
          {job.completed_at ? ` · Completed: ${formatDate(job.completed_at)}` : ''}
          {job.credits_used != null ? ` · ${job.credits_used} credit${job.credits_used !== 1 ? 's' : ''}` : ''}
        </p>
      </div>

      <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '0.625rem', padding: '1rem' }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.28)', marginBottom: '0.6rem', fontFamily: "'Space Grotesk', sans-serif" }}>
          Full Output
        </div>
        <pre style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: '0.82rem',
          color: 'rgba(255,255,255,0.75)',
          lineHeight: 1.65,
          margin: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {job.output || 'No output available for this job.'}
        </pre>
      </div>
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function JobsPage() {
  const router = useRouter()
  const [jobs, setJobs]       = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [libraryItems, setLibraryItems] = useState<LibraryItem[]>([])

  const pageRef    = useRef<HTMLDivElement>(null)
  const headerRef  = useRef<HTMLDivElement>(null)
  const tableRef   = useRef<HTMLDivElement>(null)
  const emptyRef   = useRef<HTMLDivElement>(null)

  // Load library items for quality cross-referencing
  useEffect(() => {
    try {
      const raw = localStorage.getItem('vantro_library')
      if (raw) setLibraryItems(JSON.parse(raw) as LibraryItem[])
    } catch {}
  }, [])

  useEffect(() => {
    const token = getToken()
    if (!token) { router.replace('/login'); return }

    const ac = new AbortController()
    fetch('/api/agents/jobs?skip=0&limit=50', {
      headers: { Authorization: `Bearer ${token}` },
      signal: ac.signal,
    })
      .then(r => r.json())
      .then((data: { jobs?: Job[] }) => {
        const apiJobs = data.jobs || []
        if (apiJobs.length > 0) {
          setJobs(apiJobs)
        } else {
          // Fallback: load from localStorage
          try {
            const raw = localStorage.getItem('vantro_jobs')
            if (raw) {
              const localJobs = JSON.parse(raw) as Job[]
              setJobs(localJobs)
            }
          } catch {}
        }
      })
      .catch((e: Error) => {
        if (e.name !== 'AbortError') {
          // On API error, try localStorage fallback
          try {
            const raw = localStorage.getItem('vantro_jobs')
            if (raw) {
              setJobs(JSON.parse(raw) as Job[])
            } else {
              setError('Failed to load jobs')
            }
          } catch {
            setError('Failed to load jobs')
          }
        }
      })
      .finally(() => setLoading(false))

    return () => ac.abort()
  }, [router])

  // Compute per-agent quality stats from library
  const agentStats = useMemo(() => computeAgentStats(libraryItems), [libraryItems])

  // Top agents with rated items
  const topAgents = useMemo(
    () =>
      Object.entries(agentStats)
        .filter(([, s]) => s.approved + s.rejected > 0)
        .sort((a, b) => b[1].total - a[1].total)
        .slice(0, 5),
    [agentStats]
  )

  // ── Page entry animation ──────────────────────────────────────────────────
  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.fromTo(
      headerRef.current,
      { y: -20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5 }
    )
    tl.fromTo(
      tableRef.current,
      { y: 24, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.45 },
      '-=0.25'
    )
  }, { scope: pageRef })

  // ── Rows stagger in once data loads ──────────────────────────────────────
  useGSAP(() => {
    if (loading) return
    const rows = tableRef.current?.querySelectorAll<HTMLElement>('[data-job-row]')
    if (rows?.length) {
      gsap.fromTo(
        rows,
        { x: -10, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.32, stagger: 0.05, ease: 'power2.out', delay: 0.1 }
      )
    }
  }, { scope: pageRef, dependencies: [loading] })

  // ── Empty state pulse ────────────────────────────────────────────────────
  useGSAP(() => {
    if (loading || jobs.length > 0 || !emptyRef.current) return
    gsap.to(emptyRef.current, {
      boxShadow: '0 0 28px rgba(0,217,255,0.10)',
      borderColor: 'rgba(0,217,255,0.18)',
      repeat: -1,
      yoyo: true,
      duration: 2.2,
      ease: 'sine.inOut',
    })
  }, { scope: pageRef, dependencies: [loading, jobs.length] })

  function handleViewJob(job: Job) {
    setSelectedJob(prev => (prev?.id === job.id ? null : job))
  }

  return (
    <div ref={pageRef} style={{ flex: 1, minWidth: 0, padding: '2.5rem', background: '#0A0D14', minHeight: '100%' }}>
      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`}</style>

      {/* ── Header ── */}
      <div ref={headerRef} style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.75rem', margin: 0, color: '#fff' }}>
          Activity
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.35)', marginTop: '0.375rem', fontSize: '0.9rem', fontFamily: "'Space Grotesk', sans-serif" }}>
          All past agent runs
        </p>
      </div>

      {/* ── Agent Performance Summary ── */}
      {topAgents.length > 0 && (
        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          {topAgents.map(([agentId, s]) => (
            <div key={agentId} style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 10,
              padding: '10px 14px',
              minWidth: 130,
            }}>
              <div style={{
                fontSize: 12,
                fontWeight: 600,
                color: '#fff',
                marginBottom: 4,
                fontFamily: "'Space Grotesk', sans-serif",
                textTransform: 'capitalize',
              }}>
                {agentId}
              </div>
              <div style={{
                fontSize: 20,
                fontWeight: 700,
                color: s.rate >= 80 ? '#1FFFD6' : s.rate >= 50 ? '#FF6B35' : '#f87171',
                fontFamily: "'Space Grotesk', sans-serif",
              }}>
                {s.rate >= 0 ? `${s.rate}%` : '—'}
              </div>
              <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', fontFamily: "'Space Grotesk', sans-serif" }}>
                {s.total} run{s.total !== 1 ? 's' : ''} · {s.approved}✓ {s.rejected}✗
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Table / States ── */}
      <div ref={tableRef}>
        {loading ? (
          <SkeletonRows />
        ) : error ? (
          <div style={{ ...CARD, textAlign: 'center', padding: '2.5rem 1.25rem', color: '#f87171', fontSize: '0.9rem', fontFamily: "'Space Grotesk', sans-serif" }}>
            {error}
          </div>
        ) : jobs.length === 0 ? (
          <div
            ref={emptyRef}
            style={{ ...CARD, textAlign: 'center', padding: '3rem 1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}
          >
            <svg width="38" height="38" viewBox="0 0 38 38" fill="none" aria-hidden="true">
              <polyline points="3,19 9,19 13,7 18,31 23,14 26,24 30,19 35,19" stroke="rgba(255,255,255,0.18)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div>
              <p style={{ fontFamily: "'Space Grotesk', sans-serif", color: 'rgba(255,255,255,0.45)', fontSize: '0.95rem', margin: '0 0 0.4rem', fontWeight: 500 }}>
                No jobs yet
              </p>
              <p style={{ fontFamily: "'Space Grotesk', sans-serif", color: 'rgba(255,255,255,0.25)', fontSize: '0.82rem', margin: 0 }}>
                Run an agent and your activity will appear here
              </p>
            </div>
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
          </div>
        ) : (
          <>
            {/* Table */}
            <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '1rem', overflow: 'hidden' }}>

              {/* Table header */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '2fr 1fr 1.8fr 2.5fr auto',
                gap: '0.75rem',
                padding: '0.65rem 1.25rem',
                borderBottom: '1px solid rgba(255,255,255,0.07)',
                background: 'rgba(255,255,255,0.02)',
              }}>
                {['Agent', 'Status', 'Started', 'Output Preview', ''].map((col, i) => (
                  <div key={i} style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    color: 'rgba(255,255,255,0.28)',
                    fontFamily: "'Space Grotesk', sans-serif",
                  }}>
                    {col}
                  </div>
                ))}
              </div>

              {/* Table rows */}
              {jobs.map((job, i) => (
                <JobRow
                  key={job.id}
                  job={job}
                  isLast={i === jobs.length - 1}
                  isSelected={selectedJob?.id === job.id}
                  onView={() => handleViewJob(job)}
                  libraryItems={libraryItems}
                />
              ))}
            </div>

            {/* Detail panel */}
            {selectedJob && (
              <DetailPanel job={selectedJob} onClose={() => setSelectedJob(null)} />
            )}
          </>
        )}
      </div>
    </div>
  )
}

// ─── JobRow ───────────────────────────────────────────────────────────────────

function JobRow({
  job,
  isLast,
  isSelected,
  onView,
  libraryItems,
}: {
  job: Job
  isLast: boolean
  isSelected: boolean
  onView: () => void
  libraryItems: LibraryItem[]
}) {
  const rowRef = useRef<HTMLDivElement>(null)

  function handleEnter() {
    gsap.to(rowRef.current, {
      background: 'rgba(255,255,255,0.025)',
      duration: 0.15,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.to(rowRef.current, {
      background: isSelected ? 'rgba(0,217,255,0.04)' : 'transparent',
      duration: 0.22,
      ease: 'power3.out',
    })
  }

  const quality = getJobQuality(job, libraryItems)

  return (
    <div
      ref={rowRef}
      data-job-row
      style={{
        display: 'grid',
        gridTemplateColumns: '2fr 1fr 1.8fr 2.5fr auto',
        gap: '0.75rem',
        alignItems: 'center',
        padding: '0.85rem 1.25rem',
        borderBottom: isLast ? 'none' : '1px solid rgba(255,255,255,0.05)',
        background: isSelected ? 'rgba(0,217,255,0.04)' : 'transparent',
        transition: 'background 0.15s ease',
      }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {/* Agent name */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{
            fontWeight: 600,
            fontSize: '0.875rem',
            color: 'rgba(255,255,255,0.90)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            fontFamily: "'Space Grotesk', sans-serif",
          }}>
            {job.agent_name || job.agent_id || 'Unknown'}
          </div>
          {quality && (
            <span style={{
              fontSize: 10,
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: 99,
              background: quality === 'approved' ? 'rgba(31,255,214,0.12)' : 'rgba(248,113,113,0.10)',
              color: quality === 'approved' ? '#1FFFD6' : '#f87171',
              fontFamily: "'Space Grotesk', sans-serif",
              border: `1px solid ${quality === 'approved' ? 'rgba(31,255,214,0.3)' : 'rgba(248,113,113,0.25)'}`,
              flexShrink: 0,
            }}>
              {quality === 'approved' ? '✓' : '✗'}
            </span>
          )}
        </div>
        {job.credits_used != null && (
          <div style={{ fontSize: '0.68rem', color: 'rgba(255,255,255,0.22)', marginTop: '0.15rem', fontFamily: "'Space Grotesk', sans-serif" }}>
            {job.credits_used} credit{job.credits_used !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Status */}
      <div><StatusBadge status={job.status} /></div>

      {/* Started */}
      <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.38)', fontFamily: "'Space Grotesk', sans-serif" }}>
        {formatDate(job.created_at)}
      </div>

      {/* Output preview */}
      <div style={{
        fontSize: '0.78rem',
        color: 'rgba(255,255,255,0.35)',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        fontFamily: "'Space Grotesk', sans-serif",
      }}>
        {truncate(job.output || '', 60)}
      </div>

      {/* Actions */}
      <div>
        <ViewButton isSelected={isSelected} onClick={onView} />
      </div>
    </div>
  )
}

// ─── ViewButton ───────────────────────────────────────────────────────────────

function ViewButton({ isSelected, onClick }: { isSelected: boolean; onClick: () => void }) {
  const btnRef = useRef<HTMLButtonElement>(null)

  function handleEnter() {
    gsap.to(btnRef.current, {
      scale: 1.05,
      borderColor: 'rgba(0,217,255,0.45)',
      color: '#00D9FF',
      duration: 0.16,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.to(btnRef.current, {
      scale: 1,
      borderColor: isSelected ? 'rgba(0,217,255,0.35)' : 'rgba(255,255,255,0.12)',
      color: isSelected ? '#00D9FF' : 'rgba(255,255,255,0.45)',
      duration: 0.22,
      ease: 'power3.out',
    })
  }

  return (
    <button
      ref={btnRef}
      type="button"
      onClick={onClick}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      style={{
        fontSize: '0.72rem',
        fontWeight: 600,
        color: isSelected ? '#00D9FF' : 'rgba(255,255,255,0.45)',
        background: isSelected ? 'rgba(0,217,255,0.08)' : 'transparent',
        border: `1px solid ${isSelected ? 'rgba(0,217,255,0.35)' : 'rgba(255,255,255,0.12)'}`,
        borderRadius: '0.4rem',
        padding: '0.3rem 0.65rem',
        cursor: 'pointer',
        fontFamily: "'Space Grotesk', sans-serif",
        willChange: 'transform',
        whiteSpace: 'nowrap',
      }}
    >
      {isSelected ? 'Hide' : 'View'}
    </button>
  )
}
