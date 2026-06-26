'use client'

// Ported from src/pages/DashboardPage.tsx (master branch) — adapted for Next.js App Router
import { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { AGENTS, CATEGORY_COLORS, Agent } from '@/lib/agents'

const API = process.env.NEXT_PUBLIC_API_URL ?? ''

function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('token') : null }

async function apiFetch<T = unknown>(path: string, signal?: AbortSignal): Promise<T> {
  const t = getToken()
  const res = await fetch(`${API}${path}`, {
    headers: t ? { Authorization: `Bearer ${t}` } : {},
    signal,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<T>
}

// ─── Types ────────────────────────────────────────────────────────────────────

interface Credits { total_credits: number; used_credits: number; remaining_credits: number; tier: string }
interface Job { id: string; agent_id: string; agent_name: string; status: string; credits_used: number; created_at: string; completed_at: string | null }

// ─── Helpers ──────────────────────────────────────────────────────────────────

function humanStatus(s: string) {
  const v = s?.toLowerCase() ?? ''
  if (v === 'pending' || v === 'queued') return 'Queued'
  if (v === 'running' || v === 'processing' || v === 'approved') return 'Running'
  if (v === 'pending_approval' || v === 'pending_financial_review') return 'Needs approval'
  if (v === 'completed') return 'Done'
  if (v === 'failed') return 'Failed'
  if (v === 'cancelled') return 'Cancelled'
  return s
}

function statusColor(s: string) {
  const h = humanStatus(s)
  if (h === 'Done') return 'oklch(0.75 0.22 145)'
  if (h === 'Running') return '#00D9FF'
  if (h === 'Needs approval') return 'oklch(0.75 0.18 55)'
  if (h === 'Failed') return 'oklch(0.65 0.18 25)'
  return 'oklch(0.55 0 0)'
}

function creditColor(remaining: number, total: number) {
  if (total === 0) return 'oklch(0.55 0 0)'
  const pct = remaining / total
  if (pct > 0.5) return 'oklch(0.70 0.22 145)'
  if (pct >= 0.2) return 'oklch(0.70 0.18 55)'
  return 'oklch(0.65 0.18 25)'
}

function topAgent(jobs: Job[]) {
  const freq: Record<string, number> = {}
  for (const j of jobs) { const k = j.agent_name || j.agent_id || 'Unknown'; freq[k] = (freq[k] ?? 0) + 1 }
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1])
  return sorted.length > 0 ? { name: sorted[0][0], count: sorted[0][1] } : { name: '—', count: 0 }
}

function formatDate(iso: string) {
  try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) }
  catch { return iso }
}

// ─── Sub-components ───────────────────────────────────────────────────────────

const CARD: React.CSSProperties = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '1rem', padding: '1.25rem' }

const PANEL: React.CSSProperties = {
  width: 300, flexShrink: 0, padding: '2.5rem 1.5rem',
  borderLeft: '1px solid rgba(255,255,255,0.06)'
}

// ─── Checklist & quick links data ─────────────────────────────────────────────

const CHECKLIST = [
  { label: 'Create your account',        done: true  },
  { label: 'Choose a plan',              done: true  },
  { label: 'Run your first agent',       done: false },
  { label: 'Connect a brand profile',    done: false },
  { label: 'Explore the output library', done: false },
]

const QUICK_LINKS = [
  { label: 'Docs',      href: 'https://docs.vantro.ai'      },
  { label: 'Support',   href: 'mailto:support@vantro.ai'    },
  { label: 'Changelog', href: 'https://vantro.ai/changelog' },
]

// ─── RightPanel ───────────────────────────────────────────────────────────────

function RightPanel() {
  return (
    <aside style={PANEL}>

      {/* Credit usage */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.35)', marginBottom: '0.6rem' }}>
          Credit Usage
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>500</span>
          <span style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.3)' }}>/ 500 used</span>
        </div>
        <div style={{ height: 6, borderRadius: 99, background: 'rgba(255,255,255,0.08)', marginTop: 8 }}>
          <div style={{ height: '100%', borderRadius: 99, width: '100%', background: 'linear-gradient(90deg,#FF6B35,#00D9FF)' }} />
        </div>
        <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.4rem' }}>Resets on July 1</div>
      </div>

      {/* Plan card */}
      <div style={{ background: 'linear-gradient(135deg,rgba(255,107,53,0.12),rgba(0,217,255,0.08))', border: '1px solid rgba(255,107,53,0.25)', borderRadius: '0.875rem', padding: '1rem', marginBottom: '1.75rem' }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,107,53,0.75)', marginBottom: '0.3rem' }}>Current Plan</div>
        <div style={{ fontWeight: 700, fontSize: '1rem', color: '#fff', marginBottom: '0.2rem' }}>Starter Plan</div>
        <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.35)', marginBottom: '0.9rem' }}>500 credits / month</div>
        <Link href="/dashboard/settings?tab=billing" style={{ textDecoration: 'none' }}>
          <button style={{ width: '100%', padding: '0.5rem 0.75rem', background: 'linear-gradient(135deg,#FF6B35,#FF8C42)', border: 'none', borderRadius: '0.625rem', color: '#fff', fontWeight: 600, fontSize: '0.82rem', cursor: 'pointer', letterSpacing: '0.02em' }}>
            Upgrade to Growth →
          </button>
        </Link>
      </div>

      {/* Getting started checklist */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.35)', marginBottom: '0.75rem' }}>
          Getting Started
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {CHECKLIST.map(({ label, done }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <div style={{
                width: 16, height: 16, borderRadius: 4, flexShrink: 0,
                background: done ? 'linear-gradient(135deg,#FF6B35,#00D9FF)' : 'transparent',
                border: done ? 'none' : '1.5px solid rgba(255,255,255,0.18)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {done && (
                  <svg width="9" height="9" viewBox="0 0 10 10" fill="none">
                    <path d="M1.5 5l2.5 2.5 4.5-5" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <span style={{ fontSize: '0.8rem', color: done ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.82)', textDecoration: done ? 'line-through' : 'none' }}>
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick links */}
      <div>
        <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.35)', marginBottom: '0.6rem' }}>
          Quick Links
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {QUICK_LINKS.map(({ label, href }) => (
            <a key={label} href={href} target="_blank" rel="noopener noreferrer"
              style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,0.45)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.35rem', transition: 'color 0.15s' }}
              onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.color = '#00D9FF' }}
              onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'rgba(255,255,255,0.45)' }}
            >
              <span style={{ opacity: 0.5, fontSize: '0.65rem' }}>↗</span>
              {label}
            </a>
          ))}
        </div>
      </div>

    </aside>
  )
}

function Skeleton() {
  return <div style={{ ...CARD, height: 96, background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
}

// ─── Counter hook ─────────────────────────────────────────────────────────────
// Animates a number from 0 to `target` using GSAP. Returns the display string.
function useCountUp(target: number | null, duration = 1.4): string {
  const [display, setDisplay] = useState('—')
  const objRef = useRef({ val: 0 })
  const tweenRef = useRef<gsap.core.Tween | null>(null)

  useEffect(() => {
    if (target === null) { setDisplay('—'); return }
    tweenRef.current?.kill()
    objRef.current.val = 0
    tweenRef.current = gsap.to(objRef.current, {
      val: target,
      duration,
      ease: 'power3.out',
      onUpdate() { setDisplay(Math.round(objRef.current.val).toLocaleString()) },
      onComplete() { setDisplay(target.toLocaleString()) },
    })
    return () => { tweenRef.current?.kill() }
  }, [target, duration])

  return display
}

// ─── MetricCard ───────────────────────────────────────────────────────────────
// Wraps each stat card with GSAP-powered hover physics (translateY + shadow).
function MetricCard({ children, className }: { children: React.ReactNode; className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null)

  function handleEnter() {
    if (cardRef.current) cardRef.current.style.willChange = 'transform'
    gsap.killTweensOf(cardRef.current)
    gsap.to(cardRef.current, {
      y: -4,
      boxShadow: '0 12px 40px rgba(0,217,255,0.12)',
      borderColor: 'rgba(0,217,255,0.22)',
      duration: 0.25,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.killTweensOf(cardRef.current)
    gsap.to(cardRef.current, {
      y: 0,
      boxShadow: '0 0px 0px rgba(0,0,0,0)',
      borderColor: 'rgba(255,255,255,0.08)',
      duration: 0.35,
      ease: 'power3.out',
      onComplete() { if (cardRef.current) cardRef.current.style.willChange = 'auto' },
    })
  }

  return (
    <div
      ref={cardRef}
      className={className}
      style={{ ...CARD }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {children}
    </div>
  )
}

// ─── Quick actions data ────────────────────────────────────────────────────────

function getQuickItems(lockedCount: number) {
  return [
    {
      href: '/dashboard/agents',
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <circle cx="9" cy="6" r="3" stroke="#00D9FF" strokeWidth="1.5"/>
          <path d="M3 15c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#00D9FF" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M13 1l2 2-2 2" stroke="#FF6B35" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      label: 'Run an agent',
      desc: lockedCount > 0 ? `Launch a task with your ${lockedCount} assigned agents` : 'Launch a task with any of your 22 agents',
    },
    {
      href: '/dashboard/library',
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <rect x="2" y="3" width="14" height="3" rx="1" stroke="#00D9FF" strokeWidth="1.4"/>
          <rect x="2" y="8" width="14" height="3" rx="1" stroke="#00D9FF" strokeWidth="1.4"/>
          <rect x="2" y="13" width="8" height="2.5" rx="1" stroke="#00D9FF" strokeWidth="1.4"/>
        </svg>
      ),
      label: 'Output library',
      desc: 'Browse and copy past agent outputs',
    },
    {
      href: '/dashboard/brand',
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <path d="M9 2l1.5 4H15l-3.5 2.5 1.5 4L9 10l-4 2.5 1.5-4L3 6h4.5L9 2Z" stroke="#00D9FF" strokeWidth="1.4" strokeLinejoin="round"/>
        </svg>
      ),
      label: 'Brand profile',
      desc: 'Feed your brand context to agents',
    },
    {
      href: '/dashboard/settings',
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <circle cx="9" cy="9" r="2.5" stroke="#00D9FF" strokeWidth="1.4"/>
          <path d="M9 1v2M9 15v2M1 9h2M15 9h2M3.05 3.05l1.41 1.41M13.54 13.54l1.41 1.41M3.05 14.95l1.41-1.41M13.54 4.46l1.41-1.41" stroke="#00D9FF" strokeWidth="1.4" strokeLinecap="round"/>
        </svg>
      ),
      label: 'Settings',
      desc: 'Integrations and account settings',
    },
  ]
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter()
  const [credits, setCredits] = useState<Credits | null>(null)
  const [jobs, setJobs]       = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)
  const [lockedAgents, setLockedAgents] = useState<Agent[]>([])

  // ── Refs for GSAP scope ──────────────────────────────────────────────────
  const pageRef     = useRef<HTMLDivElement>(null)
  const headerRef   = useRef<HTMLDivElement>(null)
  const metricsRef  = useRef<HTMLDivElement>(null)
  const actionsRef  = useRef<HTMLDivElement>(null)
  const activityRef = useRef<HTMLDivElement>(null)
  const emptyRef    = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('locked_agents') ?? '' : ''
    const ids = stored ? stored.split(',').map(Number).filter(Boolean) : []
    setLockedAgents(AGENTS.filter(a => ids.includes(a.id)))
  }, [])

  useEffect(() => {
    const ac = new AbortController()
    if (!getToken()) { router.replace('/login'); return }
    Promise.all([
      apiFetch<Credits>('/api/workspace/credits', ac.signal),
      apiFetch<{ jobs?: Job[] }>('/api/agents/jobs?skip=0&limit=50', ac.signal),
    ]).then(([c, jd]) => {
      if ((c as {detail?: string}).detail !== 'Not authenticated') setCredits(c)
      setJobs(Array.isArray(jd.jobs) ? jd.jobs : [])
    }).catch((e: unknown) => {
      if ((e as Error)?.name === 'AbortError') return
      console.error('[dashboard] fetch error:', e)
      setError('Failed to load dashboard data. Please refresh.')
    }).finally(() => setLoading(false))
    return () => ac.abort()
  }, [router])

  // ── 1. Page entry animation ────────────────────────────────────────────────
  // Fires once on mount: header slides down, then metric/action/activity
  // sections stagger up with a gentle fade-in.
  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

    // Header drops from -20px, opacity 0 → 1
    tl.fromTo(
      headerRef.current,
      { y: -20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.55 }
    )

    // Metric cards, action cards, activity table stagger upward
    tl.fromTo(
      [metricsRef.current, actionsRef.current, activityRef.current],
      { y: 28, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5, stagger: 0.12 },
      '-=0.3'
    )
  }, { scope: pageRef })

  // ── 2. Post-load reveal: metric cards stagger individually once data arrives
  useGSAP(() => {
    if (loading) return
    const cards = metricsRef.current?.querySelectorAll<HTMLElement>('[data-metric-card]')
    if (!cards?.length) return

    gsap.fromTo(
      cards,
      { scale: 0.96, opacity: 0, y: 12 },
      { scale: 1, opacity: 1, y: 0, duration: 0.45, stagger: 0.09, ease: 'back.out(1.4)' }
    )

    // Activity rows stagger in
    const rows = activityRef.current?.querySelectorAll<HTMLElement>('[data-activity-row]')
    if (rows?.length) {
      gsap.fromTo(
        rows,
        { x: -10, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.35, stagger: 0.06, ease: 'power2.out', delay: 0.15 }
      )
    }
  }, { scope: pageRef, dependencies: [loading] })

  // ── 3. Empty state pulse ───────────────────────────────────────────────────
  // Breathes the "No jobs run yet" card to draw the eye without being annoying.
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

  // ── Counter animations ─────────────────────────────────────────────────────
  const creditsDisplay  = useCountUp(credits?.remaining_credits ?? null, 1.4)
  const completedDisplay = useCountUp(loading ? null : jobs.filter(j => j.status === 'completed').length, 1.0)

  const best = topAgent(jobs)
  const recent = jobs.slice(0, 10)

  const QUICK = useMemo(() => getQuickItems(lockedAgents.length), [lockedAgents.length])

  return (
    <div ref={pageRef} style={{ display: 'flex', alignItems: 'flex-start', minHeight: '100%' }}>
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
      `}</style>

      {/* ── Main content column ── */}
      <div style={{ flex: 1, minWidth: 0, padding: '2.5rem' }}>

      {/* ── Header ── */}
      <div ref={headerRef} style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <h1 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: '1.75rem', margin: 0 }}>
            Dashboard
          </h1>
          {credits?.tier && (
            <span style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#00D9FF', background: 'rgba(0,217,255,0.10)', border: '1px solid rgba(0,217,255,0.25)', borderRadius: 999, padding: '0.2rem 0.65rem' }}>
              {credits.tier}
            </span>
          )}
        </div>
        <p style={{ color: 'rgba(255,255,255,0.35)', marginTop: '0.375rem', fontSize: '0.9rem' }}>Your AI agent workspace</p>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div style={{
          background: 'rgba(248,113,113,0.08)',
          border: '1px solid rgba(248,113,113,0.20)',
          borderRadius: '0.75rem',
          padding: '1rem',
          color: '#f87171',
          fontFamily: "'Space Grotesk', sans-serif",
          marginBottom: '1.5rem',
        }}>
          {error}
        </div>
      )}

      {/* ── Metric cards ── */}
      <div ref={metricsRef} style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '1rem', marginBottom: '1.75rem' }}>
        {loading ? (<><Skeleton /><Skeleton /><Skeleton /></>) : (<>
          {/* Credits remaining — number ticker */}
          <MetricCard>
            <div data-metric-card style={{ height: '100%' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Credits remaining</div>
              <div style={{ fontSize: '1.9rem', fontWeight: 700, lineHeight: 1, color: credits ? creditColor(credits.remaining_credits, credits.total_credits) : 'rgba(255,255,255,0.35)', fontVariantNumeric: 'tabular-nums' }}>
                {creditsDisplay}
              </div>
              {credits && <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>of {credits.total_credits.toLocaleString()} total</div>}
            </div>
          </MetricCard>

          {/* Jobs completed — number ticker */}
          <MetricCard>
            <div data-metric-card style={{ height: '100%' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Jobs completed</div>
              <div style={{ fontSize: '1.9rem', fontWeight: 700, lineHeight: 1, color: '#00D9FF', fontVariantNumeric: 'tabular-nums' }}>
                {completedDisplay}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>all time</div>
            </div>
          </MetricCard>

          {/* Top agent */}
          <MetricCard>
            <div data-metric-card style={{ height: '100%' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Top agent</div>
              <div style={{ fontSize: best.name.length > 16 ? '1rem' : '1.2rem', fontWeight: 700, lineHeight: 1.2, color: '#fff', wordBreak: 'break-word' }}>{best.name}</div>
              {best.count > 0 && <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>{best.count} run{best.count !== 1 ? 's' : ''}</div>}
            </div>
          </MetricCard>
        </>)}
      </div>

      {/* ── Quick actions ── */}
      <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.75rem', marginTop: 0 }}>Quick actions</h2>
      <div ref={actionsRef} style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {QUICK.map(({ href, icon, label, desc }) => (
          <QuickActionCard key={href} href={href} icon={icon} label={label} desc={desc} />
        ))}
      </div>

      {/* ── Your AI Workforce ── */}
      {lockedAgents.length > 0 && (
        <>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', marginTop: 0 }}>
            <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', margin: 0 }}>
              Your AI Workforce
            </h2>
            <span style={{ fontSize: '0.7rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,107,53,0.7)', background: 'rgba(255,107,53,0.08)', border: '1px solid rgba(255,107,53,0.2)', borderRadius: 999, padding: '0.15rem 0.55rem' }}>
              Locked
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '0.75rem', marginBottom: '2rem' }}>
            {lockedAgents.map(agent => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </>
      )}

      {/* ── Recent activity ── */}
      <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.75rem', marginTop: 0 }}>Recent activity</h2>
      <div ref={activityRef}>
        {loading ? (
          <div style={{ ...CARD, height: 120, background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
        ) : recent.length === 0 ? (
          <div
            ref={emptyRef}
            style={{ ...CARD, textAlign: 'center', padding: '2.5rem 1.25rem', color: 'rgba(255,255,255,0.3)', fontSize: '0.9rem' }}
          >
            No jobs run yet.{' '}
            <Link href="/dashboard/agents" style={{ color: '#00D9FF', textDecoration: 'none', fontWeight: 500 }}>Run your first agent →</Link>
          </div>
        ) : (
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '1rem', overflow: 'hidden' }}>
            {recent.map((job, i) => (
              <div
                key={job.id}
                data-activity-row
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1.25rem', borderBottom: i < recent.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none', gap: '1rem' }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'rgba(255,255,255,0.92)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{job.agent_name || job.agent_id}</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.15rem' }}>{formatDate(job.created_at)}</div>
                </div>
                <span style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.04em', color: statusColor(job.status), background: `${statusColor(job.status)}1a`, border: `1px solid ${statusColor(job.status)}40`, borderRadius: 999, padding: '0.2rem 0.6rem', whiteSpace: 'nowrap', flexShrink: 0 }}>
                  {humanStatus(job.status)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Weekly activity chart ── */}
      {!loading && (
        <div style={{ marginTop: '2rem' }}>
          <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.75rem', marginTop: 0 }}>
            Weekly activity
          </h2>
          <div style={{ ...CARD }}>
            <WeeklyChart />
          </div>
        </div>
      )}

      </div>{/* end main content column */}

      {/* ── Right panel ── */}
      <RightPanel />

    </div>
  )
}

// ─── QuickActionCard ──────────────────────────────────────────────────────────
// Extracted so we can attach per-card GSAP hover without polluting the main component.
function QuickActionCard({ href, icon, label, desc }: { href: string; icon: React.ReactNode; label: string; desc: string }) {
  const ref = useRef<HTMLDivElement>(null)

  function handleEnter() {
    if (ref.current) ref.current.style.willChange = 'transform'
    gsap.killTweensOf(ref.current)
    gsap.to(ref.current, {
      y: -3,
      borderColor: 'rgba(0,217,255,0.30)',
      background: 'rgba(0,217,255,0.04)',
      boxShadow: '0 8px 30px rgba(0,217,255,0.08)',
      duration: 0.22,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.killTweensOf(ref.current)
    gsap.to(ref.current, {
      y: 0,
      borderColor: 'rgba(255,255,255,0.08)',
      background: 'rgba(255,255,255,0.04)',
      boxShadow: '0 0px 0px rgba(0,0,0,0)',
      duration: 0.32,
      ease: 'power3.out',
      onComplete() { if (ref.current) ref.current.style.willChange = 'auto' },
    })
  }

  return (
    <Link href={href} style={{ textDecoration: 'none' }}>
      <div
        ref={ref}
        style={{ ...CARD, cursor: 'pointer' }}
        onMouseEnter={handleEnter}
        onMouseLeave={handleLeave}
      >
        <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: '#00D9FF' }}>{icon}</div>
        <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'rgba(255,255,255,0.92)', marginBottom: '0.25rem' }}>{label}</div>
        <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.3)', lineHeight: 1.45 }}>{desc}</div>
      </div>
    </Link>
  )
}

// ─── AgentCard ────────────────────────────────────────────────────────────────
// Subtle lift + border glow on hover for workforce cards.
function AgentCard({ agent }: { agent: Agent }) {
  const ref = useRef<HTMLDivElement>(null)
  const color = CATEGORY_COLORS[agent.category]

  function handleEnter() {
    if (ref.current) ref.current.style.willChange = 'transform'
    gsap.killTweensOf(ref.current)
    gsap.to(ref.current, {
      y: -3,
      boxShadow: `0 8px 28px ${color}22`,
      borderColor: `${color}55`,
      duration: 0.22,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.killTweensOf(ref.current)
    gsap.to(ref.current, {
      y: 0,
      boxShadow: '0 0 0 rgba(0,0,0,0)',
      borderColor: `${color}28`,
      duration: 0.32,
      ease: 'power3.out',
      onComplete() { if (ref.current) ref.current.style.willChange = 'auto' },
    })
  }

  return (
    <div
      ref={ref}
      style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${color}28`, borderRadius: '0.875rem', padding: '1rem', position: 'relative' }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      <div style={{ position: 'absolute', top: 8, right: 8, opacity: 0.35 }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      </div>
      <img src={agent.avatar} alt={agent.name} style={{ width: 40, height: 40, borderRadius: '50%', objectFit: 'cover', border: `1.5px solid ${color}`, marginBottom: '0.6rem' }} />
      <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'rgba(255,255,255,0.9)', lineHeight: 1.3, marginBottom: '0.2rem' }}>{agent.name}</div>
      <div style={{ fontSize: '0.7rem', color: color, opacity: 0.8, lineHeight: 1.3 }}>{agent.role}</div>
    </div>
  )
}

// ─── WeeklyChart ──────────────────────────────────────────────────────────────
const WEEK_DATA = [
  { day: 'Mon', jobs: 3  },
  { day: 'Tue', jobs: 7  },
  { day: 'Wed', jobs: 4  },
  { day: 'Thu', jobs: 12 },
  { day: 'Fri', jobs: 8  },
  { day: 'Sat', jobs: 2  },
  { day: 'Sun', jobs: 5  },
]

function WeeklyChart() {
  const max = Math.max(...WEEK_DATA.map(d => d.jobs))
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', height: 80 }}>
        {WEEK_DATA.map(({ day, jobs }) => {
          const pct = max > 0 ? (jobs / max) * 100 : 0
          return (
            <div key={day} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, height: '100%', justifyContent: 'flex-end' }}>
              <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)', fontVariantNumeric: 'tabular-nums' }}>{jobs}</span>
              <div
                style={{
                  width: '100%',
                  height: `${pct}%`,
                  minHeight: 4,
                  borderRadius: '4px 4px 2px 2px',
                  background: `linear-gradient(180deg, #00D9FF, #FF6B35)`,
                  opacity: 0.8,
                  transition: 'height 0.4s ease',
                }}
                title={`${day}: ${jobs} jobs`}
              />
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {WEEK_DATA.map(({ day }) => (
          <div key={day} style={{ flex: 1, textAlign: 'center', fontSize: '0.65rem', color: 'rgba(255,255,255,0.25)' }}>{day}</div>
        ))}
      </div>
    </div>
  )
}
