'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Client {
  id: string;
  email: string;
  name: string | null;
  subscription_status: string | null;
  stripe_customer_id: string | null;
  tier: string;
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  total_jobs: number;
}

const PLAN_CREDITS: Record<string, number> = { starter: 60, growth: 200, business: 300 };
const PLAN_PRICE: Record<string, string> = { starter: '$99/mo', growth: '$279/mo', business: '$399/mo' };

const PLAN_STYLE: Record<string, string> = {
  active:   'bg-green-400/10 text-green-400',
  trialing: 'bg-blue-400/10 text-blue-400',
  canceled: 'bg-red-400/10 text-red-400',
};

export default function AdminBillingPage() {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin-login'); return; }
    fetch('/api/admin/clients', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        const d = await r.json();
        setClients(d.clients || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const paid = clients.filter((c) => c.subscription_status === 'active');
  const trial = clients.filter((c) => c.subscription_status === 'trialing');
  const free = clients.filter((c) => !c.subscription_status);
  const tiers = ['starter', 'growth', 'business'];

  const totalMRR = paid.reduce((sum, c) => {
    const price = c.tier === 'business' ? 399 : c.tier === 'growth' ? 279 : c.tier === 'starter' ? 99 : 0;
    return sum + price;
  }, 0);

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Billing & Credits</h1>
        <p className="text-gray-500 text-sm mt-1">Subscription overview and credit management</p>
      </div>

      {/* MRR + breakdown */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Estimated MRR</p>
          <p className="text-2xl font-bold text-green-400">${totalMRR.toLocaleString()}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Paid accounts</p>
          <p className="text-2xl font-bold text-white">{paid.length}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Trial accounts</p>
          <p className="text-2xl font-bold text-blue-400">{trial.length}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Free accounts</p>
          <p className="text-2xl font-bold text-gray-400">{free.length}</p>
        </div>
      </div>

      {/* Plan breakdown */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {tiers.map((tier) => {
          const count = clients.filter((c) => c.tier === tier && c.subscription_status === 'active').length;
          const revenue = count * (tier === 'business' ? 399 : tier === 'growth' ? 279 : 99);
          return (
            <div key={tier} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <p className="text-gray-400 text-xs mb-1 capitalize">{tier}</p>
              <p className="text-white font-bold text-lg">{count} clients</p>
              <p className="text-gray-500 text-xs mt-1">{PLAN_PRICE[tier]} · ${revenue}/mo revenue</p>
              <p className="text-gray-600 text-xs">{PLAN_CREDITS[tier]} credits/month per client</p>
            </div>
          );
        })}
      </div>

      {/* Billing table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-x-auto">
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="font-semibold">All Accounts</h2>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              {['Client', 'Plan', 'Tier', 'Credits', 'Stripe ID', 'Actions'].map((h) => (
                <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {clients.map((c) => (
              <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                <td className="px-5 py-3">
                  <p className="text-gray-200 text-sm">{c.email}</p>
                  {c.name && <p className="text-gray-500 text-xs">{c.name}</p>}
                </td>
                <td className="px-5 py-3">
                  {c.subscription_status ? (
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${PLAN_STYLE[c.subscription_status] || 'bg-gray-700 text-gray-400'}`}>
                      {c.subscription_status}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-600">free</span>
                  )}
                </td>
                <td className="px-5 py-3 text-gray-300 text-xs capitalize">{c.tier}</td>
                <td className="px-5 py-3">
                  <p className="text-xs text-white font-mono">{c.remaining_credits} / {c.total_credits}</p>
                  <div className="w-16 bg-gray-800 rounded-full h-1 mt-1">
                    <div
                      className="h-1 rounded-full bg-purple-500"
                      style={{ width: `${c.total_credits > 0 ? Math.min((c.used_credits / c.total_credits) * 100, 100) : 0}%` }}
                    />
                  </div>
                </td>
                <td className="px-5 py-3 text-gray-600 font-mono text-xs">
                  {c.stripe_customer_id ? `${c.stripe_customer_id.slice(0, 14)}…` : '—'}
                </td>
                <td className="px-5 py-3">
                  <Link href={`/admin/clients/${c.id}`} className="text-xs text-violet-400 hover:text-violet-300">
                    Manage →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
