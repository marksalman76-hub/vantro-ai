'use client';

import { useRef, useEffect, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const STEP_ICONS = [
  // Connect
  <svg key="connect" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <circle cx="7" cy="14" r="4" stroke="currentColor" strokeWidth="1.8"/>
    <circle cx="21" cy="7" r="4" stroke="currentColor" strokeWidth="1.8"/>
    <circle cx="21" cy="21" r="4" stroke="currentColor" strokeWidth="1.8"/>
    <line x1="11" y1="12" x2="17" y2="9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <line x1="11" y1="16" x2="17" y2="19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>,
  // Agent
  <svg key="agent" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <rect x="4" y="10" width="20" height="14" rx="4" stroke="currentColor" strokeWidth="1.8"/>
    <circle cx="10" cy="17" r="2" fill="currentColor"/>
    <circle cx="18" cy="17" r="2" fill="currentColor"/>
    <path d="M10 10V7a4 4 0 0 1 8 0v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>,
  // Clock/Autopilot
  <svg key="auto" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <circle cx="14" cy="14" r="10" stroke="currentColor" strokeWidth="1.8"/>
    <path d="M14 8v6l4 2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>,
  // Dashboard
  <svg key="dash" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <rect x="3" y="5" width="22" height="15" rx="3" stroke="currentColor" strokeWidth="1.8"/>
    <path d="M3 23h22M10 23v-3M18 23v-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M8 15l4-5 4 3 4-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>,
];

const STEPS = [
  {
    number: '01',
    title: 'Connect Your Tools',
    description: 'Plug in your existing platforms with one-click integrations. No engineering required.',
    color: '#00D9FF',
  },
  {
    number: '02',
    title: 'Pick Your Agents',
    description: 'Select from 22 purpose-built AI agents. Each one trained for your specific use case.',
    color: '#FFD700',
  },
  {
    number: '03',
    title: 'Set & Forget',
    description: 'Agents work autonomously 24/7. They learn, adapt, and improve with every interaction.',
    color: '#1FFFD6',
  },
  {
    number: '04',
    title: 'Watch Them Work',
    description: 'Monitor real-time performance from a unified dashboard. Full control, zero micromanagement.',
    color: '#FF6B35',
  },
] as const;

const EASE = [0.23, 1, 0.32, 1] as const;

// ─── Connector SVG line (framer-motion path) ─────────────────────────────────

function ConnectorLine({
  fromColor,
  toColor,
  gradId,
  isInView,
  delay,
}: {
  fromColor: string;
  toColor: string;
  gradId: string;
  isInView: boolean;
  delay: number;
}) {
  return (
    <svg
      style={{
        position: 'absolute',
        top: 88,
        left: 0,
        width: '100%',
        height: 4,
        overflow: 'visible',
        pointerEvents: 'none',
      }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={fromColor} />
          <stop offset="100%" stopColor={toColor} />
        </linearGradient>
        <filter id={`${gradId}-glow`} x="-20%" y="-400%" width="140%" height="900%">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <motion.line
        x1="0"
        y1="2"
        x2="100%"
        y2="2"
        stroke={`url(#${gradId})`}
        strokeWidth="2"
        strokeLinecap="round"
        filter={`url(#${gradId}-glow)`}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={isInView ? { pathLength: 1, opacity: 1 } : { pathLength: 0, opacity: 0 }}
        transition={{ duration: 1.2, ease: EASE, delay }}
        style={{ filter: `drop-shadow(0 0 4px rgba(0,217,255,0.6))` }}
      />
    </svg>
  );
}

// ─── Step card ────────────────────────────────────────────────────────────────

function StepCard({
  step,
  index,
}: {
  step: (typeof STEPS)[number];
  index: number;
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className="step-card"
      style={{
        flex: 1,
        position: 'relative',
        background: 'rgba(255,255,255,0.05)',
        border: `1px solid ${hovered ? `${step.color}44` : 'rgba(255,255,255,0.09)'}`,
        borderRadius: 24,
        padding: '36px 28px',
        backdropFilter: 'blur(16px)',
        overflow: 'hidden',
        boxShadow: hovered
          ? `0 24px 60px ${step.color}14, 0 0 0 1px ${step.color}18`
          : 'none',
        transform: hovered ? 'translateY(-8px)' : 'translateY(0)',
        transition: 'all 350ms cubic-bezier(0.23, 1, 0.32, 1)',
        opacity: 0, // GSAP will animate this in
        cursor: 'default',
        zIndex: 1,
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Giant decorative background step number */}
      <span
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 12,
          right: 16,
          fontSize: 96,
          fontWeight: 800,
          lineHeight: 1,
          color: step.color,
          opacity: 0.08,
          pointerEvents: 'none',
          userSelect: 'none',
          letterSpacing: '-0.04em',
        }}
      >
        {step.number}
      </span>

      {/* Icon circle */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 64,
          height: 64,
          borderRadius: '50%',
          background: `${step.color}1A`,
          border: `1px solid ${step.color}33`,
          boxShadow: hovered ? `0 0 24px ${step.color}44` : 'none',
          transition: 'box-shadow 350ms cubic-bezier(0.23, 1, 0.32, 1)',
          color: step.color,
        }}
      >
        {STEP_ICONS[index]}
      </div>

      {/* Step title */}
      <h3
        style={{
          position: 'relative',
          zIndex: 10,
          color: '#ffffff',
          fontSize: 19,
          fontWeight: 700,
          marginTop: 20,
          marginBottom: 0,
          lineHeight: 1.3,
        }}
      >
        {step.title}
      </h3>

      {/* Step description */}
      <p
        style={{
          position: 'relative',
          zIndex: 10,
          color: 'rgba(255,255,255,0.5)',
          fontSize: 14,
          lineHeight: 1.7,
          marginTop: 8,
          marginBottom: 0,
        }}
      >
        {step.description}
      </p>
    </div>
  );
}

// ─── Section ──────────────────────────────────────────────────────────────────

export default function HowItWorks() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRowRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' });

  // GSAP stagger for cards
  useEffect(() => {
    if (!cardsRowRef.current) return;

    const cards = cardsRowRef.current.querySelectorAll<HTMLElement>('.step-card');
    if (!cards.length) return;

    const ctx = gsap.context(() => {
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
            trigger: cardsRowRef.current,
            start: 'top 80%',
            once: true,
          },
        }
      );
    }, cardsRowRef);

    return () => ctx.revert();
  }, []);

  // GSAP header reveal
  useEffect(() => {
    if (!headerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        headerRef.current,
        { opacity: 0, y: 32 },
        {
          opacity: 1,
          y: 0,
          duration: 0.75,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: headerRef.current,
            start: 'top 85%',
            once: true,
          },
        }
      );
    }, headerRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="how-it-works"
      ref={sectionRef}
      style={{
        width: '100%',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
        background: '#1A1F2E',
      }}
    >
      <div style={{ maxWidth: 1280, margin: '0 auto' }}>

        {/* Section header */}
        <div
          ref={headerRef}
          style={{ textAlign: 'center', marginBottom: 64, opacity: 0 }}
        >
          {/* Eyebrow */}
          <p
            style={{
              color: '#1FFFD6',
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              marginBottom: 16,
            }}
          >
            SIMPLE SETUP
          </p>

          <h2
            style={{
              fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
              fontWeight: 800,
              color: '#ffffff',
              letterSpacing: '-0.025em',
              lineHeight: 1.1,
              margin: 0,
            }}
          >
            Deploy in 4 Steps
          </h2>

          <p
            style={{
              color: 'rgba(255,255,255,0.45)',
              fontSize: 18,
              marginTop: 16,
              marginBottom: 0,
            }}
          >
            From zero to autonomous AI workforce in under 5 minutes.
          </p>
        </div>

        {/* Cards row + connector lines */}
        <div
          ref={cardsRowRef}
          style={{
            position: 'relative',
            display: 'flex',
            flexDirection: 'row',
            gap: 20,
            flexWrap: 'nowrap',
          }}
          className="how-it-works-row"
        >
          {/* Animated SVG connector lines (desktop only) */}
          <div
            className="connectors-desktop"
            style={{
              position: 'absolute',
              inset: 0,
              pointerEvents: 'none',
              zIndex: 0,
            }}
            aria-hidden="true"
          >
            {STEPS.slice(0, -1).map((step, i) => {
              const nextStep = STEPS[i + 1];
              const cardWidthPct = 100 / STEPS.length;
              return (
                <div
                  key={step.number}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: `calc(${cardWidthPct * (i + 1)}% + 0px)`,
                    width: `calc(${cardWidthPct}% - 100%)`,
                    // Span each inter-card gap: 20px gap, each gap covers space between cards
                    // More precisely: position at right edge of card[i], width = gap (20px)
                  }}
                >
                  {/* We overlay the SVG connector that spans the gap */}
                </div>
              );
            })}

            {/* Three connector spans between 4 cards */}
            {[0, 1, 2].map((i) => {
              const gradColors: [string, string] = [STEPS[i].color, STEPS[i + 1].color];
              return (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    top: 0,
                    // Each card occupies ~25% width. Connector sits in gap.
                    // Card right edge: (i+1)*25%, connector width: 20px gap
                    left: `calc(${(i + 1) * 25}% - 10px)`,
                    width: 20,
                    height: '100%',
                    overflow: 'visible',
                  }}
                >
                  <ConnectorLine
                    fromColor={gradColors[0]}
                    toColor={gradColors[1]}
                    gradId={`stepGrad${i}`}
                    isInView={isInView}
                    delay={0.4 + i * 0.18}
                  />
                </div>
              );
            })}
          </div>

          {/* Step cards */}
          {STEPS.map((step, index) => (
            <StepCard key={step.number} step={step} index={index} />
          ))}
        </div>
      </div>

      <style>{`
        @media (max-width: 1024px) {
          .how-it-works-row {
            flex-direction: column !important;
          }
          .connectors-desktop {
            display: none !important;
          }
        }
      `}</style>
    </section>
  );
}
