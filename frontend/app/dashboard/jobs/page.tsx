'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Job {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  hitl_level: string;
  credits_used: number;
  output: string | null;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
}

// Client-safe status labels — never expose internal status names
const CLIENT_STATUS: Record<string, string> = {
  pending:                  'Waiting to start',
  queued:                   'Waiting to start',
  running:                  'In progress',
  processing:               'In progress',
  approved:                 'In progress',
  pending_approval:         'Needs your approval',
  pending_financial_review: 'Needs your approval',
  completed:                'Ready',
  failed:                   'Could not complete',
  cancelled:                'Cancelled',
  rejected:                 'Not approved',
};

const CLIENT_STATUS_STYLE: Record<string, string> = {
  'Waiting to start':    'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  'In progress':         'text-blue-400 bg-blue-500/10 border-blue-500/20',
  'Needs your approval': 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  'Ready':               'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  'Could not complete':  'text-red-400 bg-red-500/10 border-red-500/20',
  'Cancelled':           'text-gray-500 bg-gray-700/20 border-gray-700',
  'Not approved':        'text-red-400 bg-red-500/10 border-red-500/20',
};

type Filter = 'all' | 'active' | 'ready' | 'approval' | 'failed';

const FILTER_LABELS: Record<Filter, string> = {
  all:      'All',
  active:   'In progress',
  ready:    'Ready',
  approval: 'Needs approval',
  failed:   'Could not complete',
};

function matchesFilter(status: string, filter: Filter): boolean {
  const cs = CLIENT_STATUS[status] || status;
  if (filter === 'all') return true;
  if (filter === 'active') return cs === 'In progress' || cs === 'Waiting to start';
  if (filter === 'ready') return cs === 'Ready';
  if (filter === 'approval') return cs === 'Needs your approval';
  if (filter === 'failed') return cs === 'Could not complete';
  return true;
}

export default function ActivityJobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>('all');
  const [expandedFailed, setExpandedFailed] = useState<string | null>(null);
  const [retrying, setRetrying] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    try {
      const res = await fetch('/api/agents/jobs?skip=0&limit=200', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await res.json();
      setJobs(d.jobs || []);
    } catch {}
    finally { setLoading(false); }
  }, [router]);

  useEffect(() => { load(); }, [load]);

  async function retry(jobId: string) {
    const token = localStorage.getItem('token');
    if (!token) return;
    setRetrying(jobId);
    try {
      await fetch(`/api/agents/jobs/${jobId}/retry`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage('Request resubmitted. Check back shortly.');
      load();
    } catch {
      setMessage('Could not retry. Please contact support.');
    } finally {
      setRetrying(null);
    }
  }

  const filtered = jobs.filter(j => matchesFilter(j.status, filter));

  const counts = {
    approval: jobs.filter(j => CLIENT_STATUS[j.status] === 'Needs your approval').length,
    failed:   jobs.filter(j => CLIENT_STATUS[j.status] === 'Could not complete').length,
    active:   jobs.filter(j => CLIENT_STATUS[j.status] === 'In progress' || CLIENT_STATUS[j.status] === 'Waiting to start').length,
  };

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Activity</h1>
        <p className="text-gray-500 text-sm mt-1">Track all your agent tasks and requests</p>
      </div>

      {message && (
        <div className="mb-5 bg-blue-500/10 border border-blue-500/20 rounded-2xl px-4 py-3 flex items-center justify-between">
          <p className="text-blue-300 text-sm">{message}</p>
          <button onClick={() => setMessage('')} className="text-blue-400/60 hover:text-blue-400 text-lg">×</button>
        </div>
      )}

      {/* Status summary */}
      {(counts.approval > 0 || counts.failed > 0) && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          {counts.approval > 0 && (
            <button
              onClick={() => setFilter('approval')}
              className="bg-orange-500/10 border border-orange-500/20 hover:border-orange-500/40 rounded-2xl p-4 text-left transition-colors"
            >
              <p className="text-orange-300 text-xs font-medium mb-1">Needs your approval</p>
              <p className="text-2xl font-bold text-orange-400">{counts.approval}</p>
              <p className="text-xs text-orange-300/60 mt-1">Tap to review</p>
            </button>
          )}
          {counts.failed > 0 && (
            <button
              onClick={() => setFilter('failed')}
              className="bg-red-500/10 border border-red-500/20 hover:border-red-500/40 rounded-2xl p-4 text-left transition-colors"
            >
              <p className="text-red-300 text-xs font-medium mb-1">Could not complete</p>
              <p className="text-2xl font-bold text-red-400">{counts.failed}</p>
              <p className="text-xs text-red-300/60 mt-1">Retry or get support</p>
            </button>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-1 flex-wrap mb-5">
        {(Object.keys(FILTER_LABELS) as Filter[]).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
              filter === f
                ? 'bg-violet-600 text-white'
                : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {FILTER_LABELS[f]}
            {f === 'approval' && counts.approval > 0 && (
              <span className="ml-1.5 bg-orange-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full">
                {counts.approval}
              </span>
            )}
          </button>
        ))}
        <span className="ml-auto text-xs text-gray-600 self-center">{filtered.length} tasks</span>
      </div>

      {/* Jobs list */}
      {filtered.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl px-6 py-16 text-center">
          <p className="text-gray-500 text-sm mb-3">No tasks match this filter</p>
          <Link href="/dashboard/create" className="text-xs text-violet-400 hover:text-violet-300 font-medium">
            Start a new task →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(job => {
            const cs = CLIENT_STATUS[job.status] || job.status;
            const isFailed = cs === 'Could not complete';
            const isReady = cs === 'Ready';
            const needsApproval = cs === 'Needs your approval';
            const isExpanded = expandedFailed === job.id;

            return (
              <div
                key={job.id}
                className={`bg-gray-900 rounded-2xl border transition-all ${
                  needsApproval ? 'border-orange-500/20' :
                  isFailed ? 'border-red-500/15' :
                  isReady ? 'border-emerald-500/15' :
                  'border-gray-800'
                }`}
              >
                <div className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1.5">
                        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                          CLIENT_STATUS_STYLE[cs] || 'text-gray-400 bg-gray-800 border-gray-700'
                        }`}>
                          {cs}
                        </span>
                        {job.credits_used > 0 && (
                          <span className="text-[10px] text-gray-600">{job.credits_used} credits</span>
                        )}
                      </div>
                      <p className="font-medium text-sm text-white">{job.agent_name}</p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        {job.created_at ? new Date(job.created_at).toLocaleString('en-GB') : '—'}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {isReady && job.output && (
                        <Link
                          href="/dashboard/assets"
                          className="px-3 py-1.5 text-xs text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded-xl font-medium transition-colors"
                        >
                          View output →
                        </Link>
                      )}
                      {needsApproval && (
                        <Link
                          href="/dashboard/approvals"
                          className="px-3 py-1.5 text-xs text-orange-400 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/20 rounded-xl font-medium transition-colors"
                        >
                          Review →
                        </Link>
                      )}
                      {isFailed && (
                        <button
                          onClick={() => setExpandedFailed(isExpanded ? null : job.id)}
                          className="text-xs text-gray-400 hover:text-gray-300"
                        >
                          {isExpanded ? '▲' : '▼'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Failed job expansion */}
                {isFailed && isExpanded && (
                  <div className="border-t border-gray-800 px-5 pb-5 pt-4">
                    <div className="bg-red-500/5 border border-red-500/15 rounded-xl px-4 py-3 mb-4">
                      <p className="text-sm text-gray-300 leading-relaxed">
                        We couldn&apos;t complete this request. Your credits were not charged, were refunded, or are under review.
                      </p>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      <button
                        onClick={() => retry(job.id)}
                        disabled={retrying === job.id}
                        className="px-3 py-1.5 text-xs text-violet-400 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/20 rounded-xl font-medium transition-colors disabled:opacity-50"
                      >
                        {retrying === job.id ? 'Retrying…' : 'Try again'}
                      </button>
                      <Link
                        href="/dashboard/support"
                        className="px-3 py-1.5 text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl font-medium transition-colors"
                      >
                        Contact support
                      </Link>
                      <Link
                        href="/dashboard/billing"
                        className="px-3 py-1.5 text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl font-medium transition-colors"
                      >
                        Review credits
                      </Link>
                    </div>
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
