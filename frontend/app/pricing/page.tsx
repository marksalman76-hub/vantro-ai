'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

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
      '14-day free trial',
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
      '14-day free trial',
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

// ─── Agent catalogue (matches billing.py AGENT_DISPLAY_NAMES) ────────────────

const PLAN_SLOTS: Record<string, number> = { starter: 2, growth: 5, business: 11 };

interface AgentMeta {
  id: string;
  name: string;
  category: string;
  desc: string;
}

const ALL_AGENTS: AgentMeta[] = [
  { id: 'intake_trial_agent',       name: 'Intake & Onboarding',      category: 'Core',        desc: 'Qualify inbound leads, book demos, activate trials' },
  { id: 'brand_voice_agent',        name: 'Brand Voice',              category: 'Core',        desc: 'Define & enforce consistent brand tone across all output' },
  { id: 'seo_agent',                name: 'SEO Optimizer',            category: 'Core',        desc: 'Keyword strategy, on-page SEO, content gap analysis' },
  { id: 'content_strategy_agent',   name: 'Content Strategy',         category: 'Content',     desc: 'Content calendars, topic clusters, editorial planning' },
  { id: 'social_media_agent',       name: 'Social Media',             category: 'Content',     desc: 'Platform-native posts, scheduling, engagement copy' },
  { id: 'video_script_agent',       name: 'Video Script',             category: 'Content',     desc: 'YouTube, Reels, TikTok, and long-form video scripts' },
  { id: 'copywriting_agent',        name: 'Copywriting',              category: 'Content',     desc: 'High-converting landing pages, ads, and sales copy' },
  { id: 'paid_ads_agent',           name: 'Paid Advertising',         category: 'Growth',      desc: 'Google Ads, Meta, LinkedIn — campaigns and creative' },
  { id: 'conversion_optimizer_agent', name: 'Conversion Optimizer',  category: 'Growth',      desc: 'CRO audits, A/B test briefs, funnel friction analysis' },
  { id: 'growth_hacking_agent',     name: 'Growth Hacking',           category: 'Growth',      desc: 'Viral loops, referral programs, PLG experiment design' },
  { id: 'market_expansion_agent',   name: 'Market Expansion',         category: 'Growth',      desc: 'New market entry strategy, geo-expansion playbooks' },
  { id: 'email_marketing_agent',    name: 'Email Marketing',          category: 'Revenue',     desc: 'Sequences, deliverability, list hygiene, A/B cadences' },
  { id: 'lead_generation_agent',    name: 'Lead Generation',          category: 'Revenue',     desc: 'Lead magnets, prospecting workflows, ICP targeting' },
  { id: 'retention_agent',          name: 'Retention',                category: 'Revenue',     desc: 'Churn prevention, win-back flows, NRR optimisation' },
  { id: 'affiliate_partnership_agent', name: 'Affiliate & Partnerships', category: 'Revenue', desc: 'Commission structures, recruit criteria, payout tiers' },
  { id: 'research_analytics_agent', name: 'Research & Analytics',     category: 'Intelligence', desc: 'Market research, KPI analysis, competitive intelligence' },
  { id: 'competitor_analyst_agent', name: 'Competitor Analysis',      category: 'Intelligence', desc: 'Competitor monitoring, gap analysis, positioning briefs' },
  { id: 'campaign_orchestrator_agent', name: 'Campaign Orchestrator', category: 'Intelligence', desc: 'Multi-channel campaign coordination and performance review' },
  { id: 'customer_success_agent',   name: 'Customer Success',         category: 'Business',    desc: 'Onboarding flows, health scores, escalation playbooks' },
  { id: 'product_launch_agent',     name: 'Product Launch',           category: 'Business',    desc: 'Launch checklists, GTM sequencing, post-launch amplification' },
  { id: 'influencer_outreach_agent', name: 'Influencer Outreach',     category: 'Business',    desc: 'Creator outreach scripts, rate negotiation, campaign briefs' },
  { id: 'pr_media_agent',           name: 'PR & Media',               category: 'Business',    desc: 'Media pitches, press releases, journalist targeting' },
];

const CATEGORY_ORDER = ['Core', 'Content', 'Growth', 'Revenue', 'Intelligence', 'Business'];

const CATEGORY_COLORS: Record<string, string> = {
  Core:        'bg-violet-500/20 text-violet-300 border-violet-500/30',
  Content:     'bg-blue-500/20 text-blue-300 border-blue-500/30',
  Growth:      'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  Revenue:     'bg-amber-500/20 text-amber-300 border-amber-500/30',
  Intelligence:'bg-pink-500/20 text-pink-300 border-pink-500/30',
  Business:    'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
};

// ─── Agent Selection Modal ────────────────────────────────────────────────────

function AgentSelectionModal({
  plan,
  onClose,
  onConfirm,
}: {
  plan: string;
  onClose: () => void;
  onConfirm: (agentIds: string[]) => void;
}) {
  const slots = PLAN_SLOTS[plan] ?? 2;
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < slots) {
        next.add(id);
      }
      return next;
    });
  };

  const planLabel: Record<string, string> = { starter: 'Starter', growth: 'Growth', business: 'Business', enterprise: 'Enterprise' };
  const grouped = CATEGORY_ORDER.map(cat => ({
    cat,
    agents: ALL_AGENTS.filter(a => a.category === cat),
  }));

  const isEnterprise = plan === 'enterprise';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

      <div
        className={`relative w-full flex flex-col rounded-2xl shadow-2xl overflow-hidden ${isEnterprise ? 'max-w-lg' : 'max-w-4xl max-h-[90vh]'}`}
        style={{ background: 'rgba(8,12,28,0.97)', border: '1px solid rgba(255,255,255,0.1)' }}
      >
        {/* Header */}
        <div className="flex items-start justify-between px-6 pt-6 pb-4 border-b border-white/[0.08] flex-shrink-0">
          <div>
            <h2 className="text-xl font-bold text-white mb-0.5">
              {isEnterprise ? 'Enterprise plan' : 'Choose your agents'}
            </h2>
            <p className="text-gray-400 text-sm">
              {isEnterprise
                ? 'Custom agent allocation · Tailored to your business'
                : `${planLabel[plan]} plan · Select up to `}
              {!isEnterprise && <span className="text-white font-semibold">{slots}</span>}
              {!isEnterprise && ` agents · `}
              {!isEnterprise && (
                <span className={selected.size === slots ? 'text-violet-400 font-semibold' : 'text-gray-400'}>
                  {selected.size}/{slots} selected
                </span>
              )}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors ml-4">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {isEnterprise ? (
          /* Enterprise — no agent picker, redirect to enquiry */
          <div className="px-6 py-8 text-center">
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg,rgba(245,158,11,0.25),rgba(234,88,12,0.25))', border: '1px solid rgba(245,158,11,0.3)' }}>
              <svg className="w-7 h-7 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Fully custom agent setup</h3>
            <p className="text-gray-400 text-sm mb-1">Enterprise plans include all 22 agents plus custom configuration,</p>
            <p className="text-gray-400 text-sm mb-6">dedicated support, and volume pricing.</p>
            <div className="space-y-2 text-sm text-left bg-white/[0.04] rounded-xl p-4 mb-6">
              {['All 22 agents unlocked', 'Custom credit allocation', 'Dedicated account manager', 'White-label option', 'SLA & uptime guarantee', 'Invoiced billing'].map(f => (
                <div key={f} className="flex items-center gap-2.5 text-gray-300">
                  <svg className="w-4 h-4 text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 12 12">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {f}
                </div>
              ))}
            </div>
            <div className="flex gap-3">
              <button onClick={onClose} className="flex-1 px-5 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-white border border-white/10 hover:border-white/20 transition-all">
                Back
              </button>
              <button
                onClick={() => onConfirm([])}
                className="flex-1 px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition-all"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}
              >
                Contact us →
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Agent grid */}
            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
              {grouped.map(({ cat, agents }) => (
                <div key={cat}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${CATEGORY_COLORS[cat]}`}>
                      {cat}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                    {agents.map(agent => {
                      const isSelected = selected.has(agent.id);
                      const isDisabled = !isSelected && selected.size >= slots;
                      return (
                        <button
                          key={agent.id}
                          onClick={() => toggle(agent.id)}
                          disabled={isDisabled}
                          className={`relative text-left p-3.5 rounded-xl border transition-all ${
                            isSelected
                              ? 'bg-violet-600/20 border-violet-500/60 shadow-[0_0_12px_rgba(124,58,237,0.2)]'
                              : isDisabled
                              ? 'bg-white/[0.02] border-white/[0.05] opacity-40 cursor-not-allowed'
                              : 'bg-white/[0.04] border-white/[0.08] hover:bg-white/[0.07] hover:border-white/[0.15]'
                          }`}
                        >
                          {isSelected && (
                            <div className="absolute top-2.5 right-2.5 w-4 h-4 bg-violet-500 rounded-full flex items-center justify-center">
                              <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          )}
                          <p className={`text-sm font-semibold mb-0.5 pr-6 ${isSelected ? 'text-white' : 'text-gray-200'}`}>
                            {agent.name}
                          </p>
                          <p className="text-xs text-gray-500 leading-relaxed">{agent.desc}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-white/[0.08] flex-shrink-0 gap-4">
              <p className="text-xs text-gray-500">
                {selected.size === 0
                  ? 'Select at least one agent to continue'
                  : selected.size < slots
                  ? `${slots - selected.size} more slot${slots - selected.size !== 1 ? 's' : ''} available`
                  : 'Selection complete — agents locked after payment'}
              </p>
              <div className="flex gap-3 flex-shrink-0">
                <button
                  onClick={onClose}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-white border border-white/10 hover:border-white/20 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={() => onConfirm(Array.from(selected))}
                  disabled={selected.size === 0}
                  className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-all"
                >
                  Confirm selection →
                </button>
              </div>
            </div>
          </>
        )}
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
    if (!token) { window.location.href = '/login?redirect=/pricing'; return; }
    setLoadingPack(credits);
    try {
      const res = await fetch('/api/stripe/create-topup-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ credits }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
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

  const handlePlanCTA = (planId: string) => {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (!token) {
      window.location.href = `/login?redirect=/pricing`;
      return;
    }
    setError('');
    setAgentModalPlan(planId);
  };

  const handleAgentConfirm = (agentIds: string[]) => {
    if (!agentModalPlan) return;
    setAgentModalPlan(null);
    if (agentModalPlan === 'enterprise') {
      setShowEnquiry(true);
      return;
    }
    const agentsParam = agentIds.join(',');
    router.push(`/checkout?plan=${agentModalPlan}&agents=${encodeURIComponent(agentsParam)}`);
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
          onClose={() => setAgentModalPlan(null)}
          onConfirm={handleAgentConfirm}
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
          <Link href="/login" className="text-white/50 hover:text-white text-sm transition-colors">Log in</Link>
          <Link href="/signup" className="btn-primary text-sm px-5 py-2">Get started free</Link>
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
          All paid plans include a 14-day free trial. Cancel anytime.{' '}
          <button onClick={() => handlePlanCTA('enterprise')} className="text-violet-400 hover:text-violet-300 transition-colors">
            Talk to sales →
          </button>
        </p>
      </div>
    </div>
  );
}
