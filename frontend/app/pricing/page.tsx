'use client';

import { useState } from 'react';
import Link from 'next/link';

// ─── Plan definitions ────────────────────────────────────────────────────────

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    credits: 60,
    description: 'For individuals and small teams exploring AI video.',
    features: [
      '60 AI videos / month',
      '720p video quality',
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
    credits: 200,
    description: 'For growing teams that need volume and quality.',
    features: [
      '200 AI videos / month',
      '1080p video quality',
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
      '300 AI videos / month',
      '4K video quality',
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

const TOPUP_PACKS = [
  { credits: 10, price: 15,  label: '10 credits',  perVideo: '$1.50' },
  { credits: 25, price: 35,  label: '25 credits',  perVideo: '$1.40' },
  { credits: 50, price: 65,  label: '50 credits',  perVideo: '$1.30' },
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
      <div className="relative w-full max-w-lg bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 pt-6 pb-4 border-b border-gray-800 flex items-start justify-between">
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
                    className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Company <span className="text-red-400">*</span></label>
                  <input
                    value={form.company}
                    onChange={set('company')}
                    placeholder="Acme Corp"
                    className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500"
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
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500"
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
                    className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">Est. videos / month</label>
                  <select
                    value={form.volume}
                    onChange={set('volume')}
                    className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-purple-500"
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
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
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

function TopUpSection({ planId }: { planId: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-4 border-t border-gray-700/60 pt-4">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center justify-between w-full text-left group"
      >
        <span className="text-xs font-semibold text-gray-400 group-hover:text-gray-200 transition-colors">
          Need more credits?
        </span>
        <svg
          className={`w-3.5 h-3.5 text-gray-500 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="mt-3 space-y-2">
          <p className="text-xs text-gray-500 mb-3">
            One-time top-ups — no subscription change required.
          </p>
          {TOPUP_PACKS.map(pack => (
            <div
              key={pack.credits}
              className="flex items-center justify-between bg-gray-800/70 border border-gray-700 rounded-xl px-3 py-2.5"
            >
              <div>
                <p className="text-sm font-medium text-white">{pack.label}</p>
                <p className="text-xs text-gray-500">{pack.perVideo} / video</p>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="text-sm font-bold text-white">${pack.price}</span>
                <button
                  onClick={() => {
                    const token = localStorage.getItem('token');
                    if (!token) { window.location.href = `/login?redirect=/pricing`; return; }
                    window.location.href = `/dashboard?topup=${pack.credits}`;
                  }}
                  className="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg font-medium transition-all"
                >
                  Add
                </button>
              </div>
            </div>
          ))}
          <p className="text-xs text-gray-600 mt-2 text-center">
            Monthly plans offer better value — from $1.33/video
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function PricingPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [showEnquiry, setShowEnquiry] = useState(false);

  const handleSubscribe = async (planId: string) => {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/login?redirect=/pricing';
      return;
    }
    setLoading(planId);
    setError('');
    try {
      const res = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ plan: planId }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || data.error || 'Something went wrong'); return; }
      window.location.href = data.checkout_url;
    } catch {
      setError('Network error — please try again');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {showEnquiry && <EnquiryModal onClose={() => setShowEnquiry(false)} />}

      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="text-lg font-bold">Vantro<span className="text-violet-400">.ai</span></span>
        </Link>
        <div className="flex gap-4 items-center">
          <Link href="/login" className="text-gray-400 hover:text-white text-sm">Log in</Link>
          <Link href="/signup" className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-4 py-2 rounded-lg font-medium">
            Get started
          </Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">Simple, transparent pricing</h1>
          <p className="text-gray-400 text-lg">Start free, scale as you grow. No hidden fees.</p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-10 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-center text-sm">
            {error}
          </div>
        )}

        {/* Plan grid — 4 columns on xl, 2 on md, 1 on mobile */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 items-start">

          {/* ── Paid plans ── */}
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`relative rounded-2xl p-7 border flex flex-col ${
                plan.style === 'popular'
                  ? 'border-purple-500 bg-purple-950/30'
                  : 'border-gray-800 bg-gray-900'
              }`}
            >
              {plan.style === 'popular' && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-purple-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full whitespace-nowrap">
                    Most popular
                  </span>
                </div>
              )}

              {/* Plan header */}
              <div className="mb-5">
                <h2 className="text-lg font-bold mb-1">{plan.name}</h2>
                <p className="text-gray-400 text-xs mb-4 leading-relaxed">{plan.description}</p>
                <div className="flex items-end gap-1">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-400 mb-1 text-sm">/mo</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{plan.credits} credits included</p>
              </div>

              {/* Features */}
              <ul className="space-y-2.5 mb-6 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                    <svg className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>

              {/* Subscribe CTA */}
              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={loading === plan.id}
                className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${
                  plan.style === 'popular'
                    ? 'bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-60'
                    : 'bg-gray-800 hover:bg-gray-700 text-white disabled:opacity-60'
                }`}
              >
                {loading === plan.id ? 'Redirecting...' : plan.cta}
              </button>

              {/* Top-up section */}
              <TopUpSection planId={plan.id} />
            </div>
          ))}

          {/* ── Enterprise card ── */}
          <div className="relative rounded-2xl p-7 border border-amber-500/40 bg-gradient-to-b from-amber-950/20 to-gray-900 flex flex-col">
            {/* Corner badge */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
              <span className="bg-gradient-to-r from-amber-500 to-orange-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full whitespace-nowrap">
                Enterprise
              </span>
            </div>

            {/* Header */}
            <div className="mb-5">
              <h2 className="text-lg font-bold mb-1 text-amber-100">Enterprise</h2>
              <p className="text-gray-400 text-xs mb-4 leading-relaxed">
                Custom-built for large orgs, studios, and platform partners.
              </p>
              <div className="flex items-end gap-1">
                <span className="text-4xl font-bold text-white">Custom</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Volume pricing · invoiced billing</p>
            </div>

            {/* Features */}
            <ul className="space-y-2.5 mb-6 flex-1">
              {ENTERPRISE_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                  <svg className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {f}
                </li>
              ))}
            </ul>

            {/* Contact CTA */}
            <button
              onClick={() => setShowEnquiry(true)}
              className="w-full py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white transition-all"
            >
              Contact us
            </button>

            {/* Reassurance */}
            <p className="text-center text-xs text-gray-500 mt-4">
              Response within 1 business day
            </p>
          </div>

        </div>

        {/* Footer note */}
        <p className="text-center text-gray-500 text-sm mt-14">
          All paid plans include a 14-day free trial. Cancel anytime.{' '}
          <button onClick={() => setShowEnquiry(true)} className="text-purple-400 hover:underline">
            Talk to sales
          </button>
        </p>
      </div>
    </div>
  );
}
