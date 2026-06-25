'use client';

import { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap } from 'lucide-react';
import { AgentSelectModal, type PlanConfig } from './AgentSelectModal';
import { SalesModal } from './SalesModal';

const TIERS = [
  {
    name: 'Starter',
    price: '$0',
    tagline: 'For solo builders testing the waters.',
    features: ['3 active agents', '1,000 actions / mo', 'Core integrations', 'Community support'],
    maxAgents: 3,
  },
  {
    name: 'Growth',
    price: '$199',
    tagline: 'For small teams finding their pace.',
    features: ['7 active agents', '15,000 actions / mo', '100+ integrations', 'Email support'],
    maxAgents: 7,
  },
  {
    name: 'Business',
    price: '$499',
    tagline: 'For teams running real operations.',
    features: ['11 active agents', '50,000 actions / mo', '200+ integrations', 'Approval workflows', 'Priority support'],
    maxAgents: 11,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    tagline: 'For organizations at scale.',
    features: ['Unlimited agents', 'Unlimited actions', 'SSO & SCIM', 'Custom agent builds', 'SLA & solutions team'],
    maxAgents: 0,
  },
];

interface TierCardProps {
  tier: typeof TIERS[0];
  index: number;
  isSelected: boolean;
  onHover: (name: string | null) => void;
  onClick: (tier: typeof TIERS[0]) => void;
}

function TierCard({ tier, index, isSelected, onHover, onClick }: TierCardProps) {
  const [hovered, setHovered] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const isEnterprise = tier.name === 'Enterprise';
  const showOrangeBorder = isSelected || hovered;

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    el.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  function handleMouseEnter() {
    setHovered(true);
    onHover(tier.name);
  }

  function handleMouseLeave() {
    setHovered(false);
    onHover(null);
  }

  return (
    <div style={{ position: 'relative', paddingTop: tier.name === 'Business' ? '1rem' : 0 }}>
      {tier.name === 'Business' && (
        <span
          style={{
            position: 'absolute',
            top: 0,
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: '#FF6B35',
            color: '#FFFFFF',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '0.65rem',
            fontWeight: 600,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            padding: '0.25rem 0.75rem',
            borderRadius: '2rem',
            zIndex: 10,
            whiteSpace: 'nowrap',
          }}
        >
          Most popular
        </span>
      )}

      <motion.div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={() => onClick(tier)}
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.5, delay: index * 0.08 }}
        style={{
          borderRadius: '0.875rem',
          padding: '1.5rem',
          backgroundColor: '#1A1F2E',
          border: showOrangeBorder
            ? '1px solid rgba(255,107,53,0.60)'
            : '1px solid #2D3748',
          boxShadow: showOrangeBorder
            ? '0 0 0 1px rgba(255,107,53,0.20), 0 32px 80px rgba(0,0,0,0.55), 0 0 60px rgba(255,107,53,0.12)'
            : '0 4px 24px rgba(0,0,0,0.35)',
          position: 'relative',
          overflow: 'hidden',
          cursor: 'pointer',
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
        }}
      >
        <div className="spotlight" />
        <div className="sheen" />

        {/* Tier name */}
        <p style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '0.7rem',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: showOrangeBorder ? '#FF6B35' : '#9CA3AF',
          marginBottom: '0.5rem',
          position: 'relative',
          zIndex: 1,
          transition: 'color 0.2s ease',
        }}>
          {tier.name}
        </p>

        {/* Price */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.25rem', marginBottom: '0.375rem', position: 'relative', zIndex: 1 }}>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: '2.25rem', color: '#FFFFFF' }}>
            {tier.price}
          </span>
          {tier.price !== 'Custom' && (
            <span style={{ fontSize: '0.95rem', color: '#9CA3AF' }}>/mo</span>
          )}
        </div>

        <p style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '1.5rem', position: 'relative', zIndex: 1 }}>
          {tier.tagline}
        </p>

        {/* Features — all orange checks */}
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem', marginBottom: '1.75rem', listStyle: 'none', padding: 0, position: 'relative', zIndex: 1 }}>
          {tier.features.map((f) => (
            <li key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Check size={14} style={{ color: '#FF6B35', flexShrink: 0 }} />
              <span style={{ fontSize: '0.875rem', color: '#E5E7EB' }}>{f}</span>
            </li>
          ))}
        </ul>

        {/* CTA — orange only when selected */}
        {isSelected && !isEnterprise ? (
          <button
            onClick={(e) => { e.stopPropagation(); onClick(tier); }}
            className="btn-orange"
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.95rem', fontWeight: 700, justifyContent: 'center', cursor: 'pointer', position: 'relative', zIndex: 1 }}
          >
            <Zap size={16} />
            Activate your agents
          </button>
        ) : isSelected && isEnterprise ? (
          <button
            onClick={(e) => { e.stopPropagation(); onClick(tier); }}
            className="btn-orange"
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.95rem', fontWeight: 700, justifyContent: 'center', cursor: 'pointer', position: 'relative', zIndex: 1 }}
          >
            Talk to sales
          </button>
        ) : (
          <button
            onClick={(e) => { e.stopPropagation(); onClick(tier); }}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.95rem',
              fontWeight: 600,
              cursor: 'pointer',
              backgroundColor: 'transparent',
              border: '1px solid #2D3748',
              color: '#E5E7EB',
              position: 'relative',
              zIndex: 1,
              display: 'block',
            }}
          >
            {isEnterprise ? 'Talk to sales' : 'Get started'}
          </button>
        )}
      </motion.div>
    </div>
  );
}

export function Pricing() {
  const [selectedTier, setSelectedTier] = useState<string>('Business');
  const [activePlan, setActivePlan] = useState<PlanConfig | null>(null);
  const [salesOpen, setSalesOpen] = useState(false);

  function handleCardClick(tier: typeof TIERS[0]) {
    setSelectedTier(tier.name);
    if (tier.name === 'Enterprise') {
      setSalesOpen(true);
    } else {
      setActivePlan({ name: tier.name, price: tier.price, maxAgents: tier.maxAgents });
    }
  }

  return (
    <>
      <section id="pricing" style={{ backgroundColor: '#0F1419', paddingTop: '6rem', paddingBottom: '6rem' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            style={{ textAlign: 'center', marginBottom: '3.5rem' }}
          >
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', letterSpacing: '-0.025em', color: '#FFFFFF', marginBottom: '0.875rem', lineHeight: 1.1 }}>
              Scale your workforce,{' '}
              <span style={{ color: '#FF6B35' }}>not your headcount.</span>
            </h2>
            <p style={{ color: '#9CA3AF', fontSize: '1.05rem', maxWidth: '32rem', margin: '0 auto', lineHeight: 1.6 }}>
              Every plan includes the full agent platform. Pick the tier that fits your volume.
            </p>
          </motion.div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 items-start">
            {TIERS.map((tier, i) => (
              <TierCard
                key={tier.name}
                tier={tier}
                index={i}
                isSelected={selectedTier === tier.name}
                onHover={() => {}}
                onClick={handleCardClick}
              />
            ))}
          </div>
        </div>
      </section>

      {activePlan && <AgentSelectModal plan={activePlan} onClose={() => setActivePlan(null)} />}
      {salesOpen && <SalesModal onClose={() => setSalesOpen(false)} />}
    </>
  );
}
