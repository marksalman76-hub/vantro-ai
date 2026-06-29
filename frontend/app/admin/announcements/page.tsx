'use client';
import { useState, useEffect, useCallback } from 'react';

type AnnType = 'info' | 'warning' | 'maintenance' | 'new_feature' | 'new_agent';
type Tier = 'all' | 'starter' | 'growth' | 'business' | 'enterprise';

interface Announcement {
  id: string;
  title: string;
  body: string;
  affects: string | null;
  type: AnnType;
  target_tier: Tier;
  active: boolean;
  show_as: string;
  created_at: string;
  expires_at: string | null;
  created_by: string | null;
}

const TYPE_COLORS: Record<AnnType, string> = {
  info:         'bg-blue-500/20 text-blue-300 border-blue-500/30',
  warning:      'bg-amber-500/20 text-amber-300 border-amber-500/30',
  maintenance:  'bg-orange-500/20 text-orange-300 border-orange-500/30',
  new_feature:  'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  new_agent:    'bg-purple-500/20 text-purple-300 border-purple-500/30',
};

const TYPE_LABELS: Record<AnnType, string> = {
  info: 'Info', warning: 'Warning', maintenance: 'Maintenance',
  new_feature: 'New Feature', new_agent: 'New Agent',
};

const BLANK: Partial<Announcement> = {
  title: '', body: '', affects: '', type: 'info',
  target_tier: 'all', show_as: 'banner', expires_at: '',
};

export default function AdminAnnouncementsPage() {
  const [list, setList]     = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm]     = useState<Partial<Announcement>>(BLANK);
  const [editing, setEditing] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg]       = useState('');

  const token = () => {
    if (typeof document === 'undefined') return '';
    const m = document.cookie.match(/access_token=([^;]+)/);
    return m ? `Bearer ${m[1]}` : (localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : '');
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch('/api/admin/announcements', { headers: { Authorization: token() } });
      if (r.ok) setList(await r.json());
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const save = async () => {
    if (!form.title?.trim() || !form.body?.trim()) { setMsg('Title and body required.'); return; }
    setSaving(true); setMsg('');
    const method = editing ? 'PUT' : 'POST';
    const url = editing ? `/api/admin/announcements/${editing}` : '/api/admin/announcements';
    const r = await fetch(url, {
      method,
      headers: { Authorization: token(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, expires_at: form.expires_at || null }),
    });
    setSaving(false);
    if (r.ok) {
      setMsg('Saved.'); setShowForm(false); setEditing(null); setForm(BLANK); load();
    } else {
      setMsg('Save failed.');
    }
  };

  const toggle = async (id: string) => {
    await fetch(`/api/admin/announcements/${id}/toggle`, {
      method: 'PATCH', headers: { Authorization: token() },
    });
    load();
  };

  const del = async (id: string) => {
    if (!confirm('Delete this announcement?')) return;
    await fetch(`/api/admin/announcements/${id}`, {
      method: 'DELETE', headers: { Authorization: token() },
    });
    load();
  };

  const startEdit = (a: Announcement) => {
    setForm({ ...a, expires_at: a.expires_at ? a.expires_at.slice(0, 10) : '' });
    setEditing(a.id); setShowForm(true); setMsg('');
  };

  const startNew = () => {
    setForm(BLANK); setEditing(null); setShowForm(true); setMsg('');
  };

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Platform Announcements</h1>
          <p className="text-gray-400 text-sm mt-1">Publish banners and notices to client portal. Clients see updates matching their tier.</p>
        </div>
        <button onClick={startNew} className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100">
          + New Announcement
        </button>
      </div>

      {msg && <div className="mb-4 text-sm text-amber-400">{msg}</div>}

      {showForm && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-8">
          <h2 className="text-white font-semibold mb-4">{editing ? 'Edit Announcement' : 'New Announcement'}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="text-xs text-gray-400 mb-1 block">Title</label>
              <input value={form.title || ''} onChange={e => setForm(f => ({...f, title: e.target.value}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-white/30"
                placeholder="e.g. Social Media Agent — improved output quality" />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-400 mb-1 block">Body</label>
              <textarea value={form.body || ''} onChange={e => setForm(f => ({...f, body: e.target.value}))} rows={4}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-white/30 resize-none"
                placeholder="What changed and what the client can expect..." />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-400 mb-1 block">What this affects (visible to clients)</label>
              <input value={form.affects || ''} onChange={e => setForm(f => ({...f, affects: e.target.value}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-white/30"
                placeholder="e.g. Social Media Agent, UGC Media Agent, all caption outputs" />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Type</label>
              <select value={form.type || 'info'} onChange={e => setForm(f => ({...f, type: e.target.value as AnnType}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none">
                <option value="info">Info</option>
                <option value="new_feature">New Feature</option>
                <option value="new_agent">New Agent</option>
                <option value="warning">Warning</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Target Tier</label>
              <select value={form.target_tier || 'all'} onChange={e => setForm(f => ({...f, target_tier: e.target.value as Tier}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none">
                <option value="all">All clients</option>
                <option value="starter">Starter only</option>
                <option value="growth">Growth only</option>
                <option value="business">Business only</option>
                <option value="enterprise">Enterprise only</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Show as</label>
              <select value={form.show_as || 'banner'} onChange={e => setForm(f => ({...f, show_as: e.target.value}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none">
                <option value="banner">Banner (top of dashboard)</option>
                <option value="notification">Notification dot</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Expires (optional)</label>
              <input type="date" value={form.expires_at || ''} onChange={e => setForm(f => ({...f, expires_at: e.target.value}))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none" />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={save} disabled={saving}
              className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 disabled:opacity-50">
              {saving ? 'Saving…' : 'Save'}
            </button>
            <button onClick={() => { setShowForm(false); setEditing(null); setMsg(''); }}
              className="text-gray-400 hover:text-white text-sm px-4 py-2">Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-gray-500 text-sm">Loading…</div>
      ) : list.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-4xl mb-3">◈</p>
          <p className="text-sm">No announcements yet. Create one to notify clients.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map(a => (
            <div key={a.id} className={`bg-white/5 border rounded-xl p-4 ${a.active ? 'border-white/10' : 'border-white/5 opacity-60'}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${TYPE_COLORS[a.type as AnnType]}`}>
                      {TYPE_LABELS[a.type as AnnType]}
                    </span>
                    <span className="text-xs text-gray-500">{a.target_tier === 'all' ? 'All tiers' : `${a.target_tier} only`}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${a.active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'}`}>
                      {a.active ? 'Live' : 'Paused'}
                    </span>
                  </div>
                  <p className="text-white font-medium text-sm">{a.title}</p>
                  <p className="text-gray-400 text-xs mt-0.5 line-clamp-2">{a.body}</p>
                  {a.affects && (
                    <p className="text-gray-500 text-xs mt-1"><span className="text-gray-400">Affects:</span> {a.affects}</p>
                  )}
                  {a.expires_at && (
                    <p className="text-gray-500 text-xs mt-1">Expires: {new Date(a.expires_at).toLocaleDateString()}</p>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button onClick={() => toggle(a.id)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                      a.active
                        ? 'border-amber-500/30 text-amber-400 hover:bg-amber-500/10'
                        : 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                    }`}>
                    {a.active ? 'Pause' : 'Activate'}
                  </button>
                  <button onClick={() => startEdit(a)}
                    className="text-xs px-3 py-1.5 rounded-lg border border-white/10 text-gray-300 hover:bg-white/5">
                    Edit
                  </button>
                  <button onClick={() => del(a.id)}
                    className="text-xs px-3 py-1.5 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10">
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
