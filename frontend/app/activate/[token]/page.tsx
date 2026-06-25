'use client'

// Route: /activate/[token]
// Called by: confirmation email link after Stripe payment
// API: GET /api/auth/activate/{token} (verify), POST /api/auth/reset-password {token, new_password}
// On success: stores access_token, redirects to /onboarding

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function ActivatePage({ params }: { params: Promise<{ token: string }> }) {
  const router = useRouter()
  const [token, setToken] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(true)
  const [tokenValid, setTokenValid] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    params.then(({ token: t }) => {
      setToken(t)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai'
      fetch(`${apiUrl}/api/auth/activate/${t}`, { method: 'GET' })
        .then(r => { setTokenValid(r.ok); setVerifying(false) })
        .catch(() => { setTokenValid(false); setVerifying(false) })
    })
  }, [params])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) { setError('Passwords do not match.'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setError('')
    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai'
      const res = await fetch(`${apiUrl}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Activation failed. The link may have expired.'); return }
      if (data.access_token) localStorage.setItem('token', data.access_token)
      router.push('/onboarding')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.10) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-30" />
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="https://vantro.ai" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
          <p className="text-white/40 text-sm mt-3">Activate your account</p>
        </div>

        <div className="rounded-2xl p-8" style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
          {verifying && (
            <div className="text-center py-4">
              <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-orange-400 animate-spin mx-auto mb-3" style={{ borderTopColor: '#FF6B35' }} />
              <p className="text-white/40 text-sm">Verifying your link…</p>
            </div>
          )}

          {!verifying && !tokenValid && (
            <div className="text-center py-4 space-y-4">
              <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                This activation link is invalid or has expired.
              </p>
              <a href="https://vantro.ai/#pricing" className="text-sm hover:opacity-80 transition-opacity block" style={{ color: '#FF6B35' }}>
                Return to pricing →
              </a>
            </div>
          )}

          {!verifying && tokenValid && (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Set your password</label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoFocus
                  placeholder="Min 8 chars, include a number"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all"
                  onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'}
                  onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Confirm password</label>
                <input
                  type="password"
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all"
                  onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'}
                  onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'}
                />
              </div>
              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2.5">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}
              >
                {loading ? 'Activating…' : 'Activate account'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
