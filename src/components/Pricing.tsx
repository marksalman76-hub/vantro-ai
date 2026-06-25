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
    cta: 'Start free',
    maxAgents: 3,
    featured: false,
  },
  {
    name: 'Growth',
    price: '$199',
    tagline: 'For small teams finding their pace.',
    features: ['7 active agents', '15,000 actions / mo', '100+ integrations', 'Email support'],
    cta: 'Start Growth',
    maxAgents: 7,
    featured: false,
  },
  {
    name: 'Business',
    price: '$499',
    tagline: 'For teams running real operations.',
    features: ['11 active agents', '50,000 actions / mo', '200+ integrations', 'Approval workflows', 'Priority support'],
    cta: 'Activate your agents',
    maxAgents: 11,
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    tagline: 'For organizations at scale.',
    features: ['Unlimited agents', 'Unlimited actions', 'SSO & SCIM', 'Custom agent builds', 'SLA & solutions team'],
    cta: 'Talk to sales',
    maxAgents: 0,
    featured: false,
  },
];

interface TierCardProps {
  tier: typeof TIERS[0];
  index: number;
  onSelect: (plan: PlanConfig) => void;
  onSales: () => void;
}

function TierCard({ tier, index, onSelect, onSales }: TierCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const isEnterprise = tier.name === 'Enterprise';

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    el.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  function handleCTA(e: React.MouseEvent) {
    if (isEnterprise) { onSales(); return; }
    e.preventDefault();
    onSelect({ name: tier.name, price: tier.price, maxAgents: tier.maxAgents });
  }

  return (
    <div style={{ position: 'relative', paddingTop: tier.featured ? '1rem' : 0 }}>
      {tier.featured && (
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
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.5, delay: index * 0.08 }}
        style={{
          borderRadius: '0.875rem',
          padding: '1.5rem',
          backgroundColor: '#1A1F2E',
          border: tier.featured
            ? '1px solid rgba(255,107,53,0.50)'
            : '1px solid #2D3748',
          boxShadow: tier.featured
            ? '0 0 0 1px rgba(255,107,53,0.20), 0 32px 80px rgba(0,0,0,0.55), 0 0 60px rgba(255,107,53,0.12)'
            : '0 4px 24px rgba(0,0,0,0.35)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Spotlight */}
        <div className="spotlight" />
        <div className="sheen" />

        {/* Tier name */}
        <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: tier.featured ? '#FF6B35' : '#9CA3AF', marginBottom: '0.5rem', position: 'relative', zIndex: 1 }}>
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

        {/* Features */}
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem', marginBottom: '1.75rem', listStyle: 'none', padding: 0, position: 'relative', zIndex: 1 }}>
          {tier.features.map((f) => (
            <li key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Check size={14} style={{ color: tier.featured ? '#FF6B35' : '#10B981', flexShrink: 0 }} />
              <span style={{ fontSize: '0.875rem', color: '#E5E7EB' }}>{f}</span>
            </li>
          ))}
        </ul>

        {/* CTA */}
        {tier.featured ? (
          <button
            onClick={handleCTA}
            className="btn-orange"
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.95rem', fontWeight: 700, justifyContent: 'center', cursor: 'pointer', position: 'relative', zIndex: 1 }}
          >
            <Zap size={16} />
            {tier.cta}
          </button>
        ) : (
          <button
            onClick={handleCTA}
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
              transition: 'border-color 0.2s ease, color 0.2s ease',
              position: 'relative',
              zIndex: 1,
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(0,217,255,0.45)';
              (e.currentTarget as HTMLButtonElement).style.color = '#FFFFFF';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = '#2D3748';
              (e.currentTarget as HTMLButtonElement).style.color = '#E5E7EB';
            }}
          >
            {tier.cta}
          </button>
        )}
      </motion.div>
    </div>
  );
}

export function Pricing() {
  const [activePlan, setActivePlan] = useState<PlanConfig | null>(null);
  const [salesOpen, setSalesOpen] = useState(false);

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
              <TierCard key={tier.name} tier={tier} index={i} onSelect={setActivePlan} onSales={() => setSalesOpen(true)} />
            ))}
          </div>
        </div>
      </section>

      {activePlan && <AgentSelectModal plan={activePlan} onClose={() => setActivePlan(null)} />}
      {salesOpen && <SalesModal onClose={() => setSalesOpen(false)} />}
    </>
  );
}
