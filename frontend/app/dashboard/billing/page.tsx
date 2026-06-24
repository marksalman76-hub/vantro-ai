'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import RefundModal from './RefundModal';

interface DashData {
  user: { email: string; name: string | null; subscription_status: string | null };
  credits: { total_credits: number; used_credits: number; remaining_credits: number; tier: string };
}

const TIER_BADGE: Record<string, string> = {
  starter:'text-green-400 bg-green-500/10 border-green-500/20',
  growth:'text-blue-400 bg-blue-500/10 border-blue-500/20',
  business:'text-violet-400 bg-violet-500/10 border-violet-500/20',
  enterprise:'text-amber-400 bg-amber-500/10 border-amber-500/20',
};

export default function BillingPage() {
  const router = useRouter();
  const [data, setData] = useState<DashData | null>(null);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);
  const [isOwnerTest, setIsOwnerTest] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [refundResult, setRefundResult] = useState<{ ok: boolean; message: string } | null>(null);

  const openPortal = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setPortalLoading(true);
    try {
      const res = await fetch('/api/stripe/customer-portal', { method:'POST', headers:{Authorization:`Bearer ${token}`} });
      const json = await res.json();
      if (json.url) window.location.href = json.url;
    } catch {} finally { setPortalLoading(false); }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/dashboard', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d) {
          setData(d);
          setIsOwnerTest(d.credits?.tier === 'enterprise' && d.credits?.total_credits >= 9999);
        }
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"/></div>;
  if (!data) return null;

  const { user, credits } = data;
  const usedPct = credits.total_credits > 0 ? Math.round((credits.used_credits / credits.total_credits) * 100) : 0;
  const tier = credits.tier || 'free';
  const subActive = user.subscription_status === 'active' || user.subscription_status === 'trialing';

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Billing & Credits</h1>
        <p className="text-gray-500 text-sm">Your subscription, credit balance, and billing management</p>
      </div>

      {isOwnerTest && (
        <div className="mb-6 bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4">
          <p className="text-amber-400 text-sm font-medium">Owner test account. Unlimited testing is enabled. Credits are not enforced for this account.</p>
        </div>
      )}

      {/* Plan */}
      <div className={`rounded-2xl border p-6 mb-6 ${subActive ? 'bg-violet-950/20 border-violet-500/20' : 'bg-gray-900 border-gray-800'}`}>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-gray-500 mb-1">Current plan</p>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-xl font-bold capitalize">{tier === 'free' ? 'Free' : tier}</h2>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border capitalize ${TIER_BADGE[tier] || 'text-gray-400 border-gray-700'}`}>{tier}</span>
            </div>
            <p className="text-xs text-gray-500">
              {subActive ? `Subscription ${user.subscription_status}` : 'No active subscription'}
            </p>
          </div>
          <div className="flex flex-col gap-2 items-end">
            {subActive
              ? <button onClick={openPortal} disabled={portalLoading} className="px-4 py-2 rounded-xl text-sm font-medium border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 disabled:opacity-50 transition-colors">{portalLoading ? 'Opening…' : 'Manage billing'}</button>
              : <Link href="/pricing" className="px-4 py-2 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors">Upgrade plan</Link>}
          </div>
        </div>
      </div>

      {/* Credits */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-white text-sm">Credits</h2>
          <Link href="/pricing" className="text-xs text-violet-400 hover:text-violet-300 font-medium">Buy more credits →</Link>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-4">
          {[
            { label:'Available', value: credits.remaining_credits, color:'text-emerald-400' },
            { label:'Used',      value: credits.used_credits,      color:'text-orange-400' },
            { label:'Total',     value: credits.total_credits,     color:'text-white' },
          ].map(s => (
            <div key={s.label} className="bg-gray-800/50 rounded-xl p-3 text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value.toLocaleString()}</p>
              <p className="text-gray-600 text-xs mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
        {credits.total_credits > 0 && (
          <div>
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1.5">
              <span>Usage</span>
              <span>{usedPct}% used</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div className={`h-2 rounded-full transition-all ${usedPct > 80 ? 'bg-red-500' : usedPct > 60 ? 'bg-orange-500' : 'bg-violet-500'}`}
                style={{ width: `${Math.min(usedPct, 100)}%` }}/>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Link href="/pricing" className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-2xl p-5 text-center group transition-all">
          <span className="text-2xl mb-2 block">↑</span>
          <p className="text-white text-sm font-semibold mb-0.5">Upgrade plan</p>
          <p className="text-gray-600 text-xs">Access more agents and credits</p>
        </Link>
        <button onClick={openPortal} disabled={!subActive || portalLoading}
          className="bg-gray-900 border border-gray-800 hover:border-gray-700 disabled:opacity-40 rounded-2xl p-5 text-center group transition-all">
          <span className="text-2xl mb-2 block">◇</span>
          <p className="text-white text-sm font-semibold mb-0.5">Billing portal</p>
          <p className="text-gray-600 text-xs">Invoices, payment method, cancel</p>
        </button>
      </div>

      {/* Refund request */}
      {subActive && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-6">
          <h2 className="font-semibold text-white text-sm mb-2">Request a Refund</h2>
          <p className="text-gray-500 text-xs mb-3">
            You may be eligible for a full refund within 72 hours of signup if no agent tasks have been run.
            {' '}<Link href="/refund-policy" className="text-violet-400 hover:text-violet-300">View refund policy →</Link>
          </p>
          {refundResult ? (
            <div className={`rounded-xl px-4 py-3 text-xs font-medium ${refundResult.ok ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border border-red-500/20 text-red-400'}`}>
              {refundResult.message}
            </div>
          ) : (
            <button
              onClick={() => setShowRefundModal(true)}
              className="px-4 py-2 rounded-xl text-sm font-medium border border-red-500/30 text-red-400 hover:bg-red-500/10 hover:border-red-500/50 transition-colors"
            >
              Request Refund
            </button>
          )}
        </div>
      )}

      {/* Help */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
        <h2 className="font-semibold text-white text-sm mb-2">Need help with billing?</h2>
        <p className="text-gray-500 text-xs mb-3">If you believe you were charged incorrectly, credits were not applied, or you need a refund, contact support and we will review within 24 hours.</p>
        <Link href="/dashboard/support" className="text-xs text-violet-400 hover:text-violet-300 font-medium">Open a support request →</Link>
      </div>

      {/* Refund confirmation modal */}
      {showRefundModal && (
        <RefundModal
          onClose={() => setShowRefundModal(false)}
          onSuccess={(msg) => { setRefundResult({ ok: true, message: msg }); setShowRefundModal(false); }}
          onError={(msg) => { setRefundResult({ ok: false, message: msg }); setShowRefundModal(false); }}
        />
      )}
    </div>
  );
}
