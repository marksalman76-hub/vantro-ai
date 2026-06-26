'use client'

import { useRef, useEffect, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import gsap from 'gsap'
import { useGSAP } from '@gsap/react'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// ─── Constants ────────────────────────────────────────────────────────────────

const EASE = [0.23, 1, 0.32, 1] as const

// ─── Main Component ───────────────────────────────────────────────────────────

export default function FinalCTA() {
  const sectionRef = useRef<HTMLElement>(null)
  const headlineRef = useRef<HTMLHeadingElement>(null)
  const subRef = useRef<HTMLParagraphElement>(null)
  const benefitsRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLAnchorElement>(null)
  const buttonPulseRef = useRef<gsap.core.Tween | null>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  // Mouse-following spotlight
  const [mousePos, setMousePos] = useState({ x: 50, y: 60 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!sectionRef.current) return
      const rect = sectionRef.current.getBoundingClientRect()
      const x = ((e.clientX - rect.left) / rect.width) * 100
      const y = ((e.clientY - rect.top) / rect.height) * 100
      setMousePos({ x, y })
    }
    const section = sectionRef.current
    section?.addEventListener('mousemove', handleMouseMove)
    return () => section?.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // GSAP ScrollTrigger entrance timeline
  useGSAP(() => {
    if (!headlineRef.current || !subRef.current || !benefitsRef.current || !buttonRef.current) return

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top 75%',
        once: true,
      },
    })

    tl.fromTo(
      headlineRef.current,
      { y: 50, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.9, ease: 'power3.out' }
    )
      .fromTo(
        subRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.7, ease: 'power3.out' },
        '-=0.75'
      )
      .fromTo(
        benefitsRef.current,
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, ease: 'power3.out' },
        '-=0.6'
      )
      .fromTo(
        buttonRef.current,
        { scale: 0.9, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(1.4)' },
        '-=0.5'
      )
  }, { scope: sectionRef })

  // GSAP breathing pulse on button box-shadow
  useGSAP(() => {
    if (!buttonRef.current) return
    buttonPulseRef.current = gsap.to(buttonRef.current, {
      boxShadow:
        '0 0 80px rgba(255,107,53,0.85), 0 20px 40px rgba(255,107,53,0.4), inset 0 1px 0 rgba(255,255,255,0.25)',
      duration: 1.8,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
    return () => {
      buttonPulseRef.current?.kill()
    }
  }, { scope: sectionRef })

  return (
    <section
      id="cta"
      ref={sectionRef}
      style={{
        background: '#0F1419',
        paddingTop: 160,
        paddingBottom: 160,
        paddingLeft: 24,
        paddingRight: 24,
        position: 'relative',
        overflow: 'hidden',
        width: '100%',
      }}
    >
      {/* Cinematic grid */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px 1px, transparent 1px 80px), repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0px 1px, transparent 1px 80px)',
          opacity: 0.04,
          pointerEvents: 'none',
        }}
      />

      {/* Orange bloom */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 70% 50% at 50% 70%, rgba(255,107,53,0.09) 0%, transparent 65%)',
          pointerEvents: 'none',
        }}
      />

      {/* Mouse-following gold spotlight */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse 50% 40% at ${mousePos.x}% ${mousePos.y}%, rgba(255,215,0,0.06) 0%, transparent 60%)`,
          pointerEvents: 'none',
          transition: 'background 0.12s ease',
        }}
      />

      {/* Corner accent lines */}
      {/* Top-left */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 120,
          height: 1,
          background: 'linear-gradient(90deg, rgba(0,217,255,0.4) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 1,
          height: 120,
          background: 'linear-gradient(180deg, rgba(0,217,255,0.4) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      {/* Top-right */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: 120,
          height: 1,
          background: 'linear-gradient(270deg, rgba(0,217,255,0.4) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: 1,
          height: 120,
          background: 'linear-gradient(180deg, rgba(0,217,255,0.4) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      {/* Bottom-left */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: 120,
          height: 1,
          background: 'linear-gradient(90deg, rgba(255,107,53,0.35) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: 1,
          height: 120,
          background: 'linear-gradient(0deg, rgba(255,107,53,0.35) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      {/* Bottom-right */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          right: 0,
          width: 120,
          height: 1,
          background: 'linear-gradient(270deg, rgba(255,107,53,0.35) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          right: 0,
          width: 1,
          height: 120,
          background: 'linear-gradient(0deg, rgba(255,107,53,0.35) 0%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />

      {/* Center content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: 800,
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 40,
          textAlign: 'center',
        }}
      >
        {/* Headline */}
        <h2
          ref={headlineRef}
          style={{
            fontSize: 'clamp(2.2rem, 4vw, 3.6rem)',
            fontWeight: 800,
            color: '#ffffff',
            textAlign: 'center',
            lineHeight: 1.15,
            opacity: 0,
          }}
        >
          Your AI Workforce{' '}
          <span
            style={{
              background: 'linear-gradient(135deg, #FF6B35 0%, #FFD700 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Starts Today.
          </span>
        </h2>

        {/* Subheading */}
        <p
          ref={subRef}
          style={{
            color: '#9ca3af',
            fontSize: 20,
            textAlign: 'center',
            maxWidth: 520,
            lineHeight: 1.65,
            opacity: 0,
          }}
        >
          Join 500+ companies already running on Vantro.
        </p>

        {/* Benefits row */}
        <div
          ref={benefitsRef}
          style={{
            display: 'flex',
            flexDirection: 'row',
            gap: 24,
            alignItems: 'center',
            justifyContent: 'center',
            flexWrap: 'wrap',
            opacity: 0,
          }}
        >
          <span style={{ color: 'rgba(255,255,255,0.72)', fontSize: 15, fontWeight: 600 }}>
            ✓ 500+ teams already deployed
          </span>
          <span
            style={{
              width: 1,
              height: 16,
              background: 'rgba(255,255,255,0.15)',
              display: 'inline-block',
            }}
          />
          <span style={{ color: 'rgba(255,255,255,0.72)', fontSize: 15, fontWeight: 600 }}>
            ✓ Live in 5 min. Cancel anytime.
          </span>
        </div>

        {/* Giant CTA button */}
        <motion.a
          ref={buttonRef}
          href="/register"
          whileHover={{
            scale: 1.06,
          }}
          whileTap={{ scale: 0.97 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: 68,
            paddingLeft: 56,
            paddingRight: 56,
            borderRadius: 16,
            background: 'linear-gradient(135deg, #FF6B35 0%, #E84D1C 100%)',
            color: '#ffffff',
            fontWeight: 800,
            fontSize: 18,
            boxShadow:
              '0 0 50px rgba(255,107,53,0.6), 0 20px 40px rgba(255,107,53,0.3), inset 0 1px 0 rgba(255,255,255,0.25)',
            textDecoration: 'none',
            opacity: 0,
            whiteSpace: 'nowrap',
          }}
        >
          Deploy Your AI Workforce →
        </motion.a>

        {/* Fine print */}
        <p
          style={{
            color: '#6b7280',
            fontSize: 13,
            marginTop: -20,
          }}
        >
          No credit card required · Cancel anytime
        </p>
      </div>
    </section>
  )
}
