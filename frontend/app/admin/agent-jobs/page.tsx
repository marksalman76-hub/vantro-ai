'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface AgentJob {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  hitl_level: string;
  credits_used: number;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
  client_email: string;
  workspace: string | null;
}

const STATUS_COLOR: Record<string, string> = {
  pending:           'bg-gray-700/50    text-gray-400',
  pending_approval:  'bg-yellow-500/10  text-yellow-400',
  approved:          'bg-blue-500/10    text-blue-400',
  rejected:          'bg-red-500/10     text-red-400',
  processing:        'bg-purple-500/10  text-purple-400',
  completed:         'bg-green-500/10   text-green-400',
  failed:            'bg-red-500/20     text-red-400',
};

export default function AdminAgentJobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<AgentJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const load = () => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin/login'); return; }
    fetch('/api/admin/agents/jobs', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        const d = await r.json();
        setJobs(d.jobs || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [router]);

  const approve = async (jobId: string) => {
    const token = localStorage.getItem('admin_token');
    if (!token) return;
    setActionLoading(jobId + '_approve');
    await fetch(`/api/admin/agents/jobs/${jobId}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    setActionLoading(null);
    load();
  };

  const reject = async (jobId: string) => {
    const token = localStorage.getItem('admin_token');
    if (!token) return;
    setActionLoading(jobId + '_reject');
    await fetch(`/api/admin/agents/jobs/${jobId}/reject`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    setActionLoading(null);
    load();
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const pending = jobs.filter((j) => j.status === 'pending_approval');

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-7">
        <h1 className="text-2xl font-bold">Agent Jobs</h1>
        <p className="text-gray-500 text-sm mt-1">{jobs.length} total · {pending.length} awaiting approval</p>
      </div>

      {/* Pending approval section */}
      {pending.length > 0 && (
        <div className="mb-8">
          <p className="text-xs font-semibold text-yellow-500/70 uppercase tracking-widest mb-3">
            Awaiting Approval ({pending.length}) — HITL-3 spend gate
          </p>
          <div className="space-y-3">
            {pending.map((j) => (
              <div key={j.id} className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-sm text-white">{j.agent_name}</p>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                        {j.hitl_level}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{j.client_email} · {j.workspace}</p>
                    <p className="text-[10px] text-gray-600 mt-1">{j.id}</p>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => approve(j.id)}
                      disabled={actionLoading === j.id + '_approve'}
                      className="px-3 py-1.5 text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg hover:bg-green-500/20 disabled:opacity-40 transition-colors"
                    >
                      {actionLoading === j.id + '_approve' ? '…' : 'Approve'}
                    </button>
                    <button
                      onClick={() => reject(j.id)}
                      disabled={actionLoading === j.id + '_reject'}
                      className="px-3 py-1.5 text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-500/20 disabled:opacity-40 transition-colors"
                    >
                      {actionLoading === j.id + '_reject' ? '…' : 'Reject'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All jobs table */}
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">All Jobs</p>
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Agent</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">HITL</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Client</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Created</th>
              <th className="text-right px-4 py-3 text-xs text-gray-500 font-semibold">Credits</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id} className="border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors">
                <td className="px-4 py-3">
                  <p className="text-white text-xs font-medium">{j.agent_name}</p>
                  <p className="text-gray-600 text-[10px] font-mono">{j.agent_id}</p>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${STATUS_COLOR[j.status] || 'bg-gray-700 text-gray-400'}`}>
                    {j.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-400">{j.hitl_level}</td>
                <td className="px-4 py-3 text-xs text-gray-400">{j.client_email}</td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {j.created_at ? new Date(j.created_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3 text-xs text-gray-400 text-right">{j.credits_used}</td>
              </tr>
            ))}
            {jobs.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-gray-600 text-sm">No agent jobs yet</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
