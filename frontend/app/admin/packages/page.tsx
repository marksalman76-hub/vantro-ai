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

export default function AdminPackagesPage() {
  const router = useRouter();
  const [packages, setPackages] = useState<PackageRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [deploying, setDeploying] = useState<string | null>(null);
  const [flash, setFlash] = useState('');
  const [flashErr, setFlashErr] = useState('');

  // Assign modal state
  const [assignPkg, setAssignPkg] = useState<PackageRow | null>(null);
  const [assignUserId, setAssignUserId] = useState('');
  const [assigning, setAssigning] = useState(false);

  const token = () => typeof window !== 'undefined' ? localStorage.getItem('admin_token') : '';

  useEffect(() => {
    if (!token()) { router.push('/admin-login'); return; }
    fetchPackages();
  }, [router]);

  async function fetchPackages() {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/packages', {
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json();
      setPackages(data.packages || []);
    } catch {
      setFlashErr('Failed to load packages.');
    } finally {
      setLoading(false);
    }
  }

  const showFlash = (msg: string, err = false) => {
    if (err) { setFlashErr(msg); setTimeout(() => setFlashErr(''), 4000); }
    else { setFlash(msg); setTimeout(() => setFlash(''), 4000); }
  };

  const deployUnlimited = async () => {
    setDeploying('unlimited');
    try {
      const res = await fetch('/api/admin/packages/deploy-unlimited', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: '', reason: 'Admin unlimited deployment from portal' }),
      });
      const data = await res.json();
      showFlash(data.message || 'Unlimited package deployed. Credits set to 9999.');
    } catch {
      showFlash('Unlimited package deployed.');
    }
    setDeploying(null);
  };

  const openAssign = (pkg: PackageRow) => {
    setAssignPkg(pkg);
    setAssignUserId('');
  };

  const submitAssign = async () => {
    if (!assignPkg || !assignUserId.trim()) return;
    setAssigning(true);
    try {
      const res = await fetch('/api/admin/packages/assign', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: assignUserId.trim(),
          tier: assignPkg.tier,
          reason: `Admin assigned ${assignPkg.name} package from portal`,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        showFlash(data.detail || 'Failed to assign package.', true);
      } else {
        showFlash(`${assignPkg.name} package assigned to ${data.target_user}.`);
        setAssignPkg(null);
      }
    } catch {
      showFlash('Assignment failed. Check user ID.', true);
    }
    setAssigning(false);
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
      {flashErr && (
        <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl px-5 py-3 text-red-400 text-sm font-medium">{flashErr}</div>
      )}

      {/* Admin-only: limitless controls */}
      <div className="bg-red-950/20 border border-red-500/20 rounded-2xl p-5 mb-8">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 uppercase tracking-wider">Admin Only</span>
              <h2 className="font-semibold text-white text-sm">Limitless Package Deployment</h2>
            </div>
            <p className="text-gray-500 text-xs">Deploy unlimited credits for internal accounts, demos, and owner test accounts. Never visible to clients.</p>
          </div>
          <button onClick={deployUnlimited} disabled={deploying === 'unlimited'}
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
          <span className="text-xs text-gray-600 italic">Tier definitions are managed via code deployment</span>
        </div>
        {loading ? (
          <div className="px-6 py-8 text-center text-gray-600 text-sm">Loading packages…</div>
        ) : (
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
                  <td className="px-6 py-4 text-gray-300">{pkg.agent_count}/22</td>
                  <td className="px-6 py-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${pkg.team_execution ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-gray-600 bg-gray-800 border-gray-700'}`}>
                      {pkg.team_execution ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border text-emerald-400 bg-emerald-500/10 border-emerald-500/20">
                      Yes
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => openAssign(pkg)}
                      className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                    >
                      Assign to user
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
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

      {/* Assign modal */}
      {assignPkg && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-white font-semibold mb-1">Assign {assignPkg.name} package</h3>
            <p className="text-gray-500 text-xs mb-4">Sets the target user's credit allocation to {assignPkg.credits_included.toLocaleString()} credits.</p>
            <label className="block text-xs font-semibold text-gray-400 mb-1.5 uppercase tracking-wide">User ID</label>
            <input
              type="text"
              value={assignUserId}
              onChange={e => setAssignUserId(e.target.value)}
              placeholder="Paste user UUID here"
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setAssignPkg(null)}
                className="flex-1 py-2.5 rounded-xl text-sm font-medium text-gray-400 bg-gray-800 hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={submitAssign}
                disabled={!assignUserId.trim() || assigning}
                className="flex-1 py-2.5 rounded-xl text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 disabled:opacity-50 transition-colors"
              >
                {assigning ? 'Assigning…' : `Assign ${assignPkg.name}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
