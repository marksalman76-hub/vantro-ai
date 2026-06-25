'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai'
      const res = await fetch(`${apiUrl}/api/auth/login`, {
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
      router.push('/dashboard')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(124,58,237,0.18) 0%, transparent 60%), #070D1F' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-40" />
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="https://vantro.ai" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#7C3AED,#3B82F6)', boxShadow: '0 0 20px rgba(124,58,237,0.45)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span className="text-violet-400">.ai</span></span>
          </Link>
          <p className="text-white/40 text-sm mt-3">Sign in to your workspace</p>
        </div>
        <div className="rounded-2xl p-8" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@company.com" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 transition-all" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 transition-all" />
            </div>
            {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-sm disabled:opacity-60">{loading ? 'Signing in…' : 'Sign in'}</button>
          </form>
          <div className="mt-6 text-center text-sm text-white/30">
            Don&apos;t have an account?{' '}
            <Link href="https://vantro.ai/#pricing" className="text-violet-400 hover:text-violet-300 transition-colors">Get started free</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
