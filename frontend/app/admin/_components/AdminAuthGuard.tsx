'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminAuthGuard({ children, sidebar }: { children: React.ReactNode; sidebar: React.ReactNode }) {
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'authed'>('loading');

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

    fetch('/api/admin/clients', { headers, credentials: 'include' })
      .then((res) => {
        if (res.ok) {
          setStatus('authed');
          return;
        }
        localStorage.removeItem('admin_token');
        localStorage.removeItem('token');
        router.replace('/admin-login');
      })
      .catch(() => {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('token');
        router.replace('/admin-login');
      });
  }, [router]);

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
