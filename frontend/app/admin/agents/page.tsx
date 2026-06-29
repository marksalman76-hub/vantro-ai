'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

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
}

interface InternalLayer {
  id: string;
  name: string;
  category: string;
  role: string;
  maps_to: string | null;
}

interface AgentsResponse {
  total: number;
  internal_total: number;
  tier_counts: Record<string, number>;
  agents: AgentMeta[];
  internal_layers: InternalLayer[];
}

interface JobResult {
  job_id: string;
  agent_name: string;
  status: string;
  output: string | null;
  error_message: string | null;
}

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
};

const HITL_COLOR: Record<string, string> = {
  'HITL-0': 'bg-green-500/10  text-green-400  border-green-500/20',
  'HITL-1': 'bg-blue-500/10   text-blue-400   border-blue-500/20',
  'HITL-2': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  'HITL-3': 'bg-red-500/10    text-red-400    border-red-500/20',
};

const CATEGORIES = ['All', 'Executive', 'Strategy', 'Research', 'Sales', 'Marketing', 'Media', 'Digital', 'Support', 'Operations'];

function OutputRenderer({ text }: { text: string }) {
  return (
    <div className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed font-mono bg-gray-950 rounded-xl p-4 max-h-96 overflow-y-auto border border-gray-800">
      {text}
    </div>
  );
}

function RunModal({ agent, token, onClose }: { agent: AgentMeta; token: string; onClose: () => void }) {
  const [prompt, setPrompt] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [job, setJob] = useState<JobResult | null>(null);
  const [polling, setPolling] = useState(false);
  const [copied, setCopied] = useState(false);

  const pollJob = useCallback(async (jobId: string) => {
    setPolling(true);
    const interval = setInterval(async () => {
      try {
        const r = await fetch(`/api/admin/agents/jobs/${jobId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const d = await r.json();
        setJob(d);
        if (['completed', 'failed', 'cancelled'].includes(d.status)) {
          clearInterval(interval);
          setPolling(false);
        }
      } catch {
        clearInterval(interval);
        setPolling(false);
      }
    }, 2500);
    return () => clearInterval(interval);
  }, [token]);

  const submit = async () => {
    if (!prompt.trim()) return;
    setSubmitting(true);
    try {
      const r = await fetch(`/api/admin/agents/${agent.id}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });
      const d = await r.json();
      if (!r.ok) {
        setJob({ job_id: '', agent_name: agent.name, status: 'failed', output: null, error_message: d.detail || 'Failed to start job' });
        return;
      }
      setJob({ job_id: d.job_id, agent_name: agent.name, status: d.status, output: null, error_message: null });
      pollJob(d.job_id);
    } catch {
      setJob({ job_id: '', agent_name: agent.name, status: 'failed', output: null, error_message: 'Network error' });
    } finally {
      setSubmitting(false);
    }
  };

  const copy = () => {
    if (job?.output) { navigator.clipboard.writeText(job.output); setCopied(true); setTimeout(() => setCopied(false), 2000); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-lg font-bold text-white">{agent.name}</h2>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${HITL_COLOR[agent.hitl_level]}`}>{agent.hitl_level}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 font-bold">Admin run</span>
            </div>
            <p className="text-gray-500 text-xs leading-relaxed max-w-lg">{agent.role}</p>
          </div>
          <button onClick={onClose} className="text-gray-600 hover:text-white transition-colors ml-4 shrink-0 text-xl leading-none">✕</button>
        </div>

        <div className="p-6 space-y-5">
          {!job ? (
            <>
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-2">Task / Prompt</label>
                <textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  rows={6}
                  placeholder={`Describe what you want ${agent.name} to do…`}
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500"
                />
                <p className="text-gray-700 text-xs mt-1.5">Admin run — no package or credit restrictions apply.</p>
              </div>
              <button
                onClick={submit}
                disabled={submitting || !prompt.trim()}
                className="w-full py-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Starting…</>
                ) : (
                  `Run ${agent.name}`
                )}
              </button>
            </>
          ) : (
            <div className="space-y-4">
              {/* Status */}
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  job.status === 'completed' ? 'bg-green-400' :
                  job.status === 'failed' ? 'bg-red-400' :
                  job.status === 'running' ? 'bg-yellow-400 animate-pulse' :
                  'bg-blue-400 animate-pulse'
                }`} />
                <span className="text-sm font-medium text-white capitalize">{job.status}</span>
                {polling && <span className="text-xs text-gray-500">Polling…</span>}
              </div>

              {/* Output */}
              {job.output && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-medium text-gray-400">Output</p>
                    <button onClick={copy} className="text-xs text-violet-400 hover:text-violet-300 transition-colors">
                      {copied ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                  <OutputRenderer text={job.output} />
                </div>
              )}

              {/* Error */}
              {job.error_message && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                  <p className="text-red-400 text-xs">{job.error_message}</p>
                </div>
              )}

              {/* Pending / running message */}
              {!job.output && !job.error_message && (
                <div className="bg-gray-800 rounded-xl px-4 py-6 text-center">
                  <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">Agent is working…</p>
                  <p className="text-gray-600 text-xs mt-1">Job ID: {job.job_id}</p>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => { setJob(null); setPrompt(''); }}
                  className="flex-1 py-2.5 rounded-xl border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 text-sm transition-colors"
                >
                  Run again
                </button>
                <button onClick={onClose} className="flex-1 py-2.5 rounded-xl bg-gray-800 text-white text-sm hover:bg-gray-700 transition-colors">
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AdminAgentsPage() {
  const router = useRouter();
  const [data, setData] = useState<AgentsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [catFilter, setCatFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [runAgent, setRunAgent] = useState<AgentMeta | null>(null);
  const [token, setToken] = useState('');

  useEffect(() => {
    const t = localStorage.getItem('admin_token');
    if (!t) { router.push('/admin-login'); return; }
    setToken(t);
    fetch('/api/admin/agents', { headers: { Authorization: `Bearer ${t}` } })
      .then(async (r) => {
        const d = await r.json();
        if (d && Array.isArray(d.agents)) setData(d);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!data) return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-gray-500 text-sm">Failed to load agents. Check backend connectivity.</p>
    </div>
  );

  const filtered = data.agents.filter((a) => {
    if (catFilter !== 'All' && a.category !== catFilter) return false;
    if (search && !a.name.toLowerCase().includes(search.toLowerCase()) && !a.role.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-8 max-w-7xl">
      {runAgent && <RunModal agent={runAgent} token={token} onClose={() => setRunAgent(null)} />}

      <div className="mb-7">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold">Run an Agent</h1>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">Admin — no restrictions</span>
        </div>
        <p className="text-gray-500 text-sm">{data.total} agents available · click any agent to run a task</p>
      </div>

      {/* Search + filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search agents…"
          className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 w-60"
        />
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCatFilter(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                catFilter === c ? 'bg-violet-600 text-white' : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Agent grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mb-10">
        {filtered.map((a) => {
          const isExpanded = expandedId === a.id;
          return (
            <div key={a.id} className="bg-gray-900 border border-gray-800 hover:border-violet-500/40 rounded-xl p-4 transition-colors">
              {/* Top row */}
              <div
                className="flex items-start justify-between gap-3 mb-2 cursor-pointer"
                onClick={() => setExpandedId(isExpanded ? null : a.id)}
              >
                <p className="font-semibold text-sm text-white leading-tight">{a.name}</p>
                <span className={`shrink-0 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${CATEGORY_COLOR[a.category] || 'bg-gray-800 text-gray-400 border-gray-700'}`}>
                  {a.category}
                </span>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-1.5 mb-2.5 cursor-pointer" onClick={() => setExpandedId(isExpanded ? null : a.id)}>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${HITL_COLOR[a.hitl_level]}`}>{a.hitl_level}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-gray-700">~{a.credit_estimate} cr</span>
              </div>

              <p className="text-gray-500 text-xs leading-relaxed line-clamp-2 cursor-pointer" onClick={() => setExpandedId(isExpanded ? null : a.id)}>
                {a.role}
              </p>

              {/* Expanded detail */}
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-gray-800">
                  {a.capabilities.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {a.capabilities.map(c => (
                        <span key={c} className="text-[10px] px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700">{c}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Run button — always visible */}
              <button
                onClick={() => setRunAgent(a)}
                className="mt-3 w-full py-2 rounded-lg bg-violet-600/20 hover:bg-violet-600 border border-violet-500/30 hover:border-violet-500 text-violet-300 hover:text-white text-xs font-semibold transition-all"
              >
                ▶ Run Task
              </button>
            </div>
          );
        })}
      </div>

      {/* Internal layers */}
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">
        Internal System Layers — not client-visible ({data.internal_layers.length})
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {data.internal_layers.map((a) => (
          <div key={a.id} className="bg-gray-900/40 border border-gray-800/50 rounded-xl p-4">
            <p className="font-medium text-sm text-gray-400 mb-1">{a.name}</p>
            <p className="text-gray-600 text-xs leading-relaxed">{a.role}</p>
            {a.maps_to && <p className="text-[10px] text-gray-700 mt-1.5">Maps to: <span className="font-mono">{a.maps_to}</span></p>}
          </div>
        ))}
      </div>
    </div>
  );
}
