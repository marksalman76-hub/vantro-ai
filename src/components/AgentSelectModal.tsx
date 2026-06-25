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
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose(); }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  function select(name: string) {
    setSelected((prev) => {
      if (prev.includes(name)) return prev.filter((n) => n !== name);
      if (prev.length >= plan.maxAgents) return prev;
      return [...prev, name];
    });
  }

  async function handleCheckout() {
    try {
      const res = await fetch('https://api.vantro.ai/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: plan.name, agents: selected }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch {
      // Stripe checkout unavailable — surface error rather than wrong redirect
      alert('Checkout is temporarily unavailable. Please try again or contact support@vantro.ai.');
    }
  }

  const ready = selected.length > 0;
  const selectedSet = new Set(selected);
  const available = ALL_AGENTS.filter((a) => !selectedSet.has(a.name));
  const selectedAgents = selected.map((n) => ALL_AGENTS.find((a) => a.name === n)!).filter(Boolean);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.80)',
        backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'linear-gradient(145deg, oklch(0.20 0 0) 0%, oklch(0.14 0 0) 100%)',
          border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '1.5rem',
          boxShadow: 'inset 0 2px 0 rgba(255,255,255,0.08), 0 40px 120px rgba(0,0,0,0.9)',
          width: '100%',
          maxWidth: '820px',
          maxHeight: '92vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* ── Header ── */}
        <div style={{
          padding: '22px 26px 18px',
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
              fontSize: 10,
              letterSpacing: '0.16em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.30)',
              marginBottom: 5,
            }}>
              {plan.name} · {plan.price}{plan.price !== 'Custom' ? '/mo' : ''}
            </p>
            <h2 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: 20,
              fontWeight: 700,
              color: 'oklch(0.97 0 0)',
              marginBottom: 3,
            }}>
              {allIncluded ? `Pick from all ${plan.maxAgents} agents` : `Pick your ${plan.maxAgents} agents`}
            </h2>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.38)', lineHeight: 1.5 }}>
              {`Choose up to ${plan.maxAgents} from 22. Selected agents drop below — click again to remove.`}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.10)',
              borderRadius: '50%',
              width: 34, height: 34,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'rgba(255,255,255,0.50)',
              cursor: 'pointer',
              flexShrink: 0,
              transition: 'background 0.15s',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.12)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'; }}
          >
            <X size={15} />
          </button>
        </div>

        {/* ── Available agents (scrollable) ── */}
        <div style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          padding: '16px 26px',
        }}>
          {available.length > 0 && (
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.25)',
              marginBottom: 12,
            }}>
              Available — {available.length} agents
            </p>
          )}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))',
            gap: 8,
          }}>
            {available.map((agent) => {
              const atLimit = selected.length >= plan.maxAgents;
              return (
                <button
                  key={agent.name}
                  onClick={() => select(agent.name)}
                  disabled={atLimit}
                  style={{
                    background: 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '0.85rem',
                    padding: 0,
                    cursor: atLimit ? 'not-allowed' : 'pointer',
                    opacity: atLimit ? 0.28 : 1,
                    transition: 'border-color 0.15s, opacity 0.15s',
                    textAlign: 'left',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    if (!atLimit)
                      (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.28)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.08)';
                  }}
                >
                  <img
                    src={agent.image}
                    alt={agent.name}
                    loading="lazy"
                    style={{
                      width: '100%',
                      aspectRatio: '3/4',
                      objectFit: 'cover',
                      display: 'block',
                      filter: 'brightness(0.60)',
                    }}
                  />
                  <div style={{ padding: '7px 9px 9px' }}>
                    <p style={{
                      fontFamily: 'Space Grotesk, sans-serif',
                      fontWeight: 600,
                      fontSize: 11,
                      color: 'oklch(0.55 0 0)',
                      marginBottom: 2,
                    }}>
                      {agent.name}
                    </p>
                    <p style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: 8,
                      letterSpacing: '0.10em',
                      textTransform: 'uppercase',
                      color: 'rgba(255,255,255,0.22)',
                    }}>
                      {agent.category}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Selected strip (drops in when agents picked) ── */}
        {selectedAgents.length > 0 && (
          <div style={{
            borderTop: '1px solid rgba(255,255,255,0.08)',
            padding: '14px 26px 12px',
            flexShrink: 0,
          }}>
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.40)',
              marginBottom: 10,
            }}>
              Selected · {selectedAgents.length} / {plan.maxAgents}
            </p>
            <div style={{
              display: 'flex',
              gap: 8,
              flexWrap: 'wrap',
            }}>
              {selectedAgents.map((agent) => (
                <button
                  key={agent.name}
                  onClick={() => select(agent.name)}
                  title={`Remove ${agent.name}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    background: 'linear-gradient(145deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.07) 100%)',
                    border: '1px solid rgba(255,255,255,0.30)',
                    borderRadius: '100px',
                    padding: '4px 12px 4px 4px',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s, background 0.15s',
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.50)';
                    (e.currentTarget as HTMLButtonElement).style.background = 'linear-gradient(145deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0.10) 100%)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.30)';
                    (e.currentTarget as HTMLButtonElement).style.background = 'linear-gradient(145deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.07) 100%)';
                  }}
                >
                  <img
                    src={agent.image}
                    alt={agent.name}
                    style={{
                      width: 28, height: 28,
                      borderRadius: '50%',
                      objectFit: 'cover',
                      objectPosition: 'top',
                      border: '1px solid rgba(255,255,255,0.25)',
                      filter: 'brightness(1.05)',
                    }}
                  />
                  <span style={{
                    fontFamily: 'Space Grotesk, sans-serif',
                    fontWeight: 600,
                    fontSize: 12,
                    color: 'oklch(0.92 0 0)',
                  }}>
                    {agent.name}
                  </span>
                  <X size={10} color="rgba(255,255,255,0.40)" style={{ marginLeft: 2 }} />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Footer ── */}
        <div style={{
          padding: '14px 26px 20px',
          borderTop: '1px solid rgba(255,255,255,0.07)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          flexShrink: 0,
        }}>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.30)' }}>
            {selected.length === 0
              ? `Select up to ${plan.maxAgents} agents`
              : selected.length >= plan.maxAgents
              ? 'Team locked in. Ready to deploy.'
              : `${selected.length} selected — add ${plan.maxAgents - selected.length} more or proceed`}
          </p>
          <button
            onClick={handleCheckout}
            disabled={!ready}
            style={{
              background: ready
                ? 'linear-gradient(180deg, #ffffff 0%, #d4d4d4 100%)'
                : 'rgba(255,255,255,0.08)',
              color: ready ? 'oklch(0.12 0 0)' : 'rgba(255,255,255,0.22)',
              border: 'none',
              borderRadius: '100px',
              padding: '11px 26px',
              fontFamily: 'Space Grotesk, sans-serif',
              fontWeight: 700,
              fontSize: 14,
              cursor: ready ? 'pointer' : 'not-allowed',
              transition: 'opacity 0.18s, transform 0.15s',
              boxShadow: ready ? 'inset 0 1px 0 rgba(255,255,255,0.55), 0 4px 18px rgba(0,0,0,0.45)' : 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
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
            {ready && <Check size={14} strokeWidth={2.5} />}
            {ready ? 'Continue to checkout' : `Select ${plan.maxAgents - selected.length} more`}
          </button>
        </div>
      </div>
    </div>
  );
}
