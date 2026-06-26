'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { AGENTS, CATEGORY_COLORS, type Agent } from '@/lib/agents';

gsap.registerPlugin(ScrollTrigger);

// ─── Constants ────────────────────────────────────────────────────────────────

const EASE = [0.23, 1, 0.32, 1] as const;

type Category = 'All' | 'Sales' | 'Operations' | 'Engineering' | 'Support' | 'Executive';
const CATEGORIES: Category[] = ['All', 'Sales', 'Operations', 'Engineering', 'Support', 'Executive'];

// ─── Agent Card ───────────────────────────────────────────────────────────────

function AgentCard({
  agent,
  onClick,
  cardRef,
}: {
  agent: Agent;
  onClick: () => void;
  cardRef?: (el: HTMLDivElement | null) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const color = CATEGORY_COLORS[agent.category];

  return (
    <motion.div
      ref={cardRef}
      layout
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.92 }}
      transition={{ duration: 0.35, ease: EASE }}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="relative flex flex-col gap-3 cursor-pointer"
      style={{
        background: 'rgba(255,255,255,0.05)',
        border: `1px solid ${hovered ? `${color}44` : 'rgba(255,255,255,0.09)'}`,
        borderRadius: 20,
        padding: 24,
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        overflow: 'hidden',
        position: 'relative',
        boxShadow: hovered
          ? `0 20px 60px ${color}18, 0 0 0 1px ${color}20`
          : 'none',
        transform: hovered ? 'translateY(-4px)' : 'translateY(0px)',
        transition: 'all 300ms cubic-bezier(0.23,1,0.32,1)',
      }}
    >
      {/* Subtle corner glow on hover */}
      {hovered && (
        <div
          style={{
            position: 'absolute',
            top: -40,
            right: -40,
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${color}18 0%, transparent 70%)`,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Top row: avatar + info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Avatar */}
        <div
          style={{
            flexShrink: 0,
            width: 76,
            height: 76,
            borderRadius: '50%',
            overflow: 'hidden',
            border: `2px solid ${color}55`,
            boxShadow: `0 0 20px ${color}22`,
          }}
        >
          <img
            src={agent.avatar}
            alt={agent.name}
            width={76}
            height={76}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </div>

        {/* Name / role / badge */}
        <div style={{ minWidth: 0 }}>
          <p
            style={{
              color: '#fff',
              fontSize: 17,
              fontWeight: 700,
              lineHeight: 1.2,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {agent.name}
          </p>
          <p
            style={{
              color,
              fontSize: 13,
              marginTop: 2,
              lineHeight: 1.3,
            }}
          >
            {agent.role}
          </p>
          <span
            style={{
              display: 'inline-block',
              marginTop: 6,
              background: `${color}20`,
              color,
              fontSize: 10,
              fontWeight: 600,
              borderRadius: 99,
              padding: '3px 8px',
              letterSpacing: '0.02em',
            }}
          >
            {agent.category}
          </span>
        </div>
      </div>

      {/* Description — 2-line clamp */}
      <p
        style={{
          fontSize: 13,
          color: 'rgba(255,255,255,0.50)',
          lineHeight: 1.65,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {agent.description}
      </p>

      {/* Stats pills */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {[
          `${agent.stats.successRate}% success`,
          agent.stats.responseTime,
          `${agent.stats.languages} langs`,
        ].map((label) => (
          <span
            key={label}
            style={{
              background: 'rgba(255,255,255,0.05)',
              borderRadius: 8,
              padding: '4px 10px',
              fontSize: 11,
              fontWeight: 600,
              color: 'rgba(255,255,255,0.65)',
            }}
          >
            {label}
          </span>
        ))}
      </div>

      {/* Deploy button — slides up on hover */}
      <AnimatePresence>
        {hovered && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2, ease: EASE }}
            style={{
              background: '#FF6B35',
              color: '#fff',
              width: '100%',
              padding: '10px',
              borderRadius: 10,
              fontWeight: 700,
              fontSize: 13,
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 0 24px rgba(255,107,53,0.45)',
              letterSpacing: '0.01em',
            }}
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
          >
            Deploy Agent →
          </motion.button>
        )}
      </AnimatePresence>
    </motion.div>
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
      {/* Backdrop */}
      <motion.div
        className="fixed inset-0 z-40"
        style={{ background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(4px)' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />

      {/* Panel */}
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
        {/* Close */}
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

        {/* Avatar */}
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

        {/* Bio */}
        <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: 14, lineHeight: 1.7, textAlign: 'center' }}>
          {agent.bio}
        </p>

        {/* Stats grid */}
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

        {/* CTA */}
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
  const gridRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);

  const filtered =
    activeCategory === 'All'
      ? AGENTS
      : AGENTS.filter((a) => a.category === activeCategory);

  // Collect card refs via callback
  const setCardRef = useCallback(
    (index: number) => (el: HTMLDivElement | null) => {
      cardRefs.current[index] = el;
    },
    []
  );

  // GSAP ScrollTrigger animations
  useGSAP(
    () => {
      if (!sectionRef.current || !headerRef.current) return;

      // Header fade-up
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

      // Card batch stagger reveal
      const cards = gridRef.current?.querySelectorAll<HTMLElement>('[data-agent-card]');
      if (cards && cards.length) {
        ScrollTrigger.batch(cards, {
          start: 'top 88%',
          onEnter: (batch) => {
            gsap.from(batch, {
              y: 30,
              opacity: 0,
              duration: 0.55,
              ease: 'power3.out',
              stagger: 0.06,
            });
          },
          once: true,
        });
      }
    },
    { scope: sectionRef, dependencies: [filtered.length] }
  );

  return (
    <section
      id="agents"
      ref={sectionRef}
      style={{
        width: '100%',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
        background: '#111720',
      }}
    >
      <div style={{ maxWidth: 1280, margin: '0 auto' }}>

        {/* Section header */}
        <div ref={headerRef} style={{ textAlign: 'center', marginBottom: 56 }}>
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

        {/* Category filter tabs */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginBottom: 40,
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
                <span
                  style={{
                    position: 'relative',
                    zIndex: 1,
                    color: isActive ? '#fff' : '#9CA3AF',
                  }}
                >
                  {cat}
                </span>
              </button>
            );
          })}
        </div>

        {/* Agent grid */}
        <div
          ref={gridRef}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          <AnimatePresence mode="popLayout">
            {filtered.map((agent, i) => (
              <div
                key={agent.id}
                data-agent-card
                ref={setCardRef(i)}
              >
                <AgentCard
                  agent={agent}
                  onClick={() => setSelectedAgent(agent)}
                />
              </div>
            ))}
          </AnimatePresence>
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
    </section>
  );
}
