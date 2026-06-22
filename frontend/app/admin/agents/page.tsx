'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Agent {
  id: string;
  name: string;
  category: string;
  description: string;
}

const CATEGORY_COLOR: Record<string, string> = {
  Leadership:    'bg-amber-400/10 text-amber-400 border-amber-400/20',
  Strategy:      'bg-violet-400/10 text-violet-400 border-violet-400/20',
  Growth:        'bg-green-400/10 text-green-400 border-green-400/20',
  Sales:         'bg-blue-400/10 text-blue-400 border-blue-400/20',
  Marketing:     'bg-pink-400/10 text-pink-400 border-pink-400/20',
  Content:       'bg-orange-400/10 text-orange-400 border-orange-400/20',
  Communication: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20',
  Operations:    'bg-gray-400/10 text-gray-300 border-gray-400/20',
  Product:       'bg-indigo-400/10 text-indigo-400 border-indigo-400/20',
  Commerce:      'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  Intelligence:  'bg-red-400/10 text-red-400 border-red-400/20',
  Finance:       'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
  Support:       'bg-teal-400/10 text-teal-400 border-teal-400/20',
};

const INTERNAL_AGENTS = [
  { id: 'orchestration_agent',       name: 'Orchestration Agent',         category: 'System', description: 'Routes and coordinates execution across all agents' },
  { id: 'security_compliance_agent', name: 'Security & Compliance Agent', category: 'System', description: 'Enforces guardrails, compliance, and access policies' },
  { id: 'qa_testing_agent',          name: 'QA Testing Agent',            category: 'System', description: 'Quality assurance and output validation layer' },
  { id: 'billing_optimisation_agent','name': 'Billing Optimisation Agent','category': 'System', description: 'Credit tracking, cost optimisation, and billing enforcement' },
];

export default function AdminAgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [catFilter, setCatFilter] = useState('All');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/admin/agents', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        const d = await r.json();
        setAgents(d.agents || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const categories = ['All', ...Array.from(new Set(agents.map((a) => a.category)))];
  const filtered = catFilter === 'All' ? agents : agents.filter((a) => a.category === catFilter);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Agent Catalogue</h1>
        <p className="text-gray-500 text-sm mt-1">{agents.length} client-facing agents · 4 internal system layers</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-1.5 mb-6">
        {categories.map((c) => (
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

      {/* Client-facing agents */}
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Client-Facing ({filtered.length})</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-8">
        {filtered.map((a) => (
          <div key={a.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-colors">
            <div className="flex items-start justify-between gap-3 mb-2">
              <p className="font-medium text-sm text-white leading-tight">{a.name}</p>
              <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full border ${CATEGORY_COLOR[a.category] || 'bg-gray-700 text-gray-400 border-gray-700'}`}>
                {a.category}
              </span>
            </div>
            <p className="text-gray-500 text-xs leading-relaxed">{a.description}</p>
          </div>
        ))}
      </div>

      {/* Internal system agents */}
      {catFilter === 'All' && (
        <>
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Internal System Layers (not client-visible)</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {INTERNAL_AGENTS.map((a) => (
              <div key={a.id} className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4 opacity-60">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <p className="font-medium text-sm text-gray-400 leading-tight">{a.name}</p>
                  <span className="shrink-0 text-xs font-medium px-2 py-0.5 rounded-full bg-gray-800 text-gray-500 border border-gray-700">
                    Internal
                  </span>
                </div>
                <p className="text-gray-600 text-xs">{a.description}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
