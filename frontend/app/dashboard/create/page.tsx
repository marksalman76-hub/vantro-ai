'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  unlocked: boolean;
  credit_estimate: number;
  hitl_level: string;
}

const CATEGORIES = [
  { id: 'leads',       label: 'Lead Generation',    icon: '◎' },
  { id: 'social',      label: 'Social Content',      icon: '◈' },
  { id: 'email',       label: 'Email Campaigns',     icon: '◉' },
  { id: 'seo',         label: 'SEO & Content',       icon: '◆' },
  { id: 'analytics',   label: 'Analytics & Reports', icon: '▣' },
  { id: 'campaign',    label: 'Campaigns',            icon: '◬' },
  { id: 'automation',  label: 'Automation',           icon: '⬡' },
  { id: 'retention',   label: 'Retention',            icon: '◎' },
  { id: 'reputation',  label: 'Reputation',           icon: '◇' },
  { id: 'media',       label: 'Create Media',         icon: '▶', href: '/dashboard/create-media' },
];

type Mode = 'single' | 'team';

export default function CreatePage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>('single');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [task, setTask] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    try {
      const res = await fetch('/api/agents', { headers: { Authorization: `Bearer ${token}` } });
      const d = await res.json();
      setAgents((d.agents || []).filter((a: Agent) => a.unlocked));
    } catch {}
    finally { setLoading(false); }
  }, [router]);

  useEffect(() => { load(); }, [load]);

  const filtered = category
    ? agents.filter(a => a.category?.toLowerCase().includes(category))
    : agents;

  async function submit() {
    if (!selectedAgent || !task.trim()) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch(`/api/agents/${selectedAgent}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ task }),
      });
      const d = await res.json();
      if (res.ok && d.job_id) {
        router.push('/dashboard/jobs');
      } else {
        setError(d.detail || 'Could not start task. Please try again or contact support.');
      }
    } catch {
      setError('Could not start task. Please contact support.');
    } finally {
      setSubmitting(false);
    }
  }

  const chosen = agents.find(a => a.id === selectedAgent);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Create</h1>
        <p className="text-gray-500 text-sm mt-1">Start a new task with your agents</p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-1 mb-6">
        {(['single', 'team'] as Mode[]).map(m => (
          <button
            key={m}
            onClick={() => { setMode(m); setSelectedAgent(null); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors ${
              mode === m
                ? 'bg-violet-600 text-white'
                : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {m === 'single' ? 'Single agent' : 'Agent team'}
          </button>
        ))}
        {mode === 'team' && (
          <Link
            href="/dashboard/team"
            className="ml-2 px-4 py-2 rounded-xl text-xs font-medium text-violet-400 hover:text-violet-300 bg-violet-500/10 border border-violet-500/20 transition-colors"
          >
            Build a team →
          </Link>
        )}
      </div>

      {/* Category filter */}
      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium mb-3">What do you need?</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          {CATEGORIES.map(cat => {
            if (cat.href) {
              return (
                <Link
                  key={cat.id}
                  href={cat.href}
                  className="bg-gray-900 border border-gray-800 hover:border-violet-500/40 rounded-xl px-3 py-2.5 flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-violet-300 transition-colors"
                >
                  <span className="opacity-60">{cat.icon}</span>
                  {cat.label}
                </Link>
              );
            }
            return (
              <button
                key={cat.id}
                onClick={() => setCategory(category === cat.id ? null : cat.id)}
                className={`bg-gray-900 border rounded-xl px-3 py-2.5 flex items-center gap-2 text-xs font-medium transition-colors text-left ${
                  category === cat.id
                    ? 'border-violet-500/50 text-violet-300 bg-violet-500/10'
                    : 'border-gray-800 text-gray-400 hover:text-white hover:border-gray-700'
                }`}
              >
                <span className={category === cat.id ? 'opacity-100' : 'opacity-50'}>{cat.icon}</span>
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Agent picker */}
      {mode === 'single' && (
        <div className="mb-6">
          <p className="text-xs text-gray-500 font-medium mb-3">
            Choose an agent {category && `(${filtered.length} in category)`}
          </p>
          {filtered.length === 0 ? (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl px-6 py-8 text-center">
              <p className="text-gray-500 text-sm mb-2">No agents in this category</p>
              <button onClick={() => setCategory(null)} className="text-xs text-violet-400 hover:text-violet-300 font-medium">
                Show all agents
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {filtered.map(agent => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                  className={`text-left bg-gray-900 border rounded-2xl px-4 py-3.5 transition-all ${
                    selectedAgent === agent.id
                      ? 'border-violet-500/50 bg-violet-500/5'
                      : 'border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{agent.name}</p>
                      <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">{agent.description}</p>
                    </div>
                    {selectedAgent === agent.id && (
                      <span className="shrink-0 w-4 h-4 rounded-full bg-violet-500 flex items-center justify-center text-[9px] text-white font-bold mt-0.5">✓</span>
                    )}
                  </div>
                  {agent.credit_estimate > 0 && (
                    <p className="text-[10px] text-gray-700 mt-2">~{agent.credit_estimate} credits</p>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Task input */}
      {(mode === 'team' || selectedAgent) && (
        <div className="mb-6">
          <label className="block text-xs text-gray-500 font-medium mb-2" htmlFor="task-input">
            Describe what you need
          </label>
          <textarea
            id="task-input"
            rows={5}
            value={task}
            onChange={e => setTask(e.target.value)}
            placeholder={
              mode === 'team'
                ? 'Describe your goal. Your agent team will coordinate to complete it.'
                : chosen
                ? `Tell ${chosen.name} what you need…`
                : 'Describe your task in detail…'
            }
            className="w-full bg-gray-900 border border-gray-800 focus:border-violet-500/50 rounded-2xl px-4 py-3 text-sm text-white placeholder-gray-700 outline-none resize-none transition-colors"
          />
          {task.length > 0 && task.length < 20 && (
            <p className="text-[10px] text-amber-400 mt-1.5">Add more detail for better results</p>
          )}
        </div>
      )}

      {/* Credit estimate */}
      {chosen && selectedAgent && (
        <div className="mb-5 bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 font-medium">{chosen.name}</p>
            {chosen.credit_estimate > 0 && (
              <p className="text-[10px] text-gray-600 mt-0.5">~{chosen.credit_estimate} credits estimated</p>
            )}
          </div>
          <button
            onClick={() => setSelectedAgent(null)}
            className="text-xs text-gray-600 hover:text-gray-400"
          >
            Change
          </button>
        </div>
      )}

      {error && (
        <div className="mb-5 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Submit */}
      <div className="flex items-center gap-3">
        <button
          onClick={submit}
          disabled={submitting || !task.trim() || (mode === 'single' && !selectedAgent)}
          className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl text-sm font-semibold transition-colors"
        >
          {submitting ? 'Starting…' : 'Start task'}
        </button>
        {mode === 'team' && !selectedAgent && (
          <p className="text-xs text-gray-600">Team coordinator will assign agents automatically</p>
        )}
      </div>
    </div>
  );
}
