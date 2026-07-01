'use client'

import { Suspense, useState, useEffect, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

type Step = 'credentials' | 'otp'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams() ?? new URLSearchParams()
  const justRegistered = searchParams.get('registered') === '1'
  const justVerified = searchParams.get('verified') === '1'

  const [step, setStep] = useState<Step>('credentials')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resendCooldown, setResendCooldown] = useState(0)
  const codeRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (resendCooldown <= 0) return
    const t = setTimeout(() => setResendCooldown(c => c - 1), 1000)
    return () => clearTimeout(t)
  }, [resendCooldown])

  async function handleCredentials(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/otp/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Invalid email or password.')
        return
      }
      setStep('otp')
      setResendCooldown(60)
      setTimeout(() => codeRef.current?.focus(), 100)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleOTP(e: React.FormEvent) {
    e.preventDefault()
    if (!code.trim() || code.length !== 6) return
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), code: code.trim() }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Invalid or expired code.')
        return
      }
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
      }
      const onboarded = localStorage.getItem('onboarding_complete')
      router.push(onboarded ? '/dashboard' : '/onboarding')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function resend() {
    if (resendCooldown > 0) return
    setError('')
    try {
      await fetch('/api/auth/otp/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      })
      setResendCooldown(60)
    } catch { /* ignore */ }
  }

  const inputStyle = {
    borderColor: 'rgba(255,255,255,0.10)',
  }
  const inputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'
  }
  const inputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.12) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-30" />
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="https://vantro.ai" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
          <p className="text-white/40 text-sm mt-3">Sign in to your workspace</p>
        </div>

        <div className="rounded-2xl p-8" style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
          {step === 'credentials' ? (
            <form onSubmit={handleCredentials} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@company.com"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all"
                  style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all"
                  style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} />
              </div>
              {justRegistered && <p className="text-green-400 text-sm bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-2.5">Account created! Sign in below.</p>}
              {justVerified && <p className="text-green-400 text-sm bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-2.5">Email verified! Sign in to continue.</p>}
              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
              <button type="submit" disabled={loading} className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}>
                {loading ? 'Sending code…' : 'Continue'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleOTP} className="space-y-5">
              <div className="text-center pb-2">
                <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3" style={{ background: 'rgba(255,107,53,0.15)', border: '1px solid rgba(255,107,53,0.30)' }}>
                  <svg className="w-5 h-5" fill="none" stroke="#FF6B35" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="text-white text-sm font-medium">Check your email</p>
                <p className="text-white/40 text-xs mt-1">We sent a 6-digit code to <span className="text-white/70">{email}</span></p>
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Verification code</label>
                <input
                  ref={codeRef}
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  maxLength={6}
                  value={code}
                  onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  autoComplete="one-time-code"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm text-center tracking-[0.4em] font-mono placeholder-white/25 focus:outline-none transition-all"
                  style={inputStyle} onFocus={inputFocus} onBlur={inputBlur}
                  required
                />
              </div>
              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
              <button type="submit" disabled={loading || code.length !== 6} className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}>
                {loading ? 'Verifying…' : 'Sign in'}
              </button>
              <div className="flex items-center justify-between pt-1">
                <button type="button" onClick={() => { setStep('credentials'); setCode(''); setError('') }}
                  className="text-xs text-white/30 hover:text-white/50 transition-colors">← Back</button>
                <button type="button" onClick={resend} disabled={resendCooldown > 0}
                  className="text-xs transition-colors disabled:cursor-not-allowed"
                  style={{ color: resendCooldown > 0 ? 'rgba(255,255,255,0.25)' : '#FF6B35' }}>
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend code'}
                </button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-sm text-white/30">
            Don&apos;t have an account?{' '}
            <a href="https://vantro.ai/#pricing" className="hover:opacity-80 transition-opacity" style={{ color: '#FF6B35' }}>Get started</a>
          </div>
          <div className="mt-4 flex items-center justify-center gap-3 text-xs text-white/20">
            <Link href="/privacy" className="hover:text-white/40 transition-colors">Privacy Policy</Link>
            <span>·</span>
            <Link href="/terms" className="hover:text-white/40 transition-colors">Terms</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  )
}
