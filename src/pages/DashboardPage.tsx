import { useEffect, useState } from 'react'
import { Link, useLocation } from 'wouter'
import { DashboardSidebar } from '../components/DashboardSidebar'
import { api, signOut, getToken } from '../lib/api'

// ─── Types ───────────────────────────────────────────────────────────────────

interface Credits {
  total_credits: number
  used_credits: number
  remaining_credits: number
  tier: string
}

interface Job {
  id: string
  agent_id: string
  agent_name: string
  status: string
  credits_used: number
  created_at: string
  completed_at: string | null
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function humanStatus(status: string): string {
  const s = status?.toLowerCase() ?? ''
  if (s === 'pending' || s === 'queued') return 'Queued'
  if (s === 'running' || s === 'processing' || s === 'approved') return 'Running'
  if (s === 'pending_approval' || s === 'pending_financial_review') return 'Needs approval'
  if (s === 'completed') return 'Done'
  if (s === 'failed') return 'Failed'
  if (s === 'cancelled') return 'Cancelled'
  return status
}

function statusColor(status: string): string {
  const h = humanStatus(status)
  if (h === 'Done') return 'oklch(0.75 0.22 145)'
  if (h === 'Running') return 'oklch(0.78 0.13 250)'
  if (h === 'Needs approval') return 'oklch(0.75 0.18 55)'
  if (h === 'Failed') return 'oklch(0.65 0.18 25)'
  if (h === 'Queued') return 'oklch(0.55 0 0)'
  return 'oklch(0.50 0 0)'
}

function creditColor(remaining: number, total: number): string {
  if (total === 0) return 'oklch(0.55 0 0)'
  const pct = remaining / total
  if (pct > 0.5) return 'oklch(0.70 0.22 145)'
  if (pct >= 0.2) return 'oklch(0.70 0.18 55)'
  return 'oklch(0.65 0.18 25)'
}

function topAgent(jobs: Job[]): { name: string; count: number } {
  const freq: Record<string, number> = {}
  for (const j of jobs) {
    const key = j.agent_name || j.agent_id || 'Unknown'
    freq[key] = (freq[key] ?? 0) + 1
  }
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1])
  return sorted.length > 0
    ? { name: sorted[0][0], count: sorted[0][1] }
    : { name: '—', count: 0 }
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return iso
  }
}

// ─── Sub-components ───────────────────────────────────────────────────────────

const CARD_STYLE: React.CSSProperties = {
  background: 'oklch(1 0 0 / 0.04)',
  border: '1px solid oklch(1 0 0 / 0.08)',
  borderRadius: '1rem',
  padding: '1.25rem',
}

function SkeletonCard() {
  return (
    <div
      style={{
        ...CARD_STYLE,
        height: '96px',
        background: 'oklch(1 0 0 / 0.03)',
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export function DashboardPage() {
  const [, setLocation] = useLocation()
  const [credits, setCredits] = useState<Credits | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) {
      setLocation('/login')
      return
    }
    loadData()
  }, [])

  async function loadData() {
    try {
      const [creditsRes, jobsRes] = await Promise.all([
        api.get('/api/workspace/credits'),
        api.get('/api/agents/jobs?skip=0&limit=50'),
      ])

      // Handle 401 on either response
      if ((creditsRes as Record<string, unknown>).detail === 'Not authenticated' ||
          (jobsRes as Record<string, unknown>).detail === 'Not authenticated') {
        signOut()
        return
      }

      setCredits(creditsRes as unknown as Credits)
      const jobsData = jobsRes as unknown as { jobs: Job[] }
      setJobs(Array.isArray(jobsData.jobs) ? jobsData.jobs : [])
    } catch {
      // Network error — stay on page, show empty state
    } finally {
      setLoading(false)
    }
  }

  const completedCount = jobs.filter((j) => j.status === 'completed').length
  const best = topAgent(jobs)
  const recent = jobs.slice(0, 10)

  const QUICK_ACTIONS = [
    { href: '/dashboard/agents', icon: '◆', label: 'Run an agent', desc: 'Launch a task with any of your 22 agents' },
    { href: '/dashboard/library', icon: '▣', label: 'Output library', desc: 'Browse and copy past agent outputs' },
    { href: '/dashboard/brand', icon: '◎', label: 'Brand profile', desc: 'Feed your brand context to agents' },
    { href: '/dashboard/settings', icon: '◌', label: 'Settings', desc: 'Integrations and account settings' },
  ]

  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        background: 'oklch(0.14 0 0)',
        color: 'oklch(0.97 0 0)',
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>

      <DashboardSidebar />

      <main
        style={{
          flex: 1,
          padding: '2.5rem',
          maxWidth: '900px',
          overflow: 'auto',
        }}
      >
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h1
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: '1.75rem',
                margin: 0,
                lineHeight: 1.2,
              }}
            >
              Dashboard
            </h1>
            {credits?.tier && (
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: 'oklch(0.78 0.13 250)',
                  background: 'oklch(0.60 0.18 250 / 0.12)',
                  border: '1px solid oklch(0.60 0.18 250 / 0.25)',
                  borderRadius: '999px',
                  padding: '0.2rem 0.65rem',
                }}
              >
                {credits.tier}
              </span>
            )}
          </div>
          <p style={{ color: 'oklch(0.50 0 0)', marginTop: '0.375rem', fontSize: '0.9rem' }}>
            Your AI agent workspace
          </p>
        </div>

        {/* Metric cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
            marginBottom: '1.75rem',
          }}
        >
          {loading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              {/* Credits remaining */}
              <div style={CARD_STYLE}>
                <div style={{ fontSize: '0.75rem', color: 'oklch(0.50 0 0)', marginBottom: '0.4rem', fontWeight: 500 }}>
                  Credits remaining
                </div>
                <div
                  style={{
                    fontSize: '1.9rem',
                    fontWeight: 700,
                    lineHeight: 1,
                    color: credits
                      ? creditColor(credits.remaining_credits, credits.total_credits)
                      : 'oklch(0.55 0 0)',
                  }}
                >
                  {credits?.remaining_credits?.toLocaleString() ?? '—'}
                </div>
                {credits && (
                  <div style={{ fontSize: '0.75rem', color: 'oklch(0.40 0 0)', marginTop: '0.35rem' }}>
                    of {credits.total_credits.toLocaleString()} total
                  </div>
                )}
              </div>

              {/* Jobs completed */}
              <div style={CARD_STYLE}>
                <div style={{ fontSize: '0.75rem', color: 'oklch(0.50 0 0)', marginBottom: '0.4rem', fontWeight: 500 }}>
                  Jobs completed
                </div>
                <div
                  style={{
                    fontSize: '1.9rem',
                    fontWeight: 700,
                    lineHeight: 1,
                    color: 'oklch(0.78 0.13 250)',
                  }}
                >
                  {completedCount.toLocaleString()}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'oklch(0.40 0 0)', marginTop: '0.35rem' }}>all time</div>
              </div>

              {/* Top agent */}
              <div style={CARD_STYLE}>
                <div style={{ fontSize: '0.75rem', color: 'oklch(0.50 0 0)', marginBottom: '0.4rem', fontWeight: 500 }}>
                  Top agent
                </div>
                <div
                  style={{
                    fontSize: best.name.length > 16 ? '1rem' : '1.2rem',
                    fontWeight: 700,
                    lineHeight: 1.2,
                    color: 'oklch(0.97 0 0)',
                    wordBreak: 'break-word',
                  }}
                >
                  {best.name}
                </div>
                {best.count > 0 && (
                  <div style={{ fontSize: '0.75rem', color: 'oklch(0.40 0 0)', marginTop: '0.35rem' }}>
                    {best.count} run{best.count !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Quick actions */}
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            fontSize: '1rem',
            color: 'oklch(0.75 0 0)',
            marginBottom: '0.75rem',
            marginTop: 0,
          }}
        >
          Quick actions
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '1rem',
            marginBottom: '2rem',
          }}
        >
          {QUICK_ACTIONS.map(({ href, icon, label, desc }) => (
            <Link key={href} href={href}>
              <a
                style={{
                  display: 'block',
                  textDecoration: 'none',
                  ...CARD_STYLE,
                  transition: 'border-color 0.15s ease, background 0.15s ease',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLElement
                  el.style.borderColor = 'oklch(0.60 0.18 250 / 0.30)'
                  el.style.background = 'oklch(0.60 0.18 250 / 0.04)'
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLElement
                  el.style.borderColor = 'oklch(1 0 0 / 0.08)'
                  el.style.background = 'oklch(1 0 0 / 0.04)'
                }}
              >
                <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: 'oklch(0.78 0.13 250)' }}>
                  {icon}
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'oklch(0.92 0 0)', marginBottom: '0.25rem' }}>
                  {label}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'oklch(0.45 0 0)', lineHeight: 1.45 }}>
                  {desc}
                </div>
              </a>
            </Link>
          ))}
        </div>

        {/* Recent activity */}
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            fontSize: '1rem',
            color: 'oklch(0.75 0 0)',
            marginBottom: '0.75rem',
            marginTop: 0,
          }}
        >
          Recent activity
        </h2>

        {loading ? (
          <div
            style={{
              ...CARD_STYLE,
              height: '120px',
              background: 'oklch(1 0 0 / 0.03)',
              animation: 'pulse 1.5s ease-in-out infinite',
            }}
          />
        ) : recent.length === 0 ? (
          <div
            style={{
              ...CARD_STYLE,
              textAlign: 'center',
              padding: '2.5rem 1.25rem',
              color: 'oklch(0.45 0 0)',
              fontSize: '0.9rem',
            }}
          >
            No jobs run yet.{' '}
            <Link href="/dashboard/agents">
              <a style={{ color: 'oklch(0.78 0.13 250)', textDecoration: 'none', fontWeight: 500 }}>
                Run your first agent →
              </a>
            </Link>
          </div>
        ) : (
          <div
            style={{
              background: 'oklch(1 0 0 / 0.03)',
              border: '1px solid oklch(1 0 0 / 0.07)',
              borderRadius: '1rem',
              overflow: 'hidden',
            }}
          >
            {recent.map((job, idx) => {
              const hStatus = humanStatus(job.status)
              const badgeColor = statusColor(job.status)
              return (
                <div
                  key={job.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.85rem 1.25rem',
                    borderBottom: idx < recent.length - 1 ? '1px solid oklch(1 0 0 / 0.05)' : 'none',
                    gap: '1rem',
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        color: 'oklch(0.92 0 0)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {job.agent_name || job.agent_id}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'oklch(0.40 0 0)', marginTop: '0.15rem' }}>
                      {formatDate(job.created_at)}
                    </div>
                  </div>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      letterSpacing: '0.04em',
                      color: badgeColor,
                      background: `${badgeColor.replace(')', ' / 0.12)').replace('oklch(', 'oklch(')}`,
                      border: `1px solid ${badgeColor.replace(')', ' / 0.25)').replace('oklch(', 'oklch(')}`,
                      borderRadius: '999px',
                      padding: '0.2rem 0.6rem',
                      whiteSpace: 'nowrap',
                      flexShrink: 0,
                    }}
                  >
                    {hStatus}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
