'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// ── Types ──────────────────────────────────────────────────────────────────────

interface AgentMeta {
  id: string;
  name: string;
  category: string;
  role: string;
  architecture: string;
  hitl_level: string;
  min_package: string;
  credit_estimate: number;
  capabilities: string[];
  visibility: 'client' | 'internal';
}

interface InternalLayer {
  id: string;
  name: string;
  category: string;
  role: string;
  maps_to: string | null;
  visibility: 'internal';
}

interface AgentsResponse {
  total: number;
  internal_total: number;
  tier_counts: Record<string, number>;
  agents: AgentMeta[];
  internal_layers: InternalLayer[];
}

// ── Color maps ─────────────────────────────────────────────────────────────────

const CATEGORY_COLOR: Record<string, string> = {
  Executive:  'bg-amber-500/10  text-amber-400  border-amber-500/20',
  Strategy:   'bg-violet-500/10 text-violet-400 border-violet-500/20',
  Research:   'bg-purple-500/10 text-purple-400 border-purple-500/20',
  Sales:      'bg-blue-500/10   text-blue-400   border-blue-500/20',
  Marketing:  'bg-pink-500/10   text-pink-400   border-pink-500/20',
  Media:      'bg-orange-500/10 text-orange-400 border-orange-500/20',
  Digital:    'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  Support:    'bg-teal-500/10   text-teal-400   border-teal-500/20',
  Operations: 'bg-gray-500/10   text-gray-300   border-gray-500/20',
  System:     'bg-zinc-500/10   text-zinc-400   border-zinc-500/20',
};

const HITL_COLOR: Record<string, string> = {
  'HITL-0': 'bg-green-500/10  text-green-400  border-green-500/20',
  'HITL-1': 'bg-blue-500/10   text-blue-400   border-blue-500/20',
  'HITL-2': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  'HITL-3': 'bg-red-500/10    text-red-400    border-red-500/20',
};

const TIER_COLOR: Record<string, string> = {
  starter:   'bg-green-500/10  text-green-400  border-green-500/20',
  growth:    'bg-blue-500/10   text-blue-400   border-blue-500/20',
  business:  'bg-violet-500/10 text-violet-400 border-violet-500/20',
  enterprise:'bg-amber-500/10  text-amber-400  border-amber-500/20',
};

const HITL_DESC: Record<string, string> = {
  'HITL-0': 'Autonomous — internal drafts, no approval needed',
  'HITL-1': 'Review — output reviewed before finalised',
  'HITL-2': 'Approval — must approve before external action',
  'HITL-3': 'Owner gate — admin must approve spend / high-risk action',
};

const CATEGORIES = ['All', 'Executive', 'Strategy', 'Research', 'Sales', 'Marketing', 'Media', 'Digital', 'Support', 'Operations'];

// ── Component ──────────────────────────────────────────────────────────────────

export default function AdminAgentsPage() {
  const router = useRouter();
  const [data, setData] = useState<AgentsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [catFilter, setCatFilter] = useState('All');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [tierFilter, setTierFilter] = useState<string>('all');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/admin/agents', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        const d = await r.json();
        setData(d);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!data) return null;

  const filtered = data.agents.filter((a) => {
    if (catFilter !== 'All' && a.category !== catFilter) return false;
    if (tierFilter !== 'all' && a.min_package !== tierFilter) return false;
    return true;
  });

  return (
    <div className="p-8 max-w-7xl">
      {/* Header */}
      <div className="mb-7">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold">Agent Catalogue</h1>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
            Admin view
          </span>
        </div>
        <p className="text-gray-500 text-sm">
          {data.total} client-facing agents · {data.internal_total} internal system layers
        </p>

        {/* Tier distribution */}
        <div className="flex flex-wrap gap-3 mt-4">
          {Object.entries(data.tier_counts).map(([tier, count]) => (
            <div key={tier} className={`px-3 py-1.5 rounded-lg border text-xs font-medium capitalize ${TIER_COLOR[tier] || ''}`}>
              {tier}: {count} agents
            </div>
          ))}
        </div>
      </div>

      {/* HITL legend */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-7">
        {Object.entries(HITL_DESC).map(([k, desc]) => (
          <div key={k} className={`rounded-lg border px-3 py-2 ${HITL_COLOR[k]}`}>
            <p className="text-[11px] font-bold">{k}</p>
            <p className="text-[10px] opacity-75 mt-0.5 leading-tight">{desc}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-2">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCatFilter(c)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              catFilter === c
                ? 'bg-violet-600 text-white'
                : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {c}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 mb-6">
        {(['all', 'starter', 'growth', 'business', 'enterprise'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTierFilter(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
              tierFilter === t
                ? 'bg-gray-700 text-white'
                : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {t === 'all' ? 'All tiers' : `${t}+`}
          </button>
        ))}
      </div>

      {/* Client-facing agents */}
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">
        Client-Facing ({filtered.length})
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mb-10">
        {filtered.map((a) => {
          const isExpanded = expandedId === a.id;
          return (
            <div
              key={a.id}
              onClick={() => setExpandedId(isExpanded ? null : a.id)}
              className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-4 cursor-pointer transition-colors"
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <p className="font-semibold text-sm text-white leading-tight">{a.name}</p>
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${CATEGORY_COLOR[a.category] || 'bg-gray-800 text-gray-400 border-gray-700'}`}>
                    {a.category}
                  </span>
                </div>
              </div>

              {/* Badges row */}
              <div className="flex flex-wrap gap-1.5 mb-2.5">
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${HITL_COLOR[a.hitl_level] || ''}`}>
                  {a.hitl_level}
                </span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize ${TIER_COLOR[a.min_package] || ''}`}>
                  {a.min_package}+
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-gray-700">
                  ~{a.credit_estimate} cr
                </span>
              </div>

              <p className="text-gray-500 text-xs leading-relaxed line-clamp-2">{a.role}</p>

              {/* Expanded */}
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-gray-800">
                  {a.capabilities.length > 0 && (
                    <div className="mb-3">
                      <p className="text-[10px] text-gray-600 uppercase tracking-wider font-semibold mb-2">Capabilities</p>
                      <div className="flex flex-wrap gap-1.5">
                        {a.capabilities.map((c) => (
                          <span key={c} className="text-[10px] px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="text-[10px] text-gray-600">
                    <span className="font-semibold">Architecture:</span>{' '}
                    <span className="text-gray-500 font-mono">{a.architecture}</span>
                  </div>
                  <div className="text-[10px] text-gray-600 mt-1">
                    <span className="font-semibold">Agent ID:</span>{' '}
                    <span className="text-gray-500 font-mono">{a.id}</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Internal system layers */}
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">
        Internal System Layers — NOT client-visible ({data.internal_layers.length})
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {data.internal_layers.map((a) => (
          <div key={a.id} className="bg-gray-900/40 border border-gray-800/50 rounded-xl p-4">
            <div className="flex items-start justify-between gap-3 mb-2">
              <p className="font-medium text-sm text-gray-400 leading-tight">{a.name}</p>
              <span className="shrink-0 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700">
                Internal
              </span>
            </div>
            <p className="text-gray-600 text-xs leading-relaxed mb-2">{a.role}</p>
            {a.maps_to && (
              <p className="text-[10px] text-gray-700">
                Maps to: <span className="text-gray-600 font-mono">{a.maps_to}</span>
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
