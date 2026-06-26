'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import AgentCarousel from './AgentCarousel'
import CinematicLighting from './CinematicLighting'
import ParticleBackground from './ParticleBackground'
import { AGENTS } from '@/lib/agents'

gsap.registerPlugin(ScrollTrigger)

// ─── Types ──────────────────────────────────────────────────────────────────

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 28 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.65,
    ease: [0.23, 1, 0.36, 1] as [number, number, number, number],
    delay,
  },
})

// ─── Benefit rows ────────────────────────────────────────────────────────────

const BENEFITS = [
  { icon: '◈', color: '#00D9FF', label: '22 Specialized Agents' },
  { icon: '◆', color: '#1FFFD6', label: '200+ Integrations' },
  { icon: '◉', color: '#FFD700', label: 'Deploy in 5 Minutes' },
]

// ─── Component ───────────────────────────────────────────────────────────────

export default function Hero() {
  const sectionRef = useRef<HTMLElement>(null)
  const leftColRef = useRef<HTMLDivElement>(null)
  const gradientRef = useRef<HTMLSpanElement>(null)

  const [cycleIdx, setCycleIdx] = useState(0)

  // Avatar cycling every 3 s
  useEffect(() => {
    const id = setInterval(() => setCycleIdx(i => (i + 1) % 5), 3000)
    return () => clearInterval(id)
  }, [])

  // GSAP: gradient shimmer + parallax
  useGSAP(() => {
    // H1 gradient shimmer animation
    if (gradientRef.current) {
      gsap.to(gradientRef.current, {
        backgroundPosition: '200% 50%',
        duration: 3,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      })
    }

    // Parallax on left column
    if (leftColRef.current && sectionRef.current) {
      gsap.fromTo(
        leftColRef.current,
        { y: 0 },
        {
          y: -40,
          ease: 'none',
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top top',
            end: 'bottom top',
            scrub: true,
          },
        },
      )
    }
  }, { scope: sectionRef })

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
        gridTemplateColumns: '55fr 45fr',
        alignItems: 'center',
      }}
    >
      {/* ── Background layers (z 0) ── */}
      <CinematicLighting followMouse goldSpotlight showGrain />
      <ParticleBackground count={14} />

      {/* Extra ambient glow */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: -200,
          left: -150,
          width: 650,
          height: 650,
          background:
            'radial-gradient(circle, rgba(255,215,0,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* ── LEFT COLUMN ── */}
      <div
        ref={leftColRef}
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
        <motion.p
          {...fadeUp(0.1)}
          style={{
            color: '#00D9FF',
            fontSize: 11,
            letterSpacing: '0.2em',
            fontWeight: 700,
            textTransform: 'uppercase',
            margin: '0 0 28px',
          }}
        >
          Autonomous AI Workforce Platform
        </motion.p>

        {/* H1 */}
        <motion.h1
          {...fadeUp(0.2)}
          style={{
            fontSize: 'clamp(2.8rem, 4.5vw, 5.4rem)',
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: '-0.03em',
            color: '#ffffff',
            maxWidth: '15ch',
            margin: '0 0 24px',
            textWrap: 'balance' as React.CSSProperties['textWrap'],
          }}
        >
          {/* Line 1 */}
          <span style={{ display: 'block' }}>
            Deploy Your{' '}
            <img
              src={AGENTS[cycleIdx]?.avatar ?? ''}
              alt={AGENTS[cycleIdx]?.name ?? 'AI Agent'}
              width={56}
              height={56}
              style={{
                display: 'inline-block',
                verticalAlign: 'middle',
                borderRadius: '50%',
                objectFit: 'cover',
                border: '2px solid #FF6B35',
                boxShadow: '0 0 20px rgba(255,107,53,0.5)',
                transition: 'opacity 400ms ease',
                marginLeft: 8,
              }}
            />
          </span>

          {/* Line 2 — gradient shimmer via GSAP */}
          <span
            ref={gradientRef}
            style={{
              display: 'block',
              background:
                'linear-gradient(135deg, #FF6B35 0%, #FFD700 60%, #FF6B35 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundSize: '200% 100%',
              backgroundPosition: '0% 50%',
            }}
          >
            AI Workforce
          </span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          {...fadeUp(0.3)}
          style={{
            fontSize: 18,
            lineHeight: 1.58,
            color: 'rgba(255,255,255,0.62)',
            maxWidth: 440,
            margin: '0 0 36px',
          }}
        >
          22 specialized agents running 24/7 across sales, ops, support, and
          engineering — so your team can focus on what only humans can do.
        </motion.p>

        {/* Benefits list — icon + label rows, no pill badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 40 }}
        >
          {BENEFITS.map(({ icon, color, label }) => (
            <div
              key={label}
              style={{ display: 'flex', alignItems: 'center', gap: 10 }}
            >
              <span
                style={{
                  color,
                  fontSize: 14,
                  flexShrink: 0,
                  lineHeight: 1,
                }}
              >
                {icon}
              </span>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 500,
                  color: 'rgba(255,255,255,0.72)',
                }}
              >
                {label}
              </span>
            </div>
          ))}
        </motion.div>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{ display: 'flex', flexDirection: 'row', gap: 14, flexWrap: 'wrap', marginBottom: 20 }}
        >
          {/* Primary CTA */}
          <a
            href="/register"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '15px 40px',
              background: 'linear-gradient(135deg, #FF6B35, #E8521A)',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: 15,
              borderRadius: 12,
              textDecoration: 'none',
              boxShadow: '0 0 40px rgba(255,107,53,0.55), 0 4px 20px rgba(255,107,53,0.3)',
              transition: 'all 200ms cubic-bezier(0.23,1,0.32,1)',
              letterSpacing: '-0.01em',
              border: 'none',
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(-3px) scale(1.04)'
              el.style.boxShadow = '0 0 60px rgba(255,107,53,0.75), 0 8px 24px rgba(255,107,53,0.4)'
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.transform = 'translateY(0) scale(1)'
              el.style.boxShadow = '0 0 40px rgba(255,107,53,0.55), 0 4px 20px rgba(255,107,53,0.3)'
            }}
          >
            Start Free Trial →
          </a>

          {/* Secondary CTA */}
          <a
            href="#how-it-works"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              padding: '15px 32px',
              background: 'transparent',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: 15,
              borderRadius: 12,
              textDecoration: 'none',
              border: '1px solid rgba(255,255,255,0.18)',
              transition: 'all 200ms cubic-bezier(0.23,1,0.32,1)',
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(0,217,255,0.5)'
              el.style.background = 'rgba(0,217,255,0.07)'
              el.style.color = '#00D9FF'
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(255,255,255,0.18)'
              el.style.background = 'transparent'
              el.style.color = '#ffffff'
            }}
          >
            ▷ Watch Demo
          </a>
        </motion.div>

        {/* Fine print */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          style={{
            fontSize: 12,
            color: 'rgba(255,255,255,0.50)',
            margin: 0,
            letterSpacing: '0.01em',
          }}
        >
          14-day free trial · No credit card · Cancel anytime
        </motion.p>
      </div>

      {/* ── RIGHT COLUMN ── */}
      <motion.div
        initial={{ opacity: 0, scale: 0.94 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.9, ease: [0.23, 1, 0.36, 1], delay: 0.25 }}
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
        }}
      >
        <AgentCarousel agents={AGENTS} />
      </motion.div>

      {/* Bottom fade overlay */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 140,
          background: 'linear-gradient(to bottom, transparent, rgba(15,20,25,0.88))',
          pointerEvents: 'none',
          gridColumn: '1 / -1',
        }}
      />

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 900px) {
          section#home {
            grid-template-columns: 1fr !important;
          }
          .hero-right-col {
            display: none !important;
          }
        }
      `}</style>
    </section>
  )
}
