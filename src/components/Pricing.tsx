'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { AgentSelectModal, type PlanConfig } from './AgentSelectModal';

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
    features: ['10 active agents', '15,000 actions / mo', '100+ integrations', 'Email support'],
    cta: 'Start Growth',
    maxAgents: 10,
    featured: false,
  },
  {
    name: 'Business',
    price: '$499',
    tagline: 'For teams running real operations.',
    features: [
      'All 22 agents',
      '50,000 actions / mo',
      '200+ integrations',
      'Approval workflows',
      'Priority support',
    ],
    cta: 'Activate your agents',
    maxAgents: 22,
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    tagline: 'For organizations at scale.',
    features: [
      'Unlimited actions',
      'SSO & SCIM',
      'Dedicated orchestration',
      'Custom agents',
      'SLA & solutions team',
    ],
    cta: 'Talk to sales',
    maxAgents: 0,
    featured: false,
  },
];

interface TierCardProps {
  tier: typeof TIERS[0];
  index: number;
  onSelect: (plan: PlanConfig) => void;
}

function TierCard({ tier, index, onSelect }: TierCardProps) {
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
    if (isEnterprise) {
      window.location.href = 'mailto:hello@vantro.ai';
      return;
    }
    e.preventDefault();
    onSelect({ name: tier.name, price: tier.price, maxAgents: tier.maxAgents });
  }

  return (
    <div className="relative" style={tier.featured ? { paddingTop: '1rem' } : {}}>
      {tier.featured && (
        <span
          className="absolute top-0 left-1/2 -translate-x-1/2 text-xs font-semibold px-3 py-1 rounded-full z-10"
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            backgroundColor: 'oklch(0.97 0 0)',
            color: 'oklch(0.14 0 0)',
          }}
        >
          Most popular
        </span>
      )}
      <motion.div
        ref={cardRef}
        className="glass-card relative"
        onMouseMove={handleMouseMove}
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.5, delay: index * 0.08 }}
        style={{
          borderRadius: '1.25rem',
          padding: '1.5rem',
          ...(tier.featured && {
            border: '1px solid rgba(255,255,255,0.22)',
            boxShadow: [
              'inset 0 2px 0 rgba(255,255,255,0.30)',
              'inset 0 -1px 0 rgba(255,255,255,0.05)',
              '0 0 0 1px rgba(255,255,255,0.09)',
              '0 32px 80px rgba(0,0,0,0.65)',
              '0 0 60px rgba(255,255,255,0.05)',
            ].join(', '),
          }),
        }}
      >
        <div className="spotlight" />
        <div className="sheen" />

        <p
          className="text-xs uppercase tracking-widest mb-2"
          style={{ fontFamily: 'JetBrains Mono, monospace', color: 'oklch(0.79 0 0)' }}
        >
          {tier.name}
        </p>

        <div className="flex items-baseline gap-1 mb-1">
          <span
            className="font-bold text-4xl"
            style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
          >
            {tier.price}
          </span>
          {tier.price !== 'Custom' && (
            <span className="text-lg" style={{ color: 'oklch(0.70 0 0)' }}>
              /mo
            </span>
          )}
        </div>

        <p className="text-sm mb-6" style={{ color: 'oklch(0.70 0 0)' }}>
          {tier.tagline}
        </p>

        <ul className="flex flex-col gap-3 mb-8">
          {tier.features.map((f) => (
            <li key={f} className="flex items-center gap-2">
              <Check size={14} style={{ color: 'rgba(200,200,200,0.70)', flexShrink: 0 }} />
              <span className="text-sm" style={{ color: 'oklch(0.70 0 0)' }}>
                {f}
              </span>
            </li>
          ))}
        </ul>

        <button
          onClick={handleCTA}
          className="w-full py-3 rounded-full font-semibold transition-all duration-200 cursor-pointer block text-center"
          style={
            tier.featured
              ? {
                  backgroundColor: 'oklch(0.97 0 0)',
                  color: 'oklch(0.14 0 0)',
                  border: 'none',
                }
              : {
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: 'oklch(0.97 0 0)',
                  background: 'transparent',
                }
          }
          onMouseEnter={(e) => {
            if (tier.featured) {
              (e.currentTarget as HTMLButtonElement).style.opacity = '0.90';
            } else {
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.30)';
            }
          }}
          onMouseLeave={(e) => {
            if (tier.featured) {
              (e.currentTarget as HTMLButtonElement).style.opacity = '1';
            } else {
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.15)';
            }
          }}
        >
          {tier.cta}
        </button>
      </motion.div>
    </div>
  );
}

export function Pricing() {
  const [activePlan, setActivePlan] = useState<PlanConfig | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const autoplan = params.get('autoplan');
    if (autoplan) {
      const tier = TIERS.find((t) => t.name.toLowerCase() === autoplan.toLowerCase());
      if (tier && tier.name !== 'Enterprise') {
        setActivePlan({ name: tier.name, price: tier.price, maxAgents: tier.maxAgents });
        params.delete('autoplan');
        const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}${window.location.hash}`;
        window.history.replaceState(null, '', newUrl);
      }
    }
  }, []);

  return (
    <>
      <section id="pricing" className="py-32" style={{ backgroundColor: 'oklch(0.28 0 0)' }}>
        <h2
          className="text-center mb-4 font-bold text-4xl md:text-5xl"
          style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
        >
          Scale your workforce, not your headcount.
        </h2>
        <p
          className="text-center mb-16 max-w-xl mx-auto text-base"
          style={{ color: 'oklch(0.70 0 0)' }}
        >
          Every plan includes the full agent platform. Pick the tier that fits your volume.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto px-6">
          {TIERS.map((tier, i) => (
            <TierCard key={tier.name} tier={tier} index={i} onSelect={setActivePlan} />
          ))}
        </div>
      </section>

      {activePlan && (
        <AgentSelectModal plan={activePlan} onClose={() => setActivePlan(null)} />
      )}
    </>
  );
}
