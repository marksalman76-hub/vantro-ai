'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface SecurityAlert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  type: string;
  label: string;
  client_email: string;
  client_id: string | null;
  related_job_id: string | null;
  related_agent: string | null;
  status: 'open' | 'acknowledged';
  detail: string;
  detected_at: string | null;
}

const SEV_STYLE: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  high:     'bg-orange-500/15 text-orange-300 border-orange-500/30',
  medium:   'bg-yellow-500/15 text-yellow-300 border-yellow-500/30',
  low:      'bg-blue-500/10 text-blue-300 border-blue-500/30',
  info:     'bg-gray-700 text-gray-400 border-gray-600',
};

const SEV_DOT: Record<string, string> = {
  critical: 'bg-red-500',
  high:     'bg-orange-400',
  medium:   'bg-yellow-400',
  low:      'bg-blue-400',
  info:     'bg-gray-500',
};

const TYPE_ICONS: Record<string, string> = {
  agent_tamper:            '⚠',
  credential_attack:       '⚠',
  malicious_request:       '⛔',
  reverse_engineering:     '⛔',
  package_redeployment:    '⛔',
  financial_review_flagged:'◈',
  prompt_extraction:       '◉',
  suspicious_automation:   '◎',
  login_failed:            '◆',
  account_locked:          '▣',
  default:                 '◇',
};

export default function SecurityAlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('open');
  const [expanded, setExpanded] = useState<string | null>(null);

  const getToken = () => localStorage.getItem('admin_token') || '';

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) { router.push('/admin-login'); return; }
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (severityFilter) params.set('severity', severityFilter);
      if (statusFilter) params.set('status', statusFilter);
      params.set('limit', '100');
      const res = await fetch(`/api/admin/security/alerts?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await res.json();
      setAlerts(d.alerts || []);
      setTotal(d.total || 0);
    } catch {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, [router, severityFilter, statusFilter]);

  useEffect(() => { load(); }, [load]);

  async function acknowledge(alertId: string) {
    setActing(alertId);
    try {
      const res = await fetch(`/api/admin/security/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: '' }),
      });
      if (res.ok) {
        setMessage('Alert acknowledged');
        load();
      }
    } finally {
      setActing(null);
    }
  }

  async function lockAccount(alertId: string) {
    setActing(`lock_${alertId}`);
    try {
      const res = await fetch(`/api/admin/security/alerts/${alertId}/lock-account`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      const d = await res.json();
      if (res.ok) {
        setMessage(`Account locked: ${d.client_email}`);
        load();
      } else {
        setMessage(d.detail || 'Lock failed');
      }
    } finally {
      setActing(null);
    }
  }

  const severities = ['', 'critical', 'high', 'medium', 'low', 'info'];
  const statuses = ['open', 'acknowledged', ''];

  const counts = alerts.reduce((acc, a) => {
    acc[a.severity] = (acc[a.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Security Alerts</h1>
        <p className="text-gray-500 text-sm mt-1">
          Agent tamper attempts, reverse-engineering, malicious requests, and package abuse
        </p>
      </div>

      {message && (
        <div className="mb-5 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 flex items-center justify-between">
          <p className="text-green-400 text-sm">{message}</p>
          <button onClick={() => setMessage('')} className="text-green-400/60 hover:text-green-400">×</button>
        </div>
      )}

      {/* Summary chips */}
      <div className="flex gap-2 flex-wrap mb-6">
        {(['critical', 'high', 'medium', 'low'] as const).map((s) => (
          counts[s] ? (
            <span key={s} className={`text-xs font-semibold px-3 py-1 rounded-full border ${SEV_STYLE[s]}`}>
              {counts[s]} {s}
            </span>
          ) : null
        ))}
        {total === 0 && !loading && (
          <span className="text-xs text-gray-500 bg-gray-900 border border-gray-800 px-3 py-1 rounded-full">
            No alerts
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <div className="flex gap-1">
          {statuses.map((s) => (
            <button
              key={s || 'all'}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
                statusFilter === s
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {s || 'all'}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          {severities.map((s) => (
            <button
              key={s || 'all-sev'}
              onClick={() => setSeverityFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
                severityFilter === s
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {s || 'all severity'}
            </button>
          ))}
        </div>
        <span className="ml-auto text-xs text-gray-600">{total} total</span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-7 h-7 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl px-6 py-16 text-center">
          <p className="text-gray-500 text-sm">No security alerts match your filters.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-gray-900 border rounded-xl overflow-hidden transition-all ${
                alert.severity === 'critical' ? 'border-red-500/30' :
                alert.severity === 'high' ? 'border-orange-500/20' :
                'border-gray-800'
              }`}
            >
              <div
                className="px-5 py-4 flex items-start gap-4 cursor-pointer hover:bg-gray-800/30 transition-colors"
                onClick={() => setExpanded(expanded === alert.id ? null : alert.id)}
              >
                {/* Severity dot */}
                <div className="flex flex-col items-center gap-1 pt-0.5 shrink-0">
                  <span className={`w-2.5 h-2.5 rounded-full ${SEV_DOT[alert.severity] || 'bg-gray-500'}`} />
                </div>

                {/* Icon + label */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-gray-500 text-sm">
                      {TYPE_ICONS[alert.type] || TYPE_ICONS.default}
                    </span>
                    <span className="font-semibold text-sm text-white">{alert.label}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wide ${SEV_STYLE[alert.severity]}`}>
                      {alert.severity}
                    </span>
                    {alert.status === 'acknowledged' && (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-700 text-gray-400 border border-gray-600 uppercase">
                        Acknowledged
                      </span>
                    )}
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                    <span>{alert.client_email}</span>
                    {alert.related_agent && <span>Agent: {alert.related_agent}</span>}
                    {alert.detected_at && (
                      <span>{new Date(alert.detected_at).toLocaleString('en-GB')}</span>
                    )}
                  </div>
                </div>

                <span className="text-gray-600 text-xs shrink-0 mt-0.5">
                  {expanded === alert.id ? '▲' : '▼'}
                </span>
              </div>

              {/* Expanded detail */}
              {expanded === alert.id && (
                <div className="border-t border-gray-800 px-5 py-4 bg-gray-900/50">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Detail</p>
                      <p className="text-sm text-gray-300">{alert.detail}</p>
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Alert ID</span>
                        <span className="font-mono text-gray-400">{alert.id.slice(0, 16)}…</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Type</span>
                        <span className="text-gray-300">{alert.type}</span>
                      </div>
                      {alert.related_job_id && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Related job</span>
                          <span className="font-mono text-gray-400">{alert.related_job_id.slice(0, 12)}…</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2 flex-wrap">
                    {alert.status === 'open' && (
                      <button
                        onClick={() => acknowledge(alert.id)}
                        disabled={acting === alert.id}
                        className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                      >
                        {acting === alert.id ? 'Saving…' : 'Mark acknowledged'}
                      </button>
                    )}
                    {alert.client_id && (
                      <Link
                        href={`/admin/clients/${alert.client_id}`}
                        className="px-3 py-1.5 bg-violet-600/10 hover:bg-violet-600/20 text-violet-400 border border-violet-500/20 rounded-lg text-xs font-medium transition-colors"
                      >
                        Open client →
                      </Link>
                    )}
                    {alert.related_job_id && (
                      <Link
                        href={`/admin/jobs?id=${alert.related_job_id}`}
                        className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-lg text-xs font-medium transition-colors"
                      >
                        View job →
                      </Link>
                    )}
                    {alert.client_id && alert.status === 'open' && (
                      <button
                        onClick={() => {
                          if (confirm(`Lock account for ${alert.client_email}? This suspends access immediately.`)) {
                            lockAccount(alert.id);
                          }
                        }}
                        disabled={acting === `lock_${alert.id}`}
                        className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                      >
                        {acting === `lock_${alert.id}` ? 'Locking…' : 'Lock account'}
                      </button>
                    )}
                    <Link
                      href="/admin/audit"
                      className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-lg text-xs font-medium transition-colors"
                    >
                      View audit trail →
                    </Link>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
