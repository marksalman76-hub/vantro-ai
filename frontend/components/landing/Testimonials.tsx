'use client'

import { useRef } from 'react'
import { motion, useMotionValue, useTransform, useReducedMotion } from 'framer-motion'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useGSAP } from '@gsap/react'

gsap.registerPlugin(ScrollTrigger)

// ─── Types ────────────────────────────────────────────────────────────────────

interface Testimonial {
  quote: string
  name: string
  role: string
  avatarSeed: string
  accent: string
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "Vantro replaced three full-time hires. Our support queue went from 48 hours to under 4. I still can't believe it runs without anyone watching it.",
    name: 'Marcus Chen',
    role: 'CEO, Stackify',
    avatarSeed: 'marcus-ceo',
    accent: '#FF6B35',
  },
  {
    quote:
      'We scaled from 50 to 500 customers without adding ops headcount. The Vantro agents handle everything our team used to dread doing manually.',
    name: 'Priya Malhotra',
    role: 'COO, NexScale',
    avatarSeed: 'priya-coo',
    accent: '#00D9FF',
  },
  {
    quote:
      'The sales agent books more qualified meetings than our two SDRs combined. ROI in 11 days. This is the most obvious no-brainer we\'ve ever bought.',
    name: 'Jordan Reeves',
    role: 'VP Sales, Clearpath',
    avatarSeed: 'jordan-vp',
    accent: '#1FFFD6',
  },
]

// ─── Tilt Card ────────────────────────────────────────────────────────────────

interface TiltCardProps {
  testimonial: Testimonial
  reducedMotion: boolean
}

function TiltCard({ testimonial, reducedMotion }: TiltCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)

  // Motion values — never useState for continuous tracking
  const mx = useMotionValue(0)
  const my = useMotionValue(0)

  const rotateX = useTransform(my, [-150, 150], [8, -8])
  const rotateY = useTransform(mx, [-150, 150], [-8, 8])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (reducedMotion || !cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    mx.set(e.clientX - rect.left - rect.width / 2)
    my.set(e.clientY - rect.top - rect.height / 2)
  }

  const handleMouseLeave = () => {
    mx.set(0)
    my.set(0)
  }

  const accent = testimonial.accent

  // Base card styles applied directly so framer-motion can merge motion values
  const baseCardStyle: React.CSSProperties = {
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 24,
    backdropFilter: 'blur(16px)',
    WebkitBackdropFilter: 'blur(16px)',
    padding: '40px 36px',
    boxShadow: '0 1px 0 rgba(255,255,255,0.06) inset',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    boxSizing: 'border-box',
    cursor: 'default',
    willChange: 'transform',
  }

  return (
    <motion.div
      ref={cardRef}
      className="testimonial-card"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={
        reducedMotion
          ? baseCardStyle
          : {
              ...baseCardStyle,
              rotateX,
              rotateY,
              transformStyle: 'preserve-3d',
              perspective: '1000px',
            }
      }
      whileHover={
        reducedMotion
          ? {}
          : {
              borderColor: `${accent}33`,
              boxShadow: `0 1px 0 rgba(255,255,255,0.06) inset, 0 32px 80px ${accent}12`,
            }
      }
      transition={{ duration: 0.25, ease: 'easeOut' }}
      aria-label={`Testimonial from ${testimonial.name}, ${testimonial.role}`}
    >
      {/* Decorative large opening quotation mark */}
      <div
        aria-hidden="true"
        style={{
          color: accent,
          fontSize: 48,
          fontWeight: 900,
          lineHeight: 1,
          opacity: 0.3,
          marginBottom: -8,
          userSelect: 'none',
          fontFamily: 'Georgia, serif',
        }}
      >
        &#8220;
      </div>

      {/* Quote text */}
      <p
        style={{
          color: 'rgba(255,255,255,0.75)',
          fontSize: 16,
          lineHeight: 1.7,
          fontStyle: 'italic',
          margin: '12px 0 0 0',
          flex: 1,
        }}
      >
        {testimonial.quote}
      </p>

      {/* Stars */}
      <div
        aria-label="5 out of 5 stars"
        role="img"
        style={{
          marginTop: 24,
          display: 'flex',
          gap: 2,
          alignItems: 'center',
        }}
      >
        {Array.from({ length: 5 }).map((_, i) => (
          <span
            key={i}
            aria-hidden="true"
            style={{ color: '#FFD700', fontSize: 14, lineHeight: 1 }}
          >
            ★
          </span>
        ))}
      </div>

      {/* Divider */}
      <div
        aria-hidden="true"
        style={{
          marginTop: 24,
          height: 1,
          background: 'rgba(255,255,255,0.08)',
          borderRadius: 99,
        }}
      />

      {/* Author row */}
      <div
        style={{
          marginTop: 20,
          display: 'flex',
          flexDirection: 'row',
          gap: 14,
          alignItems: 'center',
        }}
      >
        {/* Circular avatar */}
        <img
          src={`https://picsum.photos/seed/${testimonial.avatarSeed}/80/80`}
          alt={`Photo of ${testimonial.name}`}
          width={48}
          height={48}
          style={{
            borderRadius: '50%',
            border: `2px solid ${accent}40`,
            objectFit: 'cover',
            flexShrink: 0,
            background: '#111720',
            display: 'block',
          }}
          loading="lazy"
        />

        {/* Name and role */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span
            style={{
              color: '#ffffff',
              fontSize: 15,
              fontWeight: 600,
              lineHeight: 1.3,
            }}
          >
            {testimonial.name}
          </span>
          <span
            style={{
              color: 'rgba(255,255,255,0.45)',
              fontSize: 13,
              marginTop: 2,
              lineHeight: 1.3,
            }}
          >
            {testimonial.role}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

// ─── Main Section ─────────────────────────────────────────────────────────────

export default function Testimonials() {
  const sectionRef = useRef<HTMLElement>(null)
  const cardsRef = useRef<HTMLDivElement>(null)
  // useReducedMotion returns null on first SSR render, default to false
  const prefersReducedMotion = useReducedMotion() ?? false

  // GSAP ScrollTrigger entrance: cards fade in from y:40, opacity:0 with stagger
  useGSAP(
    () => {
      if (prefersReducedMotion || !cardsRef.current) return

      const cards = cardsRef.current.querySelectorAll<HTMLElement>('.testimonial-card')
      if (!cards.length) return

      gsap.fromTo(
        cards,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          ease: 'power3.out',
          stagger: 0.12,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top 75%',
            once: true,
          },
        }
      )
    },
    { scope: sectionRef }
  )

  return (
    <section
      id="testimonials"
      ref={sectionRef}
      style={{
        background: '#111720',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
      }}
    >
      {/* Shared styles: card base + responsive breakpoints */}
      <style>{`
        .testimonials-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 24px;
          align-items: stretch;
        }

        @media (max-width: 767px) {
          .testimonials-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
          .testimonials-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .testimonial-card {
            transition: none !important;
          }
        }
      `}</style>

      {/* Centered inner container */}
      <div style={{ maxWidth: 1280, margin: '0 auto' }}>

        {/* Section heading — no eyebrow label */}
        <h2
          style={{
            color: '#ffffff',
            fontSize: 48,
            fontWeight: 800,
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            textAlign: 'center',
            marginTop: 0,
            marginBottom: 60,
          }}
        >
          Founders Trust Vantro
        </h2>

        {/* 3-column card grid */}
        <div ref={cardsRef} className="testimonials-grid">
          {TESTIMONIALS.map((t) => (
            <TiltCard
              key={t.name}
              testimonial={t}
              reducedMotion={prefersReducedMotion}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
