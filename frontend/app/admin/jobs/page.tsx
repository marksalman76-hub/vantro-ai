'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Job {
  id: string;
  status: string;
  script: string | null;
  video_url: string | null;
  error_message: string | null;
  external_job_id: string | null;
  avatar_id: string;
  created_at: string | null;
  completed_at: string | null;
  client_id: string | null;
  client_email: string;
  client_name: string | null;
  workspace: string | null;
}

const STATUS_STYLE: Record<string, string> = {
  completed:  'bg-green-400/10 text-green-400',
  processing: 'bg-yellow-400/10 text-yellow-400',
  pending:    'bg-blue-400/10 text-blue-400',
  failed:     'bg-red-400/10 text-red-400',
  cancelled:  'bg-gray-700 text-gray-400',
};

const STATUSES = ['all', 'pending', 'processing', 'completed', 'failed', 'cancelled'] as const;
type StatusFilter = typeof STATUSES[number];

export default function AdminJobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [search, setSearch] = useState('');
  const [actionLoading, setActionLoading] = useState<string>('');
  const [message, setMessage] = useState('');

  const getToken = () => localStorage.getItem('admin_token') || '';

  function load() {
    const token = getToken();
    if (!token) { router.push('/admin-login'); return; }
    fetch('/api/admin/jobs', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        const d = await r.json();
        setJobs(d.jobs || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function jobAction(jobId: string, action: 'retry' | 'cancel') {
    setActionLoading(`${action}-${jobId}`);
    try {
      const res = await fetch(`/api/admin/jobs/${jobId}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (res.ok) {
        setMessage(`Job ${action === 'retry' ? 'requeued' : 'cancelled'}`);
        load();
      }
    } finally {
      setActionLoading('');
    }
  }

  const filtered = jobs.filter((j) => {
    const matchStatus = statusFilter === 'all' || j.status === statusFilter;
    const matchSearch =
      j.client_email.toLowerCase().includes(search.toLowerCase()) ||
      (j.client_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (j.script || '').toLowerCase().includes(search.toLowerCase()) ||
      j.id.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const counts: Record<string, number> = { all: jobs.length };
  for (const j of jobs) counts[j.status] = (counts[j.status] || 0) + 1;

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Jobs & Executions</h1>
        <p className="text-gray-500 text-sm mt-1">{jobs.length} total jobs</p>
      </div>

      {message && (
        <div className="mb-4 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-2.5 flex items-center justify-between">
          <p className="text-green-400 text-sm">{message}</p>
          <button onClick={() => setMessage('')} className="text-green-400/60 hover:text-green-400">×</button>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by client, script, or job ID…"
          className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 w-80"
        />
        <div className="flex gap-1 flex-wrap">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
                statusFilter === s
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {s} {counts[s] !== undefined ? `(${counts[s]})` : ''}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              {['Client', 'Script', 'Status', 'Created', 'Completed', 'Actions'].map((h) => (
                <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((j) => (
              <tr key={j.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                <td className="px-5 py-3">
                  {j.client_id ? (
                    <Link href={`/admin/clients/${j.client_id}`} className="text-violet-400 hover:text-violet-300 text-xs">
                      {j.client_email}
                    </Link>
                  ) : (
                    <span className="text-gray-400 text-xs">{j.client_email}</span>
                  )}
                  {j.client_name && <p className="text-gray-600 text-xs">{j.client_name}</p>}
                </td>
                <td className="px-5 py-3 max-w-xs">
                  <p className="text-gray-300 text-xs truncate">{j.script || '—'}</p>
                  {j.error_message && (
                    <p className="text-red-400 text-xs truncate mt-0.5" title={j.error_message}>
                      ⚠ {j.error_message}
                    </p>
                  )}
                </td>
                <td className="px-5 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_STYLE[j.status] || 'bg-gray-700 text-gray-400'}`}>
                    {j.status}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-500 text-xs">
                  {j.created_at ? new Date(j.created_at).toLocaleDateString('en-GB') : '—'}
                </td>
                <td className="px-5 py-3 text-gray-500 text-xs">
                  {j.completed_at ? new Date(j.completed_at).toLocaleDateString('en-GB') : '—'}
                </td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    {j.video_url && (
                      <a href={j.video_url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:text-blue-300">
                        Watch
                      </a>
                    )}
                    {(j.status === 'failed' || j.status === 'cancelled') && (
                      <button
                        onClick={() => jobAction(j.id, 'retry')}
                        disabled={actionLoading === `retry-${j.id}`}
                        className="text-xs text-green-400 hover:text-green-300 disabled:opacity-50"
                      >
                        {actionLoading === `retry-${j.id}` ? '…' : 'Retry'}
                      </button>
                    )}
                    {(j.status === 'pending' || j.status === 'processing') && (
                      <button
                        onClick={() => jobAction(j.id, 'cancel')}
                        disabled={actionLoading === `cancel-${j.id}`}
                        className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50"
                      >
                        {actionLoading === `cancel-${j.id}` ? '…' : 'Cancel'}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-gray-600">No jobs match your filter.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
