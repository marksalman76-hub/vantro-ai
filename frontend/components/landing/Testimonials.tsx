'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

// ─── Data ─────────────────────────────────────────────────────────────────────

const METRIC_COLORS = ['#FF6B35', '#00D9FF', '#1FFFD6', '#FFD700'] as const

const TESTIMONIALS = [
  {
    quote:
      'Vantro replaced three full-time SDRs. Our pipeline grew 340% in 90 days while our team focused on closing, not prospecting.',
    name: 'Alexandra Kim',
    title: 'VP of Sales',
    company: 'NexGen Financial',
    rating: 5,
    metric: '340% pipeline growth',
    avatar: 'https://randomuser.me/api/portraits/women/32.jpg',
  },
  {
    quote:
      'The operations agents handle everything from invoice reconciliation to vendor communication. We saved 60 hours of manual work per week.',
    name: 'Roberto Fuentes',
    title: 'COO',
    company: 'Meridian Logistics',
    rating: 5,
    metric: '60hrs/week saved',
    avatar: 'https://randomuser.me/api/portraits/men/43.jpg',
  },
  {
    quote:
      'Setup took 4 minutes. Our support CSAT went from 72% to 96% within the first month. The agents actually understand context.',
    name: 'Pritha Bose',
    title: 'Head of Customer Experience',
    company: 'Cloudform Technologies',
    rating: 5,
    metric: '96% CSAT score',
    avatar: 'https://randomuser.me/api/portraits/women/54.jpg',
  },
  {
    quote:
      "We're a team of 8 competing against companies with 50+ people. Vantro is our unfair advantage. It's like having enterprise resources at startup speed.",
    name: 'David Okonkwo',
    title: 'Founder & CEO',
    company: 'Apex Analytics',
    rating: 5,
    metric: '8-person team, enterprise output',
    avatar: 'https://randomuser.me/api/portraits/men/76.jpg',
  },
]

const AUTO_ADVANCE_MS = 7000

// ─── Nav Button ───────────────────────────────────────────────────────────────

interface NavButtonProps {
  onClick: () => void
  direction: 'prev' | 'next'
}

function NavButton({ onClick, direction }: NavButtonProps) {
  const [hovered, setHovered] = useState(false)

  return (
    <button
      onClick={onClick}
      aria-label={direction === 'prev' ? 'Previous testimonial' : 'Next testimonial'}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 52,
        height: 52,
        borderRadius: '50%',
        background: hovered ? 'rgba(255,107,53,0.10)' : 'rgba(255,255,255,0.07)',
        border: `1px solid ${hovered ? 'rgba(255,107,53,0.50)' : 'rgba(255,255,255,0.12)'}`,
        color: '#ffffff',
        cursor: 'pointer',
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background 0.2s ease, border-color 0.2s ease',
        backdropFilter: 'blur(12px)',
      }}
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {direction === 'prev' ? (
          <path
            d="M12.5 15L7.5 10L12.5 5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ) : (
          <path
            d="M7.5 5L12.5 10L7.5 15"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
      </svg>
    </button>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Testimonials() {
  const [activeIndex, setActiveIndex] = useState(0)
  const [direction, setDirection] = useState<1 | -1>(1)
  const [paused, setPaused] = useState(false)
  const [progressKey, setProgressKey] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const goTo = useCallback((index: number, dir: 1 | -1) => {
    setDirection(dir)
    setActiveIndex(index)
    setProgressKey((k) => k + 1)
  }, [])

  const goPrev = useCallback(() => {
    const next = (activeIndex - 1 + TESTIMONIALS.length) % TESTIMONIALS.length
    goTo(next, -1)
  }, [activeIndex, goTo])

  const goNext = useCallback(() => {
    const next = (activeIndex + 1) % TESTIMONIALS.length
    goTo(next, 1)
  }, [activeIndex, goTo])

  // Auto-advance
  useEffect(() => {
    if (paused) return
    intervalRef.current = setInterval(() => {
      setDirection(1)
      setActiveIndex((prev) => {
        const next = (prev + 1) % TESTIMONIALS.length
        setProgressKey((k) => k + 1)
        return next
      })
    }, AUTO_ADVANCE_MS)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [paused, activeIndex])

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') goPrev()
      if (e.key === 'ArrowRight') goNext()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [goPrev, goNext])

  const testimonial = TESTIMONIALS[activeIndex]
  const metricColor = METRIC_COLORS[activeIndex]

  return (
    <section
      id="testimonials"
      style={{
        background: '#1A1F2E',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
      }}
    >
      {/* Section Header */}
      <div style={{ textAlign: 'center', marginBottom: 64 }}>
        <p
          style={{
            color: '#00D9FF',
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            marginBottom: 16,
          }}
        >
          SOCIAL PROOF
        </p>
        <h2
          style={{
            color: '#ffffff',
            fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
            fontWeight: 800,
            lineHeight: 1.1,
            marginBottom: 16,
          }}
        >
          What Our Customers Say
        </h2>
        <p style={{ color: '#9ca3af', fontSize: 18, lineHeight: 1.6 }}>
          500+ companies trust Vantro to power their AI workforce.
        </p>
      </div>

      {/* Carousel area */}
      <div
        style={{ maxWidth: 900, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
      >
        {/* Progress bar */}
        <div
          style={{
            width: '100%',
            height: 2,
            background: 'rgba(255,255,255,0.10)',
            borderRadius: 99,
            marginBottom: 28,
            overflow: 'hidden',
          }}
        >
          <div
            key={`progress-${progressKey}-${activeIndex}`}
            style={{
              height: '100%',
              background: metricColor,
              borderRadius: 99,
              animation: paused
                ? 'none'
                : `testimonialProgress ${AUTO_ADVANCE_MS}ms linear forwards`,
              width: paused ? undefined : '0%',
            }}
          />
        </div>

        {/* Card + nav row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, width: '100%' }}>
          <NavButton direction="prev" onClick={goPrev} />

          {/* Card wrapper */}
          <div style={{ flex: 1, position: 'relative', minHeight: 340 }}>
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, x: direction * 80 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: direction * -80 }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.10)',
                  borderRadius: 28,
                  padding: '52px 48px',
                  backdropFilter: 'blur(20px)',
                  boxShadow: '0 40px 80px rgba(0,0,0,0.3)',
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  flexDirection: 'row',
                  gap: 40,
                }}
              >
                {/* LEFT — 60% */}
                <div
                  style={{
                    flex: '0 0 60%',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  {/* Stars */}
                  <div
                    aria-label={`${testimonial.rating} out of 5 stars`}
                    style={{ display: 'flex', gap: 4, marginBottom: 28 }}
                  >
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <span
                        key={i}
                        aria-hidden="true"
                        style={{ color: '#FFD700', fontSize: 20, lineHeight: 1 }}
                      >
                        ★
                      </span>
                    ))}
                  </div>

                  {/* Quote */}
                  <blockquote
                    style={{
                      color: '#ffffff',
                      fontSize: 21,
                      fontStyle: 'italic',
                      lineHeight: 1.7,
                      flex: 1,
                      margin: 0,
                    }}
                  >
                    &ldquo;{testimonial.quote}&rdquo;
                  </blockquote>

                  {/* Metric badge */}
                  <span
                    style={{
                      background: `${metricColor}22`,
                      border: `1px solid ${metricColor}44`,
                      color: metricColor,
                      padding: '10px 20px',
                      borderRadius: 99,
                      fontSize: 14,
                      fontWeight: 700,
                      display: 'inline-block',
                      marginTop: 28,
                      alignSelf: 'flex-start',
                    }}
                  >
                    {testimonial.metric}
                  </span>
                </div>

                {/* RIGHT — 40% */}
                <div
                  style={{
                    flex: '0 0 40%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  {/* Avatar */}
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    width={120}
                    height={120}
                    style={{
                      borderRadius: '50%',
                      border: `3px solid ${metricColor}55`,
                      boxShadow: `0 0 40px ${metricColor}28`,
                      background: '#1A1F2E',
                      objectFit: 'cover',
                    }}
                  />

                  {/* Identity */}
                  <div style={{ textAlign: 'center' }}>
                    <p
                      style={{
                        color: '#ffffff',
                        fontSize: 18,
                        fontWeight: 700,
                        marginTop: 16,
                        textAlign: 'center',
                      }}
                    >
                      {testimonial.name}
                    </p>
                    <p
                      style={{
                        color: '#9ca3af',
                        fontSize: 14,
                        marginTop: 4,
                        textAlign: 'center',
                      }}
                    >
                      {testimonial.title}
                    </p>
                    <p
                      style={{
                        color: metricColor,
                        fontSize: 13,
                        fontWeight: 600,
                        textAlign: 'center',
                        marginTop: 4,
                      }}
                    >
                      {testimonial.company}
                    </p>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          <NavButton direction="next" onClick={goNext} />
        </div>

        {/* Dot indicators */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            marginTop: 36,
          }}
          role="tablist"
          aria-label="Testimonial navigation"
        >
          {TESTIMONIALS.map((_, i) => (
            <button
              key={i}
              role="tab"
              aria-selected={i === activeIndex}
              aria-label={`Go to testimonial ${i + 1}`}
              onClick={() => goTo(i, i > activeIndex ? 1 : -1)}
              style={{
                width: i === activeIndex ? 28 : 10,
                height: 10,
                borderRadius: 99,
                background: i === activeIndex ? '#FF6B35' : 'rgba(255,255,255,0.20)',
                border: 'none',
                cursor: 'pointer',
                padding: 0,
                transition: 'width 0.3s ease, background 0.3s ease',
              }}
            />
          ))}
        </div>
      </div>

      {/* Progress bar animation */}
      <style>{`
        @keyframes testimonialProgress {
          from { width: 0%; }
          to   { width: 100%; }
        }
      `}</style>
    </section>
  )
}
