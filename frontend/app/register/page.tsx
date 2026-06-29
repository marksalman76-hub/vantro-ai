'use client'

import { Suspense } from 'react'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { AGENTS } from '@/lib/agents'

function RegisterForm() {
  const router = useRouter()
  const searchParams = useSearchParams() ?? new URLSearchParams()
  const sessionId = searchParams.get('session_id')
  const plan = searchParams.get('plan')
  const agentsParam = searchParams.get('agents') ?? ''
  const agentIds = agentsParam ? agentsParam.split(',').map(Number).filter(Boolean) : []
  const selectedAgents = AGENTS.filter(a => agentIds.includes(a.id))

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [verifying, setVerifying] = useState(false)
  const [showToast, setShowToast] = useState(false)

  useEffect(() => {
    if (!showToast) return
    const id = setTimeout(() => setShowToast(false), 5000)
    return () => clearTimeout(id)
  }, [showToast])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    localStorage.setItem('pending_agents', agentsParam)
    localStorage.setItem('pending_plan', plan ?? '')

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name, email, password,
          ...(sessionId && { session_id: sessionId }),
          ...(plan && { plan }),
          agents: agentIds,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Registration failed. Please try again.')
        return
      }
      if (data.access_token) {
        router.push(`/onboarding?plan=${plan ?? ''}&agents=${agentsParam}`)
      } else {
        setOtpSent(true)
        setShowToast(true)
      }
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleOtpChange(i: number, val: string) {
    if (!/^\d?$/.test(val)) return
    const next = [...otp]
    next[i] = val
    setOtp(next)
    if (val && i < 5) {
      document.getElementById(`otp-${i + 1}`)?.focus()
    }
  }

  function handleOtpKeyDown(i: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Backspace' && !otp[i] && i > 0) {
      document.getElementById(`otp-${i - 1}`)?.focus()
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault()
    const code = otp.join('')
    if (code.length < 6) { setError('Enter the full 6-digit code.'); return }
    setError('')
    setVerifying(true)
    try {
      const res = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp: code }),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Verification failed.'); return }
      localStorage.setItem('pending_agents', agentsParam)
      router.push(`/onboarding?plan=${plan ?? ''}&agents=${agentsParam}`)
    } catch {
      setError('Verification failed. Please try again.')
    } finally {
      setVerifying(false)
    }
  }

  const visibleAgents = selectedAgents.slice(0, 5)
  const extraCount = selectedAgents.length - visibleAgents.length

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.12) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-30" />

      {/* Toast: verification link sent */}
      <div
        style={{
          position: 'fixed',
          bottom: 32,
          left: '50%',
          transform: showToast ? 'translateX(-50%) translateY(0)' : 'translateX(-50%) translateY(120px)',
          opacity: showToast ? 1 : 0,
          transition: 'transform 0.4s cubic-bezier(0.34,1.56,0.64,1), opacity 0.3s ease',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '14px 20px',
          borderRadius: 14,
          background: 'rgba(10,13,20,0.96)',
          border: '1px solid rgba(31,255,214,0.30)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(31,255,214,0.10)',
          whiteSpace: 'nowrap',
          pointerEvents: showToast ? 'auto' : 'none',
        }}
      >
        <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(31,255,214,0.12)', border: '1px solid rgba(31,255,214,0.30)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 7l3.5 3.5L12 3.5" stroke="#1FFFD6" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div>
          <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: '#fff' }}>Verification link sent</p>
          <p style={{ margin: 0, fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 1 }}>Check your inbox at <span style={{ color: '#1FFFD6' }}>{email}</span></p>
        </div>
        <button onClick={() => setShowToast(false)} style={{ marginLeft: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.30)', fontSize: 16, lineHeight: 1, padding: 4 }}>×</button>
      </div>
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="https://vantro.ai" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
          {plan && (
            <div className="inline-flex items-center gap-1.5 mt-3 px-3 py-1 rounded-full text-xs font-semibold" style={{ background: 'rgba(255,107,53,0.1)', border: '1px solid rgba(255,107,53,0.3)', color: '#FF6B35' }}>
              Selected plan: {plan.charAt(0).toUpperCase() + plan.slice(1)}
            </div>
          )}
          <p className="text-white/40 text-sm mt-3">{otpSent ? 'Check your email' : 'Create your workspace'}</p>
        </div>

        {/* Selected agents summary */}
        {selectedAgents.length > 0 && !otpSent && (
          <div
            className="mb-4 rounded-2xl px-5 py-4 flex items-center gap-4"
            style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,107,53,0.18)', backdropFilter: 'blur(20px)' }}
          >
            {/* Avatar stack */}
            <div className="flex items-center" style={{ flexShrink: 0 }}>
              {visibleAgents.map((agent, i) => (
                <div
                  key={agent.id}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    border: '2px solid #FF6B35',
                    overflow: 'hidden',
                    marginLeft: i === 0 ? 0 : -10,
                    position: 'relative',
                    zIndex: visibleAgents.length - i,
                    background: '#1A1F2E',
                    flexShrink: 0,
                  }}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={agent.avatar}
                    alt={agent.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                  />
                </div>
              ))}
              {extraCount > 0 && (
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    border: '2px solid #FF6B35',
                    marginLeft: -10,
                    background: 'rgba(255,107,53,0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 11,
                    fontWeight: 700,
                    color: '#FF6B35',
                    flexShrink: 0,
                    position: 'relative',
                    zIndex: 0,
                  }}
                >
                  +{extraCount}
                </div>
              )}
            </div>

            {/* Info */}
            <div className="min-w-0">
              <p className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-0.5">Your AI Team</p>
              <p className="text-white text-sm font-medium">
                <span style={{ color: '#FF6B35' }}>{selectedAgents.length}</span>
                {' '}agent{selectedAgents.length !== 1 ? 's' : ''}
                {plan && (
                  <>
                    {' · '}
                    <span style={{ color: '#FF6B35' }}>{plan.charAt(0).toUpperCase() + plan.slice(1)}</span>
                    {' plan'}
                  </>
                )}
              </p>
            </div>
          </div>
        )}

        {otpSent ? (
          <div className="rounded-2xl p-8" style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.30)' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="7" width="20" height="14" rx="2" stroke="#FF6B35" strokeWidth="1.8"/>
                  <path d="M16 7V5a4 4 0 0 0-8 0v2" stroke="#FF6B35" strokeWidth="1.8" strokeLinecap="round"/>
                  <circle cx="12" cy="14" r="2" fill="#FF6B35"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white mb-1">Enter your code</h2>
              <p className="text-white/40 text-sm">We sent a 6-digit code to</p>
              <p className="text-sm font-semibold mt-1" style={{ color: '#FF6B35' }}>{email}</p>
            </div>

            <form onSubmit={handleVerify} className="space-y-5">
              <div className="flex justify-center gap-3">
                {otp.map((digit, i) => (
                  <input
                    key={i}
                    id={`otp-${i}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={e => handleOtpChange(i, e.target.value)}
                    onKeyDown={e => handleOtpKeyDown(i, e)}
                    autoFocus={i === 0}
                    className="w-12 h-14 text-center text-xl font-bold text-white rounded-xl focus:outline-none transition-all"
                    style={{
                      background: 'rgba(255,255,255,0.06)',
                      border: digit ? '1.5px solid #FF6B35' : '1.5px solid rgba(255,255,255,0.12)',
                      boxShadow: digit ? '0 0 12px rgba(255,107,53,0.20)' : 'none',
                    }}
                  />
                ))}
              </div>

              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5 text-center">{error}</p>}

              <button
                type="submit"
                disabled={verifying || otp.join('').length < 6}
                className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-40"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}
              >
                {verifying ? 'Verifying…' : 'Verify & continue'}
              </button>

              <p className="text-center text-xs text-white/25">Didn&apos;t get it? Check your spam folder.</p>
            </form>
          </div>
        ) : (
          <div className="rounded-2xl p-8" style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Full Name</label>
                <input type="text" value={name} onChange={e => setName(e.target.value)} required placeholder="Jane Smith" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all" onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'} onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@company.com" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all" onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'} onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Min 8 chars, include a number" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all" onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'} onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'} />
              </div>
              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
              <button type="submit" disabled={loading} className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60" style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}>{loading ? 'Creating account…' : 'Create account'}</button>
            </form>
            <div className="mt-6 text-center text-sm text-white/30">
              Already have an account?{' '}
              <Link href="/login" className="hover:opacity-80 transition-opacity" style={{ color: '#FF6B35' }}>Sign in</Link>
            </div>
            <div className="mt-4 flex items-center justify-center gap-3 text-xs text-white/20">
              <Link href="/privacy" className="hover:text-white/40 transition-colors">Privacy Policy</Link>
              <span>·</span>
              <Link href="/terms" className="hover:text-white/40 transition-colors">Terms</Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function RegisterPage() {
  return <Suspense><RegisterForm /></Suspense>
}
