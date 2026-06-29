'use client'

import { useRef, useEffect } from 'react'
import { useReducedMotion } from 'framer-motion'
import { gsap } from 'gsap'

// ─── Card data ────────────────────────────────────────────────────────────────

const CARDS = [
  {
    id: 'sales',
    label: 'Sales Agent',
    task: '47 leads qualified',
    sub: 'Last 24 hours',
    metric: '+340%',
    metricLabel: 'Pipeline growth',
    color: '#FF6B35',
    pulse: true,
    top: '6%',
    left: '6%',
    popDelay: 0.2,
  },
  {
    id: 'support',
    label: 'Support Agent',
    task: '1,204 resolved',
    sub: 'Zero escalations',
    metric: '94%',
    metricLabel: 'First-contact rate',
    color: '#00D9FF',
    pulse: true,
    top: '36%',
    left: '50%',
    popDelay: 1.6,
  },
  {
    id: 'finance',
    label: 'Finance Agent',
    task: '$284k reconciled',
    sub: '847 transactions',
    metric: '3',
    metricLabel: 'Anomalies caught',
    color: '#1FFFD6',
    pulse: false,
    top: '64%',
    left: '4%',
    popDelay: 2.8,
  },
  {
    id: 'ops',
    label: 'Ops Agent',
    task: '100% tasks done',
    sub: 'All SLAs met',
    metric: '99.7%',
    metricLabel: 'Uptime',
    color: '#FFD700',
    pulse: true,
    top: '16%',
    left: '54%',
    popDelay: 0.9,
  },
  {
    id: 'engineering',
    label: 'Eng Agent',
    task: '12 PRs reviewed',
    sub: '7 vulns caught',
    metric: '9',
    metricLabel: 'PRs merged',
    color: '#B084FF',
    pulse: false,
    top: '74%',
    left: '46%',
    popDelay: 2.0,
  },
  {
    id: 'analytics',
    label: 'Analytics Agent',
    task: '2.4M events tracked',
    sub: 'Real-time pipeline',
    metric: '18ms',
    metricLabel: 'Avg latency',
    color: '#1FFFD6',
    pulse: true,
    top: '22%',
    left: '24%',
    popDelay: 1.3,
  },
  {
    id: 'marketing',
    label: 'Marketing Agent',
    task: '34 campaigns live',
    sub: '$1.2M attributed',
    metric: '4.8x',
    metricLabel: 'Avg ROAS',
    color: '#FF6B35',
    pulse: false,
    top: '48%',
    left: '14%',
    popDelay: 3.1,
  },
  {
    id: 'commerce',
    label: 'Commerce Agent',
    task: '8,291 orders routed',
    sub: 'Zero stockouts',
    metric: '99.1%',
    metricLabel: 'Fulfillment rate',
    color: '#FFD700',
    pulse: true,
    top: '58%',
    left: '58%',
    popDelay: 1.8,
  },
  {
    id: 'hr',
    label: 'HR Agent',
    task: '14 roles filled',
    sub: 'Avg 6-day hire',
    metric: '4.9★',
    metricLabel: 'Candidate NPS',
    color: '#F472B6',
    pulse: false,
    top: '10%',
    left: '38%',
    popDelay: 2.4,
  },
  {
    id: 'security',
    label: 'Security Agent',
    task: '0 breaches detected',
    sub: 'Continuous scan',
    metric: '2,841',
    metricLabel: 'Threats blocked',
    color: '#34D399',
    pulse: true,
    top: '42%',
    left: '32%',
    popDelay: 1.1,
  },
  {
    id: 'legal',
    label: 'Legal Agent',
    task: '38 contracts reviewed',
    sub: '3 risks flagged',
    metric: '97%',
    metricLabel: 'Accuracy rate',
    color: '#A78BFA',
    pulse: false,
    top: '78%',
    left: '20%',
    popDelay: 3.4,
  },
  {
    id: 'cx',
    label: 'CX Agent',
    task: '1,204 tickets resolved',
    sub: 'Avg 4-min response',
    metric: '4.8★',
    metricLabel: 'CSAT score',
    color: '#00D9FF',
    pulse: true,
    top: '8%',
    left: '70%',
    popDelay: 0.7,
  },
  {
    id: 'product',
    label: 'Product Agent',
    task: '31 features scoped',
    sub: '2 shipped this week',
    metric: '89%',
    metricLabel: 'On-time rate',
    color: '#FF6B35',
    pulse: false,
    top: '34%',
    left: '68%',
    popDelay: 2.1,
  },
  {
    id: 'supply',
    label: 'Supply Agent',
    task: '9,400 units tracked',
    sub: 'Zero overstock events',
    metric: '99.4%',
    metricLabel: 'Inventory accuracy',
    color: '#1FFFD6',
    pulse: true,
    top: '60%',
    left: '72%',
    popDelay: 1.5,
  },
] as const

const r = (min: number, max: number) => gsap.utils.random(min, max)

// ─── Component ────────────────────────────────────────────────────────────────

export default function AgentDashboard() {
  const containerRef = useRef<HTMLDivElement>(null)
  const reduce = useReducedMotion()

  useEffect(() => {
    if (!containerRef.current) return
    const cards = Array.from(
      containerRef.current.querySelectorAll<HTMLElement>('.fc')
    )
    if (!cards.length) return

    // Asymmetric Z-pop: fast surge TOWARDS screen, slow retreat AWAY
    function zPop(el: HTMLElement, color: string) {
      const tl = gsap.timeline({
        onComplete() {
          // idle pause before next pop — each card gets its own random wait
          gsap.delayedCall(r(0.6, 2.4), () => zPop(el, color))
        },
      })

      // ── Phase 1: SURGE towards screen ────────────────────────────────────
      // Fast (0.45-0.65s), power4.out = explosive start, decelerates at peak
      tl.to(el, {
        x: r(-70, 70),
        y: r(-50, 50),
        scale: r(1.55, 1.85),       // visibly large — coming AT viewer
        rotationY: r(-18, 18),       // 3D tilt for depth illusion
        rotationX: r(-8, 8),
        rotation: r(-5, 5),
        duration: r(0.42, 0.62),
        ease: 'power4.out',               // explosive acceleration, hard stop at peak
      })

      // ── Phase 2: RETREAT back into depth ─────────────────────────────────
      // Slow (2.2-3.8s), power2.in = starts slow, accelerates away
      tl.to(el, {
        scale: r(0.72, 0.92),        // smaller than base = receding into bg
        rotationY: r(-6, 6),         // settle into slight tilt
        rotationX: 0,
        rotation: r(-2, 2),
        duration: r(2.2, 3.8),
        ease: 'power2.inOut',
      })

      // ── Phase 3: Drift to a new idle position ────────────────────────────
      tl.to(el, {
        x: r(-30, 30),
        y: r(-20, 20),
        scale: r(0.88, 1.05),
        rotationY: r(-4, 4),
        duration: r(1.0, 1.8),
        ease: 'sine.inOut',
      })
    }

    const killList: (() => void)[] = []

    cards.forEach((card, i) => {
      const data = CARDS[i]
      if (!data) return

      if (reduce) {
        gsap.set(card, { autoAlpha: 1, scale: 1 })
        return
      }

      // Entrance pop-in first
      gsap.fromTo(
        card,
        { autoAlpha: 0, scale: 0.5, y: 20 },
        {
          autoAlpha: 1,
          scale: 0.95,
          y: 0,
          duration: 0.6,
          ease: 'back.out(1.6)',
          delay: 0.2 + i * 0.22,
          onComplete() {
            // Start the Z-pop cycle after this card's stagger delay
            const timer = gsap.delayedCall(data.popDelay, () =>
              zPop(card, data.color)
            )
            killList.push(() => timer.kill())
          },
        }
      )
    })

    return () => {
      killList.forEach(k => k())
      gsap.killTweensOf(cards)
    }
  }, [reduce])

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: 520,
        perspective: '800px',
        perspectiveOrigin: '50% 45%',
      }}
    >
      {/* Central ambient glow */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 280,
          height: 280,
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(255,107,53,0.08) 0%, rgba(0,217,255,0.05) 45%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      {/* Dashed connector lines */}
      <svg
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 1,
          opacity: 0.14,
        }}
      >
        <defs>
          <linearGradient id="ad-g1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#FF6B35" />
            <stop offset="100%" stopColor="#FFD700" />
          </linearGradient>
          <linearGradient id="ad-g2" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFD700" />
            <stop offset="100%" stopColor="#00D9FF" />
          </linearGradient>
          <linearGradient id="ad-g3" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FF6B35" />
            <stop offset="100%" stopColor="#1FFFD6" />
          </linearGradient>
          <linearGradient id="ad-g4" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1FFFD6" />
            <stop offset="100%" stopColor="#B084FF" />
          </linearGradient>
        </defs>
        <line x1="20%" y1="12%" x2="62%" y2="22%" stroke="url(#ad-g1)" strokeWidth="1" strokeDasharray="5 8" />
        <line x1="62%" y1="22%" x2="64%" y2="44%" stroke="url(#ad-g2)" strokeWidth="1" strokeDasharray="5 8" />
        <line x1="20%" y1="12%" x2="18%" y2="72%" stroke="url(#ad-g3)" strokeWidth="1" strokeDasharray="5 8" />
        <line x1="18%" y1="72%" x2="58%" y2="82%" stroke="url(#ad-g4)" strokeWidth="1" strokeDasharray="5 8" />
      </svg>

      {/* Cards */}
      {CARDS.map((card) => (
        <div
          key={card.id}
          className="fc"
          style={{
            position: 'absolute',
            top: card.top,
            left: card.left,
            zIndex: 10,
            visibility: 'hidden',           // autoAlpha handles this
            willChange: 'transform, opacity',
            transformStyle: 'preserve-3d',
          }}
        >
          <div
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLDivElement).style.filter = `drop-shadow(0 0 12px ${card.color}55)`
              ;(e.currentTarget as HTMLDivElement).style.transition = 'filter 200ms ease-out'
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLDivElement).style.filter = 'none'
            }}
            style={{
              background: 'rgba(14, 19, 27, 0.88)',
              border: `1px solid ${card.color}30`,
              borderRadius: 16,
              padding: '15px 17px',
              backdropFilter: 'blur(24px) saturate(180%)',
              WebkitBackdropFilter: 'blur(24px) saturate(180%)',
              boxShadow: `
                inset 0 1px 0 rgba(255,255,255,0.10),
                0 12px 40px rgba(0,0,0,0.5),
                0 0 0 1px ${card.color}14,
                0 0 30px ${card.color}12
              `,
              minWidth: 170,
              maxWidth: 200,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Top highlight strip */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: '8%',
                right: '8%',
                height: 1,
                background: `linear-gradient(90deg, transparent, ${card.color}66, transparent)`,
              }}
            />

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <div style={{ position: 'relative', flexShrink: 0 }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: card.color,
                    boxShadow: `0 0 12px ${card.color}CC`,
                  }}
                />
                {card.pulse && (
                  <div
                    style={{
                      position: 'absolute',
                      inset: -4,
                      borderRadius: '50%',
                      border: `1.5px solid ${card.color}`,
                      animation: 'adRing 2s ease-out infinite',
                    }}
                  />
                )}
              </div>
              <span style={{ fontSize: 12, fontWeight: 700, color: 'rgba(255,255,255,0.9)', letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>
                {card.label}
              </span>
            </div>

            <div style={{ fontSize: 14, fontWeight: 700, color: card.color, marginBottom: 3, letterSpacing: '-0.015em' }}>
              {card.task}
            </div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.36)', marginBottom: 10 }}>
              {card.sub}
            </div>

            <div style={{ height: 1, background: `linear-gradient(90deg, ${card.color}28, rgba(255,255,255,0.06), transparent)`, marginBottom: 10 }} />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <span style={{ fontSize: 19, fontWeight: 800, color: '#fff', letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                {card.metric}
              </span>
              <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.36)', textAlign: 'right', maxWidth: 80, lineHeight: 1.3 }}>
                {card.metricLabel}
              </span>
            </div>
          </div>
        </div>
      ))}

      <style>{`
        @keyframes adRing {
          0%   { transform: scale(1);   opacity: 0.8; }
          75%  { transform: scale(2.8); opacity: 0; }
          100% { transform: scale(2.8); opacity: 0; }
        }
      `}</style>
    </div>
  )
}
