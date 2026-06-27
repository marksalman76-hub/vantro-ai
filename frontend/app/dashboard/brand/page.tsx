'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'

gsap.registerPlugin()

// ─── Types ────────────────────────────────────────────────────────────────────

interface BrandForm {
  companyName: string
  brandTone: string
  targetAudience: string
  brandVoiceNotes: string
  websiteUrl: string
  industry: string
}

const DEFAULT_FORM: BrandForm = {
  companyName: '',
  brandTone: 'Professional',
  targetAudience: '',
  brandVoiceNotes: '',
  websiteUrl: '',
  industry: 'Technology',
}

// ─── Constants ────────────────────────────────────────────────────────────────

const CARD: React.CSSProperties = {
  background: 'var(--t-surface)',
  border: '1px solid var(--t-border)',
  borderRadius: '1rem',
  padding: '1.25rem',
}

const INPUT_STYLE: React.CSSProperties = {
  width: '100%',
  background: 'var(--t-surface)',
  border: '1px solid var(--t-border)',
  borderRadius: '0.5rem',
  padding: '0.75rem 1rem',
  color: '#fff',
  fontSize: '0.9rem',
  fontFamily: "'Space Grotesk', sans-serif",
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.18s ease',
}

const LABEL_STYLE: React.CSSProperties = {
  display: 'block',
  fontSize: '0.78rem',
  fontWeight: 600,
  color: 'var(--t-text-2)',
  marginBottom: '0.45rem',
  fontFamily: "'Space Grotesk', sans-serif",
  letterSpacing: '0.04em',
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getToken() {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null
}

// ─── FormField ────────────────────────────────────────────────────────────────

function InputField({
  label,
  id,
  value,
  onChange,
  placeholder,
  type = 'text',
}: {
  label: string
  id: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  type?: string
}) {
  const [focused, setFocused] = useState(false)
  return (
    <div>
      <label htmlFor={id} style={LABEL_STYLE}>{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          ...INPUT_STYLE,
          borderColor: focused ? 'rgba(0,217,255,0.40)' : 'var(--t-border)',
          boxShadow: focused ? '0 0 0 3px rgba(0,217,255,0.07)' : 'none',
        }}
      />
    </div>
  )
}

function SelectField({
  label,
  id,
  value,
  onChange,
  options,
}: {
  label: string
  id: string
  value: string
  onChange: (v: string) => void
  options: string[]
}) {
  const [focused, setFocused] = useState(false)
  return (
    <div>
      <label htmlFor={id} style={LABEL_STYLE}>{label}</label>
      <select
        id={id}
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          ...INPUT_STYLE,
          cursor: 'pointer',
          appearance: 'none' as const,
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='var(--t-text-3)' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 0.875rem center',
          paddingRight: '2.5rem',
          borderColor: focused ? 'rgba(0,217,255,0.40)' : 'var(--t-border)',
          boxShadow: focused ? '0 0 0 3px rgba(0,217,255,0.07)' : 'none',
        }}
      >
        {options.map(opt => (
          <option key={opt} value={opt} style={{ background: 'var(--t-bg)', color: '#fff' }}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  )
}

function TextareaField({
  label,
  id,
  value,
  onChange,
  placeholder,
  rows = 4,
}: {
  label: string
  id: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  rows?: number
}) {
  const [focused, setFocused] = useState(false)
  return (
    <div>
      <label htmlFor={id} style={LABEL_STYLE}>{label}</label>
      <textarea
        id={id}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          ...INPUT_STYLE,
          resize: 'vertical',
          lineHeight: 1.6,
          borderColor: focused ? 'rgba(0,217,255,0.40)' : 'var(--t-border)',
          boxShadow: focused ? '0 0 0 3px rgba(0,217,255,0.07)' : 'none',
        }}
      />
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function BrandPage() {
  const router = useRouter()
  const [form, setForm] = useState<BrandForm>(DEFAULT_FORM)
  const [saved, setSaved] = useState(false)

  const pageRef   = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)
  const cardRef   = useRef<HTMLDivElement>(null)
  const notifRef  = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!getToken()) { router.replace('/login'); return }
    try {
      const raw = localStorage.getItem('vantro_brand')
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<BrandForm>
        setForm(prev => ({ ...prev, ...parsed }))
      }
    } catch {
      // ignore malformed data
    }
  }, [router])

  // ── Page entry animation ────────────────────────────────────────────────────
  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.fromTo(
      headerRef.current,
      { y: -20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5 }
    )
    tl.fromTo(
      cardRef.current,
      { y: 24, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.45 },
      '-=0.25'
    )
  }, { scope: pageRef })

  function field<K extends keyof BrandForm>(key: K) {
    return (v: string) => setForm(prev => ({ ...prev, [key]: v }))
  }

  function handleSave() {
    localStorage.setItem('vantro_brand', JSON.stringify(form))
    setSaved(true)

    // Animate notification in
    if (notifRef.current) {
      gsap.fromTo(
        notifRef.current,
        { opacity: 0, y: -8, scale: 0.97 },
        { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: 'back.out(1.6)' }
      )
    }

    setTimeout(() => {
      if (notifRef.current) {
        gsap.to(notifRef.current, {
          opacity: 0,
          y: -6,
          duration: 0.25,
          ease: 'power2.in',
          onComplete: () => setSaved(false),
        })
      } else {
        setSaved(false)
      }
    }, 2000)
  }

  return (
    <div ref={pageRef} style={{ flex: 1, minWidth: 0, padding: '2.5rem', background: 'var(--t-bg)', minHeight: '100%' }}>

      {/* ── Header ── */}
      <div ref={headerRef} style={{ marginBottom: '2rem', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.75rem', margin: 0, color: '#fff' }}>
            Brand Profile
          </h1>
          <p style={{ color: 'var(--t-text-3)', marginTop: '0.375rem', fontSize: '0.9rem', fontFamily: "'Space Grotesk', sans-serif" }}>
            Define your brand identity for all agents
          </p>
        </div>

        {/* Success notification */}
        {saved && (
          <div
            ref={notifRef}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.55rem 1rem',
              background: 'rgba(31,255,214,0.08)',
              border: '1px solid rgba(31,255,214,0.35)',
              borderRadius: '0.625rem',
              fontSize: '0.82rem',
              fontWeight: 600,
              color: '#1FFFD6',
              fontFamily: "'Space Grotesk', sans-serif",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <circle cx="7" cy="7" r="6" stroke="#1FFFD6" strokeWidth="1.4"/>
              <path d="M4 7l2 2 4-4" stroke="#1FFFD6" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Brand profile saved!
          </div>
        )}
      </div>

      {/* ── Form card ── */}
      <div ref={cardRef} style={{ ...CARD, maxWidth: 720 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Row 1: Company Name + Industry */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <InputField
              label="Company Name"
              id="companyName"
              value={form.companyName}
              onChange={field('companyName')}
              placeholder="e.g. Acme Corp"
            />
            <SelectField
              label="Industry"
              id="industry"
              value={form.industry}
              onChange={field('industry')}
              options={['Technology', 'Healthcare', 'Finance', 'Retail', 'Education', 'Other']}
            />
          </div>

          {/* Row 2: Brand Tone + Target Audience */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <SelectField
              label="Brand Tone"
              id="brandTone"
              value={form.brandTone}
              onChange={field('brandTone')}
              options={['Professional', 'Casual', 'Playful', 'Authoritative']}
            />
            <InputField
              label="Target Audience"
              id="targetAudience"
              value={form.targetAudience}
              onChange={field('targetAudience')}
              placeholder="e.g. B2B SaaS founders, 25-45"
            />
          </div>

          {/* Website URL */}
          <InputField
            label="Website URL"
            id="websiteUrl"
            value={form.websiteUrl}
            onChange={field('websiteUrl')}
            placeholder="https://yoursite.com"
            type="url"
          />

          {/* Brand Voice Notes */}
          <TextareaField
            label="Brand Voice Notes"
            id="brandVoiceNotes"
            value={form.brandVoiceNotes}
            onChange={field('brandVoiceNotes')}
            placeholder="Describe your brand voice..."
            rows={5}
          />

          {/* Save button */}
          <div style={{ paddingTop: '0.25rem' }}>
            <SaveButton onClick={handleSave} />
          </div>
        </div>
      </div>

    </div>
  )
}

// ─── SaveButton ───────────────────────────────────────────────────────────────

function SaveButton({ onClick }: { onClick: () => void }) {
  const btnRef = useRef<HTMLButtonElement>(null)

  function handleEnter() {
    gsap.to(btnRef.current, {
      scale: 1.025,
      boxShadow: '0 6px 24px rgba(255,107,53,0.30)',
      duration: 0.18,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    gsap.to(btnRef.current, {
      scale: 1,
      boxShadow: '0 0px 0px rgba(0,0,0,0)',
      duration: 0.24,
      ease: 'power3.out',
    })
  }

  return (
    <button
      ref={btnRef}
      type="button"
      onClick={onClick}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      style={{
        padding: '0.7rem 1.75rem',
        background: '#FF6B35',
        border: 'none',
        borderRadius: '0.625rem',
        color: '#fff',
        fontWeight: 700,
        fontSize: '0.9rem',
        cursor: 'pointer',
        fontFamily: "'Space Grotesk', sans-serif",
        letterSpacing: '0.02em',
        willChange: 'transform',
      }}
    >
      Save Brand Profile
    </button>
  )
}
