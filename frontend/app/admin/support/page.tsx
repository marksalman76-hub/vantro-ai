'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Ticket {
  id: string;
  client: string;
  subject: string;
  type: 'failed_job' | 'billing' | 'credit_review' | 'general' | 'incident';
  status: 'open' | 'in_progress' | 'resolved' | 'escalated';
  job_id?: string;
  created_at: string;
  last_updated: string;
}

const TYPE_STYLE: Record<string, string> = {
  failed_job:    'text-red-400 bg-red-500/10 border-red-500/20',
  billing:       'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  credit_review: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  general:       'text-blue-400 bg-blue-500/10 border-blue-500/20',
  incident:      'text-red-400 bg-red-500/10 border-red-500/20',
};
const STATUS_STYLE: Record<string, string> = {
  open:        'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  in_progress: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  resolved:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  escalated:   'text-red-400 bg-red-500/10 border-red-500/20',
};

const MOCK: Ticket[] = [
  { id:'TKT-001', client:'Acme Corp', subject:'Video generation failed — credits not returned', type:'failed_job', status:'open', job_id:'job_abc123', created_at:'2026-06-22T09:00:00Z', last_updated:'2026-06-22T09:00:00Z' },
  { id:'TKT-002', client:'Blue Sky Studio', subject:'Incorrect charge on invoice #INV-055', type:'billing', status:'in_progress', created_at:'2026-06-21T14:00:00Z', last_updated:'2026-06-22T07:00:00Z' },
  { id:'TKT-003', client:'RetailPros', subject:'Credit deduction for email that did not send', type:'credit_review', status:'open', created_at:'2026-06-21T11:00:00Z', last_updated:'2026-06-21T11:00:00Z' },
  { id:'TKT-004', client:'GrowthCo', subject:'Agent returned empty output on second attempt', type:'general', status:'resolved', created_at:'2026-06-20T16:00:00Z', last_updated:'2026-06-21T10:00:00Z' },
];

export default function AdminSupportPage() {
  const router = useRouter();
  const [tickets, setTickets] = useState<Ticket[]>(MOCK);
  const [filter, setFilter] = useState<string>('open');
  const [selected, setSelected] = useState<Ticket | null>(null);

  useEffect(() => { const t = localStorage.getItem('token'); if (!t) router.push('/admin-login'); }, [router]);

  const resolve = (id: string) => setTickets(prev => prev.map(t => t.id === id ? { ...t, status: 'resolved' } : t));

  const visible = tickets.filter(t => filter === 'all' || t.status === filter);
  const open = tickets.filter(t => t.status === 'open' || t.status === 'escalated').length;

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold text-white">Support & Incidents</h1>
          {open > 0 && <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{open}</span>}
        </div>
        <p className="text-gray-500 text-sm">Client support tickets, failed job reviews, billing disputes, and incident management</p>
      </div>

      <div className="flex gap-2 mb-6">
        {(['open','in_progress','resolved','all'] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${filter === f ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
            {f.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-3">
        {visible.length === 0 && <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 text-center text-gray-600 text-sm">No tickets.</div>}
        {visible.map(ticket => (
          <div key={ticket.id} className={`bg-gray-900 border rounded-2xl p-5 cursor-pointer hover:border-gray-700 transition-colors ${selected?.id === ticket.id ? 'border-violet-500/40' : 'border-gray-800'}`}
            onClick={() => setSelected(selected?.id === ticket.id ? null : ticket)}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap mb-1.5">
                  <span className="text-xs font-mono text-gray-600">{ticket.id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${STATUS_STYLE[ticket.status]}`}>{ticket.status.replace('_', ' ')}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${TYPE_STYLE[ticket.type]}`}>{ticket.type.replace('_', ' ')}</span>
                </div>
                <p className="text-white text-sm font-medium">{ticket.subject}</p>
                <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                  <span>Client: <span className="text-gray-300">{ticket.client}</span></span>
                  {ticket.job_id && <><span>·</span><span>Job: <span className="text-gray-300 font-mono text-[10px]">{ticket.job_id}</span></span></>}
                  <span>·</span>
                  <span>{new Date(ticket.created_at).toLocaleString()}</span>
                </div>
              </div>
              <span className="text-gray-600 text-lg">{selected?.id === ticket.id ? '▲' : '▼'}</span>
            </div>

            {selected?.id === ticket.id && (
              <div className="mt-4 pt-4 border-t border-gray-800">
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <button onClick={e => { e.stopPropagation(); resolve(ticket.id); }}
                    className="py-2 rounded-lg text-xs font-semibold bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-600/30 transition-colors">
                    Mark resolved
                  </button>
                  <button className="py-2 rounded-lg text-xs font-semibold bg-violet-600/20 border border-violet-500/30 text-violet-400 hover:bg-violet-600/30 transition-colors">
                    Retry job
                  </button>
                  <button className="py-2 rounded-lg text-xs font-semibold bg-orange-600/20 border border-orange-500/30 text-orange-400 hover:bg-orange-600/30 transition-colors">
                    Refund credits
                  </button>
                </div>
                <textarea placeholder="Add internal note…" rows={3}
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500" />
                <button className="mt-2 px-4 py-1.5 rounded-lg text-xs font-medium bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors">Add note</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
