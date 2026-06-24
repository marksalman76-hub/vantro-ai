'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast, { Toaster } from 'react-hot-toast';
import { apiFetch, signOut } from '@/lib/api';

interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  subscription_status: string | null;
}

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Password change state
  const [currentPwd, setCurrentPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [pwdMsg, setPwdMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [pwdLoading, setPwdLoading] = useState(false);

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Export state
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (!token) { router.replace('/login'); return; }

    apiFetch('/api/users/me')
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then((d: UserProfile) => setUser(d))
      .catch(() => router.replace('/login'))
      .finally(() => setLoading(false));
  }, [router]);

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    if (newPwd !== confirmPwd) {
      setPwdMsg({ type: 'error', text: 'New passwords do not match' });
      return;
    }
    if (newPwd.length < 8) {
      setPwdMsg({ type: 'error', text: 'Password must be at least 8 characters' });
      return;
    }
    setPwdLoading(true);
    setPwdMsg(null);
    try {
      const res = await apiFetch('/api/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password: currentPwd, new_password: newPwd }),
      });
      if (res.ok) {
        toast.success('Password updated successfully');
        setPwdMsg(null);
        setCurrentPwd(''); setNewPwd(''); setConfirmPwd('');
      } else {
        const d = await res.json();
        toast.error(d.detail || 'Failed to update password');
        setPwdMsg({ type: 'error', text: d.detail || 'Failed to update password' });
      }
    } catch {
      toast.error('Network error — try again');
      setPwdMsg({ type: 'error', text: 'Network error — try again' });
    } finally {
      setPwdLoading(false);
    }
  }

  async function handleExport() {
    setExportLoading(true);
    try {
      const res = await apiFetch('/api/users/me/export');
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'vantro-data-export.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Export failed — try again');
    } finally {
      setExportLoading(false);
    }
  }

  async function handleDeleteAccount() {
    if (deleteConfirm !== 'DELETE') return;
    setDeleteLoading(true);
    try {
      const res = await apiFetch('/api/users/me', { method: 'DELETE' });
      if (res.ok) {
        localStorage.removeItem('token');
        router.replace('/login?deleted=1');
      } else {
        const d = await res.json();
        alert(d.detail || 'Failed to delete account');
      }
    } catch {
      alert('Network error — try again');
    } finally {
      setDeleteLoading(false);
      setShowDeleteModal(false);
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!user) return null;

  return (
    <div className="p-8 max-w-2xl">
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: 'rgba(10,14,30,0.95)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(20px)' },
        }}
      />

      {/* Delete confirmation modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="glass border border-red-500/20 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Delete account permanently?</h3>
            <p className="text-white/45 text-sm mb-4">This will anonymise all your personal data in accordance with GDPR. This action cannot be undone.</p>
            <p className="text-white/45 text-sm mb-3">
              Type <span className="text-red-400 font-mono font-bold">DELETE</span> to confirm:
            </p>
            <input
              type="text"
              value={deleteConfirm}
              onChange={e => setDeleteConfirm(e.target.value)}
              placeholder="DELETE"
              className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-2.5 text-white text-sm mb-4 focus:outline-none focus:border-red-500/50 placeholder-white/20"
            />
            <div className="flex gap-3">
              <button
                onClick={() => { setShowDeleteModal(false); setDeleteConfirm(''); }}
                className="flex-1 btn-secondary text-sm px-4 py-2.5"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                disabled={deleteConfirm !== 'DELETE' || deleteLoading}
                className="flex-1 bg-red-600 hover:bg-red-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2.5 rounded-xl transition-colors"
              >
                {deleteLoading ? 'Deleting…' : 'Delete my account'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Account Settings</h1>
        <p className="text-white/35 text-sm mt-1">Manage your account, security, and data</p>
      </div>

      <div className="space-y-5">
        {/* Profile info */}
        <div className="glass border border-white/[0.08] rounded-2xl p-6">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">Profile</h2>
          <div className="space-y-0">
            <div className="flex justify-between items-center py-3 border-b border-white/[0.06]">
              <span className="text-sm text-white/45">Email</span>
              <span className="text-sm text-white font-mono">{user.email}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-white/[0.06]">
              <span className="text-sm text-white/45">Name</span>
              <span className="text-sm text-white">{user.name || '—'}</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-sm text-white/45">Plan</span>
              <span className="text-sm text-violet-400 capitalize">{user.subscription_status || 'free'}</span>
            </div>
          </div>
        </div>

        {/* Change password */}
        <div className="glass border border-white/[0.08] rounded-2xl p-6">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">Change Password</h2>
          <form onSubmit={handleChangePassword} className="space-y-3">
            <input
              type="password"
              value={currentPwd}
              onChange={e => setCurrentPwd(e.target.value)}
              placeholder="Current password"
              required
              className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-2.5 text-white text-sm placeholder-white/20 focus:outline-none focus:border-violet-500/50 transition-all"
            />
            <input
              type="password"
              value={newPwd}
              onChange={e => setNewPwd(e.target.value)}
              placeholder="New password (min 8 chars)"
              required
              className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-2.5 text-white text-sm placeholder-white/20 focus:outline-none focus:border-violet-500/50 transition-all"
            />
            <input
              type="password"
              value={confirmPwd}
              onChange={e => setConfirmPwd(e.target.value)}
              placeholder="Confirm new password"
              required
              className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl px-4 py-2.5 text-white text-sm placeholder-white/20 focus:outline-none focus:border-violet-500/50 transition-all"
            />
            {pwdMsg && (
              <p className={`text-xs ${pwdMsg.type === 'success' ? 'text-emerald-400' : 'text-red-400'}`}>
                {pwdMsg.text}
              </p>
            )}
            <button
              type="submit"
              disabled={pwdLoading}
              className="btn-primary text-sm px-5 py-2.5 disabled:opacity-50"
            >
              {pwdLoading ? 'Updating…' : 'Update password'}
            </button>
          </form>
        </div>

        {/* GDPR data */}
        <div className="glass border border-white/[0.08] rounded-2xl p-6">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-1">Your Data</h2>
          <p className="text-white/35 text-xs mb-4">Download everything Vantro holds about your account.</p>
          <button
            onClick={handleExport}
            disabled={exportLoading}
            className="btn-secondary text-sm px-5 py-2.5 disabled:opacity-50"
          >
            {exportLoading ? 'Preparing export…' : 'Download my data (JSON)'}
          </button>
        </div>

        {/* Notification preferences */}
        <div className="glass border border-white/[0.08] rounded-2xl p-6">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">Notification Preferences</h2>
          <p className="text-white/35 text-xs mb-4">Choose what we notify you about. Changes save automatically.</p>
          <div className="space-y-3">
            {[
              { key: 'notif_weekly_report', label: 'Weekly AI workforce report', desc: 'Emailed every Monday' },
              { key: 'notif_job_status',    label: 'Job status updates',         desc: 'When tasks complete or fail' },
              { key: 'notif_approvals',     label: 'Approval requests',          desc: 'When work needs your review' },
              { key: 'notif_billing',       label: 'Billing & credit alerts',    desc: 'Renewals, low credits, invoices' },
              { key: 'notif_security',      label: 'Security notices',           desc: 'New device logins, unusual activity' },
            ].map(({ key, label, desc }) => {
              const stored = typeof window !== 'undefined' ? localStorage.getItem(key) : null;
              const enabled = stored === null ? true : stored === '1';
              return (
                <div key={key} className="flex items-center justify-between py-2 border-b border-white/[0.05] last:border-0">
                  <div>
                    <p className="text-sm text-white/80">{label}</p>
                    <p className="text-xs text-white/30 mt-0.5">{desc}</p>
                  </div>
                  <button
                    onClick={() => {
                      const current = localStorage.getItem(key) !== '0';
                      localStorage.setItem(key, current ? '0' : '1');
                      // Force a re-render by dispatching a storage event
                      window.dispatchEvent(new Event('storage'));
                    }}
                    className={`relative w-10 h-5 rounded-full transition-colors shrink-0 ml-4 ${
                      enabled ? 'bg-violet-600' : 'bg-gray-700'
                    }`}
                  >
                    <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${
                      enabled ? 'left-5' : 'left-0.5'
                    }`} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Privacy & likeness */}
        <div className="glass border border-white/[0.08] rounded-2xl p-6">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">Privacy &amp; Likeness</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-white/80 mb-1">Uploaded likeness</p>
              <p className="text-white/35 text-xs mb-3">
                If you have uploaded a photo or video of yourself as a spokesperson or avatar, you can remove it here at any time.
                Removal takes effect immediately for future tasks.
              </p>
              <button
                onClick={() => alert('Contact support to remove your uploaded likeness: support@vantro.ai')}
                className="text-xs bg-white/[0.05] hover:bg-white/[0.10] border border-white/[0.10] text-white/60 hover:text-white px-4 py-2 rounded-xl transition-colors"
              >
                Remove uploaded likeness
              </button>
            </div>
            <div className="border-t border-white/[0.06] pt-4">
              <p className="text-sm text-white/80 mb-1">Consent review</p>
              <p className="text-white/35 text-xs mb-3">
                Review and manage your consent settings for AI-generated media using your likeness or brand assets.
              </p>
              <a
                href="mailto:support@vantro.ai?subject=Consent review request"
                className="text-xs text-violet-400 hover:text-violet-300 font-medium"
              >
                Contact support to review consent →
              </a>
            </div>
            <div className="border-t border-white/[0.06] pt-4">
              <p className="text-sm text-white/80 mb-1">Data export</p>
              <p className="text-white/35 text-xs mb-3">Download all data we hold about your account.</p>
              <button
                onClick={handleExport}
                disabled={exportLoading}
                className="text-xs bg-white/[0.05] hover:bg-white/[0.10] border border-white/[0.10] text-white/60 hover:text-white px-4 py-2 rounded-xl transition-colors disabled:opacity-40"
              >
                {exportLoading ? 'Preparing…' : 'Download my data (JSON)'}
              </button>
            </div>
          </div>
        </div>

        {/* Danger zone */}
        <div className="rounded-2xl p-6" style={{ background: 'rgba(239,68,68,0.04)', border: '1px solid rgba(239,68,68,0.18)' }}>
          <h2 className="text-xs font-semibold text-red-400 uppercase tracking-widest mb-1">Danger Zone</h2>
          <p className="text-white/35 text-xs mb-4">
            Permanently delete your account. All personal data will be anonymised per GDPR Article 17. This cannot be undone.
          </p>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="bg-red-600/10 hover:bg-red-600/20 border border-red-500/30 text-red-400 hover:text-red-300 text-sm font-medium px-5 py-2.5 rounded-xl transition-colors"
          >
            Delete my account
          </button>
        </div>
      </div>
    </div>
  );
}
