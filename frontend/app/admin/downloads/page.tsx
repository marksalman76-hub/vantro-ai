'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Download {
  id: string;
  package_name: string;
  otc_code: string;
  is_used: boolean;
  used_at: string | null;
  expires_at: string | null;
  ip_address: string | null;
  created_at: string | null;
  client_email: string;
  workspace: string | null;
}

export default function AdminDownloadsPage() {
  const router = useRouter();
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin-login'); return; }
    fetch('/api/admin/packages/downloads', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        const d = await r.json();
        setDownloads(d.downloads || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const used = downloads.filter((d) => d.is_used).length;
  const unused = downloads.length - used;

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-7">
        <h1 className="text-2xl font-bold">OTC Package Downloads</h1>
        <p className="text-gray-500 text-sm mt-1">
          {downloads.length} total · {used} redeemed · {unused} pending
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Package</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">OTC Code</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Client</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Generated</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">Used at</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold">IP</th>
            </tr>
          </thead>
          <tbody>
            {downloads.map((d) => (
              <tr key={d.id} className="border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors">
                <td className="px-4 py-3">
                  <p className="text-white text-xs font-medium capitalize">{d.package_name}</p>
                </td>
                <td className="px-4 py-3">
                  <code className="text-[10px] text-gray-400 font-mono bg-gray-800 px-1.5 py-0.5 rounded">
                    {d.otc_code}
                  </code>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    d.is_used
                      ? 'bg-green-500/10 text-green-400'
                      : 'bg-yellow-500/10 text-yellow-400'
                  }`}>
                    {d.is_used ? 'Redeemed' : 'Pending'}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-400">{d.client_email}</td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {d.created_at ? new Date(d.created_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {d.used_at ? new Date(d.used_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3 text-xs text-gray-600 font-mono">{d.ip_address || '—'}</td>
              </tr>
            ))}
            {downloads.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-gray-600 text-sm">No package downloads yet</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
