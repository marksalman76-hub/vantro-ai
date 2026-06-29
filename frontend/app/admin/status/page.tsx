'use client';
import { useState, useEffect, useCallback } from 'react';

type ComponentStatus = 'operational' | 'degraded' | 'maintenance' | 'outage';

interface SystemComponent {
  name: string;
  status: ComponentStatus;
  description: string;
}

interface SystemStatus {
  overall: ComponentStatus;
  message: string | null;
  components: SystemComponent[];
  updated_at: string | null;
  updated_by: string | null;
}

interface ChangelogEntry {
  id: string;
  agent_id: string;
  agent_name: string;
  version: string;
  summary: string;
  changes: string[];
  affects: string | null;
  release_date: string;
  created_by: string | null;
}

const STATUS_COLORS: Record<ComponentStatus, string> = {
  operational: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
  degraded:    'text-amber-400 bg-amber-500/20 border-amber-500/30',
  maintenance: 'text-orange-400 bg-orange-500/20 border-orange-500/30',
  outage:      'text-red-400 bg-red-500/20 border-red-500/30',
};

const STATUS_DOT: Record<ComponentStatus, string> = {
  operational: 'bg-emerald-400',
  degraded:    'bg-amber-400',
  maintenance: 'bg-orange-400',
  outage:      'bg-red-500',
};

const BLANK_LOG = { agent_id: '', agent_name: '', version: '', summary: '', changes: '', affects: '', release_date: '' };

export default function AdminStatusPage() {
  const [status, setStatus]     = useState<SystemStatus | null>(null);
  const [changelogs, setChangelogs] = useState<ChangelogEntry[]>([]);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [savingStatus, setSavingStatus] = useState(false);
  const [showLogForm, setShowLogForm] = useState(false);
  const [logForm, setLogForm] = useState(BLANK_LOG);
  const [savingLog, setSavingLog] = useState(false);
  const [msg, setMsg] = useState('');
  const [tab, setTab] = useState<'status' | 'changelog'>('status');

  const token = () => {
    if (typeof document === 'undefined') return '';
    const m = document.cookie.match(/access_token=([^;]+)/);
    return m ? `Bearer ${m[1]}` : (localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : '');
  };

  const loadStatus = useCallback(async () => {
    setLoadingStatus(true);
    try {
      const r = await fetch('/api/admin/system-status', { headers: { Authorization: token() } });
      if (r.ok) setStatus(await r.json());
    } finally { setLoadingStatus(false); }
  }, []);

  const loadLogs = useCallback(async () => {
    setLoadingLogs(true);
    try {
      const r = await fetch('/api/admin/agent-changelogs', { headers: { Authorization: token() } });
      if (r.ok) setChangelogs(await r.json());
    } finally { setLoadingLogs(false); }
  }, []);

  useEffect(() => { loadStatus(); loadLogs(); }, [loadStatus, loadLogs]);

  const updateComponentStatus = (idx: number, field: keyof SystemComponent, val: string) => {
    if (!status) return;
    const comps = [...status.components];
    comps[idx] = { ...comps[idx], [field]: val };
    setStatus({ ...status, components: comps });
  };

  const saveStatus = async () => {
    if (!status) return;
    setSavingStatus(true); setMsg('');
    const r = await fetch('/api/admin/system-status', {
      method: 'PUT',
      headers: { Authorization: token(), 'Content-Type': 'application/json' },
      body: JSON.stringify(status),
    });
    setSavingStatus(false);
    if (r.ok) { setMsg('Status updated.'); loadStatus(); }
    else setMsg('Update failed.');
  };

  const saveLog = async () => {
    if (!logForm.agent_id || !logForm.version || !logForm.summary) {
      setMsg('Agent, version, and summary required.'); return;
    }
    setSavingLog(true); setMsg('');
    const changes = logForm.changes.split('\n').map(s => s.trim()).filter(Boolean);
    const r = await fetch('/api/admin/agent-changelogs', {
      method: 'POST',
      headers: { Authorization: token(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: logForm.agent_id,
        agent_name: logForm.agent_name || logForm.agent_id,
        version: logForm.version,
        summary: logForm.summary,
        changes,
        affects: logForm.affects || null,
        release_date: logForm.release_date || null,
      }),
    });
    setSavingLog(false);
    if (r.ok) { setMsg('Changelog saved.'); setShowLogForm(false); setLogForm(BLANK_LOG); loadLogs(); }
    else setMsg('Save failed.');
  };

  const delLog = async (id: string) => {
    if (!confirm('Delete this changelog entry?')) return;
    await fetch(`/api/admin/agent-changelogs/${id}`, { method: 'DELETE', headers: { Authorization: token() } });
    loadLogs();
  };

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">System Status & Agent Changelog</h1>
        <p className="text-gray-400 text-sm mt-1">Control what clients see on the public status page and per-agent update history.</p>
      </div>

      {msg && <div className="mb-4 text-sm text-amber-400">{msg}</div>}

      <div className="flex gap-1 mb-6 bg-white/5 rounded-xl p-1 w-fit">
        {(['status', 'changelog'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === t ? 'bg-white text-black' : 'text-gray-400 hover:text-white'
            }`}>
            {t === 'status' ? 'System Status' : 'Agent Changelog'}
          </button>
        ))}
      </div>

      {tab === 'status' && (
        loadingStatus ? (
          <div className="text-gray-500 text-sm">Loading…</div>
        ) : status ? (
          <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h2 className="text-white font-semibold mb-4">Overall Status</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Status</label>
                  <select value={status.overall}
                    onChange={e => setStatus({ ...status, overall: e.target.value as ComponentStatus })}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm">
                    <option value="operational">Operational</option>
                    <option value="degraded">Degraded Performance</option>
                    <option value="maintenance">Under Maintenance</option>
                    <option value="outage">Major Outage</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Banner Message (optional)</label>
                  <input value={status.message || ''} onChange={e => setStatus({ ...status, message: e.target.value || null })}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. Scheduled maintenance 2am–4am UTC" />
                </div>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h2 className="text-white font-semibold mb-4">Component Status</h2>
              <div className="space-y-3">
                {status.components.map((c, i) => (
                  <div key={c.name} className="grid grid-cols-3 gap-3 items-center">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${STATUS_DOT[c.status]}`} />
                      <span className="text-white text-sm font-medium">{c.name}</span>
                    </div>
                    <select value={c.status} onChange={e => updateComponentStatus(i, 'status', e.target.value)}
                      className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm">
                      <option value="operational">Operational</option>
                      <option value="degraded">Degraded</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="outage">Outage</option>
                    </select>
                    <input value={c.description} onChange={e => updateComponentStatus(i, 'description', e.target.value)}
                      className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm"
                      placeholder="Optional note for clients" />
                  </div>
                ))}
              </div>
            </div>

            {status.updated_at && (
              <p className="text-xs text-gray-500">Last updated: {new Date(status.updated_at).toLocaleString()} {status.updated_by ? `by ${status.updated_by}` : ''}</p>
            )}

            <button onClick={saveStatus} disabled={savingStatus}
              className="bg-white text-black text-sm font-semibold px-5 py-2 rounded-lg hover:bg-gray-100 disabled:opacity-50">
              {savingStatus ? 'Saving…' : 'Save Status'}
            </button>
          </div>
        ) : null
      )}

      {tab === 'changelog' && (
        <div>
          <div className="flex justify-end mb-4">
            <button onClick={() => { setShowLogForm(true); setLogForm(BLANK_LOG); setMsg(''); }}
              className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100">
              + Add Changelog Entry
            </button>
          </div>

          {showLogForm && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-6">
              <h2 className="text-white font-semibold mb-4">New Changelog Entry</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Agent ID</label>
                  <input value={logForm.agent_id}
                    onChange={e => setLogForm(f => ({...f, agent_id: e.target.value, agent_name: e.target.value}))}
                    list="agent-ids"
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. social_media_agent" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Display Name</label>
                  <input value={logForm.agent_name} onChange={e => setLogForm(f => ({...f, agent_name: e.target.value}))}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. Social Media Agent" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Version</label>
                  <input value={logForm.version} onChange={e => setLogForm(f => ({...f, version: e.target.value}))}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. 1.2.0" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Release Date</label>
                  <input type="date" value={logForm.release_date} onChange={e => setLogForm(f => ({...f, release_date: e.target.value}))}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 mb-1 block">Summary (one-line headline)</label>
                  <input value={logForm.summary} onChange={e => setLogForm(f => ({...f, summary: e.target.value}))}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. Improved caption quality and hashtag relevance" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 mb-1 block">What changed (one item per line)</label>
                  <textarea value={logForm.changes} onChange={e => setLogForm(f => ({...f, changes: e.target.value}))} rows={4}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm resize-none"
                    placeholder={"Better hashtag selection\nMore concise caption output\nFixed tone consistency"} />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 mb-1 block">What clients will notice</label>
                  <input value={logForm.affects} onChange={e => setLogForm(f => ({...f, affects: e.target.value}))}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    placeholder="e.g. Caption outputs will be sharper and better targeted to each platform" />
                </div>
              </div>
              <div className="flex gap-3 mt-4">
                <button onClick={saveLog} disabled={savingLog}
                  className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 disabled:opacity-50">
                  {savingLog ? 'Saving…' : 'Save Entry'}
                </button>
                <button onClick={() => setShowLogForm(false)} className="text-gray-400 hover:text-white text-sm px-4 py-2">Cancel</button>
              </div>
            </div>
          )}

          {loadingLogs ? (
            <div className="text-gray-500 text-sm">Loading…</div>
          ) : changelogs.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <p className="text-4xl mb-3">◈</p>
              <p className="text-sm">No changelog entries yet. Add one to show clients what changed in each agent.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {changelogs.map(c => (
                <div key={c.id} className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded-full">
                          v{c.version}
                        </span>
                        <span className="text-xs text-gray-500">{c.agent_name}</span>
                        <span className="text-xs text-gray-600">{new Date(c.release_date).toLocaleDateString()}</span>
                      </div>
                      <p className="text-white text-sm font-medium">{c.summary}</p>
                      {c.changes.length > 0 && (
                        <ul className="mt-1.5 space-y-0.5">
                          {c.changes.map((ch, i) => (
                            <li key={i} className="text-gray-400 text-xs flex items-start gap-1.5">
                              <span className="text-gray-600 mt-0.5">•</span>{ch}
                            </li>
                          ))}
                        </ul>
                      )}
                      {c.affects && (
                        <p className="text-gray-500 text-xs mt-1.5"><span className="text-gray-400">Client impact:</span> {c.affects}</p>
                      )}
                    </div>
                    <button onClick={() => delLog(c.id)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10 shrink-0">
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
