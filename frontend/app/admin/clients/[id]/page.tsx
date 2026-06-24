'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';

interface ClientDetail {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  subscription_status: string | null;
  stripe_customer_id: string | null;
  created_at: string | null;
  organization: { id: string; name: string; slug: string } | null;
  workspace: { id: string; name: string } | null;
  credits: { total: number; used: number; remaining: number; tier: string };
  jobs: Job[];
}

interface Job {
  id: string;
  status: string;
  script: string | null;
  video_url: string | null;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
}

interface SecurityAlert {
  id: string;
  severity: string;
  label: string;
  type: string;
  status: string;
  detail: string;
  detected_at: string | null;
  related_job_id: string | null;
}

const STATUS_STYLE: Record<string, string> = {
  completed:  'bg-green-400/10 text-green-400',
  processing: 'bg-yellow-400/10 text-yellow-400',
  pending:    'bg-blue-400/10 text-blue-400',
  failed:     'bg-red-400/10 text-red-400',
  cancelled:  'bg-gray-700 text-gray-400',
};

const SEV_STYLE: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-300',
  high:     'bg-orange-500/15 text-orange-300',
  medium:   'bg-yellow-500/15 text-yellow-300',
  low:      'bg-blue-500/10 text-blue-300',
  info:     'bg-gray-700 text-gray-400',
};

type TabId = 'overview' | 'jobs' | 'security' | 'sessions' | 'notes';

export default function ClientDetailPage() {
  const router = useRouter();
  const params = useParams();
  const userId = (params?.id as string) ?? '';

  const [client, setClient] = useState<ClientDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [creditAmount, setCreditAmount] = useState('');
  const [creditReason, setCreditReason] = useState('');
  const [actionLoading, setActionLoading] = useState('');
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [secAlerts, setSecAlerts] = useState<SecurityAlert[]>([]);
  const [adminNote, setAdminNote] = useState('');
  const [savedNote, setSavedNote] = useState('');

  const getToken = () => localStorage.getItem('admin_token') || '';

  const load = useCallback(() => {
    const token = getToken();
    if (!token) { router.push('/admin-login'); return; }
    fetch(`/api/admin/clients/${userId}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 404) { router.push('/admin/clients'); return; }
        setClient(await r.json());
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId, router]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!userId) return;
    const token = getToken();
    // Load security alerts filtered to this client (via all alerts, then filter client_id)
    fetch(`/api/admin/security/alerts?limit=50`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.ok) {
          const d = await r.json();
          setSecAlerts((d.alerts || []).filter((a: SecurityAlert & { client_id?: string }) => a.client_id === userId));
        }
      })
      .catch(() => {});
    // Load saved admin note from localStorage (client-side only)
    const stored = localStorage.getItem(`admin_note_${userId}`) || '';
    setSavedNote(stored);
    setAdminNote(stored);
  }, [userId]);

  async function adjustCredits(sign: 1 | -1) {
    const amount = parseInt(creditAmount);
    if (!amount || isNaN(amount)) return;
    setActionLoading('credits');
    try {
      const res = await fetch(`/api/admin/clients/${userId}/credits`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: amount * sign, reason: creditReason }),
      });
      if (res.ok) {
        setMessage(sign > 0 ? `+${amount} credits granted` : `-${amount} credits removed`);
        setCreditAmount('');
        setCreditReason('');
        load();
      }
    } finally {
      setActionLoading('');
    }
  }

  async function toggleAccount(action: 'suspend' | 'reactivate') {
    setActionLoading(action);
    try {
      const res = await fetch(`/api/admin/clients/${userId}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (res.ok) {
        setMessage(action === 'suspend' ? 'Account suspended' : 'Account reactivated');
        load();
      }
    } finally {
      setActionLoading('');
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!client) return null;

  const { credits } = client;
  const usedPct = credits.total > 0 ? Math.round((credits.used / credits.total) * 100) : 0;

  const TABS: { id: TabId; label: string; badge?: number }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'jobs',     label: 'Jobs', badge: client.jobs.length },
    { id: 'security', label: 'Security', badge: secAlerts.filter(a => a.status === 'open').length || undefined },
    { id: 'sessions', label: 'Devices & Sessions' },
    { id: 'notes',    label: 'Admin Notes' },
  ];

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/admin/clients" className="text-gray-500 hover:text-gray-300 text-sm">← Clients</Link>
        <span className="text-gray-700">/</span>
        <span className="text-gray-300 text-sm">{client.email}</span>
        {!client.is_active && (
          <span className="text-xs bg-red-500/15 text-red-400 border border-red-500/20 px-2 py-0.5 rounded-full">Suspended</span>
        )}
      </div>

      {message && (
        <div className="mb-5 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 flex items-center justify-between">
          <p className="text-green-400 text-sm">{message}</p>
          <button onClick={() => setMessage('')} className="text-green-400/60 hover:text-green-400">×</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-800 pb-0">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-xs font-medium rounded-t-lg transition-colors relative flex items-center gap-1.5 ${
              activeTab === tab.id
                ? 'text-violet-300 bg-violet-600/10 border border-b-0 border-gray-800'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {tab.label}
            {tab.badge ? (
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                tab.id === 'security' ? 'bg-red-500/20 text-red-400' : 'bg-gray-700 text-gray-400'
              }`}>{tab.badge}</span>
            ) : null}
          </button>
        ))}
      </div>

      {/* ── Overview Tab ── */}
      {activeTab === 'overview' && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Profile */}
        <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="font-semibold mb-4">Client Profile</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Email</span>
              <span className="text-gray-200">{client.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Name</span>
              <span className="text-gray-200">{client.name || '—'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Organization</span>
              <span className="text-gray-200">{client.organization?.name || '—'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Plan</span>
              <span className="text-gray-200 capitalize">{client.subscription_status || 'Free'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Tier</span>
              <span className="text-gray-200 capitalize">{credits.tier}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Stripe ID</span>
              <span className="text-gray-500 font-mono text-xs">{client.stripe_customer_id || '—'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Joined</span>
              <span className="text-gray-200">{client.created_at ? new Date(client.created_at).toLocaleDateString('en-GB') : '—'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Account status</span>
              {client.is_active
                ? <span className="text-green-400 text-xs font-medium">Active</span>
                : <span className="text-red-400 text-xs font-medium">Suspended</span>}
            </div>
          </div>

          {/* Account controls */}
          <div className="mt-6 pt-5 border-t border-gray-800 flex gap-3">
            {client.is_active ? (
              <button
                onClick={() => toggleAccount('suspend')}
                disabled={actionLoading === 'suspend'}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {actionLoading === 'suspend' ? 'Suspending…' : 'Suspend account'}
              </button>
            ) : (
              <button
                onClick={() => toggleAccount('reactivate')}
                disabled={actionLoading === 'reactivate'}
                className="px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {actionLoading === 'reactivate' ? 'Reactivating…' : 'Reactivate account'}
              </button>
            )}
          </div>
        </div>

        {/* Credits panel */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="font-semibold mb-4">Credits</h2>
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total</span>
              <span className="text-white font-mono">{credits.total}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Used</span>
              <span className="text-orange-400 font-mono">{credits.used}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Remaining</span>
              <span className="text-green-400 font-mono">{credits.remaining}</span>
            </div>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-1.5 mb-5">
            <div
              className={`h-1.5 rounded-full ${usedPct > 80 ? 'bg-red-500' : 'bg-purple-500'}`}
              style={{ width: `${Math.min(usedPct, 100)}%` }}
            />
          </div>

          <p className="text-xs text-gray-500 mb-2">Adjust credits</p>
          <input
            type="number"
            value={creditAmount}
            onChange={(e) => setCreditAmount(e.target.value)}
            placeholder="Amount (e.g. 50)"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 mb-2"
          />
          <input
            value={creditReason}
            onChange={(e) => setCreditReason(e.target.value)}
            placeholder="Reason (optional)"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 mb-3"
          />
          <div className="flex gap-2">
            <button
              onClick={() => adjustCredits(1)}
              disabled={actionLoading === 'credits'}
              className="flex-1 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
            >
              + Grant
            </button>
            <button
              onClick={() => adjustCredits(-1)}
              disabled={actionLoading === 'credits'}
              className="flex-1 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
            >
              − Remove
            </button>
          </div>
        </div>
      </div>

      </div> {/* end overview grid */}
      )} {/* end overview tab */}

      {/* ── Jobs Tab ── */}
      {activeTab === 'jobs' && (
      <div className="bg-gray-900 border border-gray-800 rounded-xl">
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="font-semibold">Job History <span className="text-gray-600 font-normal text-sm">({client.jobs.length})</span></h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                {['Script', 'Status', 'Created', 'Completed', 'Output', 'Error'].map((h) => (
                  <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {client.jobs.map((j) => (
                <tr key={j.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  <td className="px-5 py-3 text-gray-300 text-xs max-w-xs truncate">{j.script || '—'}</td>
                  <td className="px-5 py-3">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_STYLE[j.status] || 'bg-gray-700 text-gray-400'}`}>
                      {j.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-500 text-xs">{j.created_at ? new Date(j.created_at).toLocaleDateString('en-GB') : '—'}</td>
                  <td className="px-5 py-3 text-gray-500 text-xs">{j.completed_at ? new Date(j.completed_at).toLocaleDateString('en-GB') : '—'}</td>
                  <td className="px-5 py-3">
                    {j.video_url
                      ? <a href={j.video_url} target="_blank" rel="noreferrer" className="text-xs text-violet-400 hover:text-violet-300">Watch →</a>
                      : <span className="text-gray-700 text-xs">—</span>}
                  </td>
                  <td className="px-5 py-3 text-red-400 text-xs max-w-xs truncate">{j.error_message || '—'}</td>
                </tr>
              ))}
              {client.jobs.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-10 text-center text-gray-600 text-sm">No jobs yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      )}

      {/* ── Security Tab ── */}
      {activeTab === 'security' && (
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-semibold">Security Events</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Alerts linked to this client account
            </p>
          </div>
          <Link href="/admin/security" className="text-xs text-violet-400 hover:text-violet-300">
            All security alerts →
          </Link>
        </div>

        {secAlerts.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl px-6 py-12 text-center">
            <p className="text-gray-500 text-sm">No security events recorded for this client.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {secAlerts.map((alert) => (
              <div key={alert.id} className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm text-white">{alert.label}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${SEV_STYLE[alert.severity] || 'bg-gray-700 text-gray-400'}`}>
                        {alert.severity}
                      </span>
                      {alert.status === 'acknowledged' && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-700 text-gray-400 uppercase">ack</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{alert.detail}</p>
                    {alert.detected_at && (
                      <p className="text-xs text-gray-600 mt-1">{new Date(alert.detected_at).toLocaleString('en-GB')}</p>
                    )}
                  </div>
                  {alert.related_job_id && (
                    <Link
                      href={`/admin/jobs?id=${alert.related_job_id}`}
                      className="text-xs text-violet-400 hover:text-violet-300 shrink-0"
                    >
                      View job →
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Account security controls */}
        <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl px-5 py-4">
          <h3 className="font-semibold text-sm mb-3">Account Security Controls</h3>
          <div className="flex gap-3 flex-wrap">
            {client.is_active ? (
              <button
                onClick={() => toggleAccount('suspend')}
                disabled={actionLoading === 'suspend'}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              >
                {actionLoading === 'suspend' ? 'Suspending…' : 'Suspend account'}
              </button>
            ) : (
              <button
                onClick={() => toggleAccount('reactivate')}
                disabled={actionLoading === 'reactivate'}
                className="px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              >
                {actionLoading === 'reactivate' ? 'Reactivating…' : 'Reactivate account'}
              </button>
            )}
            <Link
              href="/admin/audit"
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-lg text-xs font-medium transition-colors"
            >
              View audit trail →
            </Link>
          </div>
        </div>
      </div>
      )}

      {/* ── Devices & Sessions Tab ── */}
      {activeTab === 'sessions' && (
      <div>
        <div className="mb-4">
          <h2 className="font-semibold">Devices & Sessions</h2>
          <p className="text-xs text-gray-500 mt-0.5">Session metadata only — no raw device fingerprints or sensitive identifiers</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 space-y-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500 text-xs">Account status</span>
              <p className={client.is_active ? 'text-green-400 font-medium mt-0.5' : 'text-red-400 font-medium mt-0.5'}>
                {client.is_active ? 'Active' : 'Suspended'}
              </p>
            </div>
            <div>
              <span className="text-gray-500 text-xs">Subscription</span>
              <p className="text-gray-200 font-medium mt-0.5 capitalize">{client.subscription_status || 'None'}</p>
            </div>
            <div>
              <span className="text-gray-500 text-xs">Account created</span>
              <p className="text-gray-200 mt-0.5">
                {client.created_at ? new Date(client.created_at).toLocaleDateString('en-GB') : '—'}
              </p>
            </div>
            <div>
              <span className="text-gray-500 text-xs">Last job</span>
              <p className="text-gray-200 mt-0.5">
                {client.jobs[0]?.created_at ? new Date(client.jobs[0].created_at).toLocaleDateString('en-GB') : 'Never'}
              </p>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <p className="text-xs text-gray-500 mb-3">Session Controls</p>
            <div className="flex gap-3 flex-wrap">
              {client.is_active ? (
                <button
                  onClick={() => toggleAccount('suspend')}
                  disabled={actionLoading === 'suspend'}
                  className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-medium disabled:opacity-50"
                >
                  {actionLoading === 'suspend' ? 'Suspending…' : 'Suspend & revoke access'}
                </button>
              ) : (
                <button
                  onClick={() => toggleAccount('reactivate')}
                  disabled={actionLoading === 'reactivate'}
                  className="px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-medium disabled:opacity-50"
                >
                  {actionLoading === 'reactivate' ? 'Reactivating…' : 'Restore access'}
                </button>
              )}
            </div>
          </div>

          <div className="border-t border-gray-800 pt-4 text-xs text-gray-600">
            Session fingerprinting and device binding require additional infrastructure configuration.
            Contact engineering to enable advanced session management.
          </div>
        </div>
      </div>
      )}

      {/* ── Admin Notes Tab ── */}
      {activeTab === 'notes' && (
      <div>
        <div className="mb-4">
          <h2 className="font-semibold">Admin Notes</h2>
          <p className="text-xs text-gray-500 mt-0.5">Internal notes visible to admin only — never shown to clients</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <textarea
            value={adminNote}
            onChange={(e) => setAdminNote(e.target.value)}
            placeholder="Add internal notes about this client — support context, billing issues, security concerns, account history…"
            rows={8}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 resize-none"
          />
          <div className="flex items-center justify-between mt-3">
            <p className="text-xs text-gray-600">Stored locally in this browser session.</p>
            <button
              onClick={() => {
                localStorage.setItem(`admin_note_${userId}`, adminNote);
                setSavedNote(adminNote);
                setMessage('Note saved');
              }}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg text-xs font-semibold transition-colors"
            >
              Save note
            </button>
          </div>
          {savedNote && savedNote !== adminNote && (
            <p className="text-xs text-amber-400 mt-2">Unsaved changes</p>
          )}
        </div>
      </div>
      )}

    </div>
  );
}
