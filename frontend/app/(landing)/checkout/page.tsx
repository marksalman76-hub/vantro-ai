'use client'

import { Suspense, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { AGENTS, CATEGORY_COLORS } from '@/lib/agents'

const PLAN_PRICES: Record<string, { monthly: number; label: string }> = {
  starter:  { monthly: 99,  label: 'Starter' },
  growth:   { monthly: 279, label: 'Growth' },
  business: { monthly: 399, label: 'Business' },
}

function CheckoutContent() {
  const router = useRouter()
  const searchParams = useSearchParams() ?? new URLSearchParams()
  const plan = searchParams.get('plan') ?? 'starter'
  const agentsParam = searchParams.get('agents') ?? ''
  const mock = searchParams.get('mock') === '1'
  const agentIds = agentsParam ? agentsParam.split(',').map(Number).filter(Boolean) : []
  const selectedAgents = AGENTS.filter(a => agentIds.includes(a.id))
  const planInfo = PLAN_PRICES[plan] ?? PLAN_PRICES.starter

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleStripeRedirect() {
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan, agents: agentIds }),
      })
      const data = await res.json()
      if (!res.ok || !data.url) {
        setError(data.detail || 'Unable to start payment. Please try again.')
        setLoading(false)
        return
      }
      window.location.href = data.url
    } catch {
      setError('Payment service unavailable. Please try again.')
      setLoading(false)
    }
  }

  const visibleAgents = selectedAgents.slice(0, 4)
  const extraCount = selectedAgents.length - visibleAgents.length

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-16"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.10) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-20" />

      <div className="relative w-full max-w-4xl">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
          <p className="text-white/40 text-sm mt-2">Secure checkout</p>
        </div>

        <div className="grid gap-6" style={{ gridTemplateColumns: '1fr minmax(0,420px)' }}>

          {/* ── LEFT: Order summary ── */}
          <div className="space-y-5">
            <div className="rounded-2xl p-6" style={{ background: 'rgba(26,31,46,0.85)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
              <p className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'rgba(255,255,255,0.35)' }}>Order summary</p>

              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-white font-bold text-lg">{planInfo.label} Plan</p>
                  <p className="text-white/40 text-sm">Billed monthly · Cancel anytime</p>
                </div>
                <div className="text-right">
                  <p className="text-white font-black text-2xl">${planInfo.monthly}</p>
                  <p className="text-white/30 text-xs">/month</p>
                </div>
              </div>

              <div className="h-px my-4" style={{ background: 'rgba(255,255,255,0.06)' }} />

              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">AI Agents</span>
                <span className="text-white font-semibold">{selectedAgents.length} selected</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-white/50">Billing cycle</span>
                <span className="text-white font-semibold">Monthly</span>
              </div>

              <div className="h-px my-4" style={{ background: 'rgba(255,255,255,0.06)' }} />

              <div className="flex items-center justify-between">
                <span className="text-white font-bold">Total today</span>
                <span className="font-black text-xl" style={{ color: '#FF6B35' }}>${planInfo.monthly}/mo</span>
              </div>
            </div>

            {/* Selected agents */}
            {selectedAgents.length > 0 && (
              <div className="rounded-2xl p-6" style={{ background: 'rgba(26,31,46,0.85)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
                <p className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'rgba(255,255,255,0.35)' }}>Your AI Team</p>

                <div className="flex items-center mb-4">
                  {visibleAgents.map((agent, i) => (
                    <div key={agent.id} style={{ width: 40, height: 40, borderRadius: '50%', border: '2px solid #FF6B35', overflow: 'hidden', marginLeft: i === 0 ? 0 : -10, position: 'relative', zIndex: visibleAgents.length - i, flexShrink: 0, background: '#1A1F2E' }}>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={agent.avatar} alt={agent.name} style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                    </div>
                  ))}
                  {extraCount > 0 && (
                    <div style={{ width: 40, height: 40, borderRadius: '50%', border: '2px solid #FF6B35', marginLeft: -10, background: 'rgba(255,107,53,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: '#FF6B35', flexShrink: 0 }}>
                      +{extraCount}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {selectedAgents.map(agent => (
                    <div key={agent.id} className="flex items-center gap-2.5 rounded-xl px-3 py-2.5" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div className="rounded-full flex-shrink-0" style={{ width: 6, height: 6, background: CATEGORY_COLORS[agent.category] }} />
                      <div className="min-w-0">
                        <p className="text-white font-semibold truncate" style={{ fontSize: 12 }}>{agent.name}</p>
                        <p className="text-white/35 truncate" style={{ fontSize: 10 }}>{agent.role}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 flex justify-center">
                  <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold" style={{ background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.25)', color: '#FF6B35' }}>
                    <svg width="10" height="12" viewBox="0 0 10 12" fill="none">
                      <rect x="1" y="5" width="8" height="7" rx="1.5" stroke="#FF6B35" strokeWidth="1.2" />
                      <path d="M3 5V3.5a2 2 0 0 1 4 0V5" stroke="#FF6B35" strokeWidth="1.2" strokeLinecap="round" />
                    </svg>
                    Locked after activation
                  </span>
                </div>
              </div>
            )}

            {/* Trust badges */}
            <div className="flex items-center gap-5 flex-wrap">
              {['256-bit SSL', 'Cancel anytime', 'No setup fees'].map(badge => (
                <div key={badge} className="flex items-center gap-1.5">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 1L1.5 3.5V7c0 3 2.5 5.5 5.5 5.5S12.5 10 12.5 7V3.5L7 1z" stroke="#1FFFD6" strokeWidth="1.2" strokeLinejoin="round" />
                    <path d="M4.5 7l2 2 3-3" stroke="#1FFFD6" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span className="text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>{badge}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── RIGHT: Stripe payment ── */}
          <div className="rounded-2xl p-6" style={{ background: 'rgba(26,31,46,0.85)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
            <p className="text-xs font-semibold uppercase tracking-widest mb-6" style={{ color: 'rgba(255,255,255,0.35)' }}>Payment</p>

            {/* Stripe branding block */}
            <div className="rounded-xl p-5 mb-6 text-center" style={{ background: 'rgba(99,91,255,0.08)', border: '1px solid rgba(99,91,255,0.20)' }}>
              {/* Stripe wordmark SVG */}
              <svg viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-3" style={{ width: 60, height: 25 }} aria-label="Stripe">
                <path d="M3.63 9.41c0-.78.64-1.08 1.7-1.08 1.52 0 3.44.46 4.96 1.28V5.35A13.15 13.15 0 0 0 5.33 4.5C2.13 4.5 0 6.18 0 9.6c0 5.27 7.26 4.43 7.26 6.7 0 .92-.8 1.22-1.92 1.22-1.66 0-3.78-.68-5.46-1.6v4.3A13.87 13.87 0 0 0 5.34 21.5c3.28 0 5.54-1.62 5.54-5.08C10.88 10.6 3.63 11.6 3.63 9.41zm13.25-4.15L13.15 6l-.06 11.85h4.7l.03-11.85-1.04-0.54zm5.93 0h-3.3l5.93 16.1H28.7l5.93-16.1H31.3l-3.75 11.22-4.74-11.22zm11.03 0v16.1h4.68V5.26h-4.68zm10.6-.5c-1.66 0-2.74.78-3.34 1.32l-.22-1.06H37.3v21.67l4.7-1V17.4c.62.45 1.54 1.1 3.06 1.1 3.08 0 5.88-2.47 5.88-7.9 0-4.98-2.82-7.24-5.53-7.24zm-.97 11.17c-1.02 0-1.62-.36-2.04-.8l-.03-6.35c.45-.5 1.07-.84 2.07-.84 1.58 0 2.67 1.77 2.67 3.98 0 2.26-1.06 4.01-2.67 4.01z" fill="rgba(255,255,255,0.60)"/>
              </svg>
              <p className="text-xs" style={{ color: 'rgba(255,255,255,0.40)' }}>
                You&apos;ll be taken to Stripe&apos;s secure checkout. Card details, 3D Secure verification, and payment are all handled by Stripe.
              </p>
            </div>

            {/* What's included */}
            <div className="space-y-3 mb-6">
              {[
                { icon: '🔒', text: 'Encrypted card entry on Stripe' },
                { icon: '✓', text: '6-digit SMS/email verification (3D Secure)' },
                { icon: '↩', text: 'Returns here after payment' },
              ].map(item => (
                <div key={item.text} className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs" style={{ background: 'rgba(31,255,214,0.10)', border: '1px solid rgba(31,255,214,0.20)', color: '#1FFFD6' }}>{item.icon}</div>
                  <span className="text-sm" style={{ color: 'rgba(255,255,255,0.55)' }}>{item.text}</span>
                </div>
              ))}
            </div>

            {error && (
              <p className="text-sm rounded-lg px-4 py-2.5 mb-4" style={{ color: '#f87171', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.20)' }}>{error}</p>
            )}

            {mock && (
              <div className="rounded-lg px-3 py-2 mb-3 text-center text-xs font-semibold" style={{ background: 'rgba(255,214,0,0.08)', border: '1px solid rgba(255,214,0,0.25)', color: '#FFD700' }}>
                TEST MODE — payment skipped
              </div>
            )}

            <button
              onClick={mock ? () => router.push(`/register?plan=${plan}&agents=${agentsParam}`) : handleStripeRedirect}
              disabled={loading}
              className="w-full py-4 text-sm font-bold text-white rounded-xl transition-opacity disabled:opacity-60 flex items-center justify-center gap-2"
              style={mock
                ? { background: 'linear-gradient(135deg,#FFD700,#CC9900)', boxShadow: '0 0 20px rgba(255,214,0,0.25)' }
                : { background: 'linear-gradient(135deg,#635BFF,#4F46E5)', boxShadow: '0 0 24px rgba(99,91,255,0.40)' }
              }
            >
              {loading ? (
                <>
                  <svg className="animate-spin" width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
                    <path d="M8 2a6 6 0 0 1 6 6" stroke="white" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  Connecting to Stripe…
                </>
              ) : mock ? (
                'Skip payment (test mode)'
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="1" y="3" width="12" height="9" rx="1.5" stroke="white" strokeWidth="1.2" />
                    <path d="M1 6h12" stroke="white" strokeWidth="1.2" />
                  </svg>
                  Pay ${planInfo.monthly}/mo with Stripe
                </>
              )}
            </button>

            <div className="text-center mt-4">
              <Link href={`/pricing?plan=${plan}`} className="text-xs transition-colors" style={{ color: 'rgba(255,255,255,0.30)' }}>
                ← Back to agent selection
              </Link>
            </div>

            <div className="mt-6 pt-5" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <div className="flex items-center justify-center gap-2">
                <svg width="12" height="14" viewBox="0 0 12 14" fill="none">
                  <path d="M6 1L1 3.5V7c0 3 2 5.5 5 5.5S11 10 11 7V3.5L6 1z" stroke="rgba(255,255,255,0.25)" strokeWidth="1.2" strokeLinejoin="round" />
                </svg>
                <span className="text-xs" style={{ color: 'rgba(255,255,255,0.25)' }}>Payments secured by Stripe · 256-bit SSL · PCI compliant</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CheckoutPage() {
  return (
    <Suspense>
      <CheckoutContent />
    </Suspense>
  )
}
