'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function AdminAuthGuard({ children, sidebar }: { children: React.ReactNode; sidebar: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [status, setStatus] = useState<'loading' | 'authed' | 'login'>('loading');

  useEffect(() => {
    if (pathname === '/admin/login') { setStatus('login'); return; }
    const token = localStorage.getItem('admin_token');
    if (!token) {
      router.replace('/admin/login');
    } else {
      setStatus('authed');
    }
  }, [pathname, router]);

  if (status === 'login') return <>{children}</>;

  if (status === 'loading') return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white flex">
      {sidebar}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
