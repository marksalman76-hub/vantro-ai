'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  subscription_status: string | null;
  created_at: string | null;
}

const SAFE_NOTICES = [
  { key: 'new_device', label: 'New device sign-in detected', desc: 'We noticed a sign-in from a new device. If this was you, no action is needed.', action: 'Review sessions', href: '#sessions' },
  { key: 'unusual', label: 'Unusual activity detected', desc: 'We noticed some unusual activity on your account and have alerted our team.', action: 'Contact support', href: '/dashboard/support' },
  { key: 'package_pause', label: 'Package access paused', desc: 'Access was paused for your protection. Contact support to restore.', action: 'Contact support', href: '/dashboard/support' },
];

export default function AccountSecurityPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [notices, setNotices] = useState<string[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    fetch('/api/users/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setUser(d); })
      .catch(() => {})
      .finally(() => setLoading(false));

    // Check for any stored security notices (set by auth flow on suspicious events)
    const stored = localStorage.getItem('security_notices');
    if (stored) {
      try { setNotices(JSON.parse(stored)); } catch {}
    }
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!user) return null;

  const accountOk = user.is_active;

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Account Security</h1>
        <p className="text-gray-500 text-sm mt-1">
          Review your account status, sessions, and security settings
        </p>
      </div>

      {/* Active security notices */}
      {notices.map(key => {
        const n = SAFE_NOTICES.find(x => x.key === key);
        if (!n) return null;
        return (
          <div key={key} className="mb-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl px-5 py-4 flex items-start justify-between gap-4">
            <div>
              <p className="font-semibold text-amber-300 text-sm">{n.label}</p>
              <p className="text-amber-200/70 text-xs mt-1">{n.desc}</p>
            </div>
            <Link
              href={n.href}
              onClick={() => {
                const updated = notices.filter(x => x !== key);
                localStorage.setItem('security_notices', JSON.stringify(updated));
                setNotices(updated);
              }}
              className="shrink-0 text-xs text-amber-300 hover:text-amber-200 font-semibold underline"
            >
              {n.action}
            </Link>
          </div>
        );
      })}

      {/* Security status card */}
      <div className={`rounded-2xl p-6 mb-6 border ${
        accountOk
          ? 'bg-emerald-500/5 border-emerald-500/20'
          : 'bg-red-500/10 border-red-500/30'
      }`}>
        <div className="flex items-center gap-3 mb-2">
          <span className={`w-3 h-3 rounded-full ${accountOk ? 'bg-emerald-400' : 'bg-red-400'}`} />
          <h2 className={`font-semibold text-sm ${accountOk ? 'text-emerald-300' : 'text-red-300'}`}>
            {accountOk ? 'Your account is secure' : 'Account access is restricted'}
          </h2>
        </div>
        <p className={`text-xs ${accountOk ? 'text-emerald-200/60' : 'text-red-200/70'}`}>
          {accountOk
            ? 'No security issues have been detected. Keep your password safe and only use your account on trusted devices.'
            : 'Your account access is currently restricted. Please contact support to restore access.'}
        </p>
      </div>

      {/* Account info */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <h2 className="font-semibold text-sm mb-4">Account Details</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Email</span>
            <span className="text-gray-200">{user.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Name</span>
            <span className="text-gray-200">{user.name || '—'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Account status</span>
            <span className={user.is_active ? 'text-emerald-400' : 'text-red-400'}>
              {user.is_active ? 'Active' : 'Restricted'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Member since</span>
            <span className="text-gray-200">
              {user.created_at ? new Date(user.created_at).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }) : '—'}
            </span>
          </div>
        </div>
        <div className="mt-5 pt-4 border-t border-gray-800">
          <Link
            href="/dashboard/settings"
            className="text-xs text-violet-400 hover:text-violet-300 font-medium"
          >
            Change password in Settings →
          </Link>
        </div>
      </div>

      {/* Active sessions */}
      <div id="sessions" className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-sm">Active Sessions</h2>
          <span className="text-xs text-gray-600">Safe metadata only</span>
        </div>
        <div className="bg-gray-800/50 rounded-xl px-4 py-3 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-200 font-medium">Current session</p>
            <p className="text-xs text-gray-500 mt-0.5">This browser — signed in now</p>
          </div>
          <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">
            Active
          </span>
        </div>
        <p className="text-xs text-gray-600 mt-3">
          If you notice a session you don&apos;t recognise, sign out and change your password immediately.
        </p>
        <div className="mt-4 flex gap-3">
          <Link
            href="/dashboard/settings"
            className="px-4 py-2 text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl font-medium transition-colors"
          >
            Change password
          </Link>
          <Link
            href="/dashboard/support"
            className="px-4 py-2 text-xs text-violet-400 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/20 rounded-xl font-medium transition-colors"
          >
            Report suspicious activity
          </Link>
        </div>
      </div>

      {/* Package access */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <h2 className="font-semibold text-sm mb-3">Package Access</h2>
        <p className="text-xs text-gray-500 leading-relaxed">
          Your purchased package is tied to your account. Do not share your login credentials or use
          your account from shared or public devices. If you believe your package access has been
          compromised, contact support immediately.
        </p>
        <div className="mt-4">
          <p className="text-xs text-gray-600">
            If you see the message &quot;This package is already active in another environment&quot;,
            please sign out, sign back in, and contact support if the issue persists.
          </p>
        </div>
      </div>

      {/* Help */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <h2 className="font-semibold text-sm mb-3">Need help?</h2>
        <div className="flex gap-3 flex-wrap">
          <Link
            href="/dashboard/support"
            className="px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            Contact support
          </Link>
          <Link
            href="/dashboard/settings"
            className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-xl text-xs font-medium transition-colors"
          >
            Account settings
          </Link>
        </div>
      </div>
    </div>
  );
}
