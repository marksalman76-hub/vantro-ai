'use client'

// Ported from src/pages/DashboardPage.tsx (master branch) — adapted for Next.js App Router
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.vantro.ai'

function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('token') : null }

async function apiFetch(path: string) {
  const t = getToken()
  const res = await fetch(`${API}${path}`, { headers: t ? { Authorization: `Bearer ${t}` } : {} })
  return res.json()
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

function Skeleton() {
  return <div style={{ ...CARD, height: 96, background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
}

const QUICK = [
  { href: '/dashboard/agents',  icon: '◆', label: 'Run an agent',     desc: 'Launch a task with any of your 22 agents' },
  { href: '/dashboard/library', icon: '▣', label: 'Output library',   desc: 'Browse and copy past agent outputs' },
  { href: '/dashboard/brand',   icon: '◎', label: 'Brand profile',    desc: 'Feed your brand context to agents' },
  { href: '/dashboard/settings',icon: '◌', label: 'Settings',         desc: 'Integrations and account settings' },
]

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter()
  const [credits, setCredits] = useState<Credits | null>(null)
  const [jobs, setJobs]       = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) { router.replace('/login'); return }
    Promise.all([
      apiFetch('/api/workspace/credits'),
      apiFetch('/api/agents/jobs?skip=0&limit=50'),
    ]).then(([c, j]) => {
      if ((c as {detail?: string}).detail !== 'Not authenticated') setCredits(c as Credits)
      const jd = j as { jobs?: Job[] }
      setJobs(Array.isArray(jd.jobs) ? jd.jobs : [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [router])

  const completed = jobs.filter(j => j.status === 'completed').length
  const best = topAgent(jobs)
  const recent = jobs.slice(0, 10)

  return (
    <div style={{ padding: '2.5rem', maxWidth: 900 }}>
      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`}</style>

      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
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

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '1rem', marginBottom: '1.75rem' }}>
        {loading ? (<><Skeleton /><Skeleton /><Skeleton /></>) : (<>
          <div style={CARD}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Credits remaining</div>
            <div style={{ fontSize: '1.9rem', fontWeight: 700, lineHeight: 1, color: credits ? creditColor(credits.remaining_credits, credits.total_credits) : 'rgba(255,255,255,0.35)' }}>
              {credits?.remaining_credits?.toLocaleString() ?? '—'}
            </div>
            {credits && <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>of {credits.total_credits.toLocaleString()} total</div>}
          </div>
          <div style={CARD}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Jobs completed</div>
            <div style={{ fontSize: '1.9rem', fontWeight: 700, lineHeight: 1, color: '#00D9FF' }}>{completed.toLocaleString()}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>all time</div>
          </div>
          <div style={CARD}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', fontWeight: 500 }}>Top agent</div>
            <div style={{ fontSize: best.name.length > 16 ? '1rem' : '1.2rem', fontWeight: 700, lineHeight: 1.2, color: '#fff', wordBreak: 'break-word' }}>{best.name}</div>
            {best.count > 0 && <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)', marginTop: '0.35rem' }}>{best.count} run{best.count !== 1 ? 's' : ''}</div>}
          </div>
        </>)}
      </div>

      {/* Quick actions */}
      <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.75rem', marginTop: 0 }}>Quick actions</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {QUICK.map(({ href, icon, label, desc }) => (
          <Link key={href} href={href} style={{ textDecoration: 'none' }}>
            <div style={{ ...CARD, transition: 'border-color 0.15s, background 0.15s', cursor: 'pointer' }}
              onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor = 'rgba(0,217,255,0.30)'; el.style.background = 'rgba(0,217,255,0.04)' }}
              onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor = 'rgba(255,255,255,0.08)'; el.style.background = 'rgba(255,255,255,0.04)' }}
            >
              <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: '#00D9FF' }}>{icon}</div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'rgba(255,255,255,0.92)', marginBottom: '0.25rem' }}>{label}</div>
              <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.3)', lineHeight: 1.45 }}>{desc}</div>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent activity */}
      <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.75rem', marginTop: 0 }}>Recent activity</h2>
      {loading ? (
        <div style={{ ...CARD, height: 120, background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
      ) : recent.length === 0 ? (
        <div style={{ ...CARD, textAlign: 'center', padding: '2.5rem 1.25rem', color: 'rgba(255,255,255,0.3)', fontSize: '0.9rem' }}>
          No jobs run yet.{' '}
          <Link href="/dashboard/agents" style={{ color: '#00D9FF', textDecoration: 'none', fontWeight: 500 }}>Run your first agent →</Link>
        </div>
      ) : (
        <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '1rem', overflow: 'hidden' }}>
          {recent.map((job, i) => (
            <div key={job.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1.25rem', borderBottom: i < recent.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none', gap: '1rem' }}>
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
  )
}
