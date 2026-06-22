'use client';

import { useState } from 'react';
import Link from 'next/link';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    description: 'Perfect for individuals and small teams getting started with AI video.',
    features: [
      '50 AI videos per month',
      '720p video quality',
      '10 avatar styles',
      'Email support',
    ],
  },
  {
    id: 'growth',
    name: 'Growth',
    price: 279,
    description: 'For growing teams that need more volume and higher quality.',
    features: [
      '200 AI videos per month',
      '1080p video quality',
      '50 avatar styles',
      'Priority support',
      'Custom branding',
    ],
    popular: true,
  },
  {
    id: 'business',
    name: 'Business',
    price: 399,
    description: 'For enterprises that need full power and dedicated support.',
    features: [
      'Unlimited AI videos',
      '4K video quality',
      'All avatar styles',
      'Dedicated account manager',
      'Custom avatars',
      'API access',
    ],
  },
];

export default function PricingPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

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
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan: planId }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.error || 'Something went wrong');
        return;
      }

      window.location.href = data.checkout_url;
    } catch {
      setError('Network error — please try again');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-white">Vantro AI</Link>
        <div className="flex gap-4">
          <Link href="/login" className="text-gray-400 hover:text-white text-sm">Log in</Link>
          <Link href="/signup" className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-4 py-2 rounded-lg">
            Get started
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">Simple, transparent pricing</h1>
          <p className="text-gray-400 text-lg">Start free, scale as you grow. No hidden fees.</p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-8 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-center">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`relative rounded-2xl p-8 border ${
                plan.popular
                  ? 'border-purple-500 bg-purple-950/30'
                  : 'border-gray-800 bg-gray-900'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-purple-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full">
                    Most popular
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h2 className="text-xl font-bold mb-1">{plan.name}</h2>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                <div className="flex items-end gap-1">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-400 mb-1">/month</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-gray-300">
                    <svg className="w-4 h-4 text-purple-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={loading === plan.id}
                className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${
                  plan.popular
                    ? 'bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-60'
                    : 'bg-gray-800 hover:bg-gray-700 text-white disabled:opacity-60'
                }`}
              >
                {loading === plan.id ? 'Redirecting...' : `Get ${plan.name}`}
              </button>
            </div>
          ))}
        </div>

        <p className="text-center text-gray-500 text-sm mt-12">
          All plans include a 14-day free trial. Cancel anytime. Questions?{' '}
          <a href="mailto:hello@vantro.ai" className="text-purple-400 hover:underline">
            Contact us
          </a>
        </p>
      </div>
    </div>
  );
}
