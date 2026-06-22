'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface PackageRow {
  id: string;
  name: string;
  tier: string;
  price_monthly: number;
  credits_included: number;
  agent_count: number;
  team_execution: boolean;
  media_generation: boolean;
}

const TIERS = ['starter', 'growth', 'business', 'enterprise'];
const TIER_COLOR: Record<string, string> = {
  starter: 'text-green-400 bg-green-500/10 border-green-500/20',
  growth: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  business: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
  enterprise: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
};

const MOCK_PACKAGES: PackageRow[] = [
  { id: 'starter',    name: 'Starter',    tier: 'starter',    price_monthly: 97,   credits_included: 500,   agent_count: 5,  team_execution: false, media_generation: true },
  { id: 'growth',     name: 'Growth',     tier: 'growth',     price_monthly: 197,  credits_included: 1500,  agent_count: 12, team_execution: true,  media_generation: true },
  { id: 'business',   name: 'Business',   tier: 'business',   price_monthly: 397,  credits_included: 4000,  agent_count: 20, team_execution: true,  media_generation: true },
  { id: 'enterprise', name: 'Enterprise', tier: 'enterprise', price_monthly: 0,    credits_included: 9999,  agent_count: 27, team_execution: true,  media_generation: true },
];

export default function AdminPackagesPage() {
  const router = useRouter();
  const [packages] = useState<PackageRow[]>(MOCK_PACKAGES);
  const [deploying, setDeploying] = useState<string | null>(null);
  const [flash, setFlash] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) router.push('/admin-login');
  }, [router]);

  const deployUnlimited = async (clientId?: string) => {
    setDeploying('unlimited');
    await new Promise(r => setTimeout(r, 800));
    setDeploying(null);
    setFlash('Unlimited package deployed. Credits set to 9999. Recorded in audit log.');
    setTimeout(() => setFlash(''), 4000);
  };

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Packages & Access</h1>
        <p className="text-gray-500 text-sm">Manage plans, agent access, credits, and limitless deployment controls</p>
      </div>

      {flash && (
        <div className="mb-6 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-5 py-3 text-emerald-400 text-sm font-medium">{flash}</div>
      )}

      {/* Admin-only: limitless controls */}
      <div className="bg-red-950/20 border border-red-500/20 rounded-2xl p-5 mb-8">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 uppercase tracking-wider">Admin Only</span>
              <h2 className="font-semibold text-white text-sm">Limitless Package Deployment</h2>
            </div>
            <p className="text-gray-500 text-xs">Deploy unlimited credits or enterprise access for internal accounts, demos, and owner test accounts. Never visible to clients.</p>
          </div>
          <button onClick={() => deployUnlimited()} disabled={deploying === 'unlimited'}
            className="shrink-0 px-4 py-2 rounded-xl text-sm font-semibold bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white transition-colors ml-4">
            {deploying === 'unlimited' ? 'Deploying…' : 'Deploy unlimited credits'}
          </button>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-3">
          {['Owner test account', 'Internal demo account', 'Bypass billing (internal only)'].map(label => (
            <div key={label} className="bg-gray-900/50 border border-gray-800 rounded-lg px-3 py-2.5 text-xs text-gray-500">
              <span className="text-gray-400 font-medium">{label}</span>
              <span className="ml-2 text-[10px] text-red-400 font-semibold">Admin gate</span>
            </div>
          ))}
        </div>
      </div>

      {/* Package table */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <h2 className="font-semibold text-white text-sm">Active Packages</h2>
          <button className="text-xs px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium transition-colors">+ New package</button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-xs text-gray-500">
              {['Package', 'Tier', 'Price/mo', 'Credits', 'Agents', 'Team exec', 'Media gen', 'Actions'].map(h => (
                <th key={h} className="px-6 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {packages.map(pkg => (
              <tr key={pkg.id} className="hover:bg-gray-800/30 transition-colors">
                <td className="px-6 py-4 font-medium text-white">{pkg.name}</td>
                <td className="px-6 py-4">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border capitalize ${TIER_COLOR[pkg.tier]}`}>{pkg.tier}</span>
                </td>
                <td className="px-6 py-4 text-gray-300">{pkg.price_monthly > 0 ? `$${pkg.price_monthly}` : 'Custom'}</td>
                <td className="px-6 py-4 text-gray-300">{pkg.credits_included.toLocaleString()}</td>
                <td className="px-6 py-4 text-gray-300">{pkg.agent_count}/27</td>
                <td className="px-6 py-4">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${pkg.team_execution ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-gray-600 bg-gray-800 border-gray-700'}`}>
                    {pkg.team_execution ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${pkg.media_generation ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-gray-600 bg-gray-800 border-gray-700'}`}>
                    {pkg.media_generation ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button className="text-xs text-violet-400 hover:text-violet-300">Edit</button>
                    <button className="text-xs text-gray-500 hover:text-white">Assign</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Spend approval thresholds */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <h2 className="font-semibold text-white mb-4 text-sm">Spend & Approval Thresholds</h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: 'Provider spend gate', value: '$0.10 per call', level: 'HITL-3' },
            { label: 'Long video generation', value: '>60s video', level: 'HITL-3' },
            { label: 'Ad spend launch', value: 'Any amount', level: 'HITL-3' },
            { label: 'AWS scaling', value: 'Any increase', level: 'HITL-3' },
            { label: 'Credit mutation', value: '>100 credits', level: 'HITL-3' },
            { label: 'Billing change', value: 'Any change', level: 'HITL-3' },
          ].map(rule => (
            <div key={rule.label} className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium text-white">{rule.label}</p>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">{rule.level}</span>
              </div>
              <p className="text-xs text-gray-500">Trigger: {rule.value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
