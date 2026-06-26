'use client'

import { useEffect, useRef, useState } from 'react'
import { useInView } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const STATS = [
  {
    value: 500,
    suffix: '+',
    label: 'Companies Deployed',
    sublabel: 'and growing every day',
    color: '#FF6B35',
  },
  {
    value: 50000,
    suffix: '+',
    label: 'AI Agent Tasks Run',
    sublabel: 'in the last 30 days',
    color: '#00D9FF',
  },
  {
    value: 99.9,
    suffix: '%',
    label: 'Uptime SLA',
    sublabel: 'guaranteed reliability',
    color: '#1FFFD6',
  },
  {
    value: 200,
    suffix: '+',
    label: 'Integrations',
    sublabel: 'and adding more weekly',
    color: '#FFD700',
  },
]

// ─── Helpers ──────────────────────────────────────────────────────────────────

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

function formatValue(raw: number, targetValue: number): string {
  if (targetValue === 50000) {
    const k = raw / 1000
    return k >= 50 ? '50K' : `${k.toFixed(1).replace(/\.0$/, '')}K`
  }
  if (targetValue === 99.9) {
    return raw.toFixed(1)
  }
  return Math.round(raw).toString()
}

// ─── Stat card ────────────────────────────────────────────────────────────────

interface StatCardProps {
  value: number
  suffix: string
  label: string
  sublabel: string
  color: string
  animate: boolean
}

function StatCard({ value, suffix, label, sublabel, color, animate }: StatCardProps) {
  const [displayed, setDisplayed] = useState(0)
  const [counting, setCounting] = useState(false)
  const rafRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const duration = 2500

  useEffect(() => {
    if (!animate) return

    setCounting(true)
    startTimeRef.current = null

    const tick = (now: number) => {
      if (startTimeRef.current === null) startTimeRef.current = now
      const elapsed = now - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)
      const eased = easeOutCubic(progress)
      setDisplayed(eased * value)

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick)
      } else {
        setDisplayed(value)
        setCounting(false)
      }
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current)
    }
  }, [animate, value])

  return (
    <div
      className="stat-card"
      style={{
        position: 'relative',
        background: 'rgba(255,255,255,0.04)',
        border: `1px solid ${counting ? `${color}44` : 'rgba(255,255,255,0.08)'}`,
        borderRadius: 24,
        padding: '40px 32px',
        backdropFilter: 'blur(12px)',
        overflow: 'hidden',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        transition: 'border-color 0.4s ease',
        opacity: 0, // GSAP will animate this
      }}
    >
      {/* Top border accent line */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 3,
          background: `linear-gradient(90deg, transparent, ${color}99, transparent)`,
          borderRadius: '3px 3px 0 0',
        }}
      />

      {/* Subtle animated ring */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 24,
          border: `1px solid ${counting ? `${color}22` : 'transparent'}`,
          transition: 'border-color 0.4s ease',
          pointerEvents: 'none',
        }}
      />

      {/* Animated number */}
      <div style={{ position: 'relative' }}>
        {/* Glow halo */}
        <span
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            display: 'block',
            borderRadius: '50%',
            boxShadow: counting ? `0 0 80px ${color}55` : `0 0 40px ${color}22`,
            opacity: counting ? 0.9 : 0.4,
            transition: 'opacity 0.4s ease, box-shadow 0.4s ease',
            pointerEvents: 'none',
            filter: 'blur(8px)',
          }}
        />

        <span
          style={{
            display: 'block',
            fontSize: 68,
            fontWeight: 800,
            lineHeight: 1,
            color: '#ffffff',
            fontVariantNumeric: 'tabular-nums',
            textShadow: counting
              ? `0 0 40px ${color}, 0 0 80px ${color}55`
              : `0 0 16px ${color}44`,
            transition: 'text-shadow 0.3s ease',
          }}
        >
          {formatValue(displayed, value)}{suffix}
        </span>
      </div>

      {/* Label */}
      <p
        style={{
          color: color,
          fontSize: 13,
          fontWeight: 600,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          marginTop: 8,
          marginBottom: 0,
        }}
      >
        {label}
      </p>

      {/* Sublabel */}
      <p
        style={{
          color: 'rgba(255,255,255,0.35)',
          fontSize: 12,
          marginTop: 4,
          marginBottom: 0,
        }}
      >
        {sublabel}
      </p>
    </div>
  )
}

// ─── Section ──────────────────────────────────────────────────────────────────

export default function Stats() {
  const sectionRef = useRef<HTMLElement>(null)
  const gridRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  // GSAP stagger fade-in for cards
  useEffect(() => {
    if (!gridRef.current) return

    const cards = gridRef.current.querySelectorAll<HTMLElement>('.stat-card')
    if (!cards.length) return

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cards,
        { opacity: 0, y: 32 },
        {
          opacity: 1,
          y: 0,
          duration: 0.65,
          ease: 'power3.out',
          stagger: 0.1,
          scrollTrigger: {
            trigger: gridRef.current,
            start: 'top 82%',
            once: true,
          },
        }
      )
    }, gridRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      id="stats"
      ref={sectionRef}
      style={{
        background: '#0F1419',
        paddingTop: 96,
        paddingBottom: 96,
        paddingLeft: 24,
        paddingRight: 24,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background glow */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 900,
          height: 700,
          background:
            'radial-gradient(ellipse at center, rgba(0,217,255,0.04) 0%, rgba(255,107,53,0.03) 50%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      <div
        ref={gridRef}
        style={{
          position: 'relative',
          maxWidth: 1100,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 24,
        }}
        className="stats-grid"
      >
        {STATS.map((stat) => (
          <StatCard
            key={stat.label}
            value={stat.value}
            suffix={stat.suffix}
            label={stat.label}
            sublabel={stat.sublabel}
            color={stat.color}
            animate={isInView}
          />
        ))}
      </div>

      <style>{`
        @media (max-width: 768px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
      `}</style>
    </section>
  )
}
