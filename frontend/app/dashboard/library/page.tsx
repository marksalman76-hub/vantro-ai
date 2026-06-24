'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { SkeletonTable } from '@/components/Skeleton';

interface Job {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  credits_used: number;
  output: string | null;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
}

interface JobsResponse {
  jobs: Job[];
  total: number;
}

const PAGE_SIZE = 20;

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

const STATUS_STYLES: Record<string, string> = {
  'Waiting to start':    'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  'In progress':         'text-blue-400 bg-blue-500/10 border-blue-500/20',
  'Needs your approval': 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  'Ready':               'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  'Could not complete':  'text-red-400 bg-red-500/10 border-red-500/20',
  'Cancelled':           'text-gray-500 bg-gray-700/20 border-gray-700',
  'Not approved':        'text-red-400 bg-red-500/10 border-red-500/20',
};

type DateRange = '7d' | '30d' | '90d' | 'all';

const DATE_RANGE_LABELS: Record<DateRange, string> = {
  '7d':  'Last 7 days',
  '30d': 'Last 30 days',
  '90d': 'Last 90 days',
  'all': 'All time',
};

function isWithinRange(dateStr: string | null, range: DateRange): boolean {
  if (range === 'all') return true;
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const now = Date.now();
  const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
  return now - d.getTime() <= days * 86400 * 1000;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handle = () => {
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };
  return (
    <button
      onClick={handle}
      className="text-xs text-gray-500 hover:text-white border border-gray-700 hover:border-gray-600 rounded-lg px-2.5 py-1 transition-colors"
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

function JobCard({ job }: { job: Job }) {
  const [expanded, setExpanded] = useState(false);
  const preview = job.output ? job.output.slice(0, 200) : null;
  const hasMore = job.output && job.output.length > 200;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-colors">
      <div
        className="px-5 py-4 flex items-start gap-4 cursor-pointer"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            <p className="text-sm font-semibold text-white truncate">{job.agent_name}</p>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${
                STATUS_STYLES[CLIENT_STATUS[job.status]] || 'text-gray-400 bg-gray-800 border-gray-700'
              }`}
            >
              {CLIENT_STATUS[job.status] || 'In progress'}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-600">
            <span>{job.created_at ? new Date(job.created_at).toLocaleString() : '—'}</span>
            {job.credits_used > 0 && <span>{job.credits_used} credits</span>}
          </div>
          {!expanded && preview && (
            <p className="text-xs text-gray-500 mt-2 leading-relaxed line-clamp-2">
              {preview}{hasMore ? '…' : ''}
            </p>
          )}
          {!expanded && job.status === 'failed' && job.error_message && (
            <p className="text-xs text-red-400/70 mt-2 line-clamp-1">{job.error_message}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0 pt-0.5">
          <span className="text-gray-600 text-xs">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {expanded && (
        <div className="px-5 pb-4 border-t border-gray-800/60">
          <div className="mt-4">
            {job.status === 'failed' ? (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                <p className="text-red-400 text-sm font-medium mb-1">Could not complete</p>
                <p className="text-red-400/70 text-xs mb-3">
                  We couldn&apos;t complete this request. Your credits were not charged, were refunded, or are under review.
                </p>
                <div className="flex gap-2">
                  <a href="/dashboard/support" className="text-xs text-violet-400 hover:text-violet-300 font-medium">Contact support</a>
                  <span className="text-gray-700">·</span>
                  <a href="/dashboard/billing" className="text-xs text-gray-400 hover:text-gray-300">Review credits</a>
                </div>
              </div>
            ) : job.status === 'pending_financial_review' || job.status === 'pending_approval' ? (
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4">
                <p className="text-orange-400 text-sm font-medium mb-1">Needs your approval</p>
                <p className="text-orange-400/70 text-xs mb-3">This task is waiting for review before we continue.</p>
                <a href="/dashboard/approvals" className="text-xs text-orange-400 hover:text-orange-300 font-medium">Review now →</a>
              </div>
            ) : job.output ? (
              <div className="space-y-1">
                {job.output.split('\n').map((line, i) => {
                  if (/^#{1,3}\s/.test(line)) return <p key={i} className="font-bold text-white text-sm mt-4 mb-1">{line.replace(/^#+\s/, '')}</p>;
                  if (/^[-*]\s|^\d+\.\s/.test(line)) return <p key={i} className="text-gray-300 text-sm ml-3 leading-relaxed">{line}</p>;
                  if (!line.trim()) return <div key={i} className="h-2" />;
                  return <p key={i} className="text-gray-300 text-sm leading-relaxed">{line}</p>;
                })}
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No output available.</p>
            )}
          </div>
          <div className="flex items-center gap-2 mt-4">
            {job.output && <CopyButton text={job.output} />}
            <Link
              href={`/dashboard/agents?agent=${job.agent_id}`}
              className="text-xs text-violet-400 hover:text-violet-300 border border-violet-500/30 hover:border-violet-500/50 rounded-lg px-2.5 py-1 transition-colors"
              onClick={e => e.stopPropagation()}
            >
              Run again →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LibraryPage() {
  const router = useRouter();

  // All fetched jobs (up to 200 at once for client-side filtering)
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);

  // Filters
  const [search, setSearch] = useState('');
  const [agentFilter, setAgentFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateRange, setDateRange] = useState<DateRange>('all');

  const fetchJobs = useCallback(async (skip: number) => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    setLoading(true);
    try {
      const res = await fetch(`/api/agents/jobs?skip=${skip}&limit=200`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Fetch failed');
      const data: JobsResponse = await res.json();
      setAllJobs(data.jobs || []);
      setTotal(data.total || data.jobs?.length || 0);
    } catch {
      // silently fail — user sees empty state
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchJobs(0);
  }, [fetchJobs]);

  // Unique agent names for dropdown
  const agentOptions = Array.from(
    new Map(allJobs.map(j => [j.agent_id, j.agent_name])).entries()
  ).sort((a, b) => a[1].localeCompare(b[1]));

  const statusOptions = [
    'completed',
    'failed',
    'pending_financial_review',
    'pending_approval',
    'pending',
    'cancelled',
  ];

  // Apply filters
  const filtered = allJobs.filter(job => {
    if (agentFilter && job.agent_id !== agentFilter) return false;
    if (statusFilter && job.status !== statusFilter) return false;
    if (!isWithinRange(job.created_at, dateRange)) return false;
    if (search && !job.agent_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // Pagination on filtered results
  const pageCount = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  // Reset to page 0 when filters change
  const handleFilterChange = (fn: () => void) => {
    fn();
    setPage(0);
  };

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Output Library</h1>
        <p className="text-gray-500 text-sm">Browse, search, and copy all past agent outputs</p>
      </div>

      {/* Filters */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-6">
        <div className="flex flex-wrap gap-3">
          {/* Search */}
          <div className="flex-1 min-w-48">
            <input
              type="text"
              placeholder="Search by agent name…"
              value={search}
              onChange={e => handleFilterChange(() => setSearch(e.target.value))}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
            />
          </div>

          {/* Agent filter */}
          <select
            value={agentFilter}
            onChange={e => handleFilterChange(() => setAgentFilter(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
          >
            <option value="">All agents</option>
            {agentOptions.map(([id, name]) => (
              <option key={id} value={id}>{name}</option>
            ))}
          </select>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={e => handleFilterChange(() => setStatusFilter(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
          >
            <option value="">All statuses</option>
            {statusOptions.map(s => (
              <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
            ))}
          </select>

          {/* Date range */}
          <select
            value={dateRange}
            onChange={e => handleFilterChange(() => setDateRange(e.target.value as DateRange))}
            className="bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
          >
            {(Object.entries(DATE_RANGE_LABELS) as [DateRange, string][]).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
        <p className="text-xs text-gray-600 mt-3">
          {filtered.length} result{filtered.length !== 1 ? 's' : ''}
          {total > allJobs.length ? ` (showing latest ${allJobs.length} of ${total} total)` : ''}
        </p>
      </div>

      {/* Job list */}
      {loading ? (
        <SkeletonTable rows={5} />
      ) : paginated.length === 0 ? (
        <div className="text-center py-24">
          <p className="text-gray-400 text-lg font-semibold mb-2">
            {allJobs.length === 0
              ? 'No agent outputs yet. Run your first agent.'
              : 'No results match your filters.'}
          </p>
          {allJobs.length === 0 ? (
            <Link
              href="/dashboard/agents"
              className="inline-block mt-4 bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors"
            >
              Run your first agent →
            </Link>
          ) : (
            <button
              onClick={() => {
                setSearch('');
                setAgentFilter('');
                setStatusFilter('');
                setDateRange('all');
                setPage(0);
              }}
              className="mt-4 text-sm text-violet-400 hover:text-violet-300"
            >
              Clear all filters
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {paginated.map(job => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          {/* Pagination */}
          {pageCount > 1 && (
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                ← Previous
              </button>
              <p className="text-xs text-gray-500">
                Page {page + 1} of {pageCount}
              </p>
              <button
                onClick={() => setPage(p => Math.min(pageCount - 1, p + 1))}
                disabled={page >= pageCount - 1}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
