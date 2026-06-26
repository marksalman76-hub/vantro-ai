'use client'

// Route: /activate/[token]
// Called by: confirmation email link after Stripe payment
// API: GET /api/auth/activate/{token}
// On success: stores access_token + redirects to /onboarding, or shows success card with /login?verified=1

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AGENTS } from '@/lib/agents'

export default function ActivatePage({ params }: { params: Promise<{ token: string }> }) {
  const router = useRouter()
  const [state, setState] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [lockedAgentIds, setLockedAgentIds] = useState<number[]>([])

  useEffect(() => {
    params.then(({ token }) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai'
      fetch(`${apiUrl}/api/auth/activate/${token}`, { method: 'GET' })
        .then(async r => {
          if (r.ok) {
            const data = await r.json()
            if (data.access_token) {
              // Lock agents permanently
              const pendingAgents = localStorage.getItem('pending_agents') ?? ''
              if (pendingAgents) {
                localStorage.setItem('locked_agents', pendingAgents)
                localStorage.removeItem('pending_agents')
              }
              const pendingPlan = localStorage.getItem('pending_plan') ?? ''
              if (pendingPlan) {
                localStorage.setItem('locked_plan', pendingPlan)
                localStorage.removeItem('pending_plan')
              }
              localStorage.setItem('token', data.access_token)
              router.push('/onboarding')
            } else {
              // Manual verification path — lock agents then show success card
              const pendingAgents = localStorage.getItem('pending_agents') ?? ''
              if (pendingAgents) {
                localStorage.setItem('locked_agents', pendingAgents)
                localStorage.removeItem('pending_agents')
              }
              // Read locked IDs for UI
              const locked = localStorage.getItem('locked_agents') ?? ''
              if (locked) {
                const ids = locked.split(',').map(s => parseInt(s, 10)).filter(n => !isNaN(n))
                setLockedAgentIds(ids)
              }
              setState('success')
            }
          } else {
            setState('error')
          }
        })
        .catch(() => setState('error'))
    })
  }, [params, router])

  const lockedAgents = AGENTS.filter(a => lockedAgentIds.includes(a.id))

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
          {state === 'verifying' && (
            <div className="text-center py-4">
              <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-orange-400 animate-spin mx-auto mb-3" style={{ borderTopColor: '#FF6B35' }} />
              <p className="text-white/40 text-sm">Verifying your link…</p>
            </div>
          )}

          {state === 'success' && (
            <div className="text-center py-4 space-y-5">
              <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto" style={{ background: 'rgba(255,107,53,0.15)', border: '1px solid rgba(255,107,53,0.30)' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF6B35" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div>
                <h2 className="text-white font-bold text-xl mb-1">Email verified!</h2>
                <p className="text-white/50 text-sm">Your account is active. Sign in to continue.</p>
              </div>

              {lockedAgents.length > 0 && (
                <div className="flex flex-col items-center gap-2">
                  <div className="flex items-center">
                    {lockedAgents.map((agent, i) => (
                      <img
                        key={agent.id}
                        src={agent.avatar}
                        alt={agent.name}
                        title={agent.name}
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          border: '2px solid #FF6B35',
                          marginLeft: i === 0 ? 0 : -10,
                          objectFit: 'cover',
                          position: 'relative',
                          zIndex: lockedAgents.length - i,
                        }}
                      />
                    ))}
                  </div>
                  <p className="text-white/60 text-sm">
                    Your {lockedAgents.length} agent{lockedAgents.length !== 1 ? 's' : ''} are locked in and ready.
                  </p>
                </div>
              )}

              <Link
                href="/login?verified=1"
                className="block w-full py-3 text-sm font-semibold text-white rounded-xl text-center transition-opacity hover:opacity-90"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}
              >
                Sign in
              </Link>
            </div>
          )}

          {state === 'error' && (
            <div className="text-center py-4 space-y-4">
              <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto" style={{ background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.20)' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </div>
              <div>
                <h2 className="text-white font-bold text-xl mb-1">Link expired or invalid</h2>
                <p className="text-white/50 text-sm">This activation link is no longer valid. Please return to pricing to get a new one.</p>
              </div>
              <a href="https://vantro.ai/#pricing" className="text-sm hover:opacity-80 transition-opacity block" style={{ color: '#FF6B35' }}>
                Return to pricing →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
