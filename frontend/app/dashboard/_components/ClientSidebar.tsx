'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { signOut as apiSignOut } from '@/lib/api';

const NAV = [
  { href: '/dashboard',                label: 'Dashboard',        icon: '◈', exact: true },
  { href: '/dashboard/create',         label: 'Create',           icon: '◈' },
  { href: '/dashboard/create-media',   label: 'Create Media',     icon: '▶' },
  { href: '/dashboard/agents',         label: 'My Agents',        icon: '◆' },
  { href: '/dashboard/team',           label: 'Team Builder',     icon: '◉' },
  { href: '/dashboard/jobs',           label: 'Activity',         icon: '⬡' },
  { href: '/dashboard/library',        label: 'Output Library',   icon: '▣' },
  { href: '/dashboard/assets',         label: 'Assets & Outputs', icon: '▧' },
  { href: '/dashboard/brand',          label: 'Brand Profile',    icon: '◎' },
  { href: '/dashboard/billing',        label: 'Billing & Credits',icon: '◇' },
  { href: '/dashboard/reports',        label: 'Weekly Reports',   icon: '◈' },
  { href: '/dashboard/approvals',      label: 'Approvals',        icon: '◬' },
  { href: '/dashboard/security',       label: 'Account Security', icon: '◍' },
  { href: '/dashboard/support',        label: 'Support',          icon: '◎' },
  { href: '/dashboard/settings',       label: 'Settings',         icon: '◌' },
];

export default function ClientSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [credits, setCredits] = useState<{ used: number; total: number } | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    fetch('/api/dashboard/stats', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.ok ? r.json() : null)
      .then((d) => {
        if (d?.credits_used !== undefined && d?.credits_total !== undefined) {
          setCredits({ used: d.credits_used, total: d.credits_total });
        }
      })
      .catch(() => {});
  }, []);

  function signOut() {
    apiSignOut();
  }

  return (
    <aside
      className="w-56 min-h-screen flex flex-col shrink-0 sticky top-0 h-screen"
      style={{
        background: 'rgba(7,10,25,0.85)',
        borderRight: '1px solid rgba(255,255,255,0.07)',
        backdropFilter: 'blur(20px) saturate(1.4)',
      }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b border-white/[0.06]">
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-black text-xs transition-all group-hover:scale-105"
            style={{ background: 'linear-gradient(135deg,#7C3AED,#3B82F6)', boxShadow: '0 0 14px rgba(124,58,237,0.4)' }}
          >V</div>
          <div>
            <p className="font-bold text-white text-sm leading-none">Vantro</p>
            <p className="text-[10px] text-violet-400 leading-none mt-0.5 tracking-wide">Workspace</p>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map((item) => {
          const active = item.exact
            ? pathname === item.href
            : pathname?.startsWith(item.href) ?? false;
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                active
                  ? 'bg-violet-500/15 text-violet-300 border border-violet-500/20 shadow-[0_0_12px_rgba(124,58,237,0.12)]'
                  : 'text-white/40 hover:text-white/80 hover:bg-white/[0.05] border border-transparent'
              }`}
            >
              <span className={`text-base leading-none transition-opacity ${active ? 'opacity-100' : 'opacity-50'}`}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Credit balance */}
      {credits && (
        <div className="px-4 py-3 border-t border-white/[0.06]">
          <div className="flex justify-between text-xs text-white/40 mb-1.5">
            <span>Credits</span>
            <span className={credits.total - credits.used <= 5 ? 'text-red-400 font-semibold' : 'text-white/60'}>
              {credits.total - credits.used} / {credits.total}
            </span>
          </div>
          <div className="w-full bg-white/[0.07] rounded-full h-1.5">
            <div
              className={`h-1.5 rounded-full transition-all ${
                (credits.used / credits.total) > 0.8 ? 'bg-red-500' :
                (credits.used / credits.total) > 0.6 ? 'bg-amber-500' : 'bg-violet-500'
              }`}
              style={{
                width: `${Math.min(100, (credits.used / credits.total) * 100)}%`,
                boxShadow: '0 0 8px rgba(124,58,237,0.5)',
              }}
            />
          </div>
          {credits.total - credits.used <= 5 && (
            <p className="text-[10px] text-red-400 mt-1.5">Low credits — upgrade soon</p>
          )}
        </div>
      )}

      {/* Quick actions */}
      <div className="px-3 py-3 border-t border-white/[0.06] space-y-0.5">
        <Link href="/status" target="_blank"
          className="flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-gray-500 hover:text-white hover:bg-white/5 transition-all border border-transparent">
          ◉ System status
        </Link>
        <Link href="/pricing"
          className="flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-violet-400 hover:text-violet-300 hover:bg-violet-600/10 transition-all font-semibold border border-transparent hover:border-violet-500/20">
          ↑ Upgrade plan
        </Link>
        <button onClick={signOut}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-white/30 hover:text-red-400 hover:bg-red-500/[0.06] transition-all text-left border border-transparent">
          Sign out
        </button>
      </div>
    </aside>
  );
}
