'use client'

import { Suspense, useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { AGENTS, CATEGORY_COLORS } from '@/lib/agents'

const STEPS = [
  { title: 'Name your workspace', subtitle: 'This is how your team will identify your account.' },
  { title: 'What brings you to Vantro?', subtitle: 'Help us tailor your agent setup.' },
  { title: "You're all set", subtitle: 'Your AI agents are ready to deploy.' },
]

const USE_CASES = [
  { id: 'ecommerce', label: 'E-commerce & Retail' },
  { id: 'marketing', label: 'Marketing & Ads' },
  { id: 'support', label: 'Customer Support' },
  { id: 'content', label: 'Content Creation' },
  { id: 'analytics', label: 'Data & Analytics' },
  { id: 'other', label: 'Something else' },
]

function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('token') : null }

function OnboardingContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const plan = searchParams.get('plan')

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if (!token) router.push('/login')
  }, [router])

  const [step, setStep] = useState(0)
  const [workspace, setWorkspace] = useState('')
  const [useCase, setUseCase] = useState('')
  const [launching, setLaunching] = useState(false)
  const [lockedAgentIds, setLockedAgentIds] = useState<number[]>([])

  useEffect(() => {
    const stored = localStorage.getItem('locked_agents') ?? ''
    const ids = stored ? stored.split(',').map(Number).filter(Boolean) : []
    setLockedAgentIds(ids)
  }, [])

  const lockedAgents = AGENTS.filter(a => lockedAgentIds.includes(a.id))

  function handleUseCaseSelect(id: string) {
    setUseCase(id)
    setTimeout(() => setStep(2), 250)
  }

  function handleFinish() {
    setLaunching(true)
    localStorage.setItem('onboarding_complete', '1')
    if (workspace) localStorage.setItem('workspace_name', workspace)
    if (plan) localStorage.setItem('plan', plan)
    router.push('/dashboard')
  }

  const current = STEPS[step]

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.10) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-20" />

      {/* Progress */}
      <div className="fixed top-8 left-0 right-0 flex justify-center gap-2">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className="rounded-full transition-all duration-300"
            style={{
              width: i === step ? '1.5rem' : '0.5rem',
              height: '0.5rem',
              background: i <= step ? '#FF6B35' : 'rgba(255,255,255,0.15)',
            }}
          />
        ))}
      </div>

      <div className="relative w-full max-w-lg">
        <div className="text-center mb-10">
          <Link href="https://vantro.ai" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
        </div>

        <div className="rounded-2xl p-8" style={{ background: 'rgba(26,31,46,0.85)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white mb-2">{current.title}</h1>
            <p className="text-white/40 text-sm">{current.subtitle}</p>
          </div>

          {step === 0 && (
            <div className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-widest">Workspace name</label>
                <input
                  type="text"
                  value={workspace}
                  onChange={e => setWorkspace(e.target.value)}
                  placeholder="Acme Corp"
                  autoFocus
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-3 text-white text-sm placeholder-white/25 focus:outline-none transition-all"
                  onFocus={e => e.currentTarget.style.borderColor = 'rgba(255,107,53,0.60)'}
                  onBlur={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)'}
                  onKeyDown={e => { if (e.key === 'Enter' && workspace.trim()) setStep(1) }}
                />
              </div>
              <button
                disabled={!workspace.trim()}
                onClick={() => setStep(1)}
                className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-40"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}
              >
                Continue
              </button>
            </div>
          )}

          {step === 1 && (
            <div className="grid grid-cols-2 gap-3">
              {USE_CASES.map(uc => (
                <button
                  key={uc.id}
                  onClick={() => handleUseCaseSelect(uc.id)}
                  className="rounded-xl px-4 py-4 text-left transition-all"
                  style={{
                    background: useCase === uc.id ? 'rgba(255,107,53,0.15)' : 'rgba(255,255,255,0.04)',
                    border: useCase === uc.id ? '1px solid rgba(255,107,53,0.50)' : '1px solid rgba(255,255,255,0.08)',
                  }}
                  onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.07)' }}
                  onMouseLeave={e => { if (useCase !== uc.id) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.04)' }}
                >
                  <div className="text-white text-sm font-medium">{uc.label}</div>
                </button>
              ))}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              {plan && (
                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.40)' }}>
                  Plan: <span className="text-white/70 font-medium capitalize">{plan}</span> · <span style={{ color: '#FF6B35' }}>Active</span>
                </p>
              )}

              {lockedAgents.length > 0 ? (
                <div className="space-y-4">
                  <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'rgba(255,255,255,0.35)' }}>
                    Your AI Team
                  </p>
                  <div className="grid grid-cols-2 gap-3">
                    {lockedAgents.map(agent => {
                      const color = CATEGORY_COLORS[agent.category]
                      return (
                        <div
                          key={agent.id}
                          className="rounded-xl p-3 flex items-center gap-3"
                          style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                        >
                          <img
                            src={agent.avatar}
                            alt={agent.name}
                            width={40}
                            height={40}
                            className="rounded-full flex-shrink-0 object-cover"
                            style={{ border: `1.5px solid ${color}`, width: 40, height: 40 }}
                          />
                          <div className="min-w-0">
                            <div className="flex items-center gap-1.5 mb-0.5">
                              <div
                                className="rounded-full flex-shrink-0"
                                style={{ width: 6, height: 6, background: color }}
                              />
                              <span className="text-white font-bold truncate" style={{ fontSize: 13 }}>
                                {agent.name}
                              </span>
                            </div>
                            <p className="truncate" style={{ fontSize: 11, color: 'rgba(255,255,255,0.40)' }}>
                              {agent.role}
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <div className="flex justify-center">
                    <span
                      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold"
                      style={{ background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.25)', color: '#FF6B35' }}
                    >
                      <svg width="10" height="12" viewBox="0 0 10 12" fill="none" aria-hidden="true">
                        <rect x="1" y="5" width="8" height="7" rx="1.5" stroke="#FF6B35" strokeWidth="1.2"/>
                        <path d="M3 5V3.5a2 2 0 0 1 4 0V5" stroke="#FF6B35" strokeWidth="1.2" strokeLinecap="round"/>
                      </svg>
                      Locked · Cannot be changed
                    </span>
                  </div>
                </div>
              ) : (
                <div className="rounded-xl p-5 space-y-3" style={{ background: 'rgba(255,107,53,0.08)', border: '1px solid rgba(255,107,53,0.20)' }}>
                  {['22 AI agents pre-configured', 'Multi-channel integrations ready', 'Analytics dashboard live'].map(item => (
                    <div key={item} className="flex items-center gap-3">
                      <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(255,107,53,0.20)', border: '1px solid rgba(255,107,53,0.40)' }}>
                        <svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4l2.5 2.5L9 1" stroke="#FF6B35" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                      </div>
                      <span className="text-white/70 text-sm">{item}</span>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={handleFinish}
                disabled={launching}
                className="w-full py-3 text-sm font-semibold text-white rounded-xl transition-opacity disabled:opacity-60"
                style={{ background: 'linear-gradient(135deg,#FF6B35,#CC4A18)', boxShadow: '0 0 20px rgba(255,107,53,0.30)' }}
              >
                {launching ? 'Launching…' : 'Launch my workspace'}
              </button>
            </div>
          )}
        </div>

        <p className="text-center text-white/20 text-xs mt-6">Step {step + 1} of {STEPS.length}</p>
      </div>
    </div>
  )
}

export default function OnboardingPage() {
  return (
    <Suspense>
      <OnboardingContent />
    </Suspense>
  )
}
