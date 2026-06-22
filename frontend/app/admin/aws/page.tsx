'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Service {
  name: string;
  status: string;
  detail: string;
}

interface Infra {
  environment: string;
  region: string;
  account_id: string;
  services: Service[];
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === 'running' || status === 'configured' ? 'bg-green-400' :
    status === 'not_configured' ? 'bg-red-400' : 'bg-yellow-400';
  return <span className={`inline-block w-2 h-2 rounded-full ${color} mr-2`} />;
}

export default function AdminAWSPage() {
  const router = useRouter();
  const [infra, setInfra] = useState<Infra | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/admin/infrastructure', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (r.status === 403) { router.push('/dashboard'); return; }
        setInfra(await r.json());
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!infra) return null;

  const running = infra.services.filter((s) => s.status === 'running' || s.status === 'configured').length;
  const total = infra.services.length;

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">AWS Infrastructure</h1>
        <p className="text-gray-500 text-sm mt-1">Production environment — AWS Option A</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Environment</p>
          <p className="text-white font-semibold capitalize">{infra.environment}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Region</p>
          <p className="text-white font-semibold">{infra.region}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-gray-500 text-xs mb-1">Services ready</p>
          <p className={`text-2xl font-bold ${running === total ? 'text-green-400' : 'text-yellow-400'}`}>
            {running} / {total}
          </p>
        </div>
      </div>

      {/* Service list */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="font-semibold">Service Status</h2>
          <p className="text-gray-600 text-xs mt-0.5">Internal view only — not visible to clients</p>
        </div>
        <div className="divide-y divide-gray-800">
          {infra.services.map((s) => (
            <div key={s.name} className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center">
                <StatusDot status={s.status} />
                <div>
                  <p className="text-sm text-white font-medium">{s.name}</p>
                  <p className="text-xs text-gray-500">{s.detail}</p>
                </div>
              </div>
              <span className={`text-xs font-medium capitalize px-2.5 py-1 rounded-full ${
                s.status === 'running' ? 'bg-green-400/10 text-green-400' :
                s.status === 'configured' ? 'bg-blue-400/10 text-blue-400' :
                s.status === 'not_configured' ? 'bg-red-400/10 text-red-400' :
                'bg-gray-700 text-gray-400'
              }`}>
                {s.status.replace('_', ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>

      <p className="mt-4 text-xs text-gray-700">Account: {infra.account_id} · Secrets are not displayed here.</p>
    </div>
  );
}
