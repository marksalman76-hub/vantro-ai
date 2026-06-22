'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Client {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  subscription_status: string | null;
  stripe_customer_id: string | null;
  created_at: string | null;
  organization: string | null;
  tier: string;
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  total_jobs: number;
  last_execution: string | null;
}

const PLAN_STYLE: Record<string, string> = {
  active:   'bg-green-400/10 text-green-400',
  trialing: 'bg-blue-400/10 text-blue-400',
  canceled: 'bg-red-400/10 text-red-400',
};

const TIER_STYLE: Record<string, string> = {
  business: 'text-amber-400',
  growth:   'text-purple-400',
  starter:  'text-blue-400',
  free:     'text-gray-500',
};

export default function AdminClientsPage() {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'paid' | 'trial' | 'free' | 'suspended'>('all');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    fetch('/api/admin/clients', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        const d = await r.json();
        setClients(d.clients || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const filtered = clients.filter((c) => {
    const matchSearch =
      c.email.toLowerCase().includes(search.toLowerCase()) ||
      (c.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.organization || '').toLowerCase().includes(search.toLowerCase());

    const matchFilter =
      filter === 'all' ? true :
      filter === 'paid' ? c.subscription_status === 'active' :
      filter === 'trial' ? c.subscription_status === 'trialing' :
      filter === 'suspended' ? !c.is_active :
      filter === 'free' ? !c.subscription_status && c.is_active :
      true;

    return matchSearch && matchFilter;
  });

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Clients</h1>
        <p className="text-gray-500 text-sm mt-1">{clients.length} total accounts</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by email, name, or org…"
          className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 w-72"
        />
        <div className="flex gap-1">
          {(['all', 'paid', 'trial', 'free', 'suspended'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
                filter === f
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              {['Client', 'Plan / Tier', 'Credits', 'Jobs', 'Last active', 'Status', ''].map((h) => (
                <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                <td className="px-5 py-3">
                  <p className="text-gray-200 font-medium">{c.email}</p>
                  <p className="text-gray-500 text-xs">{c.name || c.organization || '—'}</p>
                </td>
                <td className="px-5 py-3">
                  {c.subscription_status ? (
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${PLAN_STYLE[c.subscription_status] || 'bg-gray-700 text-gray-400'}`}>
                      {c.subscription_status}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-600">—</span>
                  )}
                  <p className={`text-xs mt-0.5 font-medium capitalize ${TIER_STYLE[c.tier] || 'text-gray-500'}`}>{c.tier}</p>
                </td>
                <td className="px-5 py-3">
                  <p className="text-white text-xs font-mono">{c.remaining_credits} / {c.total_credits}</p>
                  <p className="text-gray-600 text-xs">{c.used_credits} used</p>
                </td>
                <td className="px-5 py-3 text-gray-300 text-xs font-mono">{c.total_jobs}</td>
                <td className="px-5 py-3 text-gray-500 text-xs">
                  {c.last_execution ? new Date(c.last_execution).toLocaleDateString('en-GB') : '—'}
                </td>
                <td className="px-5 py-3">
                  {!c.is_active ? (
                    <span className="text-xs bg-red-500/10 text-red-400 px-2 py-0.5 rounded-full">Suspended</span>
                  ) : (
                    <span className="text-xs bg-green-400/10 text-green-400 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </td>
                <td className="px-5 py-3">
                  <Link
                    href={`/admin/clients/${c.id}`}
                    className="text-xs text-violet-400 hover:text-violet-300 font-medium"
                  >
                    Manage →
                  </Link>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-12 text-center text-gray-600">
                  No clients match your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
