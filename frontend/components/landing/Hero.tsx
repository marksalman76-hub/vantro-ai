'use client'

import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'framer-motion'
import { useGSAP } from '@gsap/react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { SplitText } from 'gsap/SplitText'
import { AGENTS } from '@/lib/agents'
import AgentDashboard from './AgentDashboard'

gsap.registerPlugin(ScrollTrigger, SplitText)

// ─── Data ─────────────────────────────────────────────────────────────────────

const PILLS = [
  '22 Specialized Agents',
  '200+ Integrations',
  'Deploy in 5 Minutes',
]

// ─── Component ────────────────────────────────────────────────────────────────

export default function Hero() {
  const sectionRef = useRef<HTMLElement>(null)
  const eyebrowRef = useRef<HTMLParagraphElement>(null)
  const h1Line1Ref = useRef<HTMLSpanElement>(null)
  const h1Line2Ref = useRef<HTMLDivElement>(null)
  const subheadRef = useRef<HTMLParagraphElement>(null)
  const pillsRef = useRef<HTMLDivElement>(null)
  const ctasRef = useRef<HTMLDivElement>(null)
  const rightColRef = useRef<HTMLDivElement>(null)

  const [cycleIdx, setCycleIdx] = useState(0)
  const [primaryPressed, setPrimaryPressed] = useState(false)
  const [secondaryPressed, setSecondaryPressed] = useState(false)
  const [hoveredPill, setHoveredPill] = useState<string | null>(null)
  const prefersReducedMotion = useReducedMotion()

  // Avatar cycling every 3 s
  useEffect(() => {
    const id = setInterval(() => setCycleIdx(i => (i + 1) % AGENTS.length), 3000)
    return () => clearInterval(id)
  }, [])

  useGSAP(
    () => {
      const eyebrow = eyebrowRef.current
      const line1 = h1Line1Ref.current
      const line2 = h1Line2Ref.current
      const subhead = subheadRef.current
      const pillsContainer = pillsRef.current
      const ctas = ctasRef.current
      const rightCol = rightColRef.current

      if (!eyebrow || !line1 || !line2 || !subhead || !pillsContainer || !ctas || !rightCol) return

      if (prefersReducedMotion) {
        gsap.set(
          [eyebrow, line1, line2, subhead, pillsContainer, ctas, rightCol],
          { opacity: 1, y: 0, x: 0, scale: 1 }
        )
        if (pillsContainer.children) {
          gsap.set(Array.from(pillsContainer.children), { opacity: 1, x: 0 })
        }
        if (ctas.children) {
          gsap.set(Array.from(ctas.children), { opacity: 1, scale: 1 })
        }
        return
      }

      // Set initial hidden states
      gsap.set(eyebrow, { opacity: 0, y: 20 })
      gsap.set(line2, { opacity: 0, y: 24 })
      gsap.set(subhead, { opacity: 0, y: 24 })
      gsap.set(pillsContainer, { opacity: 1 })
      gsap.set(Array.from(pillsContainer.children), { opacity: 0, x: -20 })
      gsap.set(Array.from(ctas.children), { opacity: 0, scale: 0.9 })
      gsap.set(rightCol, { opacity: 0, x: 80 })

      // SplitText on line 1 ("Deploy Your")
      const split = new SplitText(line1, { type: 'words,chars' })
      gsap.set(split.chars, { opacity: 0, y: 60 })

      const tl = gsap.timeline()

      // t=0.0: eyebrow
      tl.to(eyebrow, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.0)

      // t=0.3: H1 line 1 chars stagger
      tl.to(
        split.chars,
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          ease: 'power4.out',
          stagger: 0.02,
        },
        0.3
      )

      // t=0.9: H1 line 2 (avatar + "AI Workforce") — animate as single unit
      tl.to(line2, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.9)

      // t=1.0: subheading
      tl.to(subhead, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, 1.0)

      // t=1.3: benefit pills stagger
      tl.to(
        Array.from(pillsContainer.children),
        {
          opacity: 1,
          x: 0,
          duration: 0.5,
          ease: 'power3.out',
          stagger: 0.08,
        },
        1.3
      )

      // t=1.6: CTA buttons + fine print
      tl.to(
        Array.from(ctas.children),
        {
          opacity: 1,
          scale: 1,
          duration: 0.5,
          ease: 'power3.out',
          stagger: 0.1,
        },
        1.6
      )
      // t=1.6: right column carousel
      tl.to(rightCol, { opacity: 1, x: 0, duration: 1.0, ease: 'power3.out' }, 1.6)

      return () => {
        tl.kill()
        split.revert()
      }
    },
    { scope: sectionRef, dependencies: [prefersReducedMotion] }
  )

  return (
    <section
      ref={sectionRef}
      id="home"
      style={{
        position: 'relative',
        minHeight: '100dvh',
        background: '#0F1419',
        overflow: 'hidden',
        display: 'grid',
        gridTemplateColumns: '35fr 65fr',
        alignItems: 'center',
      }}
    >
      {/* ── Ambient orb depth layers (z-0) ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          zIndex: 0,
        }}
      >
        {/* Orb 1 — orange at top-left */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle 600px at 15% 30%, rgba(255,107,53,0.08) 0%, transparent 100%)',
          }}
        />
        {/* Orb 2 — cyan at right-center */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle 500px at 80% 60%, rgba(0,217,255,0.06) 0%, transparent 100%)',
          }}
        />
        {/* Orb 3 — teal at bottom-center */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle 400px at 50% 90%, rgba(31,255,214,0.04) 0%, transparent 100%)',
          }}
        />
      </div>

      {/* ── LEFT COLUMN ── */}
      <div
        style={{
          position: 'relative',
          zIndex: 2,
          paddingLeft: 'clamp(24px, 6vw, 96px)',
          paddingRight: 32,
          paddingTop: 100,
          paddingBottom: 80,
        }}
      >
        {/* Eyebrow */}
        <p
          ref={eyebrowRef}
          style={{
            color: '#00D9FF',
            fontSize: 11,
            letterSpacing: '0.18em',
            fontWeight: 700,
            textTransform: 'uppercase',
            margin: '0 0 28px',
            opacity: 0,
          }}
        >
          Your AI Workforce, Always On
        </p>

        {/* H1 */}
        <h1
          style={{
            fontSize: 'clamp(2.8rem, 4.5vw, 4.2rem)',
            fontWeight: 800,
            lineHeight: 1.08,
            letterSpacing: '-0.03em',
            color: '#ffffff',
            maxWidth: '16ch',
            margin: '0 0 24px',
            textWrap: 'balance' as React.CSSProperties['textWrap'],
          }}
        >
          {/* Line 1: "Deploy Your" — SplitText target */}
          <span
            ref={h1Line1Ref}
            style={{ display: 'block' }}
          >
            Deploy Your
          </span>

          {/* Line 2: avatar + "AI Workforce" — animated as a single unit */}
          <div
            ref={h1Line2Ref}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              opacity: 0,
              marginTop: 4,
            }}
          >
            <img
              src={AGENTS[cycleIdx]?.avatar ?? ''}
              alt={AGENTS[cycleIdx]?.name ?? 'AI Agent'}
              width={52}
              height={52}
              style={{
                display: 'inline-block',
                borderRadius: '50%',
                objectFit: 'cover',
                border: '2px solid #FF6B35',
                boxShadow: '0 0 20px rgba(255,107,53,0.5)',
                transition: 'opacity 400ms ease',
                flexShrink: 0,
              }}
            />
            <span
              style={{
                background:
                  'linear-gradient(135deg, #FF6B35 0%, #FFD700 60%, #FF6B35 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AI Workforce
            </span>
          </div>
        </h1>

        {/* Subheading */}
        <p
          ref={subheadRef}
          style={{
            fontSize: 18,
            lineHeight: 1.58,
            color: 'rgba(255,255,255,0.62)',
            maxWidth: 440,
            margin: '0 0 32px',
            opacity: 0,
          }}
        >
          Deploy specialized AI agents across sales, ops, support, and engineering — running 24/7 so your team focuses on what matters.
        </p>

        {/* Benefit pills */}
        <div
          ref={pillsRef}
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 10,
            marginBottom: 36,
          }}
        >
          {PILLS.map(label => {
            const isHovered = hoveredPill === label
            return (
              <span
                key={label}
                onMouseEnter={() => setHoveredPill(label)}
                onMouseLeave={() => setHoveredPill(null)}
                style={{
                  background: isHovered ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.06)',
                  border: isHovered
                    ? '1px solid rgba(255,255,255,0.22)'
                    : '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 99,
                  padding: '6px 14px',
                  fontSize: 13,
                  color: isHovered ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.7)',
                  whiteSpace: 'nowrap',
                  fontVariantNumeric: 'tabular-nums',
                  opacity: 0,
                  transform: isHovered ? 'scale(1.02)' : 'scale(1)',
                  transition: 'background 150ms ease, border-color 150ms ease, color 150ms ease, transform 150ms ease',
                  cursor: 'default',
                }}
              >
                {label}
              </span>
            )
          })}
        </div>

        {/* CTAs */}
        <div
          ref={ctasRef}
          style={{
            display: 'flex',
            flexDirection: 'row',
            gap: 14,
            flexWrap: 'wrap',
            marginBottom: 16,
          }}
        >
          {/* Primary */}
          <a
            href="/register"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '14px 28px',
              background: '#FF6B35',
              color: '#fff',
              fontWeight: 700,
              fontSize: 15,
              borderRadius: 12,
              textDecoration: 'none',
              border: 'none',
              boxShadow: '0 0 24px rgba(255,107,53,0.4)',
              transition: 'transform 180ms ease-out, box-shadow 200ms ease-out',
              opacity: 0,
            }}
            onMouseEnter={e => {
              if (primaryPressed) return
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(-2px) scale(1.04)'
              el.style.boxShadow = '0 0 40px rgba(255,107,53,0.65)'
            }}
            onMouseLeave={e => {
              setPrimaryPressed(false)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(0) scale(1)'
              el.style.boxShadow = '0 0 24px rgba(255,107,53,0.4)'
            }}
            onMouseDown={e => {
              setPrimaryPressed(true)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(0) scale(0.97)'
              el.style.boxShadow = '0 0 16px rgba(255,107,53,0.3)'
            }}
            onMouseUp={e => {
              setPrimaryPressed(false)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(-2px) scale(1.04)'
              el.style.boxShadow = '0 0 40px rgba(255,107,53,0.65)'
            }}
          >
            Deploy Now
          </a>

          {/* Secondary */}
          <a
            href="#how-it-works"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '14px 28px',
              background: 'transparent',
              color: 'rgba(255,255,255,0.8)',
              fontWeight: 600,
              fontSize: 15,
              borderRadius: 12,
              textDecoration: 'none',
              border: '1px solid rgba(255,255,255,0.2)',
              transition: 'border-color 180ms ease, background-color 180ms ease, color 180ms ease, transform 150ms ease-out',
              opacity: 0,
            }}
            onMouseEnter={e => {
              if (secondaryPressed) return
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(0,217,255,0.5)'
              el.style.background = 'rgba(0,217,255,0.08)'
              el.style.color = '#00D9FF'
            }}
            onMouseLeave={e => {
              setSecondaryPressed(false)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(255,255,255,0.2)'
              el.style.background = 'transparent'
              el.style.color = 'rgba(255,255,255,0.8)'
              el.style.transform = 'scale(1)'
            }}
            onMouseDown={e => {
              setSecondaryPressed(true)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'scale(0.97)'
            }}
            onMouseUp={e => {
              setSecondaryPressed(false)
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'scale(1)'
            }}
          >
            Book Demo
          </a>
        </div>

      </div>

      {/* ── RIGHT COLUMN ── */}
      <div
        ref={rightColRef}
        className="hero-right-col"
        style={{
          position: 'relative',
          zIndex: 2,
          paddingTop: 100,
          paddingBottom: 80,
          paddingRight: 'clamp(16px, 4vw, 48px)',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: 0,
        }}
      >
        <AgentDashboard />
      </div>

      {/* Bottom fade overlay */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 140,
          background:
            'linear-gradient(to bottom, transparent, rgba(15,20,25,0.88))',
          pointerEvents: 'none',
          zIndex: 1,
          gridColumn: '1 / -1',
        }}
      />

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 768px) {
          section#home {
            grid-template-columns: 1fr !important;
          }
          .hero-right-col {
            display: none !important;
          }
          section#home h1 {
            font-size: clamp(2.2rem, 7vw, 3.5rem) !important;
            max-width: 100% !important;
          }
        }
      `}</style>
    </section>
  )
}
