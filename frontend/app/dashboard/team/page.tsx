'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface AgentMeta { id: string; name: string; category: string; role: string; hitl_level: string; credit_estimate: number; capabilities: string[]; unlocked: boolean; }

const HITL: Record<string, { label: string; color: string }> = {
  'HITL-0': { label: 'Autonomous', color: 'text-green-400 bg-green-500/10 border-green-500/20' },
  'HITL-1': { label: 'Review',     color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  'HITL-2': { label: 'Approval',   color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' },
  'HITL-3': { label: 'Owner gate', color: 'text-red-400 bg-red-500/10 border-red-500/20' },
};

interface TeamJob { jobId: string; agentName: string; status: string; }

export default function TeamBuilderPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<AgentMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [team, setTeam] = useState<AgentMeta[]>([]);
  const [leadId, setLeadId] = useState<string | null>(null);
  const [task, setTask] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [jobs, setJobs] = useState<TeamJob[]>([]);
  const [catFilter, setCatFilter] = useState('All');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/agents/all', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.agents) setAgents(d.agents.filter((a: AgentMeta) => a.unlocked)); })
      .finally(() => setLoading(false));
  }, [router]);

  const unlocked = agents;
  const cats = ['All', ...Array.from(new Set(unlocked.map(a => a.category)))];
  const filtered = catFilter === 'All' ? unlocked : unlocked.filter(a => a.category === catFilter);

  const addToTeam = (agent: AgentMeta) => {
    if (team.find(a => a.id === agent.id)) return;
    setTeam(prev => [...prev, agent]);
    if (!leadId) setLeadId(agent.id);
  };
  const removeFromTeam = (id: string) => {
    setTeam(prev => prev.filter(a => a.id !== id));
    if (leadId === id) setLeadId(team.find(a => a.id !== id)?.id ?? null);
  };

  const creditEstimate = team.reduce((s, a) => s + a.credit_estimate, 0);
  const needsApproval = team.some(a => a.hitl_level === 'HITL-3');

  const launch = async () => {
    if (!task.trim() || team.length === 0) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    setSubmitting(true); setError('');
    const results: TeamJob[] = [];
    for (const agent of team) {
      try {
        const res = await fetch(`/api/agents/${agent.id}/run`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: task.trim(), team_lead: agent.id === leadId, team_members: team.map(a => a.id) }),
        });
        const json = await res.json();
        if (res.ok) results.push({ jobId: json.job_id, agentName: json.agent_name, status: json.status || 'pending' });
      } catch {}
    }
    setJobs(results);
    setSubmitting(false);
  };

  if (loading) return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"/></div>;

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-1">Team Builder</h1>
        <p className="text-gray-500 text-sm">Combine your purchased agents to work as a coordinated team on a single goal</p>
      </div>

      {jobs.length > 0 && (
        <div className="mb-6 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5">
          <p className="text-emerald-400 font-semibold text-sm mb-3">Team launched — {jobs.length} agent{jobs.length > 1 ? 's' : ''} running</p>
          <div className="space-y-2">
            {jobs.map(j => (
              <div key={j.jobId} className="flex items-center gap-3 text-xs text-gray-400">
                <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin shrink-0"/>
                <span className="text-white font-medium">{j.agentName}</span>
                <span className="font-mono text-gray-600">{j.jobId.slice(0,8)}</span>
                <Link href="/dashboard/agents" className="text-violet-400 ml-auto">Track →</Link>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">
        {/* Left: agent picker */}
        <div>
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-white text-sm">Your Agents</h2>
              <span className="text-xs text-gray-500">{team.length} selected</span>
            </div>
            <div className="flex flex-wrap gap-1.5 mb-4">
              {cats.map(c => (
                <button key={c} onClick={() => setCatFilter(c)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${catFilter === c ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
                  {c}
                </button>
              ))}
            </div>
            {unlocked.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-gray-600 text-sm mb-3">No agents in your package yet.</p>
                <Link href="/pricing" className="text-violet-400 text-sm">Upgrade to unlock agents →</Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-96 overflow-y-auto pr-1">
                {filtered.map(agent => {
                  const inTeam = !!team.find(a => a.id === agent.id);
                  return (
                    <button key={agent.id} onClick={() => inTeam ? removeFromTeam(agent.id) : addToTeam(agent)}
                      className={`text-left p-3 rounded-xl border transition-all ${inTeam ? 'border-violet-500/40 bg-violet-600/10' : 'border-gray-800 bg-gray-800/30 hover:border-gray-700'}`}>
                      <div className="flex items-start justify-between mb-1">
                        <p className="text-xs font-semibold text-white">{agent.name}</p>
                        <span className={`text-[9px] font-bold ${inTeam ? 'text-violet-400' : 'text-gray-600'}`}>{inTeam ? '✓' : '+'}</span>
                      </div>
                      <p className="text-gray-500 text-[10px] leading-relaxed line-clamp-2">{agent.role}</p>
                      <div className="mt-1.5 flex items-center gap-1">
                        <span className="text-[9px] text-gray-600 bg-gray-800 px-1.5 py-0.5 rounded">{agent.category}</span>
                        <span className="text-[9px] text-gray-600">~{agent.credit_estimate}cr</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right: team config */}
        <div className="space-y-4">
          {/* Team roster */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="font-semibold text-white text-sm mb-3">Your Team</h2>
            {team.length === 0 ? (
              <p className="text-gray-600 text-xs py-4 text-center">Select agents from the left to build your team</p>
            ) : (
              <div className="space-y-2 mb-3">
                {team.map(agent => (
                  <div key={agent.id} className={`flex items-center gap-2 p-2 rounded-lg border ${leadId === agent.id ? 'border-amber-500/30 bg-amber-500/5' : 'border-gray-800'}`}>
                    <button onClick={() => setLeadId(agent.id)} title="Set as lead"
                      className={`w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-[9px] font-bold transition-colors ${leadId === agent.id ? 'bg-amber-500 text-black' : 'border border-gray-600 text-gray-600 hover:border-amber-500 hover:text-amber-500'}`}>
                      {leadId === agent.id ? '★' : '☆'}
                    </button>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-xs font-medium truncate">{agent.name}</p>
                      <p className="text-gray-600 text-[10px]">{leadId === agent.id ? 'Lead agent' : 'Supporting'}</p>
                    </div>
                    <span className="text-[9px] text-gray-600">~{agent.credit_estimate}cr</span>
                    <button onClick={() => removeFromTeam(agent.id)} className="text-gray-600 hover:text-red-400 text-xs">✕</button>
                  </div>
                ))}
              </div>
            )}
            {team.length >= 2 && (
              <div className="pt-2 border-t border-gray-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">Credit estimate</span>
                  <span className="text-white font-bold">~{creditEstimate} credits</span>
                </div>
                {needsApproval && (
                  <p className="text-red-400 text-[10px] mt-1.5">One or more agents require admin approval before execution.</p>
                )}
              </div>
            )}
          </div>

          {/* Task */}
          {team.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <h2 className="font-semibold text-white text-sm mb-3">Team Task</h2>
              <textarea value={task} onChange={e => setTask(e.target.value)} rows={5}
                placeholder="Describe the goal for your team. Be specific — each agent will use this to contribute their part."
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-violet-500 leading-relaxed mb-3"/>
              {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
              <button onClick={launch} disabled={submitting || !task.trim() || team.length < 1}
                className="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-40 text-white font-semibold py-3 rounded-xl text-sm transition-all">
                {submitting ? 'Launching team…' : needsApproval ? 'Submit team for approval' : `▶ Launch ${team.length}-agent team`}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
