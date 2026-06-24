'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

// ─── Types ────────────────────────────────────────────────────────────────────

interface BrandForm {
  business_name: string;
  industry: string;
  target_audience: string;
  preferred_tone: string;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const STEPS = [
  { number: 1, label: 'Welcome'       },
  { number: 2, label: 'Brand setup'   },
  { number: 3, label: 'First agent'   },
  { number: 4, label: 'Connect tools' },
];

const TONES = ['Fun', 'Professional', 'Bold'];

const INDUSTRIES = [
  'E-commerce / Retail', 'SaaS / Tech', 'Health & Wellness',
  'Finance', 'Real Estate', 'Food & Beverage', 'Fashion',
  'Agency / Consulting', 'Education', 'Entertainment', 'Other',
];

// ─── Step indicator ───────────────────────────────────────────────────────────

function StepIndicator({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center gap-0 mb-12">
      {STEPS.map((s, i) => (
        <div key={s.number} className="flex items-center flex-1">
          <div className="flex flex-col items-center">
            <div
              className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                currentStep > s.number
                  ? 'bg-emerald-600 text-white'
                  : currentStep === s.number
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-800 text-gray-500'
              }`}
            >
              {currentStep > s.number ? (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : s.number}
            </div>
            <span className={`text-xs mt-2 whitespace-nowrap ${currentStep === s.number ? 'text-white' : 'text-gray-500'}`}>
              {s.label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`h-0.5 flex-1 mx-3 mt-[-18px] ${currentStep > s.number ? 'bg-emerald-600' : 'bg-gray-800'}`} />
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Step 1: Welcome ──────────────────────────────────────────────────────────

function Step1Welcome({ planName, activatedAgents, onNext }: {
  planName: string;
  activatedAgents: string[];
  onNext: () => void;
}) {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-3">Welcome to Vantro</h1>
      <p className="text-gray-400 mb-8">
        Your AI agent workforce is ready. Let&apos;s get you set up in 4 quick steps.
      </p>

      {planName && (
        <div className="bg-violet-950/30 border border-violet-500/20 rounded-2xl p-5 mb-6">
          <p className="text-xs text-gray-500 mb-1">Your plan</p>
          <p className="text-lg font-bold capitalize text-violet-300">{planName}</p>
        </div>
      )}

      {activatedAgents.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-8">
          <p className="text-sm font-semibold text-white mb-3">
            Agents unlocked with your plan ({activatedAgents.length})
          </p>
          <div className="flex flex-wrap gap-2">
            {activatedAgents.map(name => (
              <span
                key={name}
                className="text-xs px-2.5 py-1 rounded-full bg-violet-600/10 border border-violet-500/20 text-violet-300"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={onNext}
        className="w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 rounded-xl transition-colors"
      >
        Get started →
      </button>
    </div>
  );
}

// ─── Step 2: Brand setup ──────────────────────────────────────────────────────

function Step2Brand({ onNext }: { onNext: () => void }) {
  const [form, setForm] = useState<BrandForm>({
    business_name: '',
    industry: '',
    target_audience: '',
    preferred_tone: 'Professional',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const save = async () => {
    if (!form.business_name.trim()) { setError('Business name is required'); return; }
    const token = localStorage.getItem('token');
    if (!token) return;
    setSaving(true); setError('');
    try {
      const res = await fetch('/api/workspace/brand', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        setError(j.detail || 'Save failed — you can update this later in Brand Profile.');
        // Non-fatal: let user proceed anyway
      }
      onNext();
    } catch {
      setError('Network error — your profile was not saved, but you can set it up later.');
      onNext();
    } finally {
      setSaving(false);
    }
  };

  const inputCls = 'w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500';

  return (
    <div>
      <h1 className="text-3xl font-bold mb-3">Set up your brand</h1>
      <p className="text-gray-400 mb-8">
        This context helps every agent produce personalised outputs for your business.
      </p>

      <div className="space-y-5 mb-8">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Business name *</label>
          <input
            type="text"
            placeholder="e.g. Acme Commerce"
            value={form.business_name}
            onChange={e => setForm(f => ({ ...f, business_name: e.target.value }))}
            className={inputCls}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Industry</label>
          <select
            value={form.industry}
            onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
            className={inputCls}
          >
            <option value="">Select industry…</option>
            {INDUSTRIES.map(ind => <option key={ind} value={ind}>{ind}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Target audience</label>
          <input
            type="text"
            placeholder="Who are your ideal customers?"
            value={form.target_audience}
            onChange={e => setForm(f => ({ ...f, target_audience: e.target.value }))}
            className={inputCls}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-2">Brand tone</label>
          <div className="flex gap-2">
            {TONES.map(tone => (
              <button
                key={tone}
                onClick={() => setForm(f => ({ ...f, preferred_tone: tone }))}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                  form.preferred_tone === tone
                    ? 'bg-violet-600 border-violet-500 text-white'
                    : 'bg-gray-800 border-gray-700 text-gray-400 hover:text-white'
                }`}
              >
                {tone}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={save}
          disabled={saving}
          className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors"
        >
          {saving ? 'Saving…' : 'Save & continue →'}
        </button>
        <button
          onClick={onNext}
          className="px-4 py-3 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors"
        >
          Skip
        </button>
      </div>
    </div>
  );
}

// ─── Step 3: Run first agent ──────────────────────────────────────────────────

function Step3RunAgent({ onNext }: { onNext: () => void }) {
  const [task, setTask] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const AGENT_ID = 'intake_trial_agent';

  const run = async () => {
    if (!task.trim()) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    setSubmitting(true); setError('');
    try {
      const res = await fetch(`/api/agents/${AGENT_ID}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: task.trim() }),
      });
      const j = await res.json();
      if (!res.ok) { setError(j.detail || 'Run failed'); return; }
      setJobId(j.job_id);
    } catch {
      setError('Network error');
    } finally {
      setSubmitting(false);
    }
  };

  if (jobId) {
    return (
      <div>
        <h1 className="text-3xl font-bold mb-3">Agent is working</h1>
        <p className="text-gray-400 mb-8">Your first agent job has been queued. Results will appear in your Output Library.</p>

        <div className="bg-gray-900 border border-violet-500/20 rounded-2xl p-6 flex items-center gap-4 mb-8">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin shrink-0" />
          <div>
            <p className="text-white text-sm font-semibold">Running…</p>
            <p className="text-gray-500 text-xs mt-0.5">Job ID: {jobId.slice(0, 8)}</p>
          </div>
        </div>

        <button
          onClick={onNext}
          className="w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 rounded-xl transition-colors"
        >
          Continue →
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-3">Run your first agent</h1>
      <p className="text-gray-400 mb-8">
        Try it out. Describe a task and your intake agent will handle it.
      </p>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-400 text-sm font-bold">
            AI
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Intake Agent</p>
            <p className="text-xs text-gray-500">Analyses your business and creates a customised action plan</p>
          </div>
        </div>

        <textarea
          value={task}
          onChange={e => setTask(e.target.value)}
          rows={5}
          placeholder="Describe your business, current challenges, and what you'd like help with. The more detail, the better."
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-violet-500 leading-relaxed"
        />
        {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
      </div>

      <div className="flex gap-3">
        <button
          onClick={run}
          disabled={!task.trim() || submitting}
          className="flex-1 bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-40 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-violet-500/20"
        >
          {submitting ? 'Launching…' : 'Run agent →'}
        </button>
        <button
          onClick={onNext}
          className="px-4 py-3 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors"
        >
          Skip
        </button>
      </div>
    </div>
  );
}

// ─── Step 4: Connect integrations ─────────────────────────────────────────────

function Step4Integrations({ onComplete }: { onComplete: () => void }) {
  const INTEGRATIONS = [
    {
      key: 'shopify',
      name: 'Shopify',
      icon: '🛒',
      desc: 'Sync products, orders, and customer data with your store agents',
    },
    {
      key: 'google_analytics',
      name: 'Google Analytics',
      icon: '📊',
      desc: 'Let analytics agents access your GA4 data for real insights',
    },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-3">Connect your tools</h1>
      <p className="text-gray-400 mb-8">
        Integrations let agents act on live data — connect your store, analytics, or email tools.
      </p>

      <div className="space-y-4 mb-8">
        {INTEGRATIONS.map(intg => (
          <div
            key={intg.key}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex items-center justify-between"
          >
            <div className="flex items-center gap-4">
              <span className="text-2xl">{intg.icon}</span>
              <div>
                <p className="text-sm font-semibold text-white">{intg.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{intg.desc}</p>
              </div>
            </div>
            <Link
              href="/dashboard/settings/integrations"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors shrink-0"
            >
              Connect
            </Link>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={onComplete}
          className="flex-1 bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 rounded-xl transition-colors"
        >
          Finish setup
        </button>
        <button
          onClick={onComplete}
          className="px-4 py-3 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors"
        >
          Skip
        </button>
      </div>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

function OnboardingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [step, setStep] = useState(1);
  const [planName, setPlanName] = useState('');
  const [activatedAgents, setActivatedAgents] = useState<string[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    // Check if already completed
    if (localStorage.getItem('onboarding_complete') === 'true') {
      router.push('/dashboard');
      return;
    }

    // Read plan/agents from URL params or localStorage
    const planParam = searchParams?.get('plan') || localStorage.getItem('activated_plan') || '';
    const agentsParam = searchParams?.get('agents') || localStorage.getItem('activated_agents') || '';
    setPlanName(planParam);
    if (agentsParam) {
      try {
        const parsed = JSON.parse(agentsParam);
        if (Array.isArray(parsed)) setActivatedAgents(parsed);
      } catch {
        // agents param might be comma-separated string
        setActivatedAgents(agentsParam.split(',').map(s => s.trim()).filter(Boolean));
      }
    }
  }, [router, searchParams]);

  const complete = () => {
    localStorage.setItem('onboarding_complete', 'true');
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between sticky top-0 bg-gray-950/95 backdrop-blur z-10">
        <div className="flex items-center gap-2">
          <span
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-black text-xs"
            style={{ background: 'linear-gradient(135deg,#7C3AED,#3B82F6)' }}
          >
            V
          </span>
          <span className="font-bold">Vantro<span className="text-violet-400">.ai</span></span>
        </div>
        <button
          onClick={complete}
          className="text-gray-500 hover:text-gray-300 text-sm transition-colors"
        >
          Skip setup
        </button>
      </nav>

      <div className="max-w-xl mx-auto px-6 py-16">
        <StepIndicator currentStep={step} />

        {step === 1 && (
          <Step1Welcome
            planName={planName}
            activatedAgents={activatedAgents}
            onNext={() => setStep(2)}
          />
        )}
        {step === 2 && (
          <Step2Brand onNext={() => setStep(3)} />
        )}
        {step === 3 && (
          <Step3RunAgent onNext={() => setStep(4)} />
        )}
        {step === 4 && (
          <Step4Integrations onComplete={complete} />
        )}
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#07091A]" />}>
      <OnboardingContent />
    </Suspense>
  );
}
