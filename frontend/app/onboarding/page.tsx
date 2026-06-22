'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const STEPS = [
  { number: 1, label: 'Choose your plan' },
  { number: 2, label: 'Create your first video' },
  { number: 3, label: 'You\'re all set!' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    const name = localStorage.getItem('user_name') || '';
    setUserName(name);
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="font-bold">Vantro<span className="text-violet-400">.ai</span></span>
        </div>
        <Link href="/dashboard" className="text-gray-500 hover:text-gray-300 text-sm">
          Skip for now
        </Link>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-16">
        {/* Step indicator */}
        <div className="flex items-center gap-0 mb-12">
          {STEPS.map((s, i) => (
            <div key={s.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  step > s.number
                    ? 'bg-green-600 text-white'
                    : step === s.number
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-800 text-gray-500'
                }`}>
                  {step > s.number ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : s.number}
                </div>
                <span className={`text-xs mt-2 whitespace-nowrap ${step === s.number ? 'text-white' : 'text-gray-500'}`}>
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`h-0.5 flex-1 mx-3 mt-[-18px] ${step > s.number ? 'bg-green-600' : 'bg-gray-800'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Choose plan */}
        {step === 1 && (
          <div>
            <h1 className="text-3xl font-bold mb-3">
              Welcome{userName ? `, ${userName.split(' ')[0]}` : ''}!
            </h1>
            <p className="text-gray-400 mb-10">
              Let&apos;s get you set up. First, pick the plan that&apos;s right for you.
            </p>

            <div className="space-y-4 mb-10">
              {[
                { name: 'Starter', price: '$99/mo', highlight: '50 videos/month, 720p quality',   color: 'border-gray-700' },
                { name: 'Growth',  price: '$279/mo', highlight: '200 videos/month, 1080p + branding', color: 'border-purple-500 bg-purple-950/20', badge: 'Most popular' },
                { name: 'Business',price: '$399/mo', highlight: 'Unlimited videos, 4K + API access',  color: 'border-gray-700' },
              ].map((plan) => (
                <Link
                  key={plan.name}
                  href="/pricing"
                  className={`flex items-center justify-between p-5 rounded-2xl border transition-all hover:border-purple-500 hover:bg-purple-950/10 ${plan.color}`}
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">{plan.name}</span>
                      {plan.badge && (
                        <span className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded-full">{plan.badge}</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400 mt-0.5">{plan.highlight}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-white">{plan.price}</span>
                    <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() => setStep(2)}
                className="text-gray-400 hover:text-white text-sm"
              >
                I&apos;ll choose later →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Create first video */}
        {step === 2 && (
          <div>
            <h1 className="text-3xl font-bold mb-3">Create your first video</h1>
            <p className="text-gray-400 mb-10">
              See Vantro in action. Write a short script and we&apos;ll generate an AI video in minutes.
            </p>

            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 mb-8 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-5">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.069A1 1 0 0121 8.882v6.236a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2">Ready to generate?</h3>
              <p className="text-gray-400 text-sm mb-6">Pick an avatar, write your script, and Vantro creates a professional AI video.</p>
              <Link
                href="/create"
                className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold px-8 py-3 rounded-xl transition-all"
              >
                Create my first video
              </Link>
            </div>

            <button
              onClick={() => setStep(3)}
              className="text-gray-400 hover:text-white text-sm"
            >
              I&apos;ll do this later →
            </button>
          </div>
        )}

        {/* Step 3: All set */}
        {step === 3 && (
          <div className="text-center">
            <div className="w-20 h-20 bg-green-600 rounded-full mx-auto mb-6 flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold mb-3">You&apos;re all set!</h1>
            <p className="text-gray-400 mb-10 max-w-md mx-auto">
              Your Vantro account is ready. Head to your dashboard to track videos, manage credits, and create content.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
              {[
                { icon: '📹', label: 'Create videos', href: '/create',    desc: 'Generate AI videos in minutes' },
                { icon: '📊', label: 'Dashboard',     href: '/dashboard', desc: 'Track usage and credits'        },
                { icon: '💳', label: 'Choose plan',   href: '/pricing',   desc: 'Unlock more video capacity'     },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-5 text-center transition-all"
                >
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <p className="font-medium text-sm">{item.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
                </Link>
              ))}
            </div>

            <Link
              href="/dashboard"
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-10 py-3.5 rounded-xl transition-all"
            >
              Go to dashboard
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
