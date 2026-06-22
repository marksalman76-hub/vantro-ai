'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

interface DashboardData {
  user: { id: string; email: string; name: string | null; subscription_status: string | null };
  credits: { total_credits: number; used_credits: number; remaining_credits: number; tier: string };
  mediaJobs: { total_jobs: number; completed: number; processing: number; pending: number; failed: number; jobs: MediaJob[] };
}
interface MediaJob { id: string; status: string; video_url: string | null; script: string | null; created_at: string | null; }

const TIER_BADGE: Record<string, string> = {
  starter:    'text-green-400 bg-green-500/10 border-green-500/20',
  growth:     'text-blue-400 bg-blue-500/10 border-blue-500/20',
  business:   'text-violet-400 bg-violet-500/10 border-violet-500/20',
  enterprise: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
};

const QUICK_ACTIONS = [
  { href:'/dashboard/agents', icon:'◆', label:'Run an Agent',    desc:'Execute a single AI agent on your task' },
  { href:'/dashboard/team',   icon:'◉', label:'Build a Team',    desc:'Coordinate multiple agents on one goal' },
  { href:'/create',           icon:'▶', label:'Create Media',    desc:'Video, image, audio, social content' },
  { href:'/dashboard/brand',  icon:'◎', label:'Brand Profile',   desc:'Store your business context for better outputs' },
  { href:'/dashboard/assets', icon:'▣', label:'View Outputs',    desc:'Access all your deliverables and downloads' },
  { href:'/dashboard/support',icon:'◍', label:'Get Support',     desc:'Report an issue or request credit review' },
];

function TopupCheck({ onSuccess }: { onSuccess: () => void }) {
  const params = useSearchParams();
  useEffect(() => { if (params?.get('topup') === 'success') onSuccess(); }, [params, onSuccess]);
  return null;
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [topupBanner, setTopupBanner] = useState(false);
  const [portalLoading, setPortalLoading] = useState(false);

  const openBillingPortal = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setPortalLoading(true);
    try {
      const res = await fetch('/api/stripe/customer-portal', { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
      const json = await res.json();
      if (json.url) window.location.href = json.url;
    } catch {} finally { setPortalLoading(false); }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/dashboard', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(setData)
      .catch(() => { localStorage.removeItem('token'); router.push('/login'); })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!data) return null;

  const { user, credits, mediaJobs } = data;
  const tier = credits.tier || 'free';
  const usedPct = credits.total_credits > 0 ? Math.round((credits.used_credits / credits.total_credits) * 100) : 0;
  const firstName = user.name?.split(' ')[0] ?? user.email.split('@')[0];
  const subActive = user.subscription_status === 'active' || user.subscription_status === 'trialing';

  return (
    <div className="p-8 max-w-5xl">
      <Suspense fallback={null}><TopupCheck onSuccess={() => setTopupBanner(true)} /></Suspense>

      {topupBanner && (
        <div className="mb-6 flex items-center justify-between bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-5 py-3">
          <p className="text-emerald-400 text-sm font-medium">Credits added successfully.</p>
          <button onClick={() => setTopupBanner(false)} className="text-emerald-400/60 hover:text-emerald-400 text-lg">×</button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Welcome back, {firstName}</h1>
          <p className="text-gray-500 text-sm">{user.email}</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/dashboard/billing" className="px-4 py-2 rounded-xl text-sm font-medium border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 transition-colors">
            Buy credits
          </Link>
          <Link href="/pricing" className="px-4 py-2 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors">
            Upgrade plan
          </Link>
        </div>
      </div>

      {/* Plan + credits row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Plan card */}
        <div className={`rounded-2xl border p-5 ${subActive ? 'bg-violet-950/20 border-violet-500/20' : 'bg-gray-900 border-gray-800'}`}>
          <p className="text-xs text-gray-500 mb-1">Current plan</p>
          <div className="flex items-center gap-2 mb-3">
            <p className="text-lg font-bold capitalize">{tier === 'free' ? 'Free' : tier}</p>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border capitalize ${TIER_BADGE[tier] || 'text-gray-400 border-gray-700'}`}>{tier}</span>
          </div>
          {subActive
            ? <button onClick={openBillingPortal} disabled={portalLoading} className="text-xs text-gray-400 hover:text-white transition-colors disabled:opacity-50">{portalLoading ? 'Opening…' : 'Manage billing →'}</button>
            : <Link href="/pricing" className="text-xs text-violet-400 hover:text-violet-300">View plans →</Link>}
        </div>

        {/* Credits */}
        <div className="md:col-span-2 bg-gray-900 border border-gray-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs text-gray-500">Credits</p>
            <span className="text-xs text-gray-500">{credits.remaining_credits} remaining of {credits.total_credits}</span>
          </div>
          <div className="flex items-end gap-6 mb-3">
            <div>
              <p className="text-2xl font-bold text-white">{credits.remaining_credits}</p>
              <p className="text-xs text-gray-500">Available</p>
            </div>
            <div>
              <p className="text-xl font-bold text-orange-400">{credits.used_credits}</p>
              <p className="text-xs text-gray-500">Used</p>
            </div>
            <div>
              <p className="text-xl font-bold text-gray-400">{credits.total_credits}</p>
              <p className="text-xs text-gray-500">Total</p>
            </div>
          </div>
          {credits.total_credits > 0 && (
            <div>
              <div className="w-full bg-gray-800 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all ${usedPct > 80 ? 'bg-red-500' : usedPct > 60 ? 'bg-orange-500' : 'bg-violet-500'}`}
                  style={{ width: `${Math.min(usedPct, 100)}%` }}
                />
              </div>
              <p className="text-[10px] text-gray-600 mt-1">{usedPct}% used</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">What would you like to do?</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {QUICK_ACTIONS.map(a => (
            <Link key={a.href} href={a.href}
              className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-2xl p-4 group transition-all hover:bg-gray-900/70">
              <span className="text-xl mb-2 block text-violet-400 group-hover:text-violet-300 transition-colors">{a.icon}</span>
              <p className="text-white text-sm font-semibold mb-0.5">{a.label}</p>
              <p className="text-gray-600 text-xs leading-relaxed">{a.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Status overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total videos',  value: mediaJobs.total_jobs,  color: 'text-violet-400' },
          { label: 'Completed',     value: mediaJobs.completed,   color: 'text-emerald-400' },
          { label: 'Processing',    value: mediaJobs.processing,  color: 'text-blue-400' },
          { label: 'Failed',        value: mediaJobs.failed,      color: 'text-red-400' },
        ].map(s => (
          <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <p className="text-gray-500 text-xs mb-1.5">{s.label}</p>
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Recent jobs */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <h2 className="font-semibold text-sm">Recent Media</h2>
          <Link href="/create" className="text-violet-400 hover:text-violet-300 text-xs font-medium">+ Create new</Link>
        </div>
        {mediaJobs.jobs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-sm mb-3">No media created yet</p>
            <Link href="/create" className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-5 py-2.5 rounded-xl font-medium transition-colors">Create your first video</Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-800/60">
            {mediaJobs.jobs.map(job => (
              <div key={job.id} className="flex items-center gap-4 px-6 py-3 hover:bg-gray-800/30 transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium truncate">{job.script || 'Untitled'}</p>
                  <p className="text-xs text-gray-600">{job.created_at ? new Date(job.created_at).toLocaleDateString() : ''}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                    job.status === 'completed' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                    job.status === 'processing' ? 'text-blue-400 bg-blue-500/10 border-blue-500/20' :
                    job.status === 'failed' ? 'text-red-400 bg-red-500/10 border-red-500/20' :
                    'text-gray-400 bg-gray-800 border-gray-700'
                  }`}>
                    {job.status === 'completed' ? 'Ready' : job.status === 'processing' ? 'In progress' : job.status === 'failed' ? 'Could not complete' : job.status}
                  </span>
                  {job.video_url && <a href={job.video_url} target="_blank" rel="noreferrer" className="text-violet-400 hover:text-violet-300 text-xs font-medium">Watch →</a>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
