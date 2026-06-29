'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { AGENTS, CATEGORY_COLORS, type Agent } from '@/lib/agents';

gsap.registerPlugin(ScrollTrigger);

const EASE = [0.23, 1, 0.32, 1] as const;

type Category = 'All' | 'Sales' | 'Operations' | 'Engineering' | 'Support' | 'Executive';
const CATEGORIES: Category[] = ['All', 'Sales', 'Operations', 'Engineering', 'Support', 'Executive'];

// ─── Carousel Card ────────────────────────────────────────────────────────────

function CarouselCard({
  agent,
  onClick,
}: {
  agent: Agent;
  onClick: () => void;
}) {
  const [hovered, setHovered] = useState(false);
  const color = CATEGORY_COLORS[agent.category];

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        flexShrink: 0,
        minWidth: 284,
        padding: '18px 20px',
        position: 'relative',
        background: 'rgba(14,19,27,0.90)',
        border: `1.5px solid ${hovered ? `${color}AA` : `${color}55`}`,
        borderRadius: 16,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        cursor: 'pointer',
        boxShadow: hovered
          ? `0 0 0 1px ${color}55, 0 0 40px ${color}35, 0 20px 48px rgba(0,0,0,0.5)`
          : `0 0 0 1px ${color}22, 0 8px 32px rgba(0,0,0,0.45), 0 0 28px ${color}15`,
        transition: 'all 280ms cubic-bezier(0.23, 1, 0.32, 1)',
        overflow: 'hidden',
        willChange: 'transform',
        transform: hovered ? 'translateY(-4px) scale(1.02)' : 'translateY(0) scale(1)',
      }}
    >
      {/* Top highlight strip */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: '10%',
          right: '10%',
          height: 1,
          background: `linear-gradient(90deg, transparent, ${color}66, transparent)`,
          pointerEvents: 'none',
        }}
      />

      {/* Corner glow */}
      <div
        style={{
          position: 'absolute',
          top: -40,
          right: -40,
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color}1A 0%, transparent 70%)`,
          pointerEvents: 'none',
          opacity: hovered ? 1 : 0,
          transition: 'opacity 280ms cubic-bezier(0.23, 1, 0.32, 1)',
        }}
      />

      {/* Content */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, position: 'relative', zIndex: 1 }}>
        {/* Avatar */}
        <div
          style={{
            flexShrink: 0,
            width: 52,
            height: 52,
            borderRadius: '50%',
            overflow: 'hidden',
            border: `2px solid ${color}55`,
            boxShadow: `0 0 16px ${color}25`,
          }}
        >
          <img
            src={agent.avatar}
            alt={agent.name}
            width={52}
            height={52}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </div>

        {/* Name / role / pill */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <p
            style={{
              color: '#fff',
              fontSize: 15,
              fontWeight: 700,
              lineHeight: 1.2,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {agent.name}
          </p>
          <p style={{ color, fontSize: 12, marginTop: 2, lineHeight: 1.3 }}>
            {agent.role}
          </p>
          <span
            style={{
              display: 'inline-block',
              marginTop: 5,
              background: `${color}20`,
              color,
              fontSize: 10,
              fontWeight: 600,
              borderRadius: 99,
              padding: '2px 8px',
              letterSpacing: '0.02em',
            }}
          >
            {agent.category}
          </span>
        </div>

        {/* Success metric */}
        <div style={{ flexShrink: 0, textAlign: 'right' }}>
          <p
            style={{
              color: '#fff',
              fontSize: 22,
              fontWeight: 800,
              lineHeight: 1,
              letterSpacing: '-0.02em',
            }}
          >
            {agent.stats.successRate}%
          </p>
          <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 10, marginTop: 3, lineHeight: 1.3 }}>
            success
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Detail Panel ─────────────────────────────────────────────────────────────

function DetailPanel({
  agent,
  onClose,
}: {
  agent: Agent;
  onClose: () => void;
}) {
  const color = CATEGORY_COLORS[agent.category];

  return (
    <>
      <motion.div
        className="fixed inset-0 z-40"
        style={{ background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(4px)' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />

      <motion.div
        className="fixed z-50 flex flex-col gap-6 overflow-y-auto"
        style={{
          background: 'rgba(15,20,30,0.97)',
          border: `1px solid ${color}33`,
          borderRadius: 24,
          padding: 36,
          boxShadow: `0 0 80px ${color}22, 0 40px 80px rgba(0,0,0,0.6)`,
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          top: '50%',
          right: 24,
          width: 'min(440px, calc(100vw - 48px))',
          maxHeight: 'calc(100vh - 80px)',
          translateY: '-50%',
        }}
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 60 }}
        transition={{ duration: 0.38, ease: EASE }}
      >
        <button
          onClick={onClose}
          aria-label="Close panel"
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            width: 32,
            height: 32,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.08)',
            border: '1px solid rgba(255,255,255,0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9ca3af',
            fontSize: 14,
            cursor: 'pointer',
          }}
        >
          ✕
        </button>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, paddingTop: 8 }}>
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: '50%',
              overflow: 'hidden',
              border: `3px solid ${color}66`,
              boxShadow: `0 0 40px ${color}33`,
            }}
          >
            <img
              src={agent.avatar}
              alt={agent.name}
              width={120}
              height={120}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>

          <div style={{ textAlign: 'center' }}>
            <h3 style={{ color: '#fff', fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em' }}>
              {agent.name}
            </h3>
            <p style={{ color, fontSize: 14, marginTop: 4 }}>{agent.role}</p>
            <span
              style={{
                display: 'inline-block',
                marginTop: 8,
                background: `${color}20`,
                color,
                fontSize: 11,
                fontWeight: 600,
                borderRadius: 99,
                padding: '4px 12px',
              }}
            >
              {agent.category}
            </span>
          </div>
        </div>

        <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: 14, lineHeight: 1.7, textAlign: 'center' }}>
          {agent.bio}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
          {[
            { label: 'Success Rate', value: `${agent.stats.successRate}%` },
            { label: 'Response Time', value: agent.stats.responseTime },
            { label: 'Languages', value: `${agent.stats.languages}` },
          ].map((stat) => (
            <div
              key={stat.label}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 4,
                padding: 16,
                borderRadius: 14,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.08)',
              }}
            >
              <span style={{ color: '#fff', fontWeight: 800, fontSize: 20, letterSpacing: '-0.02em' }}>
                {stat.value}
              </span>
              <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, textAlign: 'center', lineHeight: 1.3 }}>
                {stat.label}
              </span>
            </div>
          ))}
        </div>

        <a
          href="#pricing"
          onClick={onClose}
          style={{
            display: 'block',
            width: '100%',
            padding: '14px',
            borderRadius: 14,
            textAlign: 'center',
            color: '#fff',
            fontWeight: 800,
            fontSize: 15,
            background: '#FF6B35',
            boxShadow: '0 0 32px rgba(255,107,53,0.50)',
            textDecoration: 'none',
          }}
        >
          Deploy This Agent
        </a>
      </motion.div>
    </>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function AgentShowcase() {
  const [activeCategory, setActiveCategory] = useState<Category>('All');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  const filtered =
    activeCategory === 'All'
      ? AGENTS
      : AGENTS.filter((a) => a.category === activeCategory);

  // Duplicate for seamless infinite loop
  const doubled = [...filtered, ...filtered];

  useGSAP(
    () => {
      if (!headerRef.current) return;
      gsap.from(headerRef.current, {
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
          once: true,
        },
      });
    },
    { scope: sectionRef }
  );

  return (
    <section
      id="agents"
      ref={sectionRef}
      style={{
        width: '100%',
        paddingTop: 120,
        paddingBottom: 120,
        background: '#111720',
        overflow: 'hidden',
      }}
    >
      {/* Header + tabs */}
      <div style={{ paddingLeft: 24, paddingRight: 24 }}>
        <div ref={headerRef} style={{ textAlign: 'center', marginBottom: 56, position: 'relative' }}>
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: 400,
              height: 400,
              background:
                'radial-gradient(circle 400px at center, rgba(0,217,255,0.06) 0%, transparent 100%)',
              pointerEvents: 'none',
              zIndex: 0,
            }}
          />
          <div style={{ position: 'relative', zIndex: 1 }}>
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
              MEET YOUR TEAM
            </p>
            <h2
              style={{
                color: '#fff',
                fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
                fontWeight: 800,
                letterSpacing: '-0.025em',
                lineHeight: 1.1,
                margin: 0,
              }}
            >
              22 AI Agents Ready to Deploy
            </h2>
            <p
              style={{
                color: 'rgba(255,255,255,0.45)',
                fontSize: 18,
                marginTop: 16,
                lineHeight: 1.5,
              }}
            >
              Diverse, specialized, and working 24/7
            </p>
          </div>
        </div>

        {/* Category filter tabs */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginBottom: 48,
          }}
        >
          {CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                style={{
                  position: 'relative',
                  padding: '8px 20px',
                  borderRadius: 99,
                  fontSize: 14,
                  fontWeight: 500,
                  background: 'transparent',
                  border: isActive ? 'none' : '1px solid rgba(255,255,255,0.10)',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                {isActive && (
                  <motion.span
                    layoutId="agent-tab-pill"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      borderRadius: 99,
                      background: '#FF6B35',
                    }}
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <span style={{ position: 'relative', zIndex: 1, color: isActive ? '#fff' : '#9CA3AF' }}>
                  {cat}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Carousel — full bleed, edge-faded */}
      <div style={{ position: 'relative' }}>
        {/* Left edge fade */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            bottom: 0,
            width: 120,
            background: 'linear-gradient(to right, #111720, transparent)',
            zIndex: 2,
            pointerEvents: 'none',
          }}
        />
        {/* Right edge fade */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            width: 120,
            background: 'linear-gradient(to left, #111720, transparent)',
            zIndex: 2,
            pointerEvents: 'none',
          }}
        />

        {/* Row 1 — scrolls left */}
        <div
          className="as-row-1"
          style={{
            display: 'flex',
            gap: 16,
            marginBottom: 16,
            width: 'max-content',
            willChange: 'transform',
            paddingLeft: 16,
          }}
        >
          {doubled.map((agent, i) => (
            <CarouselCard
              key={`r1-${agent.id}-${i}`}
              agent={agent}
              onClick={() => setSelectedAgent(agent)}
            />
          ))}
        </div>

        {/* Row 2 — scrolls right */}
        <div
          className="as-row-2"
          style={{
            display: 'flex',
            gap: 16,
            width: 'max-content',
            willChange: 'transform',
            paddingLeft: 16,
          }}
        >
          {doubled.map((agent, i) => (
            <CarouselCard
              key={`r2-${agent.id}-${i}`}
              agent={agent}
              onClick={() => setSelectedAgent(agent)}
            />
          ))}
        </div>
      </div>

      {/* Detail panel */}
      <AnimatePresence>
        {selectedAgent && (
          <DetailPanel
            agent={selectedAgent}
            onClose={() => setSelectedAgent(null)}
          />
        )}
      </AnimatePresence>

      <style>{`
        @keyframes as-marquee-left {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes as-marquee-right {
          0%   { transform: translateX(-50%); }
          100% { transform: translateX(0); }
        }
        .as-row-1 {
          animation: as-marquee-left 45s linear infinite;
        }
        .as-row-2 {
          animation: as-marquee-right 60s linear infinite;
        }
        .as-row-1:hover,
        .as-row-2:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
}
