'use client'

import { useState, useEffect, useRef, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

// ─── Shared card styles ───────────────────────────────────────────────────────
const CARD: React.CSSProperties = {
  background: 'var(--t-surface)',
  border: '1px solid var(--t-border)',
  borderRadius: '1rem',
  padding: '1.25rem',
}

const WARN_CARD: React.CSSProperties = {
  background: 'rgba(255,107,53,0.04)',
  border: '1px solid rgba(255,107,53,0.20)',
  borderRadius: '1rem',
  padding: '1.5rem',
}

const DANGER_CARD: React.CSSProperties = {
  background: 'rgba(220,38,38,0.04)',
  border: '1px solid rgba(220,38,38,0.20)',
  borderRadius: '1rem',
  padding: '1.5rem',
}

// ─── Data deleted for modal ───────────────────────────────────────────────────
const ITEMS_DELETED = [
  'Your account and login credentials',
  'All agent jobs and run history',
  'All output library content',
  'Brand profile and workspace settings',
  'Remaining credits (non-refundable)',
  'Active subscription (cancelled immediately)',
  'All API keys',
]

// ─── Helpers ─────────────────────────────────────────────────────────────────
function getRenewalDate(): string {
  if (typeof window === 'undefined') return '—'
  const stored = localStorage.getItem('subscription_start')
  const base = stored ? new Date(stored) : new Date()
  const renewal = new Date(base)
  renewal.setDate(renewal.getDate() + 30)
  return renewal.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function getUserInitial(): string {
  if (typeof window === 'undefined') return 'U'
  const email = localStorage.getItem('email') ?? ''
  const name = localStorage.getItem('workspace_name') ?? ''
  if (name) return name[0].toUpperCase()
  if (email) return email[0].toUpperCase()
  return 'U'
}

// ─── Section divider component ────────────────────────────────────────────────
function SectionLabel({ label, color = 'var(--t-text-3)' }: { label: string; color?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.875rem' }}>
      <span
        style={{
          fontFamily: "'Space Grotesk',sans-serif",
          fontWeight: 700,
          fontSize: '0.75rem',
          color,
          textTransform: 'uppercase',
          letterSpacing: '0.09em',
          whiteSpace: 'nowrap',
        }}
      >
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: 'var(--t-surface-2)' }} />
    </div>
  )
}

// ─── Toggle component ─────────────────────────────────────────────────────────
function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      style={{
        width: 42,
        height: 24,
        borderRadius: 12,
        border: 'none',
        background: checked
          ? 'linear-gradient(135deg,#FF6B35,#e85d00)'
          : 'var(--t-border)',
        cursor: 'pointer',
        position: 'relative',
        flexShrink: 0,
        transition: 'background 0.2s',
        padding: 0,
        outline: 'none',
        boxShadow: checked ? '0 0 10px rgba(255,107,53,0.35)' : 'none',
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: 3,
          left: checked ? 21 : 3,
          width: 18,
          height: 18,
          borderRadius: '50%',
          background: '#fff',
          transition: 'left 0.2s',
          boxShadow: '0 1px 4px rgba(0,0,0,0.4)',
        }}
      />
    </button>
  )
}

// ─── "Coming soon" badge shimmer styles (module-scope, injected once) ─────────
const SHIMMER_STYLES = `
  @keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
  }
  .cs-badge {
    font-size: 0.72rem;
    font-style: italic;
    font-weight: 500;
    padding: 0.22rem 0.6rem;
    border-radius: 99px;
    border: 1px solid var(--t-border);
    background: linear-gradient(
      90deg,
      rgba(255,255,255,0.06) 0%,
      rgba(255,255,255,0.16) 40%,
      rgba(255,255,255,0.06) 60%,
      rgba(255,255,255,0.06) 100%
    );
    background-size: 200% auto;
    color: rgba(255,255,255,0.30);
    animation: shimmer 2.4s linear infinite;
  }
`

// ─── "Coming soon" badge with shimmer ────────────────────────────────────────
function ComingSoonBadge() {
  return <span className="cs-badge">Coming soon</span>
}

// ─── Credit bar ───────────────────────────────────────────────────────────────
function CreditBar({ used, total }: { used: number; total: number }) {
  const pct = Math.min(100, Math.round((used / total) * 100))
  const remaining = total - used
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--t-text-2)' }}>Credits used</span>
        <span style={{ fontSize: '0.78rem', color: 'var(--t-text-2)', fontVariantNumeric: 'tabular-nums' }}>
          {remaining} / {total} remaining
        </span>
      </div>
      <div style={{ height: 6, borderRadius: 99, background: 'var(--t-surface-2)', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            borderRadius: 99,
            background: pct > 80
              ? 'linear-gradient(90deg,#FF6B35,#e85d00)'
              : pct > 50
              ? 'linear-gradient(90deg,#FF6B35,#00D9FF)'
              : 'linear-gradient(90deg,#00D9FF,#0099bb)',
            transition: 'width 0.4s',
          }}
        />
      </div>
    </div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────
function SettingsPageInner() {
  const router = useRouter()
  const searchParams = useSearchParams()

  // AbortController refs for in-flight requests
  const cancelReqRef = useRef<AbortController | null>(null)
  const deleteReqRef = useRef<AbortController | null>(null)

  // Billing section ref (for ?tab=billing scroll)
  const billingSectionRef = useRef<HTMLDivElement>(null)

  // Delete account state
  const [showModal, setShowModal] = useState(false)
  const [confirmText, setConfirmText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  // Cancel subscription state
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [cancelLoading, setCancelLoading] = useState(false)
  const [cancelError, setCancelError] = useState('')
  const [cancelDone, setCancelDone] = useState(false)

  // Notification toggles (localStorage-persisted)
  const [notifEmail, setNotifEmail] = useState(false)
  const [notifJobs, setNotifJobs] = useState(false)
  const [notifDigest, setNotifDigest] = useState(false)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        if (showCancelModal) setShowCancelModal(false)
        if (showModal) { setShowModal(false); setConfirmText(''); setError('') }
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [showCancelModal, showModal])

  // Abort in-flight requests on unmount
  useEffect(() => {
    return () => {
      cancelReqRef.current?.abort()
      deleteReqRef.current?.abort()
    }
  }, [])

  // Scroll to billing section when ?tab=billing is present
  useEffect(() => {
    if (searchParams.get('tab') === 'billing' && billingSectionRef.current) {
      setTimeout(() => {
        billingSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 300)
    }
  }, [searchParams])

  // Computed from localStorage (client-only)
  const [plan, setPlan] = useState('Starter')
  const [renewalDate, setRenewalDate] = useState('—')
  const [userInitial, setUserInitial] = useState('U')
  const [creditsUsed, setCreditsUsed] = useState(0)
  const creditsTotal = 500

  useEffect(() => {
    setPlan(localStorage.getItem('plan') ?? 'Starter')
    setRenewalDate(getRenewalDate())
    setUserInitial(getUserInitial())

    const used = parseInt(localStorage.getItem('credits_used') ?? '0', 10)
    setCreditsUsed(isNaN(used) ? 0 : used)

    setNotifEmail(localStorage.getItem('notif_email') === 'true')
    setNotifJobs(localStorage.getItem('notif_jobs') === 'true')
    setNotifDigest(localStorage.getItem('notif_digest') === 'true')
  }, [])

  function setNotif(key: string, setter: (v: boolean) => void, value: boolean) {
    setter(value)
    localStorage.setItem(key, String(value))
  }

  // ─── Plan card amount (hardcoded per plan for display) ──────────────────────
  const planPrice = plan.toLowerCase() === 'pro' ? 79 : plan.toLowerCase() === 'growth' ? 39 : 19

  // ─── Handlers ───────────────────────────────────────────────────────────────
  async function handleCancelSubscription() {
    const ac = new AbortController()
    cancelReqRef.current = ac
    setCancelLoading(true)
    setCancelError('')
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch('/api/user/cancel-subscription', {
        method: 'POST',
        signal: ac.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })
      const data = await res.json()
      if (!res.ok) { setCancelError(data.detail || 'Cancellation failed. Contact support.'); return }
      setCancelDone(true)
    } catch (e) {
      if ((e as Error)?.name === 'AbortError') return
      setCancelError('Network error. Please try again.')
    } finally {
      setCancelLoading(false)
    }
  }

  async function handleDelete() {
    if (confirmText !== 'DELETE') return
    const ac = new AbortController()
    deleteReqRef.current = ac
    setLoading(true)
    setError('')
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch('/api/user/delete', {
        method: 'DELETE',
        signal: ac.signal,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Deletion failed. Please try again or contact support.')
        setLoading(false)
        return
      }
      localStorage.removeItem('token')
      localStorage.removeItem('onboarding_complete')
      localStorage.removeItem('workspace_name')
      setDone(true)
      setTimeout(() => router.replace('/'), 3000)
    } catch (e) {
      if ((e as Error)?.name === 'AbortError') return
      setError('Network error. Please try again.')
      setLoading(false)
    }
  }

  // ─── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={{ padding: '2.5rem', maxWidth: 740 }}>
      <style dangerouslySetInnerHTML={{ __html: SHIMMER_STYLES }} />

      {/* ── Page header ──────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2.5rem' }}>
        {/* Avatar circle */}
        <div
          style={{
            width: 46,
            height: 46,
            borderRadius: '50%',
            background: 'linear-gradient(135deg,#FF6B35 0%,#cc4a18 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: "'Space Grotesk',sans-serif",
            fontWeight: 700,
            fontSize: '1.1rem',
            color: '#fff',
            flexShrink: 0,
            boxShadow: '0 0 18px rgba(255,107,53,0.30)',
            border: '2px solid rgba(255,107,53,0.35)',
          }}
        >
          {userInitial}
        </div>
        <div>
          <h1 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: '1.75rem', margin: 0, lineHeight: 1.1 }}>
            Settings
          </h1>
          <p style={{ color: 'var(--t-text-3)', marginTop: '0.25rem', fontSize: '0.875rem', margin: 0 }}>
            Manage your account and preferences
          </p>
        </div>
      </div>

      {/* ── Plan card ─────────────────────────────────────────────────────────── */}
      <SectionLabel label="Plan" color="#00D9FF" />
      <div
        style={{
          background: 'linear-gradient(135deg,rgba(255,107,53,0.08) 0%,rgba(0,217,255,0.05) 100%)',
          border: '1px solid rgba(255,107,53,0.22)',
          borderRadius: '1rem',
          padding: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        {/* Top row: plan pill + upgrade button */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
              <span
                style={{
                  fontFamily: "'Space Grotesk',sans-serif",
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  color: 'var(--t-text-1)',
                }}
              >
                {plan.charAt(0).toUpperCase() + plan.slice(1)} Plan
              </span>
              <span
                style={{
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  padding: '0.15rem 0.55rem',
                  borderRadius: 99,
                  background: 'rgba(255,107,53,0.15)',
                  color: '#FF6B35',
                  border: '1px solid rgba(255,107,53,0.30)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                }}
              >
                Active
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--t-text-3)' }}>
              Monthly billing &nbsp;·&nbsp; Renews {renewalDate}
            </div>
          </div>
          <button
            style={{
              flexShrink: 0,
              padding: '0.5rem 1.15rem',
              borderRadius: '0.625rem',
              fontSize: '0.83rem',
              fontWeight: 700,
              color: '#fff',
              background: 'linear-gradient(135deg,#FF6B35,#cc4a18)',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'inherit',
              boxShadow: '0 0 14px rgba(255,107,53,0.28)',
              letterSpacing: '0.01em',
            }}
            onClick={() => router.push('/pricing')}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.boxShadow = '0 0 22px rgba(255,107,53,0.45)' }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.boxShadow = '0 0 14px rgba(255,107,53,0.28)' }}
          >
            Upgrade Plan
          </button>
        </div>

        {/* Credit bar */}
        <CreditBar used={creditsUsed} total={creditsTotal} />

        {/* Meta row */}
        <div
          style={{
            display: 'flex',
            gap: '1.5rem',
            marginTop: '1.1rem',
            paddingTop: '1.1rem',
            borderTop: '1px solid var(--t-border)',
            flexWrap: 'wrap',
          }}
        >
          {[
            { label: 'Credits', value: `${creditsTotal - creditsUsed} / ${creditsTotal}` },
            { label: 'Billing', value: 'Monthly' },
            { label: 'Next charge', value: `$${planPrice} on ${renewalDate}` },
          ].map(({ label, value }) => (
            <div key={label}>
              <div style={{ fontSize: '0.7rem', color: 'var(--t-text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.2rem' }}>{label}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--t-text-1)', fontVariantNumeric: 'tabular-nums' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Account section ───────────────────────────────────────────────────── */}
      <SectionLabel label="Account" />

      {/* Profile & workspace card */}
      <div style={{ ...CARD, marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              {/* icon */}
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style={{ opacity: 0.5 }}>
                <circle cx="8" cy="5.5" r="2.5" stroke="#fff" strokeWidth="1.4"/>
                <path d="M2 13c0-2.76 2.69-5 6-5s6 2.24 6 5" stroke="#fff" strokeWidth="1.4" strokeLinecap="round"/>
              </svg>
              <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--t-text-1)' }}>Profile &amp; workspace</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--t-text-3)' }}>Name, workspace settings and notifications</div>
          </div>
          <ComingSoonBadge />
        </div>
      </div>

      {/* Notification preferences card */}
      <div style={{ ...CARD, marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.1rem' }}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style={{ opacity: 0.5 }}>
            <path d="M8 1a5 5 0 0 1 5 5v2.5l1.5 2H1.5L3 8.5V6a5 5 0 0 1 5-5Z" stroke="#fff" strokeWidth="1.4"/>
            <path d="M6.5 13.5a1.5 1.5 0 0 0 3 0" stroke="#fff" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--t-text-1)' }}>Notification preferences</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {[
            {
              label: 'Email notifications',
              desc: 'Receive product updates and announcements',
              value: notifEmail,
              setter: (v: boolean) => setNotif('notif_email', setNotifEmail, v),
            },
            {
              label: 'Job completion alerts',
              desc: 'Get notified when an agent job finishes',
              value: notifJobs,
              setter: (v: boolean) => setNotif('notif_jobs', setNotifJobs, v),
            },
            {
              label: 'Weekly usage digest',
              desc: 'A summary of credits and activity every Monday',
              value: notifDigest,
              setter: (v: boolean) => setNotif('notif_digest', setNotifDigest, v),
            },
          ].map(({ label, desc, value, setter }) => (
            <div
              key={label}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
                paddingBottom: '0.85rem',
                borderBottom: '1px solid var(--t-border)',
              }}
            >
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--t-text-2)', marginBottom: '0.1rem' }}>{label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--t-text-3)' }}>{desc}</div>
              </div>
              <Toggle checked={value} onChange={setter} />
            </div>
          ))}
        </div>
        {/* Remove last border */}
        <style>{`.notif-row:last-child { border-bottom: none !important; }`}</style>
      </div>

      {/* ── Integrations section ──────────────────────────────────────────────── */}
      <SectionLabel label="Integrations" />
      <div style={{ ...CARD, marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style={{ opacity: 0.5 }}>
                <rect x="1.5" y="4" width="5" height="8" rx="1" stroke="#fff" strokeWidth="1.4"/>
                <rect x="9.5" y="4" width="5" height="8" rx="1" stroke="#fff" strokeWidth="1.4"/>
                <path d="M6.5 8h3" stroke="#fff" strokeWidth="1.4" strokeLinecap="round"/>
              </svg>
              <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--t-text-1)' }}>API keys &amp; webhooks</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--t-text-3)' }}>Manage programmatic access to Vantro</div>
          </div>
          <ComingSoonBadge />
        </div>
      </div>

      {/* ── Billing section ───────────────────────────────────────────────────── */}
      <div ref={billingSectionRef}>
      <SectionLabel label="Billing" color="rgba(255,107,53,0.7)" />
      <div style={{ ...WARN_CARD, marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--t-text-1)', marginBottom: '0.4rem' }}>
              Cancel subscription
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--t-text-3)', lineHeight: 1.55, marginBottom: '0.6rem' }}>
              Your access continues until the end of the current billing period. You may be eligible for a refund under our{' '}
              <Link href="/refund" style={{ color: '#FF6B35', textDecoration: 'none' }}>30-day money-back guarantee</Link>.
            </div>
            <div style={{ fontSize: '0.77rem', color: 'var(--t-text-3)' }}>
              Next charge: <span style={{ color: 'var(--t-text-2)', fontVariantNumeric: 'tabular-nums' }}>${planPrice} on {renewalDate}</span>
            </div>
          </div>
          <button
            onClick={() => { setShowCancelModal(true); setCancelError(''); setCancelDone(false) }}
            style={{ flexShrink: 0, padding: '0.55rem 1.1rem', borderRadius: '0.625rem', fontSize: '0.85rem', fontWeight: 600, color: '#FF6B35', background: 'rgba(255,107,53,0.10)', border: '1px solid rgba(255,107,53,0.35)', cursor: 'pointer', transition: 'all 0.15s', fontFamily: 'inherit' }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,107,53,0.18)' }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,107,53,0.10)' }}
          >
            Cancel subscription
          </button>
        </div>
      </div>

      </div>{/* end billingSectionRef wrapper */}

      {/* ── Cancel subscription modal ─────────────────────────────────────────── */}
      {showCancelModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '1rem' }}>
          <div role="dialog" aria-modal="true" aria-labelledby="cancel-modal-title" style={{ background: 'oklch(0.16 0 0)', border: '1px solid var(--t-border)', borderRadius: '1.25rem', padding: '2rem', maxWidth: 440, width: '100%', boxShadow: '0 24px 80px rgba(0,0,0,0.6)' }}>
            {cancelDone ? (
              <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'rgba(31,255,214,0.12)', border: '1px solid rgba(31,255,214,0.30)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 10l4 4 8-8" stroke="#1FFFD6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--t-text-1)', marginBottom: '0.5rem' }}>Subscription cancelled</div>
                <div style={{ fontSize: '0.83rem', color: 'var(--t-text-3)', lineHeight: 1.6, marginBottom: '1.25rem' }}>
                  Your access continues until the end of the billing period. No further charges will be made.
                </div>
                <button
                  onClick={() => setShowCancelModal(false)}
                  style={{ width: '100%', padding: '0.6rem', borderRadius: '0.625rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--t-text-2)', background: 'var(--t-surface)', border: '1px solid var(--t-border)', cursor: 'pointer', fontFamily: 'inherit' }}
                >
                  Close
                </button>
              </div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.30)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 5v4M8 11h.01" stroke="#FF6B35" strokeWidth="1.5" strokeLinecap="round"/><circle cx="8" cy="8" r="6.5" stroke="#FF6B35" strokeWidth="1.2"/></svg>
                  </div>
                  <h3 id="cancel-modal-title" style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: '1.05rem', color: 'var(--t-text-1)', margin: 0 }}>
                    Cancel your subscription?
                  </h3>
                </div>

                <div style={{ fontSize: '0.84rem', color: 'var(--t-text-2)', lineHeight: 1.65, marginBottom: '1.25rem' }}>
                  You&apos;re currently on the <strong style={{ color: 'var(--t-text-1)' }}>{plan.charAt(0).toUpperCase() + plan.slice(1)} plan</strong>. Cancelling will:
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.25rem', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                  {[
                    'Stop all future billing immediately',
                    'Keep your access until end of current period',
                    'Lock your agents after expiry',
                    'Preserve your data for 30 days',
                  ].map(item => (
                    <li key={item} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: 'var(--t-text-2)' }}>
                      <div style={{ width: 5, height: 5, borderRadius: '50%', background: '#FF6B35', flexShrink: 0 }} />
                      {item}
                    </li>
                  ))}
                </ul>

                <div style={{ fontSize: '0.78rem', color: 'var(--t-text-3)', marginBottom: '1.25rem' }}>
                  Within 30 days of your first payment? You may be eligible for a full refund —{' '}
                  <Link href="/refund" style={{ color: '#FF6B35', textDecoration: 'none' }} onClick={() => setShowCancelModal(false)}>see our refund policy</Link>.
                </div>

                {cancelError && (
                  <div style={{ fontSize: '0.8rem', color: '#f87171', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.20)', borderRadius: '0.5rem', padding: '0.6rem 0.75rem', marginBottom: '1rem' }}>
                    {cancelError}
                  </div>
                )}

                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => setShowCancelModal(false)}
                    disabled={cancelLoading}
                    style={{ flex: 1, padding: '0.6rem', borderRadius: '0.625rem', fontSize: '0.875rem', fontWeight: 600, color: '#fff', background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', border: 'none', cursor: 'pointer', fontFamily: 'inherit', boxShadow: '0 0 16px rgba(255,107,53,0.25)' }}
                  >
                    Keep subscription
                  </button>
                  <button
                    onClick={handleCancelSubscription}
                    disabled={cancelLoading}
                    style={{ flex: 1, padding: '0.6rem', borderRadius: '0.625rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--t-text-2)', background: 'var(--t-surface)', border: '1px solid var(--t-border)', cursor: cancelLoading ? 'not-allowed' : 'pointer', fontFamily: 'inherit', opacity: cancelLoading ? 0.6 : 1 }}
                  >
                    {cancelLoading ? 'Cancelling…' : 'Yes, cancel'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Danger zone ───────────────────────────────────────────────────────── */}
      <SectionLabel label="Danger zone" color="oklch(0.65 0.18 25)" />
      <div style={DANGER_CARD}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--t-text-1)', marginBottom: '0.4rem' }}>
              Delete my data
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--t-text-3)', lineHeight: 1.55 }}>
              Permanently delete your account and all associated data from our systems.
              This action cannot be undone.
            </div>
          </div>
          <button
            onClick={() => { setShowModal(true); setConfirmText(''); setError('') }}
            style={{ flexShrink: 0, padding: '0.55rem 1.1rem', borderRadius: '0.625rem', fontSize: '0.85rem', fontWeight: 600, color: 'oklch(0.65 0.18 25)', background: 'oklch(0.65 0.18 25 / 0.10)', border: '1px solid oklch(0.65 0.18 25 / 0.35)', cursor: 'pointer', transition: 'all 0.15s', fontFamily: 'inherit' }}
            onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.background = 'oklch(0.65 0.18 25 / 0.18)' }}
            onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.background = 'oklch(0.65 0.18 25 / 0.10)' }}
          >
            Delete account
          </button>
        </div>
      </div>

      {/* ── Delete confirmation modal ─────────────────────────────────────────── */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '1rem' }}>
          <div role="dialog" aria-modal="true" aria-labelledby="delete-modal-title" style={{ background: 'oklch(0.16 0 0)', border: '1px solid var(--t-border)', borderRadius: '1.25rem', padding: '2rem', maxWidth: 460, width: '100%', boxShadow: '0 24px 80px rgba(0,0,0,0.6)' }}>

            {done ? (
              <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>✓</div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--t-text-1)', marginBottom: '0.5rem' }}>Data deleted</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--t-text-3)' }}>All your data has been permanently removed. Redirecting…</div>
              </div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'oklch(0.65 0.18 25 / 0.15)', border: '1px solid oklch(0.65 0.18 25 / 0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <span style={{ color: 'oklch(0.65 0.18 25)', fontSize: '1rem' }}>⚠</span>
                  </div>
                  <h3 id="delete-modal-title" style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: '1.05rem', color: 'var(--t-text-1)', margin: 0 }}>
                    Delete your data permanently?
                  </h3>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--t-text-2)', marginBottom: '1rem', lineHeight: 1.6 }}>
                  This will immediately and irreversibly delete:
                </p>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.25rem', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                  {ITEMS_DELETED.map(item => (
                    <li key={item} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: 'var(--t-text-2)' }}>
                      <span style={{ color: 'oklch(0.65 0.18 25)', fontSize: '0.7rem' }}>✕</span>
                      {item}
                    </li>
                  ))}
                </ul>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--t-text-2)', marginBottom: '0.5rem' }}>
                    Type <strong style={{ color: 'oklch(0.65 0.18 25)' }}>DELETE</strong> to confirm
                  </label>
                  <input
                    type="text"
                    value={confirmText}
                    onChange={e => setConfirmText(e.target.value)}
                    placeholder="DELETE"
                    autoFocus
                    style={{ width: '100%', padding: '0.6rem 0.85rem', background: 'var(--t-surface)', border: `1px solid ${confirmText === 'DELETE' ? 'oklch(0.65 0.18 25 / 0.5)' : 'var(--t-border)'}`, borderRadius: '0.625rem', color: '#fff', fontSize: '0.9rem', outline: 'none', fontFamily: 'monospace', boxSizing: 'border-box', transition: 'border-color 0.15s' }}
                  />
                </div>

                {error && (
                  <div style={{ fontSize: '0.8rem', color: 'oklch(0.65 0.18 25)', background: 'oklch(0.65 0.18 25 / 0.08)', border: '1px solid oklch(0.65 0.18 25 / 0.25)', borderRadius: '0.5rem', padding: '0.6rem 0.75rem', marginBottom: '1rem' }}>
                    {error}
                  </div>
                )}

                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => { setShowModal(false); setConfirmText(''); setError('') }}
                    disabled={loading}
                    style={{ flex: 1, padding: '0.6rem', borderRadius: '0.625rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--t-text-2)', background: 'var(--t-surface)', border: '1px solid var(--t-border)', cursor: 'pointer', fontFamily: 'inherit' }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={confirmText !== 'DELETE' || loading}
                    style={{ flex: 1, padding: '0.6rem', borderRadius: '0.625rem', fontSize: '0.875rem', fontWeight: 600, color: confirmText === 'DELETE' && !loading ? '#fff' : 'var(--t-text-3)', background: confirmText === 'DELETE' && !loading ? 'oklch(0.55 0.20 25)' : 'var(--t-surface)', border: '1px solid transparent', cursor: confirmText === 'DELETE' && !loading ? 'pointer' : 'not-allowed', transition: 'all 0.15s', fontFamily: 'inherit' }}
                  >
                    {loading ? 'Deleting…' : 'Delete everything'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default function SettingsPage() {
  return (
    <Suspense>
      <SettingsPageInner />
    </Suspense>
  )
}
