'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';

const NAV = [
  { href: '/admin',              label: 'Command Center',     icon: '◈', exact: true },
  { href: '/admin/clients',      label: 'Clients',            icon: '◉' },
  { href: '/admin/jobs',         label: 'Jobs & Executions',  icon: '⬡' },
  { href: '/admin/agents',       label: 'Agents',             icon: '◆' },
  { href: '/admin/agent-jobs',   label: 'Agent Jobs',         icon: '◈' },
  { href: '/admin/packages',     label: 'Packages & Access',  icon: '▤' },
  { href: '/admin/billing',      label: 'Billing & Credits',  icon: '◇' },
  { href: '/admin/assets',        label: 'Assets & Outputs',   icon: '▣' },
  { href: '/admin/create-media',  label: 'Create Media',       icon: '▶' },
  { href: '/admin/brand-assets',  label: 'Brand Assets',       icon: '◈' },
  { href: '/admin/reports',      label: 'Client Reports',     icon: '◈' },
  { href: '/admin/approvals',      label: 'Approvals',            icon: '◬' },
  { href: '/admin/announcements',  label: 'Announcements',        icon: '◎' },
  { href: '/admin/status',         label: 'System Status',        icon: '◉' },
  { href: '/admin/providers',      label: 'Providers',            icon: '◎' },
  { href: '/admin/aws',          label: 'AWS Infrastructure', icon: '▲' },
  { href: '/admin/security',     label: 'Security Alerts',    icon: '⚠', alert: true },
  { href: '/admin/support',      label: 'Support & Incidents',icon: '◍' },
  { href: '/admin/audit',        label: 'Audit Logs',         icon: '≡' },
  { href: '/admin/downloads',    label: 'OTC Downloads',      icon: '⬇' },
  { href: '/admin/settings',     label: 'Settings & Governance', icon: '⚙' },
];

export default function AdminSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);

  async function signOut() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('token');
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    } catch {
      // Local session state is already cleared; continue to login.
    }
    router.replace('/admin-login');
  }

  return (
    <aside
      className={`${collapsed ? 'w-14' : 'w-56'} min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col shrink-0 sticky top-0 h-screen overflow-y-auto transition-all duration-200`}
    >
      {/* Logo + collapse toggle */}
      <div className="px-3 py-4 border-b border-gray-800 shrink-0 flex items-center justify-between">
        {!collapsed && (
          <Link href="/admin" className="flex items-center gap-2.5 min-w-0">
            <span className="w-7 h-7 shrink-0 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
            <div className="min-w-0">
              <p className="font-bold text-white text-sm leading-none">Vantro</p>
              <p className="text-xs text-red-400 leading-none mt-0.5">Admin</p>
            </div>
          </Link>
        )}
        {collapsed && (
          <Link href="/admin" className="mx-auto">
            <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          </Link>
        )}
        <button
          onClick={() => setCollapsed(c => !c)}
          className={`${collapsed ? 'mx-auto mt-2' : ''} shrink-0 w-6 h-6 rounded-md flex items-center justify-center text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors text-xs`}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? '›' : '‹'}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {NAV.map((item) => {
          const active = item.exact
            ? pathname === item.href
            : pathname?.startsWith(item.href) ?? false;
          return (
            <Link key={item.href} href={item.href}
              title={collapsed ? item.label : undefined}
              className={`flex items-center gap-2.5 px-2 py-2 rounded-lg text-xs font-medium transition-colors ${
                collapsed ? 'justify-center' : ''
              } ${
                active ? 'bg-violet-600/20 text-violet-300' : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <span className={`text-sm leading-none shrink-0 ${item.alert ? 'text-red-400' : 'opacity-60'}`}>{item.icon}</span>
              {!collapsed && <span className={item.alert && !active ? 'text-red-300' : ''}>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="px-3 pb-4 pt-3 border-t border-gray-800 shrink-0 space-y-1">
          <Link href="/dashboard" prefetch={false}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors">
            ← Client view
          </Link>
          <button onClick={signOut}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors text-left">
            Sign out
          </button>
        </div>
      )}
      {collapsed && (
        <div className="px-2 pb-4 pt-3 border-t border-gray-800 shrink-0 space-y-1">
          <Link href="/dashboard" prefetch={false} title="Client view"
            className="flex justify-center px-2 py-2 rounded-lg text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors">
            ←
          </Link>
          <button onClick={signOut} title="Sign out"
            className="w-full flex justify-center px-2 py-2 rounded-lg text-xs text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors">
            ✕
          </button>
        </div>
      )}
    </aside>
  );
}
