'use client';
import { useState, useEffect } from 'react';

interface AdminReport {
  id: string;
  workspace_id: string;
  reporting_period_start: string;
  reporting_period_end: string;
  executive_summary: string;
  sections: any[];
  status: string;
  delivery_status: string;
  email_sent_at: string | null;
  email_recipients: string[];
  created_at: string;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    sent: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
    generated: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
    pending: 'bg-amber-400/10 text-amber-400 border-amber-400/20',
    failed: 'bg-red-400/10 text-red-400 border-red-400/20',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${map[status] || 'bg-gray-800 text-gray-400 border-gray-700'}`}>
      {status}
    </span>
  );
}

export default function AdminReportsPage() {
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<AdminReport | null>(null);
  const [filterWs, setFilterWs] = useState('');
  const [wsFilter, setWsFilter] = useState('');
  const [generating, setGenerating] = useState('');
  const [actionMsg, setActionMsg] = useState('');
  const PAGE_SIZE = 20;

  async function fetchReports() {
    setLoading(true);
    try {
      const qs = wsFilter ? `&workspace_id=${encodeURIComponent(wsFilter)}` : '';
      const res = await fetch(`/api/admin/reports/weekly?skip=${skip}&limit=${PAGE_SIZE}${qs}`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setReports(data.reports || []);
        setTotal(data.total || 0);
      }
    } catch {}
    setLoading(false);
  }

  useEffect(() => { fetchReports(); }, [skip, wsFilter]);

  async function handleResend(reportId: string) {
    setActionMsg('');
    const res = await fetch(`/api/admin/reports/weekly/${reportId}/resend`, { method: 'POST', credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      setActionMsg(`Sent to ${(data.recipients || []).join(', ')}`);
      fetchReports();
    } else {
      const err = await res.json().catch(() => ({}));
      setActionMsg(err.detail || 'Failed to resend');
    }
  }

  async function handleDisable(reportId: string) {
    const res = await fetch(`/api/admin/reports/weekly/${reportId}/disable`, { method: 'POST', credentials: 'include' });
    if (res.ok) {
      setActionMsg('Report disabled');
      fetchReports();
    }
  }

  async function handleGenerateForWs(workspaceId: string) {
    setGenerating(workspaceId);
    const res = await fetch(`/api/admin/reports/weekly/generate/${workspaceId}`, { method: 'POST', credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      setActionMsg(`Report generated: ${data.report_id} (${data.sections} agent sections)`);
      fetchReports();
    } else {
      const err = await res.json().catch(() => ({}));
      setActionMsg(err.detail || 'Failed to generate');
    }
    setGenerating('');
  }

  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Client Reports</h1>
            <p className="text-gray-400 text-sm mt-1">Manage weekly AI workforce reports across all clients</p>
          </div>
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Filter by workspace ID..."
              value={filterWs}
              onChange={e => setFilterWs(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && setWsFilter(filterWs)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 w-52"
            />
            <button
              onClick={() => setWsFilter(filterWs)}
              className="bg-gray-700 hover:bg-gray-600 text-white text-sm px-3 py-2 rounded-lg transition-colors"
            >
              Filter
            </button>
          </div>
        </div>

        {actionMsg && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 mb-4 text-sm text-gray-200 flex items-center justify-between">
            <span>{actionMsg}</span>
            <button onClick={() => setActionMsg('')} className="text-gray-500 hover:text-white ml-4">✕</button>
          </div>
        )}

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-4">
            <p className="text-2xl font-bold text-white">{total}</p>
            <p className="text-xs text-gray-500 mt-0.5">Total reports</p>
          </div>
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-4">
            <p className="text-2xl font-bold text-emerald-400">{reports.filter(r => r.delivery_status === 'sent').length}</p>
            <p className="text-xs text-gray-500 mt-0.5">Sent this page</p>
          </div>
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-4">
            <p className="text-2xl font-bold text-amber-400">{reports.filter(r => r.delivery_status !== 'sent').length}</p>
            <p className="text-xs text-gray-500 mt-0.5">Not yet sent</p>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Table */}
          <div className="flex-1 min-w-0">
            {loading ? (
              <div className="space-y-3">
                {[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-gray-800 rounded-xl animate-pulse" />)}
              </div>
            ) : reports.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <p className="text-4xl mb-3">📭</p>
                <p>No reports found</p>
                {wsFilter && (
                  <button onClick={() => { setWsFilter(''); setFilterWs(''); }} className="text-violet-400 text-sm mt-2 hover:underline">
                    Clear filter
                  </button>
                )}
              </div>
            ) : (
              <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-xs text-gray-500">
                      <th className="text-left px-4 py-3">Period</th>
                      <th className="text-left px-4 py-3">Workspace</th>
                      <th className="text-left px-4 py-3">Status</th>
                      <th className="text-left px-4 py-3">Agents</th>
                      <th className="text-left px-4 py-3">Created</th>
                      <th className="text-left px-4 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map(r => (
                      <tr
                        key={r.id}
                        className={`border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors ${selected?.id === r.id ? 'bg-gray-800/70' : ''}`}
                        onClick={() => setSelected(selected?.id === r.id ? null : r)}
                      >
                        <td className="px-4 py-3 text-white">
                          {formatDate(r.reporting_period_start)} – {formatDate(r.reporting_period_end)}
                        </td>
                        <td className="px-4 py-3 text-gray-400 font-mono text-xs">{r.workspace_id.slice(0, 8)}…</td>
                        <td className="px-4 py-3"><StatusBadge status={r.delivery_status || r.status} /></td>
                        <td className="px-4 py-3 text-gray-400">{(r.sections || []).filter((s: any) => s.total_jobs > 0).length}</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">{formatDate(r.created_at)}</td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                            <button
                              onClick={() => handleResend(r.id)}
                              className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                            >
                              Resend
                            </button>
                            <span className="text-gray-700">·</span>
                            <button
                              onClick={() => handleDisable(r.id)}
                              className="text-xs text-red-400 hover:text-red-300 transition-colors"
                            >
                              Disable
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Pagination */}
                <div className="flex items-center justify-between px-4 py-3 border-t border-gray-700">
                  <span className="text-xs text-gray-500">
                    {skip + 1}–{Math.min(skip + PAGE_SIZE, total)} of {total}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}
                      disabled={skip === 0}
                      className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 text-gray-400 hover:text-white disabled:opacity-30 transition-colors"
                    >
                      ← Prev
                    </button>
                    <button
                      onClick={() => setSkip(skip + PAGE_SIZE)}
                      disabled={skip + PAGE_SIZE >= total}
                      className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 text-gray-400 hover:text-white disabled:opacity-30 transition-colors"
                    >
                      Next →
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Detail panel */}
          {selected && (
            <div className="w-80 shrink-0">
              <div className="bg-gray-900 rounded-xl border border-gray-700 p-5 sticky top-6">
                <div className="flex items-start justify-between mb-4">
                  <p className="font-semibold text-white text-sm">Report Detail</p>
                  <button onClick={() => setSelected(null)} className="text-gray-500 hover:text-white text-xs">✕</button>
                </div>

                <dl className="space-y-2 text-xs mb-4">
                  <div className="flex justify-between">
                    <dt className="text-gray-500">ID</dt>
                    <dd className="text-gray-300 font-mono">{selected.id.slice(0, 8)}…</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Workspace</dt>
                    <dd className="text-gray-300 font-mono">{selected.workspace_id.slice(0, 8)}…</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Period</dt>
                    <dd className="text-gray-300">{formatDate(selected.reporting_period_start)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Status</dt>
                    <dd><StatusBadge status={selected.delivery_status || selected.status} /></dd>
                  </div>
                  {selected.email_sent_at && (
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Sent at</dt>
                      <dd className="text-gray-300">{formatDate(selected.email_sent_at)}</dd>
                    </div>
                  )}
                  {selected.email_recipients?.length > 0 && (
                    <div>
                      <dt className="text-gray-500 mb-1">Recipients</dt>
                      <dd className="text-gray-300 break-all">{selected.email_recipients.join(', ')}</dd>
                    </div>
                  )}
                </dl>

                <p className="text-xs text-gray-500 mb-2">Executive summary</p>
                <p className="text-xs text-gray-300 leading-relaxed mb-4">{selected.executive_summary}</p>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleResend(selected.id)}
                    className="w-full text-xs bg-violet-600 hover:bg-violet-500 text-white py-2 rounded-lg font-semibold transition-colors"
                  >
                    Resend email
                  </button>
                  <button
                    onClick={() => handleGenerateForWs(selected.workspace_id)}
                    disabled={!!generating}
                    className="w-full text-xs bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white py-2 rounded-lg font-semibold transition-colors"
                  >
                    {generating === selected.workspace_id ? 'Generating...' : 'Generate new report'}
                  </button>
                  <button
                    onClick={() => handleDisable(selected.id)}
                    className="w-full text-xs text-red-400 hover:text-red-300 py-2 transition-colors"
                  >
                    Disable this report
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
