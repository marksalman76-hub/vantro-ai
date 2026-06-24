import { useState, useEffect } from 'react'
import { useLocation } from 'wouter'

// ─── TYPES ────────────────────────────────────────────────────────────────────

type Tone = 'Fun' | 'Professional' | 'Bold'

// ─── DESIGN TOKENS ────────────────────────────────────────────────────────────

const BLUE_ACTIVE  = 'oklch(0.60 0.18 250)'
const GREEN_DONE   = 'oklch(0.60 0.22 145)'
const PENDING_BG   = 'oklch(0.25 0 0)'

const inputStyle: React.CSSProperties = {
  background: 'oklch(1 0 0 / 0.06)',
  border: '1px solid oklch(1 0 0 / 0.12)',
  borderRadius: '0.625rem',
  padding: '0.75rem 1rem',
  color: 'oklch(0.97 0 0)',
  fontFamily: 'Inter, sans-serif',
  width: '100%',
  fontSize: '0.875rem',
  outline: 'none',
  boxSizing: 'border-box' as const,
}

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  appearance: 'none' as const,
  WebkitAppearance: 'none' as const,
  cursor: 'pointer',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23888' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 1rem center',
  paddingRight: '2.5rem',
}

const primaryButtonStyle: React.CSSProperties = {
  background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
  color: 'oklch(0.98 0 0)',
  border: 'none',
  borderRadius: '9999px',
  padding: '0.75rem 2rem',
  fontWeight: 600,
  cursor: 'pointer',
  width: '100%',
  fontSize: '1rem',
  fontFamily: 'Inter, sans-serif',
}

const skipButtonStyle: React.CSSProperties = {
  background: 'none',
  border: '1px solid oklch(1 0 0 / 0.12)',
  borderRadius: '9999px',
  padding: '0.75rem 1.5rem',
  color: 'oklch(0.55 0 0)',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontFamily: 'Inter, sans-serif',
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  color: 'oklch(0.65 0 0)',
  marginBottom: '0.375rem',
  fontFamily: 'Inter, sans-serif',
}

// ─── STEP INDICATOR ───────────────────────────────────────────────────────────

const STEP_LABELS = ['Welcome', 'Brand setup', 'Run agent', 'Connect tools']

function StepIndicator({ current }: { current: number }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 0,
        marginBottom: '3rem',
      }}
    >
      {STEP_LABELS.map((label, i) => {
        const step = i + 1
        const isDone    = step < current
        const isActive  = step === current
        const isPending = step > current

        const circleBg = isDone ? GREEN_DONE : isActive ? BLUE_ACTIVE : PENDING_BG
        const circleColor = isPending ? 'oklch(0.45 0 0)' : 'oklch(0.98 0 0)'

        return (
          <div key={step} style={{ display: 'flex', alignItems: 'center', flex: step < 4 ? 1 : 'none' }}>
            {/* Circle + label */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.375rem' }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: circleBg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  color: circleColor,
                  flexShrink: 0,
                  transition: 'background 0.3s ease',
                }}
              >
                {isDone ? '✓' : step}
              </div>
              <span
                style={{
                  fontSize: '0.6875rem',
                  color: isActive ? 'oklch(0.85 0 0)' : 'oklch(0.45 0 0)',
                  whiteSpace: 'nowrap',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: isActive ? 500 : 400,
                }}
              >
                {label}
              </span>
            </div>

            {/* Connector line */}
            {step < 4 && (
              <div
                style={{
                  flex: 1,
                  height: 1,
                  background: isDone ? GREEN_DONE : 'oklch(1 0 0 / 0.10)',
                  margin: '0 0.5rem',
                  marginBottom: '1.2rem',
                  transition: 'background 0.3s ease',
                }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── NAVBAR ───────────────────────────────────────────────────────────────────

function OnboardingNav({ onSkip }: { onSkip: () => void }) {
  return (
    <nav
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1rem 1.5rem',
        background: 'oklch(0.14 0 0 / 0.92)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid oklch(1 0 0 / 0.07)',
      }}
    >
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <img
          src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png"
          alt="Vantro"
          style={{ width: 24, height: 24, objectFit: 'contain' }}
        />
        <span
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: '0.9375rem',
            color: 'oklch(0.97 0 0)',
            letterSpacing: '0.03em',
          }}
        >
          VANTRO.ai
        </span>
      </div>

      {/* Skip setup */}
      <button onClick={onSkip} style={skipButtonStyle}>
        Skip setup
      </button>
    </nav>
  )
}

// ─── STEP 1 — WELCOME ─────────────────────────────────────────────────────────

function Step1({ onNext }: { onNext: () => void }) {
  const planName = localStorage.getItem('activated_plan')

  return (
    <div>
      {planName && (
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.375rem',
            background: 'oklch(0.60 0.18 250 / 0.15)',
            border: '1px solid oklch(0.60 0.18 250 / 0.35)',
            borderRadius: '9999px',
            padding: '0.3rem 0.875rem',
            fontSize: '0.8125rem',
            color: 'oklch(0.80 0.12 250)',
            fontFamily: 'Inter, sans-serif',
            marginBottom: '1.5rem',
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'oklch(0.60 0.18 250)', display: 'inline-block' }} />
          {planName} plan activated
        </div>
      )}

      <h1
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 'clamp(2rem, 4vw, 2.75rem)',
          fontWeight: 700,
          color: 'oklch(0.97 0 0)',
          letterSpacing: '-0.025em',
          margin: '0 0 1rem',
          lineHeight: 1.1,
        }}
      >
        Your agents are ready.
      </h1>

      <p
        style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: '1rem',
          color: 'oklch(0.65 0 0)',
          lineHeight: 1.6,
          margin: '0 0 2.5rem',
        }}
      >
        Let's get your workspace set up in 4 quick steps.
      </p>

      <button onClick={onNext} style={primaryButtonStyle}>
        Get started →
      </button>
    </div>
  )
}

// ─── STEP 2 — BRAND SETUP ─────────────────────────────────────────────────────

const INDUSTRIES = [
  'E-commerce / Retail',
  'SaaS / Tech',
  'Health & Wellness',
  'Finance',
  'Real Estate',
  'Agency / Consulting',
  'Education',
  'Other',
]

const TONES: Tone[] = ['Fun', 'Professional', 'Bold']

function Step2({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) {
  const [businessName, setBusinessName] = useState('')
  const [industry, setIndustry] = useState('')
  const [targetAudience, setTargetAudience] = useState('')
  const [tone, setTone] = useState<Tone>('Professional')
  const [loading, setLoading] = useState(false)
  const [warning, setWarning] = useState('')

  async function handleSave() {
    if (!businessName.trim()) return
    setLoading(true)
    setWarning('')
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('https://api.vantro.ai/api/workspace/brand', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          business_name: businessName.trim(),
          industry,
          target_audience: targetAudience.trim(),
          preferred_tone: tone,
        }),
      })
      if (!res.ok) {
        setWarning('Brand info could not be saved — you can update it later in settings.')
      }
    } catch {
      setWarning('Brand info could not be saved — you can update it later in settings.')
    } finally {
      setLoading(false)
      onNext()
    }
  }

  return (
    <div>
      <h1
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 'clamp(1.75rem, 3.5vw, 2.25rem)',
          fontWeight: 700,
          color: 'oklch(0.97 0 0)',
          letterSpacing: '-0.025em',
          margin: '0 0 0.5rem',
        }}
      >
        Set up your brand
      </h1>
      <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.9375rem', color: 'oklch(0.60 0 0)', margin: '0 0 2rem', lineHeight: 1.5 }}>
        Agents use this context to tailor every output to your business.
      </p>

      {warning && (
        <div
          style={{
            background: 'oklch(0.75 0.15 60 / 0.12)',
            border: '1px solid oklch(0.75 0.15 60 / 0.35)',
            borderRadius: '0.625rem',
            padding: '0.75rem 1rem',
            color: 'oklch(0.85 0.10 60)',
            fontSize: '0.8125rem',
            fontFamily: 'Inter, sans-serif',
            marginBottom: '1.25rem',
          }}
        >
          {warning}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
        {/* Business name */}
        <div>
          <label style={labelStyle}>Business name *</label>
          <input
            type="text"
            value={businessName}
            onChange={e => setBusinessName(e.target.value)}
            placeholder="e.g. Acme Store"
            style={inputStyle}
          />
        </div>

        {/* Industry */}
        <div>
          <label style={labelStyle}>Industry</label>
          <select
            value={industry}
            onChange={e => setIndustry(e.target.value)}
            style={selectStyle}
          >
            <option value="" disabled style={{ background: 'oklch(0.18 0 0)', color: 'oklch(0.50 0 0)' }}>
              Select your industry
            </option>
            {INDUSTRIES.map(ind => (
              <option key={ind} value={ind} style={{ background: 'oklch(0.18 0 0)', color: 'oklch(0.97 0 0)' }}>
                {ind}
              </option>
            ))}
          </select>
        </div>

        {/* Target audience */}
        <div>
          <label style={labelStyle}>Target audience <span style={{ color: 'oklch(0.40 0 0)' }}>(optional)</span></label>
          <input
            type="text"
            value={targetAudience}
            onChange={e => setTargetAudience(e.target.value)}
            placeholder="e.g. Small business owners aged 30–50"
            style={inputStyle}
          />
        </div>

        {/* Preferred tone */}
        <div>
          <label style={labelStyle}>Preferred tone</label>
          <div style={{ display: 'flex', gap: '0.625rem' }}>
            {TONES.map(t => (
              <button
                key={t}
                onClick={() => setTone(t)}
                style={{
                  flex: 1,
                  padding: '0.6rem 0',
                  borderRadius: '0.5rem',
                  border: tone === t ? `1px solid ${BLUE_ACTIVE}` : '1px solid oklch(1 0 0 / 0.12)',
                  background: tone === t ? 'oklch(0.60 0.18 250 / 0.15)' : 'oklch(1 0 0 / 0.04)',
                  color: tone === t ? 'oklch(0.82 0.12 250)' : 'oklch(0.55 0 0)',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '0.875rem',
                  fontWeight: tone === t ? 600 : 400,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <button
          onClick={handleSave}
          disabled={!businessName.trim() || loading}
          style={{
            ...primaryButtonStyle,
            opacity: !businessName.trim() || loading ? 0.5 : 1,
            cursor: !businessName.trim() || loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Saving…' : 'Save & continue →'}
        </button>
        <button onClick={onSkip} style={{ ...skipButtonStyle, width: '100%' }}>
          Skip
        </button>
      </div>
    </div>
  )
}

// ─── STEP 3 — RUN FIRST AGENT ─────────────────────────────────────────────────

function Step3({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) {
  const [task, setTask] = useState('')
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)

  async function handleRun() {
    if (!task.trim()) return
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('https://api.vantro.ai/api/agents/intake_trial_agent/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt: task.trim() }),
      })
      if (res.ok) {
        const data = await res.json()
        setJobId(data?.job_id ?? data?.id ?? 'started')
      }
    } catch {
      // Non-fatal — still advance
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem 0' }}>
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            border: `3px solid oklch(1 0 0 / 0.08)`,
            borderTopColor: BLUE_ACTIVE,
            animation: 'spin 0.8s linear infinite',
            margin: '0 auto 1.5rem',
          }}
        />
        <p
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            fontSize: '1.125rem',
            color: 'oklch(0.90 0 0)',
            margin: '0 0 0.5rem',
          }}
        >
          Agent is working…
        </p>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.875rem', color: 'oklch(0.50 0 0)', margin: 0 }}>
          This usually takes a few seconds
        </p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  if (jobId) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem 0' }}>
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: '50%',
            background: 'oklch(0.60 0.22 145 / 0.15)',
            border: `1px solid oklch(0.60 0.22 145 / 0.40)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            margin: '0 auto 1.25rem',
          }}
        >
          ✓
        </div>
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: '1.375rem',
            color: 'oklch(0.97 0 0)',
            margin: '0 0 0.5rem',
          }}
        >
          Agent dispatched
        </h2>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.875rem', color: 'oklch(0.55 0 0)', margin: '0 0 0.375rem' }}>
          Your intake agent is working on your task.
        </p>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.75rem', color: 'oklch(0.40 0 0)', margin: '0 0 2rem' }}>
          Job ID: {jobId}
        </p>
        <button onClick={onNext} style={primaryButtonStyle}>
          Continue →
        </button>
      </div>
    )
  }

  return (
    <div>
      <h1
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 'clamp(1.75rem, 3.5vw, 2.25rem)',
          fontWeight: 700,
          color: 'oklch(0.97 0 0)',
          letterSpacing: '-0.025em',
          margin: '0 0 0.5rem',
        }}
      >
        Run your first agent
      </h1>
      <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.9375rem', color: 'oklch(0.60 0 0)', margin: '0 0 2rem', lineHeight: 1.5 }}>
        Describe a task — your intake agent will handle it.
      </p>

      {/* Agent card */}
      <div
        style={{
          background: 'oklch(1 0 0 / 0.04)',
          border: '1px solid oklch(1 0 0 / 0.10)',
          borderRadius: '0.875rem',
          padding: '1rem 1.125rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.875rem',
          marginBottom: '1.5rem',
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: '0.625rem',
            background: 'linear-gradient(135deg, oklch(0.60 0.18 250 / 0.25), oklch(0.60 0.18 250 / 0.08))',
            border: '1px solid oklch(0.60 0.18 250 / 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.125rem',
            flexShrink: 0,
          }}
        >
          🧠
        </div>
        <div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.9375rem', color: 'oklch(0.92 0 0)', marginBottom: '0.125rem' }}>
            Intake Agent
          </div>
          <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.8125rem', color: 'oklch(0.55 0 0)', lineHeight: 1.4 }}>
            Analyses your business and creates a customised action plan
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '1.75rem' }}>
        <label style={labelStyle}>Describe your task</label>
        <textarea
          rows={5}
          value={task}
          onChange={e => setTask(e.target.value)}
          placeholder="Describe your business, current challenges, and what you'd like help with."
          style={{
            ...inputStyle,
            resize: 'vertical',
            lineHeight: 1.6,
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <button
          onClick={handleRun}
          disabled={!task.trim()}
          style={{
            ...primaryButtonStyle,
            opacity: !task.trim() ? 0.5 : 1,
            cursor: !task.trim() ? 'not-allowed' : 'pointer',
          }}
        >
          Run agent →
        </button>
        <button onClick={onSkip} style={{ ...skipButtonStyle, width: '100%' }}>
          Skip
        </button>
      </div>
    </div>
  )
}

// ─── STEP 4 — CONNECT TOOLS ───────────────────────────────────────────────────

const INTEGRATIONS = [
  {
    name: 'Slack',
    icon: '💬',
    desc: 'Let agents send updates and alerts to your team channels',
  },
  {
    name: 'Notion',
    icon: '📝',
    desc: 'Sync agent outputs directly to your Notion workspace',
  },
  {
    name: 'Google Analytics',
    icon: '📊',
    desc: 'Let analytics agents access your GA4 data',
  },
]

function Step4({ onComplete }: { onComplete: () => void }) {
  return (
    <div>
      <h1
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 'clamp(1.75rem, 3.5vw, 2.25rem)',
          fontWeight: 700,
          color: 'oklch(0.97 0 0)',
          letterSpacing: '-0.025em',
          margin: '0 0 0.5rem',
        }}
      >
        Connect your tools
      </h1>
      <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.9375rem', color: 'oklch(0.60 0 0)', margin: '0 0 2rem', lineHeight: 1.5 }}>
        Connect apps so your agents can act across your stack. You can always do this from settings.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', marginBottom: '2rem' }}>
        {INTEGRATIONS.map(integ => (
          <div
            key={integ.name}
            style={{
              background: 'oklch(1 0 0 / 0.04)',
              border: '1px solid oklch(1 0 0 / 0.10)',
              borderRadius: '0.875rem',
              padding: '1rem 1.125rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
            }}
          >
            {/* Icon */}
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '0.75rem',
                background: 'oklch(1 0 0 / 0.06)',
                border: '1px solid oklch(1 0 0 / 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.25rem',
                flexShrink: 0,
              }}
            >
              {integ.icon}
            </div>

            {/* Info */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.9375rem', color: 'oklch(0.92 0 0)', marginBottom: '0.125rem' }}>
                {integ.name}
              </div>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.8125rem', color: 'oklch(0.55 0 0)', lineHeight: 1.4 }}>
                {integ.desc}
              </div>
            </div>

            {/* Connect */}
            <a
              href="/dashboard"
              style={{
                flexShrink: 0,
                background: 'none',
                border: '1px solid oklch(1 0 0 / 0.15)',
                borderRadius: '9999px',
                padding: '0.4rem 1rem',
                color: 'oklch(0.75 0 0)',
                fontFamily: 'Inter, sans-serif',
                fontSize: '0.8125rem',
                fontWeight: 500,
                cursor: 'pointer',
                textDecoration: 'none',
                display: 'inline-block',
                transition: 'border-color 0.2s ease, color 0.2s ease',
              }}
            >
              Connect
            </a>
          </div>
        ))}
      </div>

      <button onClick={onComplete} style={primaryButtonStyle}>
        Finish setup
      </button>
    </div>
  )
}

// ─── PAGE ROOT ────────────────────────────────────────────────────────────────

export function OnboardingPage() {
  const [, setLocation] = useLocation()
  const [step, setStep] = useState(1)

  // Auth guard
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLocation('/login')
      return
    }
    if (localStorage.getItem('onboarding_complete') === 'true') {
      setLocation('/dashboard')
    }
  }, [setLocation])

  function complete() {
    localStorage.setItem('onboarding_complete', 'true')
    setLocation('/dashboard')
  }

  function next() {
    setStep(s => Math.min(s + 1, 4))
  }

  return (
    <div
      style={{
        background: 'oklch(0.14 0 0)',
        color: 'oklch(0.97 0 0)',
        minHeight: '100vh',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      <OnboardingNav onSkip={complete} />

      <div
        style={{
          maxWidth: '560px',
          margin: '0 auto',
          padding: '4rem 1.5rem',
        }}
      >
        <StepIndicator current={step} />

        {step === 1 && <Step1 onNext={next} />}
        {step === 2 && <Step2 onNext={next} onSkip={next} />}
        {step === 3 && <Step3 onNext={next} onSkip={next} />}
        {step === 4 && <Step4 onComplete={complete} />}
      </div>
    </div>
  )
}
