'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

const PLAN_LABELS: Record<string, { name: string; color: string; amount: string }> = {
  active:   { name: 'Active',   color: 'text-green-400 bg-green-400/10 border-green-400/20',  amount: '' },
  canceled: { name: 'Canceled', color: 'text-red-400 bg-red-400/10 border-red-400/20',       amount: '' },
  trialing: { name: 'Trial',    color: 'text-blue-400 bg-blue-400/10 border-blue-400/20',    amount: '' },
};

interface DashboardData {
  user: { id: string; email: string; name: string | null; subscription_status: string | null };
  credits: { total_credits: number; used_credits: number; remaining_credits: number; tier: string };
  mediaJobs: { total_jobs: number; completed: number; processing: number; pending: number; failed: number; jobs: Job[] };
}

interface Job {
  id: string;
  status: string;
  video_url: string | null;
  script: string | null;
  created_at: string | null;
}

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [portalLoading, setPortalLoading] = useState(false);
  const [topupSuccess, setTopupSuccess] = useState(false);

  const openBillingPortal = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setPortalLoading(true);
    try {
      const res = await fetch('/api/stripe/customer-portal', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json();
      if (json.url) window.location.href = json.url;
      else setError(json.error || 'Could not open billing portal');
    } catch {
      setError('Could not open billing portal');
    } finally {
      setPortalLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    fetch('/api/dashboard', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.ok ? r.json() : Promise.reject(r.status))
      .then(setData)
      .catch(() => { setError('Session expired'); localStorage.removeItem('token'); router.push('/login'); })
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (searchParams?.get('topup') === 'success') setTopupSuccess(true);
  }, [searchParams]);

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return null;

  const { user, credits, mediaJobs } = data;
  const subStatus = user.subscription_status;
  const planInfo = subStatus ? PLAN_LABELS[subStatus] : null;
  const usedPct = credits.total_credits > 0 ? Math.round((credits.used_credits / credits.total_credits) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="font-bold text-white">Vantro<span className="text-violet-400">.ai</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/create" className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-4 py-2 rounded-lg font-medium transition-all">
            + Create Video
          </Link>
          <button
            onClick={() => { localStorage.removeItem('token'); router.push('/login'); }}
            className="text-gray-400 hover:text-white text-sm"
          >
            Sign out
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Top-up success banner */}
        {topupSuccess && (
          <div className="mb-6 flex items-center justify-between bg-green-500/10 border border-green-500/30 rounded-xl px-5 py-3">
            <p className="text-green-400 text-sm font-medium">Credits added to your account.</p>
            <button onClick={() => setTopupSuccess(false)} className="text-green-400/60 hover:text-green-400 text-lg leading-none">×</button>
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Welcome back{user.name ? `, ${user.name.split(' ')[0]}` : ''}!</h1>
            <p className="text-gray-400 text-sm mt-1">{user.email}</p>
          </div>
          {!subStatus || subStatus === 'canceled' ? (
            <Link href="/pricing" className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-5 py-2.5 rounded-xl font-medium">
              Upgrade plan
            </Link>
          ) : null}
        </div>

        {/* Subscription card */}
        <div className={`rounded-2xl border p-6 mb-6 ${subStatus === 'active' || subStatus === 'trialing' ? 'bg-purple-950/30 border-purple-500/30' : 'bg-gray-900 border-gray-800'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Current plan</p>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold capitalize">
                  {credits.tier === 'starter' ? 'Starter' : credits.tier === 'growth' ? 'Growth' : credits.tier === 'business' ? 'Business' : 'Free'}
                </h2>
                {planInfo && (
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${planInfo.color}`}>
                    {planInfo.name}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              {(!subStatus || subStatus === 'canceled') && (
                <Link href="/pricing" className="text-purple-400 hover:text-purple-300 text-sm font-medium">
                  View plans →
                </Link>
              )}
              {subStatus === 'active' && (
                <button
                  onClick={openBillingPortal}
                  disabled={portalLoading}
                  className="text-sm text-gray-400 hover:text-white border border-gray-700 hover:border-gray-500 px-4 py-1.5 rounded-lg transition-all disabled:opacity-50"
                >
                  {portalLoading ? 'Opening…' : 'Manage billing'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Total credits',   value: credits.total_credits,     color: 'text-white' },
            { label: 'Credits used',    value: credits.used_credits,      color: 'text-orange-400' },
            { label: 'Credits left',    value: credits.remaining_credits, color: 'text-green-400' },
            { label: 'Videos created',  value: mediaJobs.total_jobs,      color: 'text-purple-400' },
          ].map((s) => (
            <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <p className="text-gray-400 text-xs mb-2">{s.label}</p>
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* Usage bar */}
        {credits.total_credits > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-6">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium">Credit usage</p>
              <p className="text-sm text-gray-400">{usedPct}% used</p>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${usedPct > 80 ? 'bg-red-500' : usedPct > 60 ? 'bg-orange-500' : 'bg-purple-500'}`}
                style={{ width: `${Math.min(usedPct, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Recent videos */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold">Recent Videos</h2>
            <Link href="/create" className="text-purple-400 hover:text-purple-300 text-sm">+ New video</Link>
          </div>

          {mediaJobs.jobs.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-14 h-14 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-7 h-7 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.069A1 1 0 0121 8.882v6.236a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
                </svg>
              </div>
              <p className="text-gray-400 mb-4">No videos yet</p>
              <Link href="/create" className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-5 py-2.5 rounded-xl font-medium">
                Create your first video
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {mediaJobs.jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-300 truncate">{job.script || 'Untitled'}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{job.created_at ? new Date(job.created_at).toLocaleDateString() : ''}</p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                      job.status === 'completed' ? 'bg-green-400/10 text-green-400' :
                      job.status === 'processing' ? 'bg-yellow-400/10 text-yellow-400' :
                      job.status === 'failed' ? 'bg-red-400/10 text-red-400' :
                      'bg-gray-700 text-gray-400'
                    }`}>{job.status}</span>
                    {job.video_url && (
                      <a href={job.video_url} target="_blank" rel="noreferrer" className="text-purple-400 hover:text-purple-300 text-xs font-medium">Watch →</a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
