'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Provider {
  name: string;
  category: string;
  configured: boolean;
  readiness: string;
  notes: string;
  role: 'primary' | 'future';
}

export default function AdminProvidersPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/admin/providers', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        const d = await r.json();
        setProviders(d.providers || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const primary = providers.filter((p) => p.role === 'primary');
  const future = providers.filter((p) => p.role === 'future');

  function ReadinessTag({ status }: { status: string }) {
    const style =
      status === 'ready' ? 'bg-green-400/10 text-green-400 border-green-400/20' :
      status === 'not_configured' ? 'bg-red-400/10 text-red-400 border-red-400/20' :
      'bg-yellow-400/10 text-yellow-400 border-yellow-400/20';
    const label =
      status === 'ready' ? 'Ready' :
      status === 'not_configured' ? 'Not configured' : status;
    return (
      <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${style}`}>{label}</span>
    );
  }

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Provider Health</h1>
        <p className="text-gray-500 text-sm mt-1">Live provider configuration and readiness status. API keys are not shown.</p>
      </div>

      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Active Providers</p>
      <div className="space-y-3 mb-8">
        {primary.map((p) => (
          <div key={p.name} className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <p className="font-semibold text-white">{p.name}</p>
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">{p.category}</span>
              </div>
              <p className="text-gray-500 text-xs">{p.notes}</p>
              <p className="text-gray-700 text-xs mt-1">Credential: {p.configured ? '••••••• present' : 'missing'}</p>
            </div>
            <div className="shrink-0">
              <ReadinessTag status={p.readiness} />
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-3">Future Providers</p>
      <div className="space-y-3">
        {future.map((p) => (
          <div key={p.name} className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-5 flex items-start justify-between gap-4 opacity-60">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <p className="font-medium text-gray-400">{p.name}</p>
                <span className="text-xs text-gray-600 bg-gray-800/50 px-2 py-0.5 rounded-full">{p.category}</span>
              </div>
              <p className="text-gray-600 text-xs">{p.notes}</p>
            </div>
            <div className="shrink-0">
              <ReadinessTag status={p.readiness} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
