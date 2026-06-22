'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Asset {
  id: string;
  client: string;
  type: 'video' | 'image' | 'audio' | 'script' | 'report' | 'social_post' | 'email' | 'campaign';
  name: string;
  agent: string;
  status: 'visible' | 'hidden' | 'archived';
  consent_required: boolean;
  job_id: string;
  created_at: string;
  size_label: string;
}

const TYPE_ICON: Record<string, string> = {
  video:'▶', image:'▧', audio:'♪', script:'✎', report:'≡', social_post:'◈', email:'✉', campaign:'◆',
};
const TYPE_COLOR: Record<string, string> = {
  video:'text-violet-400 bg-violet-500/10 border-violet-500/20',
  image:'text-blue-400 bg-blue-500/10 border-blue-500/20',
  audio:'text-teal-400 bg-teal-500/10 border-teal-500/20',
  script:'text-gray-300 bg-gray-800 border-gray-700',
  report:'text-amber-400 bg-amber-500/10 border-amber-500/20',
  social_post:'text-pink-400 bg-pink-500/10 border-pink-500/20',
  email:'text-orange-400 bg-orange-500/10 border-orange-500/20',
  campaign:'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
};

const MOCK: Asset[] = [
  { id:'AST-001', client:'Acme Corp', type:'video', name:'Product demo — Summer 2026', agent:'UGC Media Agent', status:'visible', consent_required:true, job_id:'job_v001', created_at:'2026-06-22T10:00:00Z', size_label:'42 MB' },
  { id:'AST-002', client:'Blue Sky Studio', type:'social_post', name:'Instagram campaign brief Q3', agent:'Social Media Agent', status:'visible', consent_required:false, job_id:'job_s002', created_at:'2026-06-21T15:00:00Z', size_label:'3 KB' },
  { id:'AST-003', client:'GrowthCo', type:'report', name:'Q2 analytics breakdown', agent:'Analytics Agent', status:'visible', consent_required:false, job_id:'job_r003', created_at:'2026-06-21T11:00:00Z', size_label:'18 KB' },
  { id:'AST-004', client:'RetailPros', type:'email', name:'Welcome sequence — 5 emails', agent:'Email Reply Agent', status:'hidden', consent_required:false, job_id:'job_e004', created_at:'2026-06-20T09:00:00Z', size_label:'8 KB' },
  { id:'AST-005', client:'Founder Mode', type:'campaign', name:'Full launch campaign plan', agent:'Marketing Specialist Agent', status:'archived', consent_required:false, job_id:'job_c005', created_at:'2026-06-18T14:00:00Z', size_label:'22 KB' },
];

export default function AdminAssetsPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<Asset[]>(MOCK);
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => { const t = localStorage.getItem('token'); if (!t) router.push('/admin-login'); }, [router]);

  const types = ['all', ...Array.from(new Set(MOCK.map(a => a.type)))];
  const visible = assets.filter(a =>
    (typeFilter === 'all' || a.type === typeFilter) &&
    (statusFilter === 'all' || a.status === statusFilter)
  );

  const toggleStatus = (id: string, newStatus: 'visible' | 'hidden') =>
    setAssets(prev => prev.map(a => a.id === id ? { ...a, status: newStatus } : a));

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Assets & Outputs</h1>
        <p className="text-gray-500 text-sm">All client deliverables — control visibility, consent, and access</p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {types.map(t => (
          <button key={t} onClick={() => setTypeFilter(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${typeFilter === t ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
            {TYPE_ICON[t] ?? ''} {t.replace('_', ' ')}
          </button>
        ))}
        <div className="ml-auto flex gap-2">
          {(['all','visible','hidden','archived'] as const).map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${statusFilter === s ? 'bg-gray-700 text-white' : 'bg-gray-800 border border-gray-800 text-gray-500 hover:text-white'}`}>
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-xs text-gray-500">
              {['Asset', 'Client', 'Agent', 'Status', 'Consent', 'Size', 'Created', 'Actions'].map(h => (
                <th key={h} className="px-5 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {visible.length === 0 && (
              <tr><td colSpan={8} className="text-center text-gray-600 text-sm py-10">No assets match filters.</td></tr>
            )}
            {visible.map(asset => (
              <tr key={asset.id} className="hover:bg-gray-800/30 transition-colors">
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${TYPE_COLOR[asset.type]}`}>{TYPE_ICON[asset.type]}</span>
                    <div>
                      <p className="text-white text-xs font-medium">{asset.name}</p>
                      <p className="text-gray-600 text-[10px] font-mono">{asset.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-4 text-gray-300 text-xs">{asset.client}</td>
                <td className="px-5 py-4 text-gray-400 text-xs">{asset.agent}</td>
                <td className="px-5 py-4">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    asset.status === 'visible' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                    asset.status === 'hidden' ? 'text-gray-400 bg-gray-800 border-gray-700' :
                    'text-red-400 bg-red-500/10 border-red-500/20'
                  }`}>{asset.status}</span>
                </td>
                <td className="px-5 py-4">
                  {asset.consent_required
                    ? <span className="text-[10px] font-bold text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 px-2 py-0.5 rounded-full">Required</span>
                    : <span className="text-[10px] text-gray-600">—</span>}
                </td>
                <td className="px-5 py-4 text-gray-500 text-xs">{asset.size_label}</td>
                <td className="px-5 py-4 text-gray-500 text-xs">{new Date(asset.created_at).toLocaleDateString()}</td>
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <button className="text-xs text-violet-400 hover:text-violet-300">Open</button>
                    {asset.status === 'visible'
                      ? <button onClick={() => toggleStatus(asset.id, 'hidden')} className="text-xs text-gray-500 hover:text-yellow-400">Hide</button>
                      : <button onClick={() => toggleStatus(asset.id, 'visible')} className="text-xs text-gray-500 hover:text-emerald-400">Show</button>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
