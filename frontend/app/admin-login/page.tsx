'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Already logged in? Go straight to admin
    const token = localStorage.getItem('admin_token');
    if (token) router.replace('/admin');
    emailRef.current?.focus();
  }, [router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) return;
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      const json = await res.json();

      if (!res.ok) {
        setError(json.detail || 'Invalid email or password');
        return;
      }

      // Verify this account has admin access by hitting an admin-gated endpoint
      const check = await fetch('/api/admin/clients', {
        headers: { Authorization: `Bearer ${json.access_token}` },
      });

      if (check.status === 403) {
        setError('This account does not have admin access.');
        return;
      }

      // Store token and go
      localStorage.setItem('admin_token', json.access_token);
      router.push('/admin');
    } catch {
      setError('Network error — is the server running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xl mb-4 shadow-lg shadow-violet-500/20">
            V
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Vantro Admin</h1>
          <p className="text-gray-500 text-sm mt-1">Owner access only</p>
        </div>

        {/* Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={submit} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5" htmlFor="email">
                Email
              </label>
              <input
                ref={emailRef}
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@example.com"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition-colors"
                required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl text-sm transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in…
                </>
              ) : (
                'Sign in to Admin'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-700 text-xs mt-6">
          Not an admin?{' '}
          <a href="/login" className="text-gray-500 hover:text-gray-300 transition-colors">
            Go to client login
          </a>
        </p>
      </div>
    </div>
  );
}
