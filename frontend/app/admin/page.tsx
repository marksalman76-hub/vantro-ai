'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Stats {
  total_users: number;
  active_subscriptions: number;
  trial_subscriptions: number;
  paid_clients: number;
  suspended_accounts: number;
  free_accounts: number;
  total_media_jobs: number;
  completed_media_jobs: number;
  processing_media_jobs: number;
  pending_media_jobs: number;
  failed_media_jobs: number;
  queued_jobs: number;
}

interface Job {
  id: string;
  status: string;
  script: string | null;
  client_email: string;
  client_name: string | null;
  created_at: string | null;
  completed_at: string | null;
  video_url: string | null;
  error_message: string | null;
}

const STATUS_STYLE: Record<string, string> = {
  completed:  'bg-green-400/10 text-green-400',
  processing: 'bg-yellow-400/10 text-yellow-400',
  pending:    'bg-blue-400/10 text-blue-400',
  failed:     'bg-red-400/10 text-red-400',
  cancelled:  'bg-gray-700 text-gray-400',
};

function StatCard({ label, value, color, sub }: { label: string; value: number | string; color: string; sub?: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-gray-500 text-xs mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-gray-600 text-xs mt-1">{sub}</p>}
    </div>
  );
}

export default function AdminCommandCenter() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin/login'); return; }

    Promise.all([
      fetch('/api/admin/stats', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/admin/jobs', { headers: { Authorization: `Bearer ${token}` } }),
    ])
      .then(async ([sr, jr]) => {
        if (sr.status === 403) { router.push('/dashboard'); return; }
        const [s, j] = await Promise.all([sr.json(), jr.json()]);
        setStats(s);
        setJobs((j.jobs || []).slice(0, 10));
      })
      .catch(() => setError('Failed to load dashboard data'))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error) return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-red-400">{error}</p>
    </div>
  );

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Command Center</h1>
        <p className="text-gray-500 text-sm mt-1">Platform health and activity overview</p>
      </div>

      {stats && (
        <>
          {/* Client stats */}
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Clients</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
            <StatCard label="Total users"    value={stats.total_users}          color="text-white" />
            <StatCard label="Paid"           value={stats.paid_clients}         color="text-green-400" />
            <StatCard label="Trial"          value={stats.trial_subscriptions}  color="text-blue-400" />
            <StatCard label="Free"           value={stats.free_accounts}        color="text-gray-400" />
            <StatCard label="Suspended"      value={stats.suspended_accounts}   color="text-red-400" />
            <StatCard
              label="Conversion"
              value={stats.total_users > 0 ? `${Math.round((stats.paid_clients / stats.total_users) * 100)}%` : '0%'}
              color="text-amber-400"
            />
          </div>

          {/* Job stats */}
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Jobs</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
            <StatCard label="Total jobs"   value={stats.total_media_jobs}      color="text-white" />
            <StatCard label="Completed"    value={stats.completed_media_jobs}  color="text-green-400" />
            <StatCard label="Processing"   value={stats.processing_media_jobs} color="text-yellow-400" />
            <StatCard label="Queued"       value={stats.queued_jobs}           color="text-blue-400" />
            <StatCard label="Failed"       value={stats.failed_media_jobs}     color="text-red-400" />
            <StatCard
              label="Success rate"
              value={stats.total_media_jobs > 0
                ? `${Math.round((stats.completed_media_jobs / stats.total_media_jobs) * 100)}%`
                : '—'}
              color="text-purple-400"
            />
          </div>
        </>
      )}

      {/* Quick nav */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { href: '/admin/clients',   label: 'Manage Clients',    desc: 'Credits, plans, controls' },
          { href: '/admin/jobs',      label: 'All Jobs',          desc: 'Retry, cancel, inspect' },
          { href: '/admin/providers', label: 'Provider Health',   desc: 'HeyGen, Stripe, SQS' },
          { href: '/admin/aws',       label: 'AWS Infra',         desc: 'ECS, RDS, WAF, ALB' },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="bg-gray-900 border border-gray-800 hover:border-violet-500/50 rounded-xl p-4 transition-colors group"
          >
            <p className="font-semibold text-sm text-white group-hover:text-violet-300 transition-colors">{item.label}</p>
            <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
          </Link>
        ))}
      </div>

      {/* Recent jobs */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl">
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <h2 className="font-semibold">Recent Jobs</h2>
          <Link href="/admin/jobs" className="text-xs text-violet-400 hover:text-violet-300">View all →</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                {['Client', 'Script', 'Status', 'Created', 'Actions'].map((h) => (
                  <th key={h} className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="px-6 py-3">
                    <p className="text-gray-200 text-xs">{j.client_email}</p>
                    {j.client_name && <p className="text-gray-500 text-xs">{j.client_name}</p>}
                  </td>
                  <td className="px-6 py-3 text-gray-400 text-xs max-w-xs truncate">{j.script || '—'}</td>
                  <td className="px-6 py-3">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_STYLE[j.status] || 'bg-gray-700 text-gray-400'}`}>
                      {j.status}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-gray-500 text-xs">
                    {j.created_at ? new Date(j.created_at).toLocaleDateString('en-GB') : '—'}
                  </td>
                  <td className="px-6 py-3">
                    <Link href={`/admin/jobs?id=${j.id}`} className="text-xs text-violet-400 hover:text-violet-300">
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
              {jobs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-10 text-center text-gray-600 text-sm">No jobs yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
