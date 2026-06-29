'use client'

import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import { useReducedMotion } from 'framer-motion'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// ─── Data ─────────────────────────────────────────────────────────────────────

const AGENT_LIST = [
  { label: 'Sales Agent',       color: '#00D9FF' },
  { label: 'Support Agent',     color: '#1FFFD6' },
  { label: 'Finance Agent',     color: '#FF6B35' },
  { label: 'Ops Agent',         color: '#FFD700' },
  { label: 'Engineering Agent', color: '#00D9FF' },
  { label: 'Marketing Agent',   color: '#1FFFD6' },
]

const STAT_CHIPS = [
  '47 leads qualified today',
  '1,204 tickets resolved',
  '99.7% uptime',
]

const SETUP_STEPS = [
  '1. Connect your tools',
  '2. Pick your agents',
  '3. Go live',
]

const INTEGRATION_BADGES = [
  { abbr: 'SF', color: '#00A1E0' },
  { abbr: 'HS', color: '#FF7A59' },
  { abbr: 'ZD', color: '#00D9FF' },
  { abbr: 'SL', color: '#E01E5A' },
  { abbr: 'JI', color: '#0052CC' },
  { abbr: 'ST', color: '#635BFF' },
  { abbr: 'GH', color: '#B084FF' },
  { abbr: 'NO', color: '#9CA3AF' },
]

// ─── Component ────────────────────────────────────────────────────────────────

export default function Features() {
  const sectionRef = useRef<HTMLElement>(null)
  const reduce = useReducedMotion()

  useGSAP(
    () => {
      if (reduce) return
      gsap.from('.bento-cell', {
        opacity: 0,
        y: 40,
        scale: 0.96,
        duration: 0.7,
        ease: 'power3.out',
        stagger: 0.1,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
          once: true,
        },
      })
    },
    { scope: sectionRef },
  )

  return (
    <>
      {/* ─── Scoped hover styles ─────────────────────────────────────────── */}
      <style>{`
        .bento-cell {
          transition:
            border-color 0.25s ease,
            box-shadow 0.25s ease;
        }
        .bento-cell-a:hover {
          border-color: rgba(255, 107, 53, 0.3) !important;
          box-shadow: 0 20px 60px rgba(255, 107, 53, 0.08);
        }
        .bento-cell-c:hover {
          border-color: rgba(0, 217, 255, 0.3) !important;
        }
        .bento-cell-d:hover {
          border-color: rgba(31, 255, 214, 0.3) !important;
        }
        .agent-cta-link:hover {
          text-decoration: underline;
        }
      `}</style>

      {/* ─── Section ─────────────────────────────────────────────────────── */}
      <section
        id="features"
        ref={sectionRef}
        style={{
          background: '#111720',
          paddingTop: 120,
          paddingBottom: 120,
          paddingLeft: 24,
          paddingRight: 24,
        }}
      >
        {/* Inner container */}
        <div
          style={{
            maxWidth: 1280,
            margin: '0 auto',
          }}
        >
          {/* Section heading */}
          <h2
            style={{
              color: '#ffffff',
              fontSize: 'clamp(48px, 4.5vw, 56px)',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 1.1,
              textAlign: 'center',
              marginBottom: 56,
              marginTop: 0,
            }}
          >
            Your AI Workforce, Working
          </h2>

          {/* ─── Bento Grid ──────────────────────────────────────────────── */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gridTemplateRows: 'auto auto',
              gap: 16,
              gridAutoFlow: 'dense',
            }}
            className="bento-grid"
          >
            {/* ── Cell A — Autonomous Operations (col-span-2, row-span-1) ── */}
            <div
              className="bento-cell bento-cell-a"
              style={{
                gridColumn: 'span 2',
                gridRow: 'span 1',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 24,
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                padding: 40,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Ambient orange orb — top-right */}
              <div
                aria-hidden
                style={{
                  position: 'absolute',
                  top: -60,
                  right: -60,
                  width: 280,
                  height: 280,
                  borderRadius: '50%',
                  background:
                    'radial-gradient(circle, rgba(255,107,53,0.15) 0%, rgba(255,107,53,0) 70%)',
                  pointerEvents: 'none',
                }}
              />

              {/* Live-status indicator — top-right */}
              <div
                style={{
                  position: 'absolute',
                  top: 28,
                  right: 32,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                {/* Pulsing green dot */}
                <span
                  style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: '#22c55e',
                    boxShadow: '0 0 0 0 rgba(34,197,94,0.5)',
                    animation: 'pulse-dot 1.8s ease-out infinite',
                  }}
                />
                <span
                  style={{
                    color: 'rgba(255,255,255,0.55)',
                    fontSize: 12,
                    fontWeight: 500,
                  }}
                >
                  22 agents running
                </span>
              </div>

              {/* Headline */}
              <h3
                style={{
                  color: '#ffffff',
                  fontSize: 28,
                  fontWeight: 700,
                  lineHeight: 1.25,
                  margin: '0 0 12px',
                  maxWidth: '80%',
                }}
              >
                Your entire ops on autopilot.
              </h3>

              {/* Subtext */}
              <p
                style={{
                  color: 'rgba(255,255,255,0.55)',
                  fontSize: 15,
                  lineHeight: 1.6,
                  margin: '0 0 32px',
                  maxWidth: 520,
                }}
              >
                Sales, support, finance, and engineering agents working in
                parallel, 24 hours a day.
              </p>

              {/* Stat chips */}
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: 8,
                }}
              >
                {STAT_CHIPS.map((chip) => (
                  <span
                    key={chip}
                    style={{
                      background: 'rgba(255,255,255,0.06)',
                      borderRadius: 9999,
                      paddingTop: 6,
                      paddingBottom: 6,
                      paddingLeft: 12,
                      paddingRight: 12,
                      fontSize: 12,
                      color: 'rgba(255,255,255,0.6)',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {chip}
                  </span>
                ))}
              </div>
            </div>

            {/* ── Cell B — 22 AI Agents (col-span-1, row-span-2) ──────────── */}
            <div
              className="bento-cell bento-cell-b"
              style={{
                gridColumn: 'span 1',
                gridRow: 'span 2',
                background:
                  'linear-gradient(160deg, rgba(255,107,53,0.12) 0%, rgba(255,107,53,0.03) 100%)',
                border: '1px solid rgba(255,107,53,0.2)',
                borderRadius: 24,
                padding: '40px 32px',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Big stat number */}
              <span
                style={{
                  color: '#FF6B35',
                  fontSize: 96,
                  fontWeight: 900,
                  lineHeight: 1,
                  letterSpacing: '-0.05em',
                  display: 'block',
                }}
              >
                22
              </span>

              {/* Label */}
              <span
                style={{
                  color: '#ffffff',
                  fontSize: 18,
                  fontWeight: 600,
                  marginTop: 8,
                  display: 'block',
                }}
              >
                Specialized AI Agents
              </span>

              {/* Subtext */}
              <p
                style={{
                  color: 'rgba(255,255,255,0.5)',
                  fontSize: 14,
                  lineHeight: 1.55,
                  marginTop: 8,
                  marginBottom: 28,
                }}
              >
                Each one trained for a specific role in your business.
              </p>

              {/* Agent list */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 10,
                  flex: 1,
                }}
              >
                {AGENT_LIST.map(({ label, color }) => (
                  <div
                    key={label}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                    }}
                  >
                    <span
                      aria-hidden
                      style={{
                        width: 7,
                        height: 7,
                        borderRadius: '50%',
                        background: color,
                        flexShrink: 0,
                        boxShadow: `0 0 6px ${color}66`,
                      }}
                    />
                    <span
                      style={{
                        color: 'rgba(255,255,255,0.65)',
                        fontSize: 13,
                      }}
                    >
                      {label}
                    </span>
                  </div>
                ))}
              </div>

              {/* CTA link */}
              <a
                href="#agents"
                className="agent-cta-link"
                style={{
                  display: 'inline-block',
                  marginTop: 28,
                  color: '#FF6B35',
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: 'pointer',
                  textDecoration: 'none',
                }}
              >
                See all agents →
              </a>
            </div>

            {/* ── Cell C — Deploy in 5 Minutes (col-span-1, row-span-1) ───── */}
            <div
              className="bento-cell bento-cell-c"
              style={{
                gridColumn: 'span 1',
                gridRow: 'span 1',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 24,
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                padding: 32,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Ambient cyan orb — bottom-left */}
              <div
                aria-hidden
                style={{
                  position: 'absolute',
                  bottom: -50,
                  left: -50,
                  width: 220,
                  height: 220,
                  borderRadius: '50%',
                  background:
                    'radial-gradient(circle, rgba(0,217,255,0.14) 0%, rgba(0,217,255,0) 70%)',
                  pointerEvents: 'none',
                }}
              />

              {/* Stat */}
              <span
                style={{
                  color: '#00D9FF',
                  fontSize: 48,
                  fontWeight: 800,
                  lineHeight: 1,
                  display: 'block',
                }}
              >
                5 min
              </span>

              {/* Label */}
              <span
                style={{
                  color: '#ffffff',
                  fontSize: 16,
                  fontWeight: 600,
                  marginTop: 4,
                  display: 'block',
                }}
              >
                Average setup time
              </span>

              {/* Steps */}
              <div
                style={{
                  marginTop: 20,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                }}
              >
                {SETUP_STEPS.map((step) => (
                  <span
                    key={step}
                    style={{
                      color: 'rgba(255,255,255,0.55)',
                      fontSize: 13,
                      lineHeight: 1.5,
                    }}
                  >
                    {step}
                  </span>
                ))}
              </div>
            </div>

            {/* ── Cell D — 200+ Integrations (col-span-1, row-span-1) ──────── */}
            <div
              className="bento-cell bento-cell-d"
              style={{
                gridColumn: 'span 1',
                gridRow: 'span 1',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 24,
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                padding: 32,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Ambient teal orb — top-right */}
              <div
                aria-hidden
                style={{
                  position: 'absolute',
                  top: -50,
                  right: -50,
                  width: 220,
                  height: 220,
                  borderRadius: '50%',
                  background:
                    'radial-gradient(circle, rgba(31,255,214,0.12) 0%, rgba(31,255,214,0) 70%)',
                  pointerEvents: 'none',
                }}
              />

              {/* Stat */}
              <span
                style={{
                  color: '#1FFFD6',
                  fontSize: 48,
                  fontWeight: 800,
                  lineHeight: 1,
                  display: 'block',
                }}
              >
                200+
              </span>

              {/* Label */}
              <span
                style={{
                  color: '#ffffff',
                  fontSize: 16,
                  fontWeight: 600,
                  marginTop: 4,
                  display: 'block',
                }}
              >
                Native Integrations
              </span>

              {/* Badge grid */}
              <div
                style={{
                  marginTop: 20,
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 36px)',
                  gap: 8,
                }}
              >
                {INTEGRATION_BADGES.map(({ abbr, color }) => (
                  <div
                    key={abbr}
                    title={abbr}
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 8,
                      background: `${color}33`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 11,
                      fontWeight: 700,
                      color: color,
                      flexShrink: 0,
                    }}
                  >
                    {abbr}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Keyframe: pulsing dot ───────────────────────────────────────────── */}
      <style>{`
        @keyframes pulse-dot {
          0% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.55);
          }
          70% {
            box-shadow: 0 0 0 8px rgba(34, 197, 94, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
          }
        }

        /* ── Mobile: single-column stack ── */
        @media (max-width: 767px) {
          .bento-grid {
            grid-template-columns: 1fr !important;
            grid-template-rows: auto !important;
          }
          .bento-grid .bento-cell {
            grid-column: span 1 !important;
            grid-row: span 1 !important;
          }
        }
      `}</style>
    </>
  )
}
