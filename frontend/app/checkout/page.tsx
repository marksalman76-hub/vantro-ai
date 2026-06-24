'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense } from 'react';
import { loadStripe, Stripe, StripeCardElement } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const PLAN_LABELS: Record<string, string> = {
  starter: 'Starter',
  growth: 'Growth',
  business: 'Business',
};

const PLAN_PRICES: Record<string, string> = {
  starter: '$99',
  growth: '$279',
  business: '$399',
};

interface Agent {
  id: string;
  name: string;
}

interface SetupData {
  client_secret: string;
  plan: string;
  amount_cents: number;
  credits: number;
  agents: Agent[];
}

// ─── Step 1: Card collection ────────────────────────────────────────────────

function CardStep({
  setupData,
  onCardReady,
}: {
  setupData: SetupData;
  onCardReady: (pmId: string) => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [cardError, setCardError] = useState('');

  const handleSubmit = useCallback(async () => {
    if (!stripe || !elements) return;
    const card = elements.getElement(CardElement);
    if (!card) return;

    setLoading(true);
    setCardError('');

    const { setupIntent, error } = await stripe.confirmCardSetup(setupData.client_secret, {
      payment_method: { card },
    });

    if (error) {
      setCardError(error.message || 'Card verification failed');
      setLoading(false);
      return;
    }

    const pmId = typeof setupIntent?.payment_method === 'string'
      ? setupIntent.payment_method
      : setupIntent?.payment_method?.id ?? '';

    if (!pmId) {
      setCardError('Could not retrieve payment method. Please try again.');
      setLoading(false);
      return;
    }

    onCardReady(pmId);
  }, [stripe, elements, setupData.client_secret, onCardReady]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-1">Payment details</h2>
        <p className="text-sm text-gray-400">Your card is securely processed. We never store raw card data.</p>
      </div>

      <div className="bg-[#1a1a2e] border border-white/10 rounded-xl p-4">
        <label className="block text-xs font-medium text-gray-400 mb-3 uppercase tracking-wide">
          Card information
        </label>
        <CardElement
          options={{
            style: {
              base: {
                color: '#e5e7eb',
                fontFamily: 'ui-sans-serif, system-ui, sans-serif',
                fontSize: '15px',
                '::placeholder': { color: '#6b7280' },
                iconColor: '#8b5cf6',
              },
              invalid: { color: '#f87171' },
            },
          }}
        />
      </div>

      {cardError && (
        <p className="text-red-400 text-sm bg-red-950/30 border border-red-900/40 rounded-lg px-4 py-3">
          {cardError}
        </p>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-500">
        <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        256-bit SSL encryption · Payments processed by Stripe
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !stripe}
        className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-900 disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            Verifying card...
          </>
        ) : (
          'Continue to review'
        )}
      </button>
    </div>
  );
}

// ─── Step 2: Order review + confirm ────────────────────────────────────────────

function ConfirmStep({
  setupData,
  pmId,
  plan,
  onBack,
  onSuccess,
}: {
  setupData: SetupData;
  pmId: string;
  plan: string;
  onBack: () => void;
  onSuccess: () => void;
  agentIds: string[];
}) {
  const stripe = useStripe();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConfirm = useCallback(async () => {
    if (!stripe) return;
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch('/api/billing/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ payment_method_id: pmId, plan, agent_ids: setupData.agents.map(a => a.id) }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Subscription failed. Please contact support.');
        setLoading(false);
        return;
      }

      if (data.client_secret) {
        const { error: payErr } = await stripe.confirmCardPayment(data.client_secret);
        if (payErr) {
          setError(payErr.message || 'Payment failed. Please try again.');
          setLoading(false);
          return;
        }
      }

      onSuccess();
    } catch {
      setError('An unexpected error occurred. Please try again.');
      setLoading(false);
    }
  }, [stripe, pmId, plan, onSuccess]);

  const planLabel = PLAN_LABELS[plan] ?? plan;
  const priceLabel = PLAN_PRICES[plan] ?? '';

  return (
    <div className="space-y-6">
      <div>
        <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-400 hover:text-white mb-4 transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <h2 className="text-xl font-semibold text-white mb-1">Review your order</h2>
        <p className="text-sm text-gray-400">Monthly billing starts today. Cancel anytime.</p>
      </div>

      {/* Plan summary */}
      <div className="bg-[#1a1a2e] border border-white/10 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-white">{planLabel} Plan</p>
            <p className="text-sm text-gray-400">{setupData.credits} agent credits per month</p>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-white">{priceLabel}</p>
            <p className="text-xs text-gray-500">/month</p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-4">
          <div className="flex items-center gap-2 mb-3">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Your agents</p>
            <span className="flex items-center gap-1 text-[10px] font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30 rounded-full px-2 py-0.5">
              <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Locked after payment
            </span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {setupData.agents.map((agent) => (
              <div key={agent.id} className="flex items-center gap-2 text-sm text-gray-300">
                <div className="w-1.5 h-1.5 rounded-full bg-violet-500 flex-shrink-0" />
                {agent.name}
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-white/10 pt-4 flex items-center justify-between">
          <span className="text-sm text-gray-400">Billed monthly</span>
          <span className="font-semibold text-white">{priceLabel}/mo</span>
        </div>
      </div>

      {/* Activation note */}
      <div className="bg-violet-950/30 border border-violet-800/30 rounded-xl p-4 flex gap-3">
        <svg className="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p className="text-sm text-violet-300">
          After payment, we&apos;ll email you a secure one-time activation link to unlock your agents.
        </p>
      </div>

      {error && (
        <p className="text-red-400 text-sm bg-red-950/30 border border-red-900/40 rounded-lg px-4 py-3">
          {error}
        </p>
      )}

      <button
        onClick={handleConfirm}
        disabled={loading || !stripe}
        className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-900 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            Processing payment...
          </>
        ) : (
          `Confirm & start billing — ${priceLabel}/mo`
        )}
      </button>

      <p className="text-xs text-center text-gray-500">
        By confirming, you agree to our Terms of Service. Cancel anytime from billing settings.
      </p>
    </div>
  );
}

// ─── Main checkout wrapper ──────────────────────────────────────────────────────

function CheckoutContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const plan = searchParams?.get('plan') ?? 'growth';
  const agentsParam = searchParams?.get('agents') ?? '';
  const agentIds = agentsParam ? agentsParam.split(',').filter(Boolean) : [];

  const [stripePromise] = useState(() =>
    loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY ?? '')
  );

  const [step, setStep] = useState<1 | 2 | 'success'>(1);
  const [setupData, setSetupData] = useState<SetupData | null>(null);
  const [pmId, setPmId] = useState('');
  const [initError, setInitError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.replace(`/login?redirect=/checkout?plan=${plan}&agents=${agentsParam}`);
      return;
    }

    fetch('/api/billing/setup-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ plan, agent_ids: agentIds }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.detail || data.error) {
          setInitError(data.detail ?? data.error ?? 'Failed to initialize checkout');
        } else {
          setSetupData(data);
        }
      })
      .catch(() => setInitError('Failed to connect. Please try again.'))
      .finally(() => setLoading(false));
  }, [plan, router]);

  const handleCardReady = useCallback((id: string) => {
    setPmId(id);
    setStep(2);
  }, []);

  const handleSuccess = useCallback(() => {
    setStep('success');
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (initError || !setupData) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-6">
        <div className="max-w-sm w-full text-center">
          <p className="text-red-400 mb-4">{initError || 'Could not load checkout'}</p>
          <button onClick={() => router.push('/pricing')} className="text-violet-400 hover:text-violet-300 text-sm underline">
            Back to pricing
          </button>
        </div>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-600 rounded-full mx-auto mb-6 flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-3">Payment confirmed!</h1>
          <p className="text-gray-400 mb-2">
            Check your email — we&apos;ve sent a secure activation link to unlock your agents.
          </p>
          <p className="text-sm text-gray-500 mb-8">The link expires in 7 days and can only be used once.</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="inline-block bg-violet-600 hover:bg-violet-500 text-white font-semibold px-8 py-3 rounded-xl transition-all"
          >
            Go to dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="border-b border-white/5 px-6 py-4">
        <span className="text-lg font-bold text-white">
          Vantro<span className="text-violet-500">.ai</span>
        </span>
      </div>

      <div className="max-w-lg mx-auto px-6 py-10">
        {/* Progress */}
        <div className="flex items-center gap-3 mb-8">
          {([1, 2] as const).map((s) => {
            const numStep = step as 1 | 2;
            const isActive = numStep >= s;
            const isDone = numStep > s;
            return (
              <div key={s} className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${isActive ? 'bg-violet-600 text-white' : 'bg-white/10 text-gray-500'}`}
                >
                  {isDone ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : s}
                </div>
                <span className={`text-sm ${isActive ? 'text-white' : 'text-gray-600'}`}>
                  {s === 1 ? 'Payment details' : 'Confirm order'}
                </span>
                {s < 2 && <div className="flex-1 h-px bg-white/10 w-8" />}
              </div>
            );
          })}
        </div>

        {/* Plan badge */}
        <div className="mb-6 inline-flex items-center gap-2 bg-violet-950/50 border border-violet-800/40 rounded-full px-4 py-1.5">
          <div className="w-2 h-2 rounded-full bg-violet-500" />
          <span className="text-sm text-violet-300 font-medium">
            {PLAN_LABELS[plan] ?? plan} Plan — {PLAN_PRICES[plan] ?? ''}/month
          </span>
        </div>

        {/* Form card */}
        <div className="bg-[#13131f] border border-white/8 rounded-2xl p-6">
          <Elements stripe={stripePromise}>
            {step === 1 ? (
              <CardStep setupData={setupData} onCardReady={handleCardReady} />
            ) : (
              <ConfirmStep
                setupData={setupData}
                pmId={pmId}
                plan={plan}
                agentIds={agentIds}
                onBack={() => setStep(1)}
                onSuccess={handleSuccess}
              />
            )}
          </Elements>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense>
      <CheckoutContent />
    </Suspense>
  );
}
