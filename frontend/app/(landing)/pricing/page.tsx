'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AGENTS, CATEGORY_COLORS } from '@/lib/agents';

// ─── Plan definitions ────────────────────────────────────────────────────────

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    credits: 50,
    description: 'For individuals and small teams getting started with AI agents.',
    features: [
      '50 credits / month',
      'Videos up to 30 seconds (720p)',
      '1 credit per 15s of video',
      'Agent tasks: 1–5 credits each',
      '10 avatar styles',
      'Email support',
      'Refund T&Cs apply',
    ],
    cta: 'Get Starter',
    style: 'default' as const,
  },
  {
    id: 'growth',
    name: 'Growth',
    price: 279,
    credits: 150,
    description: 'For growing teams that need volume, quality, and longer videos.',
    features: [
      '150 credits / month',
      'Videos up to 90 seconds (1080p)',
      '1 credit per 15s of video',
      'Agent tasks: 1–5 credits each',
      '50 avatar styles',
      'Priority support',
      'Custom branding',
      'Refund T&Cs apply',
    ],
    cta: 'Get Growth',
    style: 'popular' as const,
  },
  {
    id: 'business',
    name: 'Business',
    price: 399,
    credits: 300,
    description: 'Full power for high-volume teams and studios.',
    features: [
      '300 credits / month',
      'Videos up to 90 seconds (4K)',
      '1 credit per 15s of video',
      'Agent tasks: 1–5 credits each',
      'All avatar styles',
      'Dedicated account manager',
      'Custom avatars',
      'API access',
    ],
    cta: 'Get Business',
    style: 'default' as const,
  },
];

// ─── Top-up packs (same packs available on all paid plans) ───────────────────
// Priced above effective monthly rate to incentivise staying subscribed.
// Margins: 10-pack 50% | 25-pack 46% | 50-pack 42% (all ≥ 40%)

// Top-up packs — priced above effective monthly rate to incentivise subscription
// 1 credit = 15s video or 1 standard agent task
const TOPUP_PACKS = [
  { credits: 10, price: 18,  label: '10 credits',  perCredit: '$1.80/credit' },
  { credits: 25, price: 40,  label: '25 credits',  perCredit: '$1.60/credit' },
  { credits: 50, price: 70,  label: '50 credits',  perCredit: '$1.40/credit' },
];

// ─── Enterprise features ─────────────────────────────────────────────────────

const ENTERPRISE_FEATURES = [
  'Custom credit allocation',
  'Unlimited 4K videos',
  'White-label option',
  'Custom AI avatar training',
  'SLA & uptime guarantee',
  'SSO / SAML',
  'Dedicated CSM',
  'Custom API limits',
  'Volume discounts',
  'Invoiced billing',
];

// ─── Plan limits (how many agents each plan can select) ──────────────────────

const PLAN_LIMITS: Record<string, number> = { starter: 3, growth: 8, business: 22 };

// ─── Category ordering ────────────────────────────────────────────────────────

const CATEGORY_ORDER = ['Sales', 'Operations', 'Engineering', 'Support', 'Executive'] as const;

// ─── Agent Selection Modal ────────────────────────────────────────────────────

function AgentSelectionModal({
  plan,
  selectedAgentIds,
  onToggle,
  onClose,
  onContinue,
}: {
  plan: string;
  selectedAgentIds: number[];
  onToggle: (id: number) => void;
  onClose: () => void;
  onContinue: () => void;
}) {
  const limit = PLAN_LIMITS[plan] ?? 3;
  const planLabel: Record<string, string> = {
    starter: 'Starter', growth: 'Growth', business: 'Business',
  };

  const grouped = CATEGORY_ORDER.map(cat => ({
    cat,
    color: CATEGORY_COLORS[cat],
    agents: AGENTS.filter(a => a.category === cat),
  }));

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(6px)',
        }}
      />

      {/* Card */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '760px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          borderRadius: '20px',
          background: 'rgba(10,14,30,0.97)',
          border: '1px solid rgba(255,255,255,0.10)',
          backdropFilter: 'blur(24px)',
          boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            flexShrink: 0,
            padding: '24px 28px 20px',
            borderBottom: '1px solid rgba(255,255,255,0.07)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '16px',
          }}
        >
          <div>
            <h2
              style={{
                margin: 0,
                fontSize: '20px',
                fontWeight: 700,
                color: '#fff',
                letterSpacing: '-0.01em',
              }}
            >
              Select Your AI Team
            </h2>
            <p
              style={{
                margin: '4px 0 0',
                fontSize: '14px',
                color: 'rgba(255,255,255,0.45)',
              }}
            >
              {planLabel[plan]} plan &mdash; Choose up to{' '}
              <span style={{ color: '#fff', fontWeight: 600 }}>{limit}</span> agents
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
            {/* Counter pill */}
            <div
              style={{
                padding: '4px 12px',
                borderRadius: '999px',
                background: 'rgba(255,107,53,0.15)',
                border: '1px solid rgba(255,107,53,0.35)',
                fontSize: '13px',
                fontWeight: 600,
                color: '#FF6B35',
                whiteSpace: 'nowrap',
              }}
            >
              {selectedAgentIds.length}/{limit} selected
            </div>

            {/* Close button */}
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'rgba(255,255,255,0.35)',
                padding: '2px',
                display: 'flex',
                alignItems: 'center',
              }}
              onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
              onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.35)')}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Scrollable agent list */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px 28px',
          }}
        >
          {grouped.map(({ cat, color, agents }) => (
            <div key={cat} style={{ marginBottom: '28px' }}>
              {/* Category label */}
              <div style={{ marginBottom: '12px' }}>
                <span
                  style={{
                    display: 'inline-block',
                    padding: '3px 10px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: color,
                    background: `${color}18`,
                    border: `1px solid ${color}40`,
                  }}
                >
                  {cat}
                </span>
              </div>

              {/* 2-col agent grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '10px',
                }}
              >
                {agents.map(agent => {
                  const isSelected = selectedAgentIds.includes(agent.id);
                  const atLimit = selectedAgentIds.length >= limit;
                  const isDisabled = !isSelected && atLimit;

                  return (
                    <button
                      key={agent.id}
                      onClick={() => !isDisabled && onToggle(agent.id)}
                      disabled={isDisabled}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px 14px',
                        borderRadius: '12px',
                        border: isSelected
                          ? '1px solid rgba(255,107,53,0.5)'
                          : '1px solid rgba(255,255,255,0.08)',
                        background: isSelected
                          ? 'rgba(255,107,53,0.08)'
                          : 'rgba(255,255,255,0.04)',
                        cursor: isDisabled ? 'not-allowed' : 'pointer',
                        opacity: isDisabled ? 0.4 : 1,
                        textAlign: 'left',
                        transition: 'border-color 0.15s, background 0.15s',
                        width: '100%',
                      }}
                      onMouseEnter={e => {
                        if (!isDisabled && !isSelected) {
                          e.currentTarget.style.background = 'rgba(255,255,255,0.07)';
                          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)';
                        }
                      }}
                      onMouseLeave={e => {
                        if (!isDisabled && !isSelected) {
                          e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
                        }
                      }}
                    >
                      {/* Avatar */}
                      <img
                        src={agent.avatar}
                        alt={agent.name}
                        style={{
                          width: '36px',
                          height: '36px',
                          borderRadius: '50%',
                          objectFit: 'cover',
                          flexShrink: 0,
                          border: isSelected
                            ? '2px solid rgba(255,107,53,0.6)'
                            : '2px solid rgba(255,255,255,0.08)',
                        }}
                      />

                      {/* Text */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p
                          style={{
                            margin: 0,
                            fontSize: '13px',
                            fontWeight: 600,
                            color: isSelected ? '#fff' : 'rgba(255,255,255,0.85)',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {agent.name}
                        </p>
                        <p
                          style={{
                            margin: '1px 0 0',
                            fontSize: '11px',
                            color: 'rgba(255,255,255,0.40)',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {agent.role}
                        </p>
                      </div>

                      {/* Checkbox */}
                      <div
                        style={{
                          flexShrink: 0,
                          width: '18px',
                          height: '18px',
                          borderRadius: '5px',
                          border: isSelected
                            ? '2px solid #FF6B35'
                            : '2px solid rgba(255,255,255,0.20)',
                          background: isSelected ? '#FF6B35' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'background 0.15s, border-color 0.15s',
                        }}
                      >
                        {isSelected && (
                          <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                            <path
                              d="M2 6l3 3 5-5"
                              stroke="#fff"
                              strokeWidth="1.8"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div
          style={{
            flexShrink: 0,
            padding: '16px 28px 20px',
            borderTop: '1px solid rgba(255,255,255,0.07)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
          }}
        >
          {/* Back link */}
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '14px',
              color: 'rgba(255,255,255,0.40)',
              padding: 0,
              textDecoration: 'underline',
              textUnderlineOffset: '3px',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.70)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.40)')}
          >
            Back
          </button>

          {/* Continue button */}
          <button
            onClick={onContinue}
            disabled={selectedAgentIds.length === 0}
            style={{
              padding: '11px 28px',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 600,
              color: '#fff',
              border: 'none',
              cursor: selectedAgentIds.length === 0 ? 'not-allowed' : 'pointer',
              opacity: selectedAgentIds.length === 0 ? 0.4 : 1,
              background:
                selectedAgentIds.length === 0
                  ? 'rgba(255,255,255,0.08)'
                  : 'linear-gradient(135deg, #FF6B35, #e85520)',
              boxShadow:
                selectedAgentIds.length === 0
                  ? 'none'
                  : '0 4px 20px rgba(255,107,53,0.35)',
              transition: 'opacity 0.15s, box-shadow 0.15s',
            }}
          >
            Continue to Create Account →
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Inquiry modal ────────────────────────────────────────────────────────────

interface EnquiryForm {
  name: string;
  company: string;
  email: string;
  phone: string;
  volume: string;
  message: string;
}

const VOLUME_OPTIONS = ['Under 100', '100 – 500', '500 – 1,000', '1,000 – 5,000', '5,000+'];

function EnquiryModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState<EnquiryForm>({
    name: '', company: '', email: '', phone: '', volume: '', message: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [err, setErr] = useState('');

  const set = (k: keyof EnquiryForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => setForm(prev => ({ ...prev, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.company || !form.email) {
      setErr('Please fill in name, company, and email.');
      return;
    }
    setErr('');
    setSubmitting(true);
    try {
      await fetch('/api/contact/enterprise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setSubmitted(true);
    } catch {
      setErr('Something went wrong — please email us at hello@vantro.ai');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
        style={{ background: 'rgba(10,14,30,0.95)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(24px)' }}>
        {/* Header */}
        <div className="px-6 pt-6 pb-4 border-b border-white/[0.08] flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-6 h-6 rounded-md bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </span>
              <h2 className="text-lg font-bold text-white">Enterprise enquiry</h2>
            </div>
            <p className="text-gray-400 text-sm">We'll get back to you within one business day.</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors ml-4 mt-0.5">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 max-h-[70vh] overflow-y-auto">
          {submitted ? (
            <div className="text-center py-8">
              <div className="w-14 h-14 bg-green-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">Thanks, {form.name.split(' ')[0]}!</h3>
              <p className="text-gray-400 text-sm mb-6">
                We've received your enquiry and will reach out to <span className="text-white">{form.email}</span> within one business day.
              </p>
              <button
                onClick={onClose}
                className="bg-gray-800 hover:bg-gray-700 text-white text-sm px-6 py-2.5 rounded-xl transition-all"
              >
                Close
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Full name <span className="text-red-400">*</span></label>
                  <input
                    value={form.name}
                    onChange={set('name')}
                    placeholder="Jane Smith"
                    className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/[0.07] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Company <span className="text-red-400">*</span></label>
                  <input
                    value={form.company}
                    onChange={set('company')}
                    placeholder="Acme Corp"
                    className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/[0.07] transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">Work email <span className="text-red-400">*</span></label>
                <input
                  type="email"
                  value={form.email}
                  onChange={set('email')}
                  placeholder="jane@acme.com"
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/[0.07] transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Phone <span className="text-gray-500 font-normal">(optional)</span></label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={set('phone')}
                    placeholder="+1 555 000 0000"
                    className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/[0.07] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Est. videos / month</label>
                  <select
                    value={form.volume}
                    onChange={set('volume')}
                    className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500/60 transition-all"
                  >
                    <option value="">Select range</option>
                    {VOLUME_OPTIONS.map(v => <option key={v}>{v}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">Message <span className="text-gray-500 font-normal">(optional)</span></label>
                <textarea
                  value={form.message}
                  onChange={set('message')}
                  rows={3}
                  placeholder="Tell us about your use case, integrations needed, or any specific requirements..."
                  className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/25 focus:outline-none focus:border-violet-500/60 transition-all resize-none"
                />
              </div>

              {err && (
                <p className="text-red-400 text-xs">{err}</p>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-all text-sm"
              >
                {submitting ? 'Sending...' : 'Send enquiry'}
              </button>

              <p className="text-center text-gray-500 text-xs">
                Or email us directly at{' '}
                <a href="mailto:hello@vantro.ai" className="text-purple-400 hover:underline">hello@vantro.ai</a>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Top-up packs section ─────────────────────────────────────────────────────

function TopUpSection() {
  const [open, setOpen] = useState(false);
  const [loadingPack, setLoadingPack] = useState<number | null>(null);

  const handleTopUp = async (credits: number) => {
    const token = localStorage.getItem('token');
    // TODO: replace with internal /login route once that page is created
    if (!token) { window.location.href = 'https://vantro.ai/login?redirect=/pricing'; return; }
    setLoadingPack(credits);
    try {
      const res = await fetch('/api/stripe/create-topup-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ credits }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        const SAFE_REDIRECT_ORIGINS = ['https://checkout.stripe.com', 'https://billing.stripe.com'];
        function isSafeRedirect(url: string): boolean {
          try { const { origin } = new URL(url); return SAFE_REDIRECT_ORIGINS.includes(origin); } catch { return false; }
        }
        if (isSafeRedirect(data.checkout_url)) {
          window.location.href = data.checkout_url;
        } else {
          console.error('Unsafe redirect blocked:', data.checkout_url);
        }
      }
    } catch {
      // silently fall back
    } finally {
      setLoadingPack(null);
    }
  };

  return (
    <div className="mt-4 border-t border-white/[0.07] pt-4">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center justify-between w-full text-left group"
      >
        <span className="text-xs font-semibold text-white/40 group-hover:text-white/70 transition-colors">
          Need more credits?
        </span>
        <svg
          className={`w-3.5 h-3.5 text-white/30 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="mt-3 space-y-2">
          <p className="text-xs text-white/30 mb-3">
            One-time top-ups — no subscription change required.
          </p>
          {TOPUP_PACKS.map(pack => (
            <div
              key={pack.credits}
              className="flex items-center justify-between bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-2.5"
            >
              <div>
                <p className="text-sm font-medium text-white">{pack.label}</p>
                <p className="text-xs text-white/30">{pack.perCredit}</p>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="text-sm font-bold text-white">${pack.price}</span>
                <button
                  onClick={() => handleTopUp(pack.credits)}
                  disabled={loadingPack === pack.credits}
                  className="text-xs bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg font-medium transition-all"
                >
                  {loadingPack === pack.credits ? '…' : 'Add'}
                </button>
              </div>
            </div>
          ))}
          <p className="text-xs text-white/20 mt-2 text-center">
            Monthly plans offer better value — from $0.66/credit on Growth
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function PricingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [showEnquiry, setShowEnquiry] = useState(false);
  const [agentModalPlan, setAgentModalPlan] = useState<string | null>(null);
  const [selectedAgentIds, setSelectedAgentIds] = useState<number[]>([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const plan = params.get('plan');
    if (plan && ['starter', 'growth', 'business'].includes(plan)) {
      setAgentModalPlan(plan);
      setSelectedAgentIds([]);
    }
  }, []);

  const handlePlanCTA = (planId: string) => {
    if (planId === 'enterprise') {
      setShowEnquiry(true);
      return;
    }
    // For non-enterprise: open agent selection modal (unauthenticated path)
    const token = localStorage.getItem('token');
    if (token) {
      // Authenticated: go straight to checkout / dashboard
      setError('');
      setAgentModalPlan(planId);
      setSelectedAgentIds([]);
    } else {
      // Unauthenticated: open agent modal first so they can pick their team
      setError('');
      setAgentModalPlan(planId);
      setSelectedAgentIds([]);
    }
  };

  const handleToggleAgent = (id: number) => {
    if (!agentModalPlan) return;
    const limit = PLAN_LIMITS[agentModalPlan] ?? 3;
    setSelectedAgentIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(a => a !== id);
      }
      if (prev.length >= limit) return prev;
      return [...prev, id];
    });
  };

  const handleAgentContinue = () => {
    if (!agentModalPlan || selectedAgentIds.length === 0) return;
    const agentsParam = selectedAgentIds.join(',');
    setAgentModalPlan(null);
    setSelectedAgentIds([]);
    router.push(`/checkout?plan=${agentModalPlan}&agents=${agentsParam}`);
  };

  return (
    <div
      className="min-h-screen text-white"
      style={{
        background: [
          'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(124,58,237,0.18) 0%, transparent 60%)',
          'radial-gradient(ellipse 50% 40% at 80% 70%, rgba(59,130,246,0.10) 0%, transparent 55%)',
          '#070D1F',
        ].join(', '),
      }}
    >
      {/* Ambient grid */}
      <div className="pointer-events-none fixed inset-0 mesh-grid opacity-40" />

      {/* Ambient blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
        <div className="absolute -top-40 left-1/4 w-[500px] h-[500px] bg-violet-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-blue-600/08 rounded-full blur-[100px]" />
      </div>

      {showEnquiry && <EnquiryModal onClose={() => setShowEnquiry(false)} />}
      {agentModalPlan && (
        <AgentSelectionModal
          plan={agentModalPlan}
          selectedAgentIds={selectedAgentIds}
          onToggle={handleToggleAgent}
          onClose={() => { setAgentModalPlan(null); setSelectedAgentIds([]); }}
          onContinue={handleAgentContinue}
        />
      )}

      {/* Nav */}
      <nav className="sticky top-0 z-40 border-b border-white/[0.06] px-6 py-4 flex items-center justify-between"
        style={{ backdropFilter: 'blur(20px) saturate(1.5)', background: 'rgba(7,13,31,0.85)' }}>
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-black text-xs"
            style={{ background: 'linear-gradient(135deg,#7C3AED,#3B82F6)', boxShadow: '0 0 16px rgba(124,58,237,0.45)' }}>V</div>
          <span className="text-lg font-bold tracking-tight">Vantro<span className="text-violet-400">.ai</span></span>
        </Link>
        <div className="flex gap-3 items-center">
          <Link href="https://vantro.ai/login" className="text-white/50 hover:text-white text-sm transition-colors">Log in</Link>
          <Link href="https://vantro.ai/register" className="btn-primary text-sm px-5 py-2">Get started free</Link>
        </div>
      </nav>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <span className="section-badge-violet mb-5 inline-flex">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            Transparent pricing
          </span>
          <h1 className="text-5xl sm:text-6xl font-bold mb-4 tracking-tight">
            Simple,{' '}
            <span className="gradient-text">honest pricing</span>
          </h1>
          <p className="text-white/50 text-lg max-w-xl mx-auto">Start free. Scale as you grow. No hidden fees, no surprises.</p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-10 bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-xl text-center text-sm">
            {error}
          </div>
        )}

        {/* Plan grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 items-start">

          {/* Paid plans */}
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`relative rounded-2xl p-7 flex flex-col transition-all duration-300 ${
                plan.style === 'popular'
                  ? 'glass-iridescent shadow-[0_0_40px_rgba(124,58,237,0.20)]'
                  : 'glass border border-white/[0.08]'
              }`}
            >
              {plan.style === 'popular' && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="aurora text-white text-xs font-semibold px-4 py-1.5 rounded-full whitespace-nowrap shadow-[0_4px_16px_rgba(124,58,237,0.5)]">
                    Most popular
                  </span>
                </div>
              )}

              {/* Plan header */}
              <div className="mb-5">
                <h2 className="text-lg font-bold mb-1 text-white">{plan.name}</h2>
                <p className="text-white/40 text-xs mb-4 leading-relaxed">{plan.description}</p>
                <div className="flex items-end gap-1">
                  <span className="text-4xl font-bold text-white">${plan.price}</span>
                  <span className="text-white/40 mb-1 text-sm">/mo</span>
                </div>
                <p className="text-xs text-white/30 mt-1">{plan.credits} credits included</p>
              </div>

              {/* Features */}
              <ul className="space-y-2.5 mb-6 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm text-white/65">
                    <div className="w-4 h-4 rounded-full bg-violet-500/20 border border-violet-400/30 flex items-center justify-center shrink-0 mt-0.5">
                      <svg className="w-2.5 h-2.5 text-violet-400" fill="none" viewBox="0 0 12 12">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    {f}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                onClick={() => handlePlanCTA(plan.id)}
                disabled={loading === plan.id}
                className={`w-full py-3 rounded-xl font-semibold text-sm transition-all disabled:opacity-60 ${
                  plan.style === 'popular'
                    ? 'btn-primary'
                    : 'btn-secondary'
                }`}
              >
                {loading === plan.id ? 'Loading…' : plan.cta}
              </button>

              <TopUpSection />
            </div>
          ))}

          {/* Enterprise card */}
          <div className="relative rounded-2xl p-7 flex flex-col"
            style={{
              background: 'linear-gradient(160deg, rgba(245,158,11,0.08) 0%, rgba(10,17,40,0.6) 100%)',
              border: '1px solid rgba(245,158,11,0.25)',
              backdropFilter: 'blur(20px)',
            }}>
            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
              <span className="bg-gradient-to-r from-amber-500 to-orange-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full whitespace-nowrap shadow-[0_4px_16px_rgba(245,158,11,0.4)]">
                Enterprise
              </span>
            </div>

            <div className="mb-5">
              <h2 className="text-lg font-bold mb-1 text-amber-100">Enterprise</h2>
              <p className="text-white/40 text-xs mb-4 leading-relaxed">Custom-built for large orgs, studios, and platform partners.</p>
              <div className="flex items-end gap-1">
                <span className="text-4xl font-bold text-white">Custom</span>
              </div>
              <p className="text-xs text-white/30 mt-1">Volume pricing · invoiced billing</p>
            </div>

            <ul className="space-y-2.5 mb-6 flex-1">
              {ENTERPRISE_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-sm text-white/65">
                  <div className="w-4 h-4 rounded-full bg-amber-500/20 border border-amber-400/30 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-2.5 h-2.5 text-amber-400" fill="none" viewBox="0 0 12 12">
                      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handlePlanCTA('enterprise')}
              className="w-full py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white transition-all shadow-[0_4px_20px_rgba(245,158,11,0.3)]"
            >
              Contact us
            </button>

            <p className="text-center text-xs text-white/25 mt-4">Response within 1 business day</p>
          </div>
        </div>

        {/* How credits work */}
        <div className="mt-16 max-w-3xl mx-auto rounded-2xl border border-white/[0.08] bg-white/[0.03] px-8 py-7">
          <h3 className="text-white font-semibold text-base mb-4">How credits work</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-white/55 leading-relaxed">
            <div>
              <p className="text-white/80 font-medium mb-1">AI video generation</p>
              <p>1 credit per 15 seconds of video (minimum 1 credit). A 30-second video costs 2 credits; a 90-second video costs 6 credits.</p>
            </div>
            <div>
              <p className="text-white/80 font-medium mb-1">AI agent tasks</p>
              <p>Every agent task (research, copywriting, strategy, email sequences, etc.) consumes 1–5 credits depending on complexity. You always see the credit cost before confirming a task.</p>
            </div>
            <div>
              <p className="text-white/80 font-medium mb-1">Unused credits</p>
              <p>Credits reset each billing cycle and do not roll over. Top up at any time from your billing dashboard if you need more mid-cycle.</p>
            </div>
            <div>
              <p className="text-white/80 font-medium mb-1">No hidden charges</p>
              <p>You are only ever charged the monthly subscription price. Credits are the usage unit within that subscription — there are no surprise per-task fees on top.</p>
            </div>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-center text-white/30 text-sm mt-14">
          Refund T&Cs apply. Cancel anytime.{' '}
          <button onClick={() => handlePlanCTA('enterprise')} className="text-violet-400 hover:text-violet-300 transition-colors">
            Talk to sales →
          </button>
        </p>
        <div className="flex items-center justify-center gap-4 mt-4 text-xs text-white/20">
          <Link href="/privacy" className="hover:text-white/50 transition-colors">Privacy Policy</Link>
          <span>·</span>
          <Link href="/terms" className="hover:text-white/50 transition-colors">Terms of Service</Link>
          <span>·</span>
          <span>GDPR & CCPA Compliant</span>
        </div>
      </div>
    </div>
  );
}
