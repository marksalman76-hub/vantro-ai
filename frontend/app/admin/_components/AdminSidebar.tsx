'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const NAV = [
  { href: '/admin',           label: 'Command Center',  icon: '◈' },
  { href: '/admin/clients',   label: 'Clients',         icon: '◉' },
  { href: '/admin/jobs',      label: 'Jobs',            icon: '⬡' },
  { href: '/admin/agents',    label: 'Agents',          icon: '◆' },
  { href: '/admin/billing',   label: 'Billing',         icon: '◇' },
  { href: '/admin/providers', label: 'Providers',       icon: '◎' },
  { href: '/admin/aws',       label: 'AWS Infra',       icon: '▣' },
  { href: '/admin/audit',     label: 'Audit Logs',      icon: '≡' },
];

export default function AdminSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function signOut() {
    localStorage.removeItem('token');
    router.push('/login');
  }

  return (
    <aside className="w-56 min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800">
        <Link href="/admin" className="flex items-center gap-2.5">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <div>
            <p className="font-bold text-white text-sm leading-none">Vantro</p>
            <p className="text-xs text-violet-400 leading-none mt-0.5">Admin</p>
          </div>
        </Link>
        <span className="mt-2 inline-block text-[10px] font-semibold text-gray-600 bg-gray-800 px-2 py-0.5 rounded-full tracking-widest uppercase">Internal</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map((item) => {
          const active = item.href === '/admin'
            ? pathname === '/admin'
            : pathname?.startsWith(item.href) ?? false;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? 'bg-violet-600/20 text-violet-300'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <span className="text-base leading-none opacity-70">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 pb-4 space-y-1">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
        >
          ← Client view
        </Link>
        <button
          onClick={signOut}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors text-left"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
