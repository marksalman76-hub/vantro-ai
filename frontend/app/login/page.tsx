'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError('We could not sign you in. Please check your details and try again.');
        return;
      }
      localStorage.setItem('token', data.token);
      window.location.href = '/dashboard';
    } catch {
      setError('We could not connect to the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex">
      {/* Left brand panel */}
      <div className="hidden lg:flex flex-col justify-between w-[45%] bg-gray-900 border-r border-gray-800 px-12 py-10">
        <div>
          <Link href="/" className="flex items-center gap-2.5 mb-12">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-sm">V</span>
            <span className="font-bold text-white text-lg">Vantro<span className="text-violet-400">.ai</span></span>
          </Link>
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white leading-tight mb-4">
              Your AI agent<br />workforce, ready<br />to work.
            </h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              27 specialised agents. Singular or team execution. Human-in-the-loop governance. Built for ecommerce and digital businesses.
            </p>
          </div>
          <div className="space-y-3">
            {[
              '27 AI agents across 9 business functions',
              'Team execution with lead + supporting agents',
              'Create media, run campaigns, automate workflows',
              'Full credit and spend visibility',
            ].map(f => (
              <div key={f} className="flex items-center gap-2.5 text-sm text-gray-400">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 shrink-0"/>
                {f}
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-gray-600 text-xs">
            Secured by JWT authentication. Your data is never shared or used to train AI models.
          </p>
        </div>
      </div>

      {/* Right login panel */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        {/* Mobile logo */}
        <div className="lg:hidden mb-8">
          <Link href="/" className="flex items-center gap-2.5 justify-center">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-sm">V</span>
            <span className="font-bold text-white text-lg">Vantro<span className="text-violet-400">.ai</span></span>
          </Link>
        </div>

        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-1">Welcome back</h2>
            <p className="text-gray-500 text-sm">Sign in to your workspace</p>
          </div>

          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Email address</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email"
                placeholder="you@company.com"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-violet-500 transition-colors"/>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-gray-400">Password</label>
                <Link href="/forgot-password" className="text-xs text-violet-400 hover:text-violet-300 transition-colors">Forgot password?</Link>
              </div>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required autoComplete="current-password"
                placeholder="••••••••"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-violet-500 transition-colors"/>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold text-sm transition-colors mt-2">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="mt-6 space-y-3">
            <p className="text-center text-sm text-gray-600">
              Don&apos;t have an account?{' '}
              <Link href="/signup" className="text-violet-400 hover:text-violet-300 transition-colors">Start free trial</Link>
            </p>
            <p className="text-center text-xs text-gray-700">
              <Link href="/terms" className="hover:text-gray-500 transition-colors">Terms</Link>
              {' · '}
              <Link href="/privacy" className="hover:text-gray-500 transition-colors">Privacy</Link>
              {' · '}
              <Link href="/dashboard/support" className="hover:text-gray-500 transition-colors">Support</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
