'use client'

import { useRef, useEffect } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useReducedMotion } from 'framer-motion'

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

// ─── Types ─────────────────────────────────────────────────────────────────────

interface HeroStat {
  display: string
  label: string
  color: string
  // For counter animation: provide targetVal + formatter. null = no count.
  targetVal: number | null
  formatter: ((val: number) => string) | null
}

interface SmallStat {
  display: string
  label: string
  color: string
  targetVal: number | null
  formatter: ((val: number) => string) | null
}

// ─── Data ──────────────────────────────────────────────────────────────────────

const HERO: HeroStat = {
  display: '$2.4M',
  label: 'Saved in operational costs by customers in their first year',
  color: '#FFD700',
  targetVal: 2.4,
  formatter: (v: number) => `$${v.toFixed(1)}M`,
}

const SMALL_STATS: SmallStat[] = [
  {
    display: '22',
    label: 'Specialized AI agents, each with a dedicated function',
    color: '#FF6B35',
    targetVal: 22,
    formatter: (v: number) => `${Math.round(v)}`,
  },
  {
    display: '99.7%',
    label: 'Uptime SLA across all agents, all integrations',
    color: '#00D9FF',
    targetVal: 99.7,
    formatter: (v: number) => `${v.toFixed(1)}%`,
  },
  {
    display: '5 min',
    label: 'Average time from signup to first agent running',
    color: '#1FFFD6',
    targetVal: null,
    formatter: null,
  },
]

// ─── Component ─────────────────────────────────────────────────────────────────

export default function Stats() {
  const sectionRef = useRef<HTMLElement>(null)
  const heroNumRef = useRef<HTMLSpanElement>(null)
  const heroRowRef = useRef<HTMLDivElement>(null)
  const smallRowRef = useRef<HTMLDivElement>(null)
  const smallNumRefs = useRef<(HTMLSpanElement | null)[]>([])
  const reducedMotion = useReducedMotion()

  // ── Counter animation helper ──────────────────────────────────────────────
  function animateCounter(
    el: HTMLSpanElement,
    targetVal: number,
    formatter: (v: number) => string,
    trigger: Element,
    delay = 0
  ) {
    const obj = { val: 0 }
    gsap.to(obj, {
      val: targetVal,
      duration: 1.5,
      ease: 'power2.out',
      delay,
      scrollTrigger: {
        trigger,
        start: 'top 80%',
        once: true,
      },
      onUpdate() {
        el.textContent = formatter(obj.val)
      },
      onComplete() {
        el.textContent = formatter(targetVal)
      },
    })
  }

  // ── Entrance + counter animations ────────────────────────────────────────
  useEffect(() => {
    if (!sectionRef.current) return

    const ctx = gsap.context(() => {
      // Hero row entrance
      if (heroRowRef.current) {
        const heroEls = heroRowRef.current.querySelectorAll<HTMLElement>('[data-animate]')
        if (!reducedMotion) {
          gsap.fromTo(
            heroEls,
            { opacity: 0, y: 32 },
            {
              opacity: 1,
              y: 0,
              duration: 0.75,
              ease: 'power3.out',
              stagger: 0.12,
              scrollTrigger: {
                trigger: heroRowRef.current,
                start: 'top 82%',
                once: true,
              },
            }
          )
        } else {
          gsap.set(heroEls, { opacity: 1, y: 0 })
        }
      }

      // Small stats row entrance
      if (smallRowRef.current) {
        const smallEls = smallRowRef.current.querySelectorAll<HTMLElement>('[data-animate]')
        if (!reducedMotion) {
          gsap.fromTo(
            smallEls,
            { opacity: 0, y: 32 },
            {
              opacity: 1,
              y: 0,
              duration: 0.75,
              ease: 'power3.out',
              stagger: 0.12,
              scrollTrigger: {
                trigger: smallRowRef.current,
                start: 'top 82%',
                once: true,
              },
            }
          )
        } else {
          gsap.set(smallEls, { opacity: 1, y: 0 })
        }
      }

      // Hero counter
      if (
        heroNumRef.current &&
        HERO.targetVal !== null &&
        HERO.formatter !== null
      ) {
        if (!reducedMotion) {
          animateCounter(
            heroNumRef.current,
            HERO.targetVal,
            HERO.formatter,
            heroRowRef.current ?? sectionRef.current!
          )
        } else {
          heroNumRef.current.textContent = HERO.display
        }
      }

      // Small stat counters
      SMALL_STATS.forEach((stat, i) => {
        const el = smallNumRefs.current[i]
        if (!el || stat.targetVal === null || stat.formatter === null) return
        if (!reducedMotion) {
          animateCounter(
            el,
            stat.targetVal,
            stat.formatter,
            smallRowRef.current ?? sectionRef.current!,
            i * 0.12
          )
        } else {
          el.textContent = stat.display
        }
      })
    }, sectionRef)

    return () => ctx.revert()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reducedMotion])

  return (
    <section
      id="stats"
      ref={sectionRef}
      style={{
        background: '#0F1419',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: '0 auto',
        }}
      >
        {/* ── Row 1: Hero stat ─────────────────────────────────────────────── */}
        <div
          ref={heroRowRef}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 0,
          }}
          className="stats-hero-row"
        >
          {/* Large number */}
          <div data-animate style={{ opacity: 0, flexShrink: 0 }}>
            <span
              ref={heroNumRef}
              aria-label={HERO.display}
              style={{
                display: 'block',
                fontSize: 'clamp(4rem, 8vw, 7rem)',
                fontWeight: 900,
                lineHeight: 1,
                letterSpacing: '-0.04em',
                color: HERO.color,
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {HERO.display}
            </span>
          </div>

          {/* Divider line */}
          <div
            data-animate
            aria-hidden="true"
            style={{
              flexGrow: 1,
              height: 1,
              background: 'rgba(255,255,255,0.08)',
              marginLeft: 48,
              marginRight: 48,
              opacity: 0,
            }}
            className="stats-hero-divider"
          />

          {/* Label */}
          <p
            data-animate
            style={{
              maxWidth: 360,
              fontSize: 18,
              lineHeight: 1.6,
              color: 'rgba(255,255,255,0.55)',
              margin: 0,
              flexShrink: 0,
              alignSelf: 'center',
              opacity: 0,
            }}
          >
            {HERO.label}
          </p>
        </div>

        {/* ── Row 2: 3 smaller stats ───────────────────────────────────────── */}
        <div
          ref={smallRowRef}
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            marginTop: 64,
          }}
          className="stats-small-row"
        >
          {SMALL_STATS.map((stat, i) => (
            <div
              key={stat.label}
              style={{
                display: 'flex',
                alignItems: 'stretch',
                flex: 1,
              }}
            >
              {/* Stat block */}
              <div
                data-animate
                style={{
                  flex: 1,
                  opacity: 0,
                }}
                className="stats-small-item"
              >
                {/* Number */}
                <span
                  ref={(el) => { smallNumRefs.current[i] = el }}
                  aria-label={stat.display}
                  style={{
                    display: 'block',
                    fontSize: 64,
                    fontWeight: 900,
                    lineHeight: 1,
                    letterSpacing: '-0.04em',
                    color: stat.color,
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {stat.display}
                </span>

                {/* Label */}
                <p
                  style={{
                    margin: '8px 0 0',
                    fontSize: 15,
                    lineHeight: 1.5,
                    color: 'rgba(255,255,255,0.5)',
                    maxWidth: 200,
                  }}
                >
                  {stat.label}
                </p>
              </div>

              {/* Vertical divider between stats (not after last) */}
              {i < SMALL_STATS.length - 1 && (
                <div
                  aria-hidden="true"
                  style={{
                    width: 1,
                    background: 'rgba(255,255,255,0.08)',
                    alignSelf: 'stretch',
                    marginLeft: 48,
                    marginRight: 48,
                    minHeight: 80,
                  }}
                  className="stats-small-divider"
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── Responsive styles ──────────────────────────────────────────────── */}
      <style>{`
        @media (max-width: 767px) {
          .stats-hero-row {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 24px !important;
          }
          .stats-hero-divider {
            display: none !important;
          }
          .stats-hero-row p {
            max-width: 100% !important;
          }
          .stats-small-row {
            flex-direction: column !important;
            gap: 0 !important;
          }
          .stats-small-item {
            padding-bottom: 40px !important;
            margin-bottom: 40px !important;
            border-bottom: 1px solid rgba(255,255,255,0.08) !important;
          }
          .stats-small-row > div:last-child .stats-small-item {
            border-bottom: none !important;
            padding-bottom: 0 !important;
            margin-bottom: 0 !important;
          }
          .stats-small-divider {
            display: none !important;
          }
        }
      `}</style>
    </section>
  )
}
