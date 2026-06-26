'use client';

import { motion } from 'framer-motion';

// ─── SVG Icons ────────────────────────────────────────────────────────────────

const SupportHeadsetIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M3 11a9 9 0 0 1 18 0"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <rect x="2" y="11" width="4" height="6" rx="2" stroke="currentColor" strokeWidth="1.8" />
    <rect x="18" y="11" width="4" height="6" rx="2" stroke="currentColor" strokeWidth="1.8" />
    <path
      d="M22 17v1a4 4 0 0 1-4 4h-3"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <circle cx="13" cy="22" r="1.2" fill="currentColor" />
  </svg>
);

const FinanceChartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <rect x="2" y="3" width="20" height="16" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
    <path
      d="M6 16l3-4 3 2.5 3-5 3 3"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M2 20h20"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      opacity="0.4"
    />
  </svg>
);

const EngineeringCodeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M8 6L3 12l5 6"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M16 6l5 6-5 6"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M14 3l-4 18"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      opacity="0.6"
    />
  </svg>
);

const SalesDollarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 2v2M12 20v2M17 7H9.5a2.5 2.5 0 0 0 0 5h5a2.5 2.5 0 0 1 0 5H7"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

// ─── Card data ────────────────────────────────────────────────────────────────

interface OutcomeCard {
  stat: string;
  statLabel: string;
  sub: string;
  category: string;
  color: string;
  body: string;
  icon: React.ReactNode;
}

const OUTCOME_CARDS: OutcomeCard[] = [
  {
    stat: '1,204',
    statLabel: 'tickets resolved',
    sub: 'Zero human intervention',
    category: 'Support',
    color: '#00D9FF',
    body: 'Your Support Agent handled all incoming tickets. 94% resolved on first contact. 6% escalated with full context ready for your team.',
    icon: <SupportHeadsetIcon />,
  },
  {
    stat: '$284k',
    statLabel: 'reconciled',
    sub: 'Across 847 transactions',
    category: 'Finance',
    color: '#1FFFD6',
    body: 'Your Finance Agent matched invoices, flagged 3 anomalies, and prepared the monthly close report. No accountant required at 3am.',
    icon: <FinanceChartIcon />,
  },
  {
    stat: '12',
    statLabel: 'PRs reviewed',
    sub: 'Code shipped faster',
    category: 'Engineering',
    color: '#B084FF',
    body: 'Your Engineering Agent reviewed pull requests, ran test suites, caught 7 security vulnerabilities, and merged 9 approved changes to production.',
    icon: <EngineeringCodeIcon />,
  },
  {
    stat: '47',
    statLabel: 'leads qualified',
    sub: 'Last 24 hours',
    category: 'Sales',
    color: '#FF6B35',
    body: 'Your Sales Agent scored inbound leads, drafted personalized outreach, and booked 12 discovery calls — all before your team\'s first coffee.',
    icon: <SalesDollarIcon />,
  },
];

// ─── Single outcome card ──────────────────────────────────────────────────────

function OutcomeCardItem({
  card,
  index,
}: {
  card: OutcomeCard;
  index: number;
}) {
  const { color, stat, statLabel, sub, category, body, icon } = card;

  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.55, ease: [0.23, 1, 0.32, 1], delay: index * 0.1 }}
      whileHover={{
        backgroundColor: `rgba(${hexToRgb(color)}, 0.06)`,
        borderColor: `rgba(${hexToRgb(color)}, 0.25)`,
        scale: 1.02,
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        transition: {
          duration: 0.2,
          ease: [0.23, 1, 0.32, 1],
          boxShadow: { duration: 0.2, ease: 'easeOut' },
        },
      }}
      style={{
        position: 'relative',
        backgroundColor: 'rgba(255,255,255,0.03)',
        borderWidth: 1,
        borderStyle: 'solid',
        borderColor: 'rgba(255,255,255,0.08)',
        borderRadius: 20,
        padding: '36px 32px',
        display: 'flex',
        flexDirection: 'column',
        gap: 0,
        overflow: 'hidden',
        cursor: 'default',
        willChange: 'transform',
      }}
    >
      {/* Top accent strip */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: '12%',
          right: '12%',
          height: 1,
          background: `linear-gradient(90deg, transparent, ${color}55, transparent)`,
          pointerEvents: 'none',
        }}
      />

      {/* Corner glow */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: -60,
          right: -60,
          width: 160,
          height: 160,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color}12 0%, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />

      {/* Category badge + icon row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 24,
        }}
      >
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.14em',
            textTransform: 'uppercase' as const,
            color,
            background: `${color}14`,
            border: `1px solid ${color}28`,
            borderRadius: 99,
            padding: '4px 12px',
          }}
        >
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              color,
            }}
          >
            {icon}
          </span>
          {category}
        </span>
      </div>

      {/* Large stat number */}
      <div
        style={{
          fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
          fontWeight: 800,
          color: '#ffffff',
          lineHeight: 1,
          letterSpacing: '-0.035em',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {stat}
      </div>

      {/* Stat label */}
      <div
        style={{
          fontSize: 15,
          fontWeight: 500,
          color: 'rgba(255,255,255,0.55)',
          marginTop: 6,
          letterSpacing: '0.01em',
        }}
      >
        {statLabel}
      </div>

      {/* Sub-label */}
      <div
        style={{
          fontSize: 12,
          fontWeight: 600,
          color,
          marginTop: 8,
          letterSpacing: '0.02em',
        }}
      >
        {sub}
      </div>

      {/* Hairline divider */}
      <div
        style={{
          height: 1,
          background: `linear-gradient(90deg, ${color}22, transparent)`,
          margin: '20px 0',
        }}
      />

      {/* Body copy */}
      <p
        style={{
          fontSize: 14,
          color: 'rgba(255,255,255,0.55)',
          lineHeight: 1.7,
          margin: 0,
          flex: 1,
          textWrap: 'pretty',
        } as React.CSSProperties}
      >
        {body}
      </p>
    </motion.div>
  );
}

// ─── Hex → RGB helper (for rgba() in whileHover) ──────────────────────────────

function hexToRgb(hex: string): string {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return `${r},${g},${b}`;
}

// ─── ScrollStory Section ──────────────────────────────────────────────────────

export default function ScrollStory() {
  return (
    <section
      id="scroll-story"
      style={{
        background: '#0F1419',
        padding: '120px 24px',
        width: '100%',
        boxSizing: 'border-box' as const,
      }}
    >
      {/* Section heading */}
      <div
        style={{
          maxWidth: 1280,
          margin: '0 auto 64px',
          textAlign: 'center',
        }}
      >
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.2em',
            textTransform: 'uppercase' as const,
            color: '#FF6B35',
            marginBottom: 20,
            marginTop: 0,
          }}
        >
          OVERNIGHT OPERATIONS
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.55, ease: [0.23, 1, 0.32, 1], delay: 0.05 }}
          style={{
            fontSize: 'clamp(1.8rem, 3vw, 2.8rem)',
            fontWeight: 800,
            color: '#ffffff',
            letterSpacing: '-0.03em',
            lineHeight: 1.15,
            margin: 0,
          }}
        >
          What happens while you sleep.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.55, ease: [0.23, 1, 0.32, 1], delay: 0.1 }}
          style={{
            color: 'rgba(255,255,255,0.5)',
            fontSize: 16,
            lineHeight: 1.65,
            marginTop: 16,
            marginBottom: 0,
          }}
        >
          Your AI workforce never stops. Here&rsquo;s what 22 agents accomplish in a typical night.
        </motion.p>
      </div>

      {/* 2×2 grid */}
      <div
        className="outcome-grid"
        style={{
          maxWidth: 1280,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '1px',
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 24,
          overflow: 'hidden',
        }}
      >
        {OUTCOME_CARDS.map((card, i) => (
          <OutcomeCardItem key={card.category} card={card} index={i} />
        ))}
      </div>

      {/* Responsive overrides */}
      <style>{`
        @media (max-width: 767px) {
          .outcome-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}
