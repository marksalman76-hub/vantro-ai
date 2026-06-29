'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface AgentJob {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  hitl_level: string;
  input_data: string;
  credits_used: number;
  error_message: string | null;
  created_at: string;
  workspace_id: string;
  client_email?: string;
}

const HITL_RISK: Record<string, 'high' | 'medium' | 'low'> = {
  '3': 'high', '2': 'medium', '1': 'low', '0': 'low',
};
const RISK_STYLE: Record<string, string> = {
  high:   'text-red-400 bg-red-500/10 border-red-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};
const STATUS_STYLE: Record<string, string> = {
  pending_approval:         'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  pending_financial_review: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  approved:                 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  rejected:                 'text-red-400 bg-red-500/10 border-red-500/20',
};

export default function AdminApprovalsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<AgentJob[]>([]);
  const [filter, setFilter] = useState<'pending_approval' | 'pending_financial_review' | 'approved' | 'rejected' | 'all'>('pending_approval');
  const [expandedOutput, setExpandedOutput] = useState<string | null>(null);
  const [acting, setActing] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<Record<string, string>>({});
  const [showRejectInput, setShowRejectInput] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApprovals = useCallback(async () => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin-login'); return; }
    try {
      // Fetch both pending_approval (pre-execution) and pending_financial_review (post-execution)
      const [r1, r2] = await Promise.all([
        fetch('/api/admin/agents/jobs?status=pending_approval&limit=100', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/admin/agents/jobs?status=pending_financial_review&limit=100', { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (!r1.ok || !r2.ok) throw new Error('Failed to load approvals');
      const [d1, d2] = await Promise.all([r1.json(), r2.json()]);
      setJobs([...(d1.jobs ?? []), ...(d2.jobs ?? [])]);
      setError(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 10_000);
    return () => clearInterval(interval);
  }, [fetchApprovals]);

  const approve = async (jobId: string) => {
    const token = localStorage.getItem('admin_token');
    setActing(jobId);
    try {
      const res = await fetch(`/api/admin/agents/jobs/${jobId}/approve`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (!res.ok) throw new Error('Approve failed');
      await fetchApprovals();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Approve failed');
    } finally {
      setActing(null);
    }
  };

  const reject = async (jobId: string) => {
    const token = localStorage.getItem('admin_token');
    const reason = rejectReason[jobId] || '';
    setActing(jobId);
    try {
      const res = await fetch(`/api/admin/agents/jobs/${jobId}/reject`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      if (!res.ok) throw new Error('Reject failed');
      setShowRejectInput(null);
      setRejectReason(r => { const c = { ...r }; delete c[jobId]; return c; });
      await fetchApprovals();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Reject failed');
    } finally {
      setActing(null);
    }
  };

  const visible = filter === 'all' ? jobs : jobs.filter(j => j.status === filter);
  const pending  = jobs.filter(j => j.status === 'pending_approval').length;
  const finReview = jobs.filter(j => j.status === 'pending_financial_review').length;

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold text-white">Approvals</h1>
          {pending > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{pending}</span>
          )}
        </div>
        <p className="text-gray-500 text-sm">All spend, scaling, provider, and financial actions requiring human approval before release</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{error}</div>
      )}

      {finReview > 0 && (
        <div className="mb-4 bg-orange-950/50 border border-orange-600 rounded-xl px-4 py-3">
          <p className="text-orange-300 text-sm font-semibold">
            ⚠ {finReview} agent output{finReview !== 1 ? 's' : ''} held for financial review
          </p>
          <p className="text-orange-400/70 text-xs mt-0.5">
            An agent produced output containing financial-action language. Review the output below before releasing it to the client.
          </p>
        </div>
      )}

      <div className="flex flex-wrap gap-2 mb-6">
        {(['pending_approval', 'pending_financial_review', 'approved', 'rejected', 'all'] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${filter === f ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
            {f === 'pending_approval'
              ? `pre-execution${pending > 0 ? ` (${pending})` : ''}`
              : f === 'pending_financial_review'
              ? `financial review${finReview > 0 ? ` (${finReview})` : ''}`
              : f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-5 animate-pulse h-24"/>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {visible.length === 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 text-center text-gray-600 text-sm">
              No {filter === 'pending_approval' ? 'pending' : filter} approvals.
            </div>
          )}
          {visible.map(job => {
            const risk = HITL_RISK[String(job.hitl_level)] ?? 'medium';
            return (
              <div key={job.id} className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
                <div className="flex items-start gap-5">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-2">
                      <span className="text-xs font-mono text-gray-600">{job.id.slice(0, 8)}…</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${STATUS_STYLE[job.status] ?? ''}`}>
                        {job.status.replace('_', ' ')}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${RISK_STYLE[risk]}`}>
                        HITL {job.hitl_level} · {risk} risk
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-gray-800 border border-gray-700 text-gray-400">
                        {job.credits_used} credits
                      </span>
                    </div>
                    <p className="text-white text-sm font-medium mb-0.5">{job.agent_name || job.agent_id}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                      {job.client_email && <span>Client: <span className="text-gray-300">{job.client_email}</span></span>}
                      <span>{new Date(job.created_at).toLocaleString()}</span>
                    </div>
                    {job.input_data && (
                      <p className="text-gray-600 text-xs mt-1 truncate max-w-lg">{job.input_data.slice(0, 120)}</p>
                    )}
                  </div>
                  {(job.status === 'pending_approval' || job.status === 'pending_financial_review') && (
                    <div className="flex gap-2 shrink-0">
                      {job.status === 'pending_financial_review' && (
                        <button
                          onClick={() => setExpandedOutput(expandedOutput === job.id ? null : job.id)}
                          className="px-3 py-2 rounded-lg text-xs font-semibold bg-orange-600/20 border border-orange-500/30 text-orange-400 hover:bg-orange-600/30 transition-colors">
                          {expandedOutput === job.id ? 'Hide output' : 'Review output'}
                        </button>
                      )}
                      <button onClick={() => approve(job.id)} disabled={acting === job.id}
                        className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white transition-colors">
                        {acting === job.id ? '…' : job.status === 'pending_financial_review' ? 'Release to client' : 'Approve'}
                      </button>
                      <button onClick={() => setShowRejectInput(showRejectInput === job.id ? null : job.id)}
                        disabled={acting === job.id}
                        className="px-4 py-2 rounded-lg text-xs font-semibold bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 text-red-400 transition-colors">
                        Reject
                      </button>
                    </div>
                  )}
                </div>
                {/* Financial review: show agent output so admin can verify it's suggestion-only */}
                {expandedOutput === job.id && job.status === 'pending_financial_review' && (
                  <div className="mt-3 bg-orange-950/30 border border-orange-700 rounded-xl p-4">
                    <p className="text-xs font-bold text-orange-400 mb-2">
                      ⚠ Agent output held for financial review — verify this is a suggestion, not an execution
                    </p>
                    <div className="bg-gray-950 rounded-lg p-3 max-h-60 overflow-y-auto">
                      <pre className="text-xs text-gray-300 whitespace-pre-wrap">{(job as any).output_data?.replace(/^<!-- provider:.*? -->\n/, '') ?? 'Output not available'}</pre>
                    </div>
                    <p className="text-xs text-orange-400/70 mt-2">
                      If this output recommends a financial action for the owner to consider (not executes one), click "Release to client".
                      If it attempts to authorise, commit, or execute a financial action, click "Reject".
                    </p>
                  </div>
                )}

                {showRejectInput === job.id && (
                  <div className="mt-3 flex gap-2">
                    <input
                      type="text"
                      placeholder="Reason for rejection (optional)"
                      value={rejectReason[job.id] ?? ''}
                      onChange={e => setRejectReason(r => ({ ...r, [job.id]: e.target.value }))}
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500"
                    />
                    <button onClick={() => reject(job.id)} disabled={acting === job.id}
                      className="px-4 py-2 rounded-lg text-xs font-semibold bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white">
                      {acting === job.id ? '…' : 'Confirm reject'}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
