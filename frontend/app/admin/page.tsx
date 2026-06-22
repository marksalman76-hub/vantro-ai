'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Stats {
  total_users: number;
  active_subscriptions: number;
  total_media_jobs: number;
  completed_media_jobs: number;
  processing_media_jobs: number;
  pending_media_jobs: number;
  failed_media_jobs: number;
}

interface AdminUser {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  subscription_status: string | null;
  stripe_customer_id: string | null;
  created_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  active:   'bg-green-400/10 text-green-400',
  canceled: 'bg-red-400/10 text-red-400',
  trialing: 'bg-blue-400/10 text-blue-400',
};

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    Promise.all([
      fetch('/api/admin/stats', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/admin/users', { headers: { Authorization: `Bearer ${token}` } }),
    ])
      .then(async ([sr, ur]) => {
        if (sr.status === 403 || ur.status === 403) {
          router.push('/dashboard');
          return;
        }
        const [s, u] = await Promise.all([sr.json(), ur.json()]);
        setStats(s);
        setUsers(u.users || []);
      })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [router]);

  const filtered = users.filter(
    (u) =>
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.name || '').toLowerCase().includes(search.toLowerCase()),
  );

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="font-bold">Admin</span>
          <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">Internal</span>
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="text-gray-400 hover:text-white text-sm"
        >
          ← Dashboard
        </button>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold mb-8">Overview</h1>

        {/* Stats grid */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
            {[
              { label: 'Total users',         value: stats.total_users,          color: 'text-white' },
              { label: 'Active subscriptions', value: stats.active_subscriptions, color: 'text-green-400' },
              { label: 'Total jobs',           value: stats.total_media_jobs,     color: 'text-purple-400' },
              { label: 'Completed jobs',       value: stats.completed_media_jobs, color: 'text-blue-400' },
              { label: 'Processing',           value: stats.processing_media_jobs,color: 'text-yellow-400' },
              { label: 'Pending',              value: stats.pending_media_jobs,   color: 'text-gray-400' },
              { label: 'Failed',               value: stats.failed_media_jobs,    color: 'text-red-400' },
              {
                label: 'Conversion rate',
                value: stats.total_users > 0
                  ? `${Math.round((stats.active_subscriptions / stats.total_users) * 100)}%`
                  : '0%',
                color: 'text-amber-400',
              },
            ].map((s) => (
              <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <p className="text-gray-400 text-xs mb-2">{s.label}</p>
                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              </div>
            ))}
          </div>
        )}

        {/* Users table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl">
          <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between gap-4">
            <h2 className="font-semibold">Users <span className="text-gray-500 text-sm font-normal">({users.length})</span></h2>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by email or name…"
              className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 w-72"
            />
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  {['Email', 'Name', 'Plan', 'Stripe', 'Signed up'].map((h) => (
                    <th key={h} className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => (
                  <tr key={u.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 text-gray-200">{u.email}</td>
                    <td className="px-6 py-4 text-gray-400">{u.name || '—'}</td>
                    <td className="px-6 py-4">
                      {u.subscription_status ? (
                        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[u.subscription_status] || 'bg-gray-700 text-gray-400'}`}>
                          {u.subscription_status}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-600">free</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {u.stripe_customer_id ? (
                        <span className="text-xs font-mono text-gray-500">{u.stripe_customer_id.slice(0, 16)}…</span>
                      ) : (
                        <span className="text-xs text-gray-700">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-xs">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString('en-GB') : '—'}
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-gray-600">No users match your search.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
