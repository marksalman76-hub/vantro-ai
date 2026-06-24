'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

type ComponentStatus = 'operational' | 'degraded' | 'maintenance' | 'outage';

interface SystemComponent { name: string; status: ComponentStatus; description: string; }
interface StatusData {
  overall: ComponentStatus;
  message: string | null;
  components: SystemComponent[];
  updated_at: string | null;
}

const OVERALL_CONFIG: Record<ComponentStatus, { label: string; color: string; dot: string; bg: string }> = {
  operational: { label: 'All systems operational',       color: 'text-emerald-400', dot: 'bg-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  degraded:    { label: 'Some systems degraded',         color: 'text-amber-400',   dot: 'bg-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20' },
  maintenance: { label: 'Scheduled maintenance',         color: 'text-orange-400',  dot: 'bg-orange-400',  bg: 'bg-orange-500/10 border-orange-500/20' },
  outage:      { label: 'Service disruption in progress',color: 'text-red-400',     dot: 'bg-red-500',     bg: 'bg-red-500/10 border-red-500/20' },
};

const COMPONENT_STATUS: Record<ComponentStatus, { label: string; color: string; dot: string }> = {
  operational: { label: 'Operational', color: 'text-emerald-400', dot: 'bg-emerald-400' },
  degraded:    { label: 'Degraded',    color: 'text-amber-400',   dot: 'bg-amber-400'   },
  maintenance: { label: 'Maintenance', color: 'text-orange-400',  dot: 'bg-orange-400'  },
  outage:      { label: 'Outage',      color: 'text-red-400',     dot: 'bg-red-500'     },
};

export default function StatusPage() {
  const [data, setData]       = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/platform/status')
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setData(d); })
      .finally(() => setLoading(false));
  }, []);

  const cfg = data ? OVERALL_CONFIG[data.overall] : OVERALL_CONFIG.operational;

  return (
    <div className="min-h-screen bg-[#080808] text-white">
      {/* Nav */}
      <nav className="border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-white font-bold text-lg tracking-tight">Vantro</Link>
        <Link href="/login" className="text-gray-400 hover:text-white text-sm transition-colors">Sign in →</Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-3xl font-bold text-white mb-2">System Status</h1>
        <p className="text-gray-400 text-sm mb-10">Real-time status of the Vantro platform and services.</p>

        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />)}
          </div>
        ) : data ? (
          <>
            {/* Overall banner */}
            <div className={`border rounded-2xl p-5 mb-8 flex items-center gap-4 ${cfg.bg}`}>
              <span className={`w-3 h-3 rounded-full flex-shrink-0 ${cfg.dot} ${data.overall !== 'operational' ? 'animate-pulse' : ''}`} />
              <div className="flex-1">
                <p className={`font-semibold ${cfg.color}`}>{cfg.label}</p>
                {data.message && <p className="text-sm text-gray-300 mt-0.5">{data.message}</p>}
              </div>
              {data.updated_at && (
                <p className="text-xs text-gray-500 shrink-0">
                  Updated {new Date(data.updated_at).toLocaleString()}
                </p>
              )}
            </div>

            {/* Components */}
            <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden mb-10">
              <div className="px-5 py-3 border-b border-white/5">
                <h2 className="text-sm font-semibold text-white">Platform Components</h2>
              </div>
              <div className="divide-y divide-white/5">
                {data.components.map(c => {
                  const cs = COMPONENT_STATUS[c.status];
                  return (
                    <div key={c.name} className="px-5 py-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${cs.dot}`} />
                        <span className="text-white text-sm font-medium">{c.name}</span>
                        {c.description && (
                          <span className="text-gray-500 text-xs">{c.description}</span>
                        )}
                      </div>
                      <span className={`text-xs font-medium ${cs.color}`}>{cs.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Uptime note */}
            <div className="text-center">
              <p className="text-gray-600 text-xs">
                Issues? Contact <a href="mailto:support@vantro.ai" className="text-gray-400 hover:text-white">support@vantro.ai</a>
              </p>
            </div>
          </>
        ) : (
          <div className="text-gray-500 text-sm">Could not load status. Try refreshing.</div>
        )}
      </div>
    </div>
  );
}
