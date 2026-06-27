'use client'

import { useState, useEffect, useCallback } from 'react'

interface Charge {
  id: string
  amount: number
  currency: string
  status: string
  description: string | null
  email: string | null
  created: number
}

interface Customer {
  id: string
  email: string | null
  created: number
}

interface Stats {
  balance: { available: number; pending: number }
  mrr: number
  activeSubscriptions: number
  recentCharges: Charge[]
  recentCustomers: Customer[]
}

function fmt(cents: number) {
  return '$' + (cents / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

function fmtDate(unix: number) {
  return new Date(unix * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const QUICK_LINKS = [
  { label: 'Stripe Dashboard', url: 'https://dashboard.stripe.com', color: '#635bff' },
  { label: 'Resend Emails', url: 'https://resend.com/emails', color: '#1FFFD6' },
  { label: 'Vercel Deploy', url: 'https://vercel.com/marksalman76-5799s-projects/vantro-ai', color: '#ffffff' },
  { label: 'GitHub Repo', url: 'https://github.com/marksalman76-hub/vantro-ai', color: '#f0f6fc' },
]

export default function AdminPage() {
  const [authed, setAuthed] = useState<boolean | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [password, setPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [loading, setLoading] = useState(false)
  const [statsError, setStatsError] = useState('')

  const loadStats = useCallback(async () => {
    const res = await fetch('/api/admin/stats')
    if (res.status === 401) { setAuthed(false); return }
    if (!res.ok) { setStatsError('Failed to load Stripe stats — check STRIPE_SECRET_KEY'); setAuthed(true); return }
    const data = await res.json()
    setStats(data)
    setAuthed(true)
  }, [])

  useEffect(() => { loadStats() }, [loadStats])

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setLoginError('')
    const res = await fetch('/api/admin/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (res.ok) {
      setPassword('')
      await loadStats()
    } else {
      setLoginError('Invalid password')
    }
    setLoading(false)
  }

  async function handleLogout() {
    await fetch('/api/admin/auth', { method: 'DELETE' })
    setAuthed(false)
    setStats(null)
  }

  if (authed === null) {
    return (
      <div style={{ minHeight: '100vh', background: '#0A0D14', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#1FFFD6' }} />
      </div>
    )
  }

  if (!authed) {
    return (
      <div style={{ minHeight: '100vh', background: '#0A0D14', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui' }}>
        <form onSubmit={handleLogin} style={{ width: 360, padding: '2rem', background: '#12151E', borderRadius: 16, border: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: 11, letterSpacing: '0.15em', color: '#1FFFD6', textTransform: 'uppercase', marginBottom: 8 }}>Vantro Admin</div>
            <h1 style={{ fontSize: 22, fontWeight: 600, color: '#fff', margin: 0 }}>Sign in</h1>
          </div>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Admin password"
            required
            autoFocus
            style={{ width: '100%', boxSizing: 'border-box', padding: '0.75rem 1rem', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', marginBottom: 12 }}
          />
          {loginError && <p style={{ color: '#ff6b6b', fontSize: 13, margin: '0 0 12px' }}>{loginError}</p>}
          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: '0.75rem', background: '#1FFFD6', color: '#0A0D14', border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0A0D14', color: '#fff', fontFamily: 'system-ui', padding: '2rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <div style={{ fontSize: 11, letterSpacing: '0.15em', color: '#1FFFD6', textTransform: 'uppercase', marginBottom: 4 }}>Vantro.ai</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>Admin Portal</h1>
          </div>
          <button onClick={handleLogout} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 8, color: '#aaa', fontSize: 13, cursor: 'pointer' }}>
            Sign out
          </button>
        </div>

        {statsError && (
          <div style={{ padding: '1rem', background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.3)', borderRadius: 8, color: '#ff6b6b', marginBottom: '1.5rem', fontSize: 14 }}>
            {statsError}
          </div>
        )}

        {/* Revenue metrics */}
        {stats && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              {[
                { label: 'MRR', value: fmt(stats.mrr), sub: 'monthly recurring revenue' },
                { label: 'Active Plans', value: String(stats.activeSubscriptions), sub: 'live subscriptions' },
                { label: 'Available', value: fmt(stats.balance.available), sub: 'Stripe balance' },
                { label: 'Pending', value: fmt(stats.balance.pending), sub: 'processing' },
              ].map(m => (
                <div key={m.label} style={{ background: '#12151E', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '1.25rem' }}>
                  <div style={{ fontSize: 11, color: '#555', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>{m.label}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: '#1FFFD6', marginBottom: 2 }}>{m.value}</div>
                  <div style={{ fontSize: 12, color: '#444' }}>{m.sub}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
              {/* Recent charges */}
              <div style={{ background: '#12151E', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '1.25rem' }}>
                <h2 style={{ fontSize: 13, fontWeight: 600, color: '#888', margin: '0 0 1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Recent Charges</h2>
                {stats.recentCharges.length === 0
                  ? <p style={{ color: '#444', fontSize: 13 }}>No charges yet</p>
                  : stats.recentCharges.map(c => (
                    <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <div>
                        <div style={{ fontSize: 13, color: '#ddd' }}>{c.email || 'unknown'}</div>
                        <div style={{ fontSize: 11, color: '#444' }}>{fmtDate(c.created)}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 14, fontWeight: 600, color: c.status === 'succeeded' ? '#1FFFD6' : '#ff6b6b' }}>{fmt(c.amount)}</div>
                        <div style={{ fontSize: 10, color: '#444', textTransform: 'uppercase' }}>{c.status}</div>
                      </div>
                    </div>
                  ))
                }
              </div>

              {/* Recent customers */}
              <div style={{ background: '#12151E', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '1.25rem' }}>
                <h2 style={{ fontSize: 13, fontWeight: 600, color: '#888', margin: '0 0 1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Recent Customers</h2>
                {stats.recentCustomers.length === 0
                  ? <p style={{ color: '#444', fontSize: 13 }}>No customers yet</p>
                  : stats.recentCustomers.map(c => (
                    <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <div style={{ fontSize: 13, color: '#ddd' }}>{c.email || c.id}</div>
                      <div style={{ fontSize: 11, color: '#444' }}>{fmtDate(c.created)}</div>
                    </div>
                  ))
                }
              </div>
            </div>
          </>
        )}

        {/* Quick links */}
        <div style={{ background: '#12151E', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '1.25rem', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#888', margin: '0 0 1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Admin Tools</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            {QUICK_LINKS.map(link => (
              <a
                key={link.label}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ padding: '0.6rem 1.2rem', background: 'rgba(255,255,255,0.04)', border: `1px solid ${link.color}25`, borderRadius: 8, color: link.color, fontSize: 13, fontWeight: 500, textDecoration: 'none' }}
              >
                {link.label} ↗
              </a>
            ))}
          </div>
        </div>

        {/* Pending actions */}
        <div style={{ background: '#12151E', border: '1px solid rgba(255,165,0,0.2)', borderRadius: 12, padding: '1.25rem' }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#888', margin: '0 0 0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Pending Actions</h2>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#888', fontSize: 13, lineHeight: 2.2 }}>
            <li>Rotate <code style={{ color: '#1FFFD6', background: 'rgba(31,255,214,0.08)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>ANTHROPIC_API_KEY</code> in Vercel env vars</li>
            <li>Rotate <code style={{ color: '#1FFFD6', background: 'rgba(31,255,214,0.08)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>RUNWAY_API_KEY</code> and <code style={{ color: '#1FFFD6', background: 'rgba(31,255,214,0.08)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>ELEVENLABS_API_KEY</code></li>
            <li>Set <code style={{ color: '#ffa500', background: 'rgba(255,165,0,0.08)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>ADMIN_PASSWORD</code> in Vercel env vars → redeploy</li>
            <li>Set <code style={{ color: '#ffa500', background: 'rgba(255,165,0,0.08)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>STRIPE_SECRET_KEY</code> in Vercel env vars if not done</li>
          </ul>
        </div>

      </div>
    </div>
  )
}
