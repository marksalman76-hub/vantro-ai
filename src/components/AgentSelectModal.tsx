'use client';

import { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';

const ALL_AGENTS = [
  { name: 'Atlas', role: 'Operations Orchestrator', category: 'Operations', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-01-atlas-HcT8hzhWCVimMA7hv773NB.webp' },
  { name: 'Echo', role: 'Customer Support', category: 'Support', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-02-echo-jBseNuruo6zVaNEwKn4uiC.webp' },
  { name: 'Ledger', role: 'Finance & Accounting', category: 'Finance', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-03-ledger-F85UZALSwUyRYrbFukUT32.webp' },
  { name: 'Quill', role: 'Content Writer', category: 'Content', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-04-quill-bj87Aczd4DkvzVpDymRCXC.webp' },
  { name: 'Pixel', role: 'Design & Creative', category: 'Creative', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-05-pixel-5wPhecN9KKS2GP83txqg3L.webp' },
  { name: 'Forge', role: 'Code & Engineering', category: 'Engineering', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-06-forge-74Qoi5iZ6HSHfAKCtpmGiV.webp' },
  { name: 'Sentinel', role: 'Security & Compliance', category: 'Security', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-07-sentinel-R2z9W7XcosMCmKrgyy5egK.webp' },
  { name: 'Pulse', role: 'Marketing Strategist', category: 'Marketing', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-08-pulse-HnoLtavTCfRkHgHn4oRHWY.webp' },
  { name: 'Harbor', role: 'Recruiting & HR', category: 'People', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-09-harbor-JSYpGWNWqMBKuGkeADyUGQ.webp' },
  { name: 'Vector', role: 'Data Analyst', category: 'Data', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-10-vector-h5yum6XcwDvxJveuEcaaRr.webp' },
  { name: 'Scout', role: 'Research Agent', category: 'Research', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-11-scout-RA2fVyF7bjnc6jF6huf2u7.webp' },
  { name: 'Relay', role: 'Email & Comms', category: 'Comms', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-12-relay-hw2y7EPjNeEPfnsw4Gbb8v.webp' },
  { name: 'Nova', role: 'Sales Closer', category: 'Sales', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-13-nova-RjP6GCP9dydGjYzxoGqUS4.webp' },
  { name: 'Cipher', role: 'Legal Reviewer', category: 'Legal', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-14-cipher-6bpayqEPE2evcWh4kx4ewj.webp' },
  { name: 'Tempo', role: 'Project Manager', category: 'Operations', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-15-tempo-SH2nCJiGUVjw6yNbfvyR5r.webp' },
  { name: 'Mosaic', role: 'Social Media Manager', category: 'Marketing', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-16-mosaic-BLWJNJuQDBV5a4YBrz4p5X.webp' },
  { name: 'Lumen', role: 'Brand Strategist', category: 'Marketing', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-17-lumen-2qvMVEXiCmKsKCbwvMDhsa.webp' },
  { name: 'Drift', role: 'Logistics & Supply', category: 'Operations', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-18-drift-53Ynh9MkY87HuXeNL6Rtqc.webp' },
  { name: 'Sage', role: 'Knowledge Base', category: 'Support', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-19-sage-8wXDmjtcYDgZwwVf5p8Tyn.webp' },
  { name: 'Bolt', role: 'Automation Engineer', category: 'Engineering', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-20-bolt-62QDSf9Xu4fefkZnymAYSB.webp' },
  { name: 'Aria', role: 'Voice & Telephony', category: 'Support', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-21-aria-GdEzW9bgD4tMZaCrMfUAUK.webp' },
  { name: 'Onyx', role: 'Executive Assistant', category: 'Operations', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-22-onyx-YJEsc2eKjrVan3gzHX8awN.webp' },
];

export interface PlanConfig {
  name: string;
  price: string;
  maxAgents: number;
}

interface AgentSelectModalProps {
  plan: PlanConfig;
  onClose: () => void;
}

export function AgentSelectModal({ plan, onClose }: AgentSelectModalProps) {
  const allIncluded = plan.maxAgents >= ALL_AGENTS.length;
  const [selected, setSelected] = useState<Set<string>>(
    allIncluded ? new Set(ALL_AGENTS.map((a) => a.name)) : new Set()
  );

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose(); }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  function toggle(name: string) {
    if (allIncluded) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else if (next.size < plan.maxAgents) {
        next.add(name);
      }
      return next;
    });
  }

  function handleCheckout() {
    const agents = Array.from(selected).join(',');
    const url = `https://app.vantro.ai/register?plan=${plan.name.toLowerCase()}&agents=${encodeURIComponent(agents)}`;
    window.location.href = url;
  }

  const ready = allIncluded || selected.size === plan.maxAgents;

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(6px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'linear-gradient(145deg, oklch(0.20 0 0) 0%, oklch(0.15 0 0) 100%)',
          border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '1.5rem',
          boxShadow: 'inset 0 2px 0 rgba(255,255,255,0.08), 0 40px 100px rgba(0,0,0,0.8)',
          width: '100%',
          maxWidth: '780px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '24px 28px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: 16,
          flexShrink: 0,
        }}>
          <div>
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 11,
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.35)',
              marginBottom: 6,
            }}>
              {plan.name} plan · {plan.price}{plan.price !== 'Custom' ? '/mo' : ''}
            </p>
            <h2 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: 22,
              fontWeight: 700,
              color: 'oklch(0.97 0 0)',
              marginBottom: 4,
            }}>
              {allIncluded ? 'Your full agent team' : `Choose your ${plan.maxAgents} agents`}
            </h2>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.40)', lineHeight: 1.5 }}>
              {allIncluded
                ? 'All 22 specialists are included. Review your team and proceed to checkout.'
                : `Select ${plan.maxAgents} agent${plan.maxAgents > 1 ? 's' : ''} to deploy. Swap them anytime from your dashboard.`}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.10)',
              borderRadius: '50%',
              width: 36, height: 36,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'rgba(255,255,255,0.55)',
              cursor: 'pointer',
              flexShrink: 0,
              transition: 'background 0.15s',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.12)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'; }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Agent grid */}
        <div style={{
          overflowY: 'auto',
          padding: '20px 28px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
          gap: 10,
          flex: 1,
        }}>
          {ALL_AGENTS.map((agent) => {
            const isSelected = selected.has(agent.name);
            const isDisabled = !allIncluded && !isSelected && selected.size >= plan.maxAgents;
            return (
              <button
                key={agent.name}
                onClick={() => toggle(agent.name)}
                disabled={isDisabled}
                style={{
                  background: isSelected
                    ? 'linear-gradient(145deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.06) 100%)'
                    : 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
                  border: isSelected
                    ? '1px solid rgba(255,255,255,0.35)'
                    : '1px solid rgba(255,255,255,0.09)',
                  borderRadius: '1rem',
                  padding: 0,
                  cursor: isDisabled ? 'not-allowed' : allIncluded ? 'default' : 'pointer',
                  opacity: isDisabled ? 0.30 : 1,
                  transition: 'all 0.18s ease',
                  textAlign: 'left',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  if (!isDisabled && !allIncluded && !isSelected) {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.22)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.09)';
                  }
                }}
              >
                {isSelected && (
                  <div style={{
                    position: 'absolute', top: 8, right: 8, zIndex: 2,
                    width: 20, height: 20,
                    borderRadius: '50%',
                    background: 'oklch(0.97 0 0)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
                  }}>
                    <Check size={11} color="oklch(0.14 0 0)" strokeWidth={2.5} />
                  </div>
                )}
                <img
                  src={agent.image}
                  alt={agent.name}
                  loading="lazy"
                  style={{
                    width: '100%',
                    aspectRatio: '3/4',
                    objectFit: 'cover',
                    display: 'block',
                    filter: isSelected ? 'brightness(1.05)' : 'brightness(0.65)',
                    transition: 'filter 0.18s ease',
                  }}
                />
                <div style={{ padding: '8px 10px 10px' }}>
                  <p style={{
                    fontFamily: 'Space Grotesk, sans-serif',
                    fontWeight: 600,
                    fontSize: 12,
                    color: isSelected ? 'oklch(0.97 0 0)' : 'oklch(0.60 0 0)',
                    marginBottom: 2,
                    transition: 'color 0.18s',
                  }}>
                    {agent.name}
                  </p>
                  <p style={{
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: 9,
                    letterSpacing: '0.10em',
                    textTransform: 'uppercase',
                    color: 'rgba(255,255,255,0.25)',
                    lineHeight: 1.4,
                  }}>
                    {agent.category}
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 28px 24px',
          borderTop: '1px solid rgba(255,255,255,0.07)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          flexShrink: 0,
        }}>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.35)' }}>
            {allIncluded
              ? `All ${ALL_AGENTS.length} agents included`
              : `${selected.size} / ${plan.maxAgents} selected`}
          </p>
          <button
            onClick={handleCheckout}
            disabled={!ready}
            style={{
              background: ready
                ? 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 100%)'
                : 'rgba(255,255,255,0.10)',
              color: ready ? 'oklch(0.14 0 0)' : 'rgba(255,255,255,0.25)',
              border: 'none',
              borderRadius: '100px',
              padding: '12px 28px',
              fontFamily: 'Space Grotesk, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              cursor: ready ? 'pointer' : 'not-allowed',
              transition: 'opacity 0.2s, transform 0.15s',
              boxShadow: ready ? 'inset 0 1px 0 rgba(255,255,255,0.60), 0 4px 16px rgba(0,0,0,0.40)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (ready) {
                (e.currentTarget as HTMLButtonElement).style.opacity = '0.88';
                (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1.02)';
              }
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.opacity = '1';
              (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1)';
            }}
          >
            {ready ? 'Continue to checkout →' : `Select ${plan.maxAgents - selected.size} more`}
          </button>
        </div>
      </div>
    </div>
  );
}
