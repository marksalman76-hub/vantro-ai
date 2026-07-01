'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams() ?? new URLSearchParams()
  const justRegistered = searchParams.get('registered') === '1'
  const justVerified = searchParams.get('verified') === '1'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Invalid email or password.')
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
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@company.com" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all" onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'} onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all" onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'} onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'} />
            </div>
            {justRegistered && <p className="text-green-400 text-sm bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-2.5">Account created! Sign in below.</p>}
            {justVerified && <p className="text-green-400 text-sm bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-2.5">Email verified! Sign in to continue.</p>}
            {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
            <button type="submit" disabled={loading} className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60" style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}>{loading ? 'Signing in…' : 'Sign in'}</button>
          </form>
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
