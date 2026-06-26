'use client'

import { useRef, useEffect } from 'react'
import gsap from 'gsap'
import { useGSAP } from '@gsap/react'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// ─── Reduced-motion hook ──────────────────────────────────────────────────────

function useReducedMotion(): boolean {
  const ref = useRef(
    typeof window !== 'undefined'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false
  )
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const handler = () => { ref.current = mq.matches }
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])
  return ref.current
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function FinalCTA() {
  const sectionRef  = useRef<HTMLElement>(null)
  const headlineRef = useRef<HTMLHeadingElement>(null)
  const subRef      = useRef<HTMLParagraphElement>(null)
  const benefitsRef = useRef<HTMLDivElement>(null)
  const btnRef      = useRef<HTMLAnchorElement>(null)
  const pulseTween  = useRef<gsap.core.Tween | null>(null)
  const reduce      = useReducedMotion()

  // ── DOM-only mouse spotlight (zero React re-renders) ──────────────────────
  useEffect(() => {
    const el = sectionRef.current
    if (!el || reduce) return

    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      el.style.background = `radial-gradient(circle 600px at ${x}px ${y}px, rgba(255,107,53,0.06) 0%, transparent 70%), linear-gradient(180deg, #111720 0%, #0F1419 100%)`
    }

    el.addEventListener('mousemove', onMove, { passive: true })
    return () => el.removeEventListener('mousemove', onMove)
  }, [reduce])

  // ── GSAP entrance timeline ─────────────────────────────────────────────────
  useGSAP(() => {
    if (
      !headlineRef.current ||
      !subRef.current ||
      !benefitsRef.current ||
      !btnRef.current
    ) return

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
        btnRef.current,
        { scale: 0.88, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(1.6)' },
        '-=0.5'
      )
  }, { scope: sectionRef })

  // ── GSAP scale pulse (GPU-safe transform — no box-shadow animation) ────────
  useGSAP(() => {
    if (!btnRef.current || reduce) return

    pulseTween.current = gsap.to(btnRef.current, {
      scale: 1.04,
      duration: 1.8,
      ease: 'sine.inOut',
      yoyo: true,
      repeat: -1,
    })

    return () => {
      pulseTween.current?.kill()
    }
  }, { scope: sectionRef })

  // ── Button hover handlers ──────────────────────────────────────────────────
  const handleBtnMouseEnter = () => {
    pulseTween.current?.pause()
    if (btnRef.current) {
      btnRef.current.style.boxShadow = '0 0 48px rgba(255,107,53,0.6)'
    }
  }

  const handleBtnMouseLeave = () => {
    if (!reduce) pulseTween.current?.resume()
    if (btnRef.current) {
      btnRef.current.style.boxShadow = '0 0 0 rgba(255,107,53,0.4)'
      btnRef.current.style.transform = ''
    }
  }

  const handleBtnMouseDown = () => {
    if (btnRef.current) {
      btnRef.current.style.transform = 'scale(0.96)'
    }
  }

  const handleBtnMouseUp = () => {
    if (btnRef.current) {
      btnRef.current.style.transform = 'scale(1.0)'
    }
  }

  return (
    <section
      id="cta"
      ref={sectionRef}
      style={{
        background: 'linear-gradient(180deg, #111720 0%, #0F1419 100%)',
        paddingTop: 160,
        paddingBottom: 160,
        paddingLeft: 24,
        paddingRight: 24,
        position: 'relative',
        overflow: 'hidden',
        width: '100%',
      }}
    >
      {/* Cinematic grid overlay */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px 1px, transparent 1px 80px), repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0px 1px, transparent 1px 80px)',
          opacity: 0.035,
          pointerEvents: 'none',
        }}
      />

      {/* Orange bloom — lower canvas warmth */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 70% 50% at 50% 80%, rgba(255,107,53,0.07) 0%, transparent 65%)',
          pointerEvents: 'none',
        }}
      />

      {/* Depth gradient overlay */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 80% 50% at 50% 100%, rgba(255,107,53,0.05) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Corner accent lines — top-left */}
      <div aria-hidden="true" style={{ position: 'absolute', top: 0, left: 0, width: 120, height: 1, background: 'linear-gradient(90deg, rgba(0,217,255,0.4) 0%, transparent 100%)', pointerEvents: 'none' }} />
      <div aria-hidden="true" style={{ position: 'absolute', top: 0, left: 0, width: 1, height: 120, background: 'linear-gradient(180deg, rgba(0,217,255,0.4) 0%, transparent 100%)', pointerEvents: 'none' }} />
      {/* top-right */}
      <div aria-hidden="true" style={{ position: 'absolute', top: 0, right: 0, width: 120, height: 1, background: 'linear-gradient(270deg, rgba(0,217,255,0.4) 0%, transparent 100%)', pointerEvents: 'none' }} />
      <div aria-hidden="true" style={{ position: 'absolute', top: 0, right: 0, width: 1, height: 120, background: 'linear-gradient(180deg, rgba(0,217,255,0.4) 0%, transparent 100%)', pointerEvents: 'none' }} />
      {/* bottom-left */}
      <div aria-hidden="true" style={{ position: 'absolute', bottom: 0, left: 0, width: 120, height: 1, background: 'linear-gradient(90deg, rgba(255,107,53,0.35) 0%, transparent 100%)', pointerEvents: 'none' }} />
      <div aria-hidden="true" style={{ position: 'absolute', bottom: 0, left: 0, width: 1, height: 120, background: 'linear-gradient(0deg, rgba(255,107,53,0.35) 0%, transparent 100%)', pointerEvents: 'none' }} />
      {/* bottom-right */}
      <div aria-hidden="true" style={{ position: 'absolute', bottom: 0, right: 0, width: 120, height: 1, background: 'linear-gradient(270deg, rgba(255,107,53,0.35) 0%, transparent 100%)', pointerEvents: 'none' }} />
      <div aria-hidden="true" style={{ position: 'absolute', bottom: 0, right: 0, width: 1, height: 120, background: 'linear-gradient(0deg, rgba(255,107,53,0.35) 0%, transparent 100%)', pointerEvents: 'none' }} />

      {/* ── Center content ── */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: 800,
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        {/* Headline */}
        <h2
          ref={headlineRef}
          style={{
            fontSize: 'clamp(2.4rem, 4.5vw, 4rem)',
            fontWeight: 800,
            color: '#ffffff',
            textAlign: 'center',
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            margin: 0,
            opacity: 0,
            textWrap: 'balance',
          } as React.CSSProperties}
        >
          Your AI Workforce Starts Today.
        </h2>

        {/* Subheading */}
        <p
          ref={subRef}
          style={{
            color: 'rgba(255,255,255,0.55)',
            fontSize: 20,
            marginTop: 16,
            textAlign: 'center',
            maxWidth: 520,
            lineHeight: 1.6,
            opacity: 0,
          }}
        >
          22 agents. 200+ integrations. Zero headcount added.
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
            marginTop: 32,
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
            ✓ Live in 5 min.
          </span>
        </div>

        {/* CTA button */}
        <a
          ref={btnRef}
          href="/register"
          onMouseEnter={handleBtnMouseEnter}
          onMouseLeave={handleBtnMouseLeave}
          onMouseDown={handleBtnMouseDown}
          onMouseUp={handleBtnMouseUp}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginTop: 40,
            padding: '18px 48px',
            borderRadius: 14,
            background: '#FF6B35',
            color: '#ffffff',
            fontWeight: 700,
            fontSize: 18,
            textDecoration: 'none',
            whiteSpace: 'nowrap',
            boxShadow: '0 0 0 rgba(255,107,53,0.4)',
            // CSS-only transitions; GSAP drives the idle scale pulse
            transition: 'box-shadow 0.3s ease, transform 150ms ease-out',
            opacity: 0,
            // will-change keeps the element on its own compositor layer
            willChange: 'transform',
          }}
        >
          Deploy Now
        </a>

      </div>
    </section>
  )
}
