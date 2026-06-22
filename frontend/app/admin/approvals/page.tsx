'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Approval {
  id: string;
  type: string;
  client: string;
  agent: string;
  description: string;
  cost_estimate: string;
  risk: 'high' | 'medium' | 'low';
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

const RISK_STYLE: Record<string, string> = {
  high: 'text-red-400 bg-red-500/10 border-red-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};
const STATUS_STYLE: Record<string, string> = {
  pending: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  approved: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  rejected: 'text-red-400 bg-red-500/10 border-red-500/20',
};

const MOCK: Approval[] = [
  { id:'APR-001', type:'Provider spend', client:'Acme Corp', agent:'Ads Optimisation Agent', description:'Launch Meta Ads campaign with $200 budget', cost_estimate:'$200 provider spend', risk:'high', status:'pending', created_at:'2026-06-22T10:00:00Z' },
  { id:'APR-002', type:'Long media generation', client:'Blue Sky Studio', agent:'UGC Media Agent', description:'Generate 90-second product video', cost_estimate:'~$0.40 provider cost', risk:'medium', status:'pending', created_at:'2026-06-22T09:30:00Z' },
  { id:'APR-003', type:'Credit mutation', client:'Founder Mode', agent:'Admin', description:'Grant 500 extra credits — billing dispute resolution', cost_estimate:'500 credits', risk:'medium', status:'pending', created_at:'2026-06-22T08:00:00Z' },
  { id:'APR-004', type:'CRM write', client:'GrowthCo', agent:'CRM Agent', description:'Bulk update 450 contact records in GoHighLevel', cost_estimate:'0 provider cost', risk:'medium', status:'approved', created_at:'2026-06-21T17:00:00Z' },
  { id:'APR-005', type:'Email send', client:'RetailPros', agent:'Email Reply Agent', description:'Send campaign to 1,200 subscribers', cost_estimate:'~$0.06 Brevo', risk:'high', status:'rejected', created_at:'2026-06-21T14:00:00Z' },
];

export default function AdminApprovalsPage() {
  const router = useRouter();
  const [approvals, setApprovals] = useState<Approval[]>(MOCK);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('pending');
  const [acting, setActing] = useState<string | null>(null);

  useEffect(() => { const t = localStorage.getItem('admin_token'); if (!t) router.push('/admin-login'); }, [router]);

  const act = async (id: string, action: 'approved' | 'rejected') => {
    setActing(id);
    await new Promise(r => setTimeout(r, 500));
    setApprovals(prev => prev.map(a => a.id === id ? { ...a, status: action } : a));
    setActing(null);
  };

  const visible = approvals.filter(a => filter === 'all' || a.status === filter);
  const pending = approvals.filter(a => a.status === 'pending').length;

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold text-white">Approvals</h1>
          {pending > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{pending}</span>
          )}
        </div>
        <p className="text-gray-500 text-sm">All spend, scaling, provider, and credit actions requiring human approval</p>
      </div>

      <div className="flex gap-2 mb-6">
        {(['pending','approved','rejected','all'] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${filter === f ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
            {f} {f === 'pending' && pending > 0 ? `(${pending})` : ''}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {visible.length === 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 text-center text-gray-600 text-sm">No {filter} approvals.</div>
        )}
        {visible.map(appr => (
          <div key={appr.id} className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex items-start gap-5">
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap mb-2">
                <span className="text-xs font-mono text-gray-600">{appr.id}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${STATUS_STYLE[appr.status]}`}>{appr.status}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${RISK_STYLE[appr.risk]}`}>{appr.risk} risk</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-gray-800 border border-gray-700 text-gray-400">{appr.type}</span>
              </div>
              <p className="text-white text-sm font-medium mb-0.5">{appr.description}</p>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>Client: <span className="text-gray-300">{appr.client}</span></span>
                <span>·</span>
                <span>Agent: <span className="text-gray-300">{appr.agent}</span></span>
                <span>·</span>
                <span>Cost: <span className="text-gray-300">{appr.cost_estimate}</span></span>
                <span>·</span>
                <span>{new Date(appr.created_at).toLocaleString()}</span>
              </div>
            </div>
            {appr.status === 'pending' && (
              <div className="flex gap-2 shrink-0">
                <button onClick={() => act(appr.id, 'approved')} disabled={acting === appr.id}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white transition-colors">
                  Approve
                </button>
                <button onClick={() => act(appr.id, 'rejected')} disabled={acting === appr.id}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 text-red-400 transition-colors">
                  Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
