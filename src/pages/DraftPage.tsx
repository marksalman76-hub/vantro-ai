'use client'

import { useState } from 'react'
import { Cpu, BrainCircuit, ShieldCheck } from 'lucide-react'

// ─── DRAFT A ──────────────────────────────────────────────────────────────────

function DraftA() {
  return (
    <section
      style={{
        minHeight: '80vh',
        background: 'oklch(0.10 0 0)',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Label */}
      <span
        style={{
          position: 'absolute',
          top: 16,
          left: 32,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.15em',
          color: 'rgba(255,255,255,0.40)',
          zIndex: 20,
          pointerEvents: 'none',
        }}
      >
        DRAFT A — CHROME TYPE + LIGHT RAYS
      </span>

      {/* Scanline overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.018) 2px, rgba(255,255,255,0.018) 3px)',
          animation: 'scanMove 8s linear infinite',
          pointerEvents: 'none',
          zIndex: 1,
        }}
      />

      {/* Light rays */}
      {[
        { right: '42%', width: 120, opacity: 0.07, animDelay: '0s', anim: 'rayPulse' },
        { right: '28%', width: 80,  opacity: 0.09, animDelay: '1.2s', anim: 'rayPulse2' },
        { right: '15%', width: 160, opacity: 0.12, animDelay: '2.4s', anim: 'rayPulse' },
        { right: '5%',  width: 50,  opacity: 0.07, animDelay: '3.6s', anim: 'rayPulse2' },
      ].map((ray, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: 0,
            right: ray.right,
            width: ray.width,
            height: '100%',
            background: 'linear-gradient(180deg, rgba(255,255,255,0.9) 0%, transparent 70%)',
            clipPath: 'polygon(40% 0%, 60% 0%, 120% 100%, -20% 100%)',
            opacity: ray.opacity,
            animation: `${ray.anim} 4s ease-in-out infinite`,
            animationDelay: ray.animDelay,
            pointerEvents: 'none',
            zIndex: 1,
          }}
        />
      ))}

      {/* Content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: 1280,
          margin: '0 auto',
          padding: '80px 48px',
        }}
      >
        {/* H1 line 1 */}
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(3.5rem, 6vw, 6rem)',
            fontWeight: 700,
            lineHeight: 1.0,
            letterSpacing: '-0.03em',
            margin: 0,
            padding: 0,
            background: 'linear-gradient(180deg, #ffffff 0%, #d0d0d0 35%, #888888 65%, #4a4a4a 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Deploy a workforce
        </h1>
        {/* H1 line 2 */}
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(3.5rem, 6vw, 6rem)',
            fontWeight: 700,
            lineHeight: 1.0,
            letterSpacing: '-0.03em',
            margin: '0 0 32px',
            background: 'linear-gradient(180deg, #d0d0d0 0%, #808080 50%, #3a3a3a 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          that never sleeps.
        </h1>

        {/* Subtext */}
        <p
          style={{
            color: 'oklch(0.70 0 0)',
            fontSize: 18,
            lineHeight: 1.6,
            maxWidth: 520,
            marginBottom: 40,
          }}
        >
          Autonomous AI agents that handle your operations, sales, support, and
          more — 24 hours a day, without interruption.
        </p>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a
            href="/pricing"
            style={{
              background: 'linear-gradient(90deg, #fff 0%, #e8e8e8 100%)',
              color: '#000',
              borderRadius: 9999,
              padding: '12px 32px',
              fontWeight: 600,
              fontSize: 15,
              border: 'none',
              cursor: 'pointer',
              boxShadow:
                '0 0 30px rgba(255,255,255,0.25), inset 0 1px 0 rgba(255,255,255,0.9)',
              transition: 'box-shadow 0.2s ease, transform 0.2s ease',
              textDecoration: 'none',
              display: 'inline-block',
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.boxShadow =
                '0 0 50px rgba(255,255,255,0.45), inset 0 1px 0 rgba(255,255,255,1)'
              el.style.transform = 'translateY(-1px)'
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.boxShadow =
                '0 0 30px rgba(255,255,255,0.25), inset 0 1px 0 rgba(255,255,255,0.9)'
              el.style.transform = 'translateY(0)'
            }}
          >
            Deploy your team
          </a>
          <a
            href="#how-it-works"
            style={{
              background: 'transparent',
              color: 'rgba(255,255,255,0.70)',
              borderRadius: 9999,
              padding: '12px 32px',
              fontWeight: 500,
              fontSize: 15,
              border: '1px solid rgba(255,255,255,0.18)',
              cursor: 'pointer',
              transition: 'border-color 0.2s ease, color 0.2s ease',
              textDecoration: 'none',
              display: 'inline-block',
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(255,255,255,0.40)'
              el.style.color = '#fff'
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLAnchorElement
              el.style.borderColor = 'rgba(255,255,255,0.18)'
              el.style.color = 'rgba(255,255,255,0.70)'
            }}
          >
            See how it works
          </a>
        </div>
      </div>
    </section>
  )
}

// ─── DRAFT B ──────────────────────────────────────────────────────────────────

const CARDS = [
  {
    Icon: Cpu,
    category: 'Architecture',
    title: 'Autonomous by Design',
    body: 'Every agent acts independently, escalating only when human judgment is required. No micromanagement needed.',
  },
  {
    Icon: BrainCircuit,
    category: 'Memory',
    title: 'One Shared Memory',
    body: 'All agents share a single knowledge graph. Context flows freely — no repeated briefings, no lost context.',
  },
  {
    Icon: ShieldCheck,
    category: 'Security',
    title: 'Enterprise-Grade Security',
    body: 'Financial guardrails baked in. Agents can never spend, scale paid services, or sign agreements without human approval.',
  },
]

const metalCardBase: React.CSSProperties = {
  background: 'oklch(0.18 0 0)',
  borderRadius: 16,
  padding: 28,
  position: 'relative',
  overflow: 'hidden',
  boxShadow: `
    0 0 0 1px rgba(255,255,255,0.08),
    0 1px 0 0 rgba(255,255,255,0.30),
    0 20px 60px rgba(0,0,0,0.6),
    inset 0 1px 0 rgba(255,255,255,0.12)
  `,
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  flex: 1,
}

const metalCardHover: React.CSSProperties = {
  ...metalCardBase,
  boxShadow: `
    0 0 0 1px rgba(255,255,255,0.18),
    0 1px 0 0 rgba(255,255,255,0.50),
    0 30px 80px rgba(0,0,0,0.7),
    0 0 60px rgba(255,255,255,0.07),
    inset 0 1px 0 rgba(255,255,255,0.20)
  `,
  transform: 'translateY(-8px)',
}

const currentCardStyle: React.CSSProperties = {
  background: 'oklch(0.16 0 0)',
  borderRadius: 16,
  padding: 28,
  border: '1px solid rgba(255,255,255,0.06)',
  flex: 1,
}

interface MetalCardProps {
  Icon: React.ElementType
  category: string
  title: string
  body: string
}

function MetalCard({ Icon, category, title, body }: MetalCardProps) {
  const [hovered, setHovered] = useState(false)
  return (
    <div
      style={hovered ? metalCardHover : metalCardBase}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Icon area */}
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.03))',
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.20), inset 0 -1px 0 rgba(0,0,0,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Icon size={18} style={{ color: 'rgba(255,255,255,0.70)' }} />
      </div>

      {/* Category chip */}
      <span
        style={{
          display: 'inline-block',
          marginTop: 16,
          background:
            'repeating-linear-gradient(90deg, rgba(255,255,255,0.04) 0px, rgba(255,255,255,0.04) 1px, transparent 1px, transparent 4px)',
          border: '1px solid rgba(255,255,255,0.12)',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10,
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
          color: 'rgba(255,255,255,0.55)',
          padding: '2px 8px',
          borderRadius: 4,
        }}
      >
        {category}
      </span>

      <h3
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontWeight: 600,
          fontSize: 18,
          color: '#fff',
          margin: '16px 0 8px',
        }}
      >
        {title}
      </h3>
      <p style={{ color: 'rgba(255,255,255,0.50)', fontSize: 14, lineHeight: 1.6, margin: 0 }}>
        {body}
      </p>
    </div>
  )
}

function DraftB() {
  return (
    <section
      style={{
        padding: '96px 48px',
        background: 'oklch(0.14 0 0)',
        position: 'relative',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Label */}
      <span
        style={{
          position: 'absolute',
          top: 16,
          left: 32,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.15em',
          color: 'rgba(255,255,255,0.40)',
        }}
      >
        DRAFT B — METAL CARD SYSTEM
      </span>

      <div style={{ maxWidth: 1280, margin: '0 auto' }}>
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(2rem, 3.5vw, 3rem)',
            fontWeight: 700,
            color: '#fff',
            letterSpacing: '-0.025em',
            marginBottom: 48,
          }}
        >
          Built for enterprise scale
        </h2>

        {/* BEFORE / AFTER comparison for one card */}
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: 'flex', gap: 24, alignItems: 'stretch' }}>
            {/* BEFORE */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 10,
                  letterSpacing: '0.12em',
                  color: 'rgba(255,255,255,0.35)',
                  marginBottom: 8,
                  textTransform: 'uppercase',
                }}
              >
                BEFORE
              </div>
              <div style={currentCardStyle}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 10,
                    background: 'rgba(255,255,255,0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Cpu size={18} style={{ color: 'rgba(255,255,255,0.40)' }} />
                </div>
                <h3
                  style={{
                    fontFamily: "'Space Grotesk', sans-serif",
                    fontWeight: 600,
                    fontSize: 18,
                    color: 'rgba(255,255,255,0.80)',
                    margin: '20px 0 8px',
                  }}
                >
                  Autonomous by Design
                </h3>
                <p style={{ color: 'rgba(255,255,255,0.40)', fontSize: 14, lineHeight: 1.6, margin: 0 }}>
                  Every agent acts independently, escalating only when human judgment is required.
                </p>
              </div>
            </div>

            {/* Separator */}
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                paddingTop: 24,
              }}
            >
              <div style={{ width: 1, flex: 1, background: 'rgba(255,255,255,0.08)' }} />
              <span
                style={{
                  color: 'rgba(255,255,255,0.25)',
                  fontSize: 10,
                  fontFamily: 'JetBrains Mono, monospace',
                  letterSpacing: '0.1em',
                  writingMode: 'vertical-rl',
                }}
              >
                →
              </span>
              <div style={{ width: 1, flex: 1, background: 'rgba(255,255,255,0.08)' }} />
            </div>

            {/* AFTER */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 10,
                  letterSpacing: '0.12em',
                  color: 'rgba(255,255,255,0.35)',
                  marginBottom: 8,
                  textTransform: 'uppercase',
                }}
              >
                AFTER
              </div>
              <MetalCard
                Icon={Cpu}
                category="Architecture"
                title="Autonomous by Design"
                body="Every agent acts independently, escalating only when human judgment is required. No micromanagement needed."
              />
            </div>
          </div>
        </div>

        {/* Divider */}
        <div
          style={{
            borderTop: '1px solid rgba(255,255,255,0.06)',
            marginBottom: 40,
          }}
        />

        {/* 3-column new cards */}
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.12em',
            color: 'rgba(255,255,255,0.35)',
            textTransform: 'uppercase',
            marginBottom: 20,
          }}
        >
          All three cards (new style — hover to see effect)
        </p>
        <div style={{ display: 'flex', gap: 24 }}>
          {CARDS.map((c) => (
            <MetalCard key={c.title} Icon={c.Icon} category={c.category} title={c.title} body={c.body} />
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── DRAFT C ──────────────────────────────────────────────────────────────────

const AGENTS = [
  {
    name: 'Atlas',
    category: 'Operations',
    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-01-atlas-HcT8hzhWCVimMA7hv773NB.webp',
  },
  {
    name: 'Echo',
    category: 'Support',
    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-02-echo-jBseNuruo6zVaNEwKn4uiC.webp',
  },
  {
    name: 'Nova',
    category: 'Sales',
    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-13-nova-RjP6GCP9dydGjYzxoGqUS4.webp',
  },
  {
    name: 'Forge',
    category: 'Engineering',
    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-06-forge-74Qoi5iZ6HSHfAKCtpmGiV.webp',
  },
  {
    name: 'Sentinel',
    category: 'Security',
    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-07-sentinel-R2z9W7XcosMCmKrgyy5egK.webp',
  },
]

interface AgentCardProps {
  agent: (typeof AGENTS)[0]
  variant: 'before' | 'after'
}

function AgentCard({ agent, variant }: AgentCardProps) {
  const [hovered, setHovered] = useState(false)
  const isAfter = variant === 'after'

  return (
    <div
      style={{
        width: 200,
        borderRadius: 16,
        overflow: 'hidden',
        position: 'relative',
        flexShrink: 0,
        cursor: 'default',
        transition: 'transform 0.3s ease',
        transform: hovered && isAfter ? 'translateY(-6px)' : 'none',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Image */}
      <img
        src={agent.img}
        alt={agent.name}
        style={{
          width: '100%',
          height: 260,
          objectFit: 'cover',
          display: 'block',
          filter: isAfter ? 'none' : 'brightness(0.75) saturate(0.8)',
        }}
      />

      {/* Uplight overlay — AFTER only, on hover */}
      {isAfter && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(ellipse 140% 80% at 50% 120%, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.08) 40%, transparent 70%)',
            mixBlendMode: 'screen',
            opacity: hovered ? 1 : 0,
            transition: 'opacity 0.4s ease',
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Vignette — always */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: isAfter
            ? 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 40%, transparent 70%)'
            : 'linear-gradient(to top, rgba(0,0,0,0.90) 0%, rgba(0,0,0,0.50) 50%, rgba(0,0,0,0.10) 100%)',
          pointerEvents: 'none',
        }}
      />

      {/* Rim light top — AFTER only, on hover */}
      {isAfter && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 1,
            background:
              'linear-gradient(90deg, transparent, rgba(255,255,255,0.6) 50%, transparent)',
            opacity: hovered ? 1 : 0,
            transition: 'opacity 0.4s ease',
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Bottom info */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          padding: 16,
        }}
      >
        <span
          style={{
            display: 'inline-block',
            background:
              'repeating-linear-gradient(90deg, rgba(255,255,255,0.06) 0px, rgba(255,255,255,0.06) 1px, transparent 1px, transparent 4px)',
            border: '1px solid rgba(255,255,255,0.10)',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 10,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.60)',
            padding: '3px 8px',
            borderRadius: 4,
          }}
        >
          {agent.category}
        </span>

        <div
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: 20,
            marginTop: 6,
            ...(isAfter && hovered
              ? {
                  background: 'linear-gradient(90deg, #fff, #aaa)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }
              : { color: '#fff' }),
          }}
        >
          {agent.name}
        </div>
      </div>
    </div>
  )
}

function DraftC() {
  return (
    <section
      style={{
        padding: '96px 0',
        background: 'oklch(0.10 0 0)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Label */}
      <span
        style={{
          position: 'absolute',
          top: 16,
          left: 32,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.15em',
          color: 'rgba(255,255,255,0.40)',
          zIndex: 20,
        }}
      >
        DRAFT C — AGENT UPLIGHTING + EDGE FOG
      </span>

      {/* Edge fog — left */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: 128,
          background: 'linear-gradient(90deg, oklch(0.10 0 0), transparent)',
          zIndex: 10,
          pointerEvents: 'none',
        }}
      />
      {/* Edge fog — right */}
      <div
        style={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: 128,
          background: 'linear-gradient(270deg, oklch(0.10 0 0), transparent)',
          zIndex: 10,
          pointerEvents: 'none',
        }}
      />

      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 48px' }}>
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(2rem, 3.5vw, 3rem)',
            fontWeight: 700,
            color: '#fff',
            letterSpacing: '-0.025em',
            marginBottom: 12,
          }}
        >
          Meet your AI workforce
        </h2>
        <p
          style={{
            color: 'rgba(255,255,255,0.50)',
            fontSize: 16,
            marginBottom: 48,
          }}
        >
          Hover each agent to see the uplighting effect.
        </p>

        {/* BEFORE / AFTER single agent comparison */}
        <div style={{ display: 'flex', gap: 32, alignItems: 'flex-end', marginBottom: 56 }}>
          <div>
            <div
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: 10,
                letterSpacing: '0.12em',
                color: 'rgba(255,255,255,0.35)',
                marginBottom: 8,
                textTransform: 'uppercase',
              }}
            >
              BEFORE — flat vignette
            </div>
            <AgentCard agent={AGENTS[0]} variant="before" />
          </div>

          <div
            style={{
              alignSelf: 'center',
              color: 'rgba(255,255,255,0.25)',
              fontSize: 24,
              fontFamily: 'JetBrains Mono, monospace',
            }}
          >
            →
          </div>

          <div>
            <div
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: 10,
                letterSpacing: '0.12em',
                color: 'rgba(255,255,255,0.35)',
                marginBottom: 8,
                textTransform: 'uppercase',
              }}
            >
              AFTER — hover to see uplight
            </div>
            <AgentCard agent={AGENTS[0]} variant="after" />
          </div>
        </div>

        {/* Divider */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', marginBottom: 40 }} />

        {/* 5-agent row */}
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.12em',
            color: 'rgba(255,255,255,0.35)',
            textTransform: 'uppercase',
            marginBottom: 20,
          }}
        >
          All agents — new style (hover each)
        </p>
        <div style={{ display: 'flex', gap: 20, justifyContent: 'center' }}>
          {AGENTS.map((agent) => (
            <AgentCard key={agent.name} agent={agent} variant="after" />
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── PAGE ROOT ────────────────────────────────────────────────────────────────

export function DraftPage() {
  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @keyframes scanMove {
          0%   { transform: translateY(0); }
          100% { transform: translateY(60px); }
        }
        @keyframes rayPulse {
          0%, 100% { opacity: 0.05; }
          50%       { opacity: 0.14; }
        }
        @keyframes rayPulse2 {
          0%, 100% { opacity: 0.08; }
          50%       { opacity: 0.18; }
        }
      `}</style>

      {/* Page header */}
      <div
        style={{
          padding: '40px 48px 32px',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.15em',
            color: 'rgba(255,255,255,0.30)',
            marginBottom: 8,
            textTransform: 'uppercase',
          }}
        >
          Vantro.AI — Aesthetic Draft Review
        </p>
        <p style={{ color: 'rgba(255,255,255,0.50)', fontSize: 14, margin: 0 }}>
          Three proposed enhancement directions. Review each, then approve to apply live.
        </p>
      </div>

      <DraftA />
      <DraftB />
      <DraftC />
    </div>
  )
}
