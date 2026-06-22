'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const NAV = [
  { href: '/admin',              label: 'Command Center',    icon: '◈', exact: true },
  { href: '/admin/clients',      label: 'Clients',           icon: '◉' },
  { href: '/admin/jobs',         label: 'Jobs & Executions', icon: '⬡' },
  { href: '/admin/agents',       label: 'Agents',            icon: '◆' },
  { href: '/admin/agent-jobs',   label: 'Agent Jobs',        icon: '◈' },
  { href: '/admin/packages',     label: 'Packages & Access', icon: '▤' },
  { href: '/admin/billing',      label: 'Billing & Credits', icon: '◇' },
  { href: '/admin/assets',       label: 'Assets & Outputs',  icon: '▣' },
  { href: '/admin/approvals',    label: 'Approvals',         icon: '◬' },
  { href: '/admin/providers',    label: 'Providers',         icon: '◎' },
  { href: '/admin/aws',          label: 'AWS Infrastructure', icon: '▲' },
  { href: '/admin/support',      label: 'Support & Incidents',icon: '◍' },
  { href: '/admin/audit',        label: 'Audit Logs',        icon: '≡' },
  { href: '/admin/downloads',    label: 'OTC Downloads',     icon: '⬇' },
];

export default function AdminSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function signOut() {
    localStorage.removeItem('admin_token');
    router.push('/admin-login');
  }

  return (
    <aside className="w-56 min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col shrink-0 sticky top-0 h-screen overflow-y-auto">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800 shrink-0">
        <Link href="/admin" className="flex items-center gap-2.5">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <div>
            <p className="font-bold text-white text-sm leading-none">Vantro</p>
            <p className="text-xs text-red-400 leading-none mt-0.5">Admin</p>
          </div>
        </Link>
        <span className="mt-2 inline-block text-[9px] font-bold text-gray-600 bg-gray-800 px-2 py-0.5 rounded-full tracking-widest uppercase border border-gray-700">Internal</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 space-y-0.5">
        {NAV.map((item) => {
          const active = item.exact
            ? pathname === item.href
            : pathname?.startsWith(item.href) ?? false;
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                active ? 'bg-violet-600/20 text-violet-300' : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <span className="text-sm leading-none opacity-60">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 pb-4 pt-3 border-t border-gray-800 shrink-0 space-y-1">
        <Link href="/dashboard"
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors">
          ← Client view
        </Link>
        <button onClick={signOut}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors text-left">
          Sign out
        </button>
      </div>
    </aside>
  );
}
