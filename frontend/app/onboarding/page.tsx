'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

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

export default function OnboardingPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [workspace, setWorkspace] = useState('')
  const [useCase, setUseCase] = useState('')
  const [launching, setLaunching] = useState(false)

  function handleUseCaseSelect(id: string) {
    setUseCase(id)
    setTimeout(() => setStep(2), 250)
  }

  function handleFinish() {
    setLaunching(true)
    localStorage.setItem('onboarding_complete', '1')
    if (workspace) localStorage.setItem('workspace_name', workspace)
    router.push(getToken() ? '/dashboard' : '/login')
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
