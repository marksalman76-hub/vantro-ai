'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Job {
  id: string;
  status: string;
  client_email: string;
  client_id: string | null;
  created_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

interface Client {
  id: string;
  email: string;
  subscription_status: string | null;
  created_at: string | null;
  is_active: boolean;
}

interface AuditEvent {
  time: string;
  type: string;
  actor: string;
  detail: string;
  link?: string;
  severity: 'info' | 'success' | 'warning' | 'error';
}

const SEV_STYLE: Record<string, string> = {
  info:    'text-gray-400',
  success: 'text-green-400',
  warning: 'text-yellow-400',
  error:   'text-red-400',
};

const SEV_DOT: Record<string, string> = {
  info:    'bg-gray-600',
  success: 'bg-green-400',
  warning: 'bg-yellow-400',
  error:   'bg-red-400',
};

export default function AdminAuditPage() {
  const router = useRouter();
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin/login'); return; }

    Promise.all([
      fetch('/api/admin/jobs', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/admin/clients', { headers: { Authorization: `Bearer ${token}` } }),
    ])
      .then(async ([jr, cr]) => {
        if (jr.status === 403) { router.push('/dashboard'); return; }
        const [jd, cd] = await Promise.all([jr.json(), cr.json()]);
        const jobs: Job[] = jd.jobs || [];
        const clients: Client[] = cd.clients || [];

        const ev: AuditEvent[] = [];

        // Job events
        for (const j of jobs) {
          if (j.status === 'completed' && j.completed_at) {
            ev.push({ time: j.completed_at, type: 'Job completed', actor: j.client_email, detail: `Job ${j.id.slice(0, 8)}… completed`, link: `/admin/clients/${j.client_id}`, severity: 'success' });
          }
          if (j.status === 'failed' && j.created_at) {
            ev.push({ time: j.created_at, type: 'Job failed', actor: j.client_email, detail: j.error_message ? `${j.id.slice(0, 8)}… — ${j.error_message.slice(0, 60)}` : `Job ${j.id.slice(0, 8)}… failed`, link: `/admin/clients/${j.client_id}`, severity: 'error' });
          }
          if ((j.status === 'pending' || j.status === 'processing') && j.created_at) {
            ev.push({ time: j.created_at, type: 'Job queued', actor: j.client_email, detail: `Job ${j.id.slice(0, 8)}… queued for processing`, link: `/admin/clients/${j.client_id}`, severity: 'info' });
          }
        }

        // Client events
        for (const c of clients) {
          if (c.created_at) {
            ev.push({ time: c.created_at, type: 'Account created', actor: c.email, detail: `New account registered`, link: `/admin/clients/${c.id}`, severity: 'info' });
          }
          if (c.subscription_status === 'active') {
            ev.push({ time: c.created_at || '', type: 'Subscription activated', actor: c.email, detail: `Plan activated`, link: `/admin/clients/${c.id}`, severity: 'success' });
          }
          if (!c.is_active) {
            ev.push({ time: c.created_at || '', type: 'Account suspended', actor: c.email, detail: `Account is suspended`, link: `/admin/clients/${c.id}`, severity: 'warning' });
          }
        }

        // Sort by time descending
        ev.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());
        setEvents(ev.slice(0, 100));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Audit Logs</h1>
        <p className="text-gray-500 text-sm mt-1">Recent platform activity — jobs, accounts, and billing events</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="divide-y divide-gray-800/50">
          {events.map((e, i) => (
            <div key={i} className="flex items-start gap-4 px-6 py-4 hover:bg-gray-800/20 transition-colors">
              <div className="mt-1.5 shrink-0">
                <span className={`inline-block w-2 h-2 rounded-full ${SEV_DOT[e.severity]}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2 flex-wrap">
                  <span className={`text-xs font-semibold ${SEV_STYLE[e.severity]}`}>{e.type}</span>
                  <span className="text-gray-500 text-xs truncate">{e.actor}</span>
                </div>
                <p className="text-gray-400 text-xs mt-0.5 truncate">{e.detail}</p>
              </div>
              <div className="shrink-0 text-right">
                <p className="text-gray-600 text-xs">
                  {e.time ? new Date(e.time).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) : '—'}
                </p>
                {e.link && (
                  <Link href={e.link} className="text-xs text-violet-400 hover:text-violet-300 mt-0.5 block">
                    View →
                  </Link>
                )}
              </div>
            </div>
          ))}
          {events.length === 0 && (
            <div className="px-6 py-12 text-center text-gray-600">No activity logged yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
