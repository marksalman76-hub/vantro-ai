'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface Asset {
  id: string;
  client: string;
  type: 'video' | 'image' | 'audio' | 'script' | 'report' | 'social_post' | 'email' | 'campaign';
  name: string;
  agent: string;
  status: 'visible' | 'hidden' | 'archived';
  job_status: string;
  error_message?: string;
  consent_required: boolean;
  job_id: string;
  created_at: string;
  completed_at?: string;
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

const AGENT_TYPE_MAP: Record<string, Asset['type']> = {
  ugc_media: 'video', ugc: 'video', video: 'video',
  social: 'social_post', social_media: 'social_post',
  email: 'email', email_reply: 'email',
  analytics: 'report', report: 'report',
  marketing: 'campaign', campaign: 'campaign',
  audio: 'audio', script: 'script', image: 'image',
};

function inferType(agentId = '', agentName = ''): Asset['type'] {
  const key = (agentId + '_' + agentName).toLowerCase();
  for (const [k, v] of Object.entries(AGENT_TYPE_MAP)) {
    if (key.includes(k)) return v;
  }
  return 'report';
}

interface JobDetail {
  name: string;
  output: string;
  agent: string;
  status: string;
  error_message?: string;
  created_at: string;
}

interface MediaGenerationOutput {
  type?: string;
  requested_agent_id?: string;
  script?: string;
  preview_url?: string;
  download_url?: string;
  asset_url?: string;
  real_media_asset_created?: boolean;
  preview_ready?: boolean;
  download_ready?: boolean;
  provider_readiness?: {
    execution_mode?: string;
    provider_ready?: boolean;
    message?: string;
    selected_video_provider?: string | null;
    selected_video_model?: string | null;
    selected_image_provider?: string | null;
    selected_image_model?: string | null;
    next_steps?: string[];
  };
}

function cleanOutput(output: string) {
  return output.replace(/^<!-- provider:.*? -->\n/, '').trim();
}

function parseMediaGenerationOutput(output: string): MediaGenerationOutput | null {
  const clean = cleanOutput(output);
  if (!clean.startsWith('{')) return null;
  try {
    const parsed = JSON.parse(clean);
    return parsed?.type === 'media_generation' ? parsed : null;
  } catch {
    return null;
  }
}

function jobStatusClass(status: string) {
  const normalized = status.toLowerCase();
  if (normalized === 'completed') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
  if (['failed', 'rejected', 'cancelled'].includes(normalized)) return 'text-red-400 bg-red-500/10 border-red-500/20';
  if (['running', 'processing', 'approved'].includes(normalized)) return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
  if (['pending_approval', 'pending_financial_review'].includes(normalized)) return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
  return 'text-violet-300 bg-violet-500/10 border-violet-500/20';
}

export default function AdminAssetsPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [viewJob, setViewJob] = useState<JobDetail | null>(null);
  const [viewLoading, setViewLoading] = useState(false);
  const mediaPreview = viewJob ? parseMediaGenerationOutput(viewJob.output) : null;

  useEffect(() => {
    const t = localStorage.getItem('admin_token');
    if (!t) { router.push('/admin-login'); return; }
    fetch('/api/admin/agents/jobs', { headers: { Authorization: `Bearer ${t}` }, credentials: 'include' })
      .then(r => r.json())
      .then(data => setAssets((data.jobs || [])
        .map((j: any): Asset => ({
          id: j.id,
          client: j.client_email || 'Unknown',
          type: inferType(j.agent_id, j.agent_name),
          name: (j.agent_name || j.agent_id) + (j.created_at ? ' — ' + new Date(j.created_at).toLocaleDateString() : ''),
          agent: j.agent_name || j.agent_id,
          status: 'visible',
          job_status: j.status || 'pending',
          error_message: j.error_message || '',
          consent_required: false,
          job_id: j.id,
          created_at: j.created_at || '',
          size_label: j.credits_used ? `${j.credits_used} cr` : '—',
        }))
      ))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const types = ['all', ...Array.from(new Set(assets.map(a => a.type)))];
  const visible = assets.filter(a =>
    (typeFilter === 'all' || a.type === typeFilter) &&
    (statusFilter === 'all' || a.status === statusFilter)
  );

  const toggleStatus = (id: string, newStatus: 'visible' | 'hidden') =>
    setAssets(prev => prev.map(a => a.id === id ? { ...a, status: newStatus } : a));

  const openJob = useCallback(async (asset: Asset) => {
    const t = localStorage.getItem('admin_token');
    if (!t) return;
    setViewLoading(true);
    try {
      const res = await fetch(`/api/admin/agents/jobs/${asset.job_id}`, {
        headers: { Authorization: `Bearer ${t}` },
        credentials: 'include',
      });
      const d = await res.json();
      setViewJob({
        name: asset.name,
        output: d.output || asset.error_message || '(no output yet)',
        agent: asset.agent,
        status: d.status || asset.job_status,
        error_message: d.error_message || asset.error_message || '',
        created_at: asset.created_at,
      });
    } catch {
      setViewJob({ name: asset.name, output: '(could not load output)', agent: asset.agent, status: asset.job_status, created_at: asset.created_at });
    } finally {
      setViewLoading(false);
    }
  }, []);

  return (
    <div className="p-8 max-w-6xl">
      {/* Output viewer modal */}
      {viewJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
              <div>
                <p className="font-semibold text-white text-sm">{viewJob.name}</p>
                <p className="text-xs text-gray-500">{viewJob.agent} · {new Date(viewJob.created_at).toLocaleString()}</p>
              </div>
              <button onClick={() => setViewJob(null)} className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors">✕</button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-5">
              {mediaPreview ? (
                <div className="space-y-4">
                  <div className="overflow-hidden rounded-xl border border-gray-800 bg-gray-950">
                    {mediaPreview.preview_url ? (
                      mediaPreview.preview_url.includes('.mp4') || mediaPreview.preview_url.startsWith('data:video')
                        ? <video src={mediaPreview.preview_url} controls className="w-full max-h-[420px] bg-black" />
                        : <img src={mediaPreview.preview_url} alt={viewJob.name} className="w-full max-h-[420px] object-contain bg-black" />
                    ) : (
                      <div className="flex h-64 items-center justify-center text-xs text-gray-600">Preview not available yet</div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-gray-800 bg-gray-950 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-gray-600">Status</p>
                      <p className="mt-1 text-xs text-white">
                        {mediaPreview.real_media_asset_created ? 'Live media asset created' : 'Preview generated; live provider not ready'}
                      </p>
                    </div>
                    <div className="rounded-xl border border-gray-800 bg-gray-950 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-gray-600">Selected route</p>
                      <p className="mt-1 text-xs text-white">
                        {mediaPreview.provider_readiness?.selected_video_model || mediaPreview.provider_readiness?.selected_image_model || 'No model selected'}
                      </p>
                    </div>
                  </div>

                  {mediaPreview.provider_readiness?.message && (
                    <div className="rounded-xl border border-gray-800 bg-gray-950 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-gray-600">Provider readiness</p>
                      <p className="mt-1 text-xs text-gray-300">{mediaPreview.provider_readiness.message}</p>
                    </div>
                  )}

                  {mediaPreview.script && (
                    <div className="rounded-xl border border-gray-800 bg-gray-950 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-gray-600 mb-2">Generated brief</p>
                      <p className="text-xs leading-relaxed text-gray-300 whitespace-pre-wrap">{mediaPreview.script}</p>
                    </div>
                  )}
                </div>
              ) : (
                cleanOutput(viewJob.output).split('\n').map((line, i) => {
                  if (/^#{1,3}\s/.test(line)) return <p key={i} className="font-bold text-white text-sm mt-4 mb-1">{line.replace(/^#+\s/, '')}</p>;
                  if (/^[-*]\s|^\d+\.\s/.test(line)) return <p key={i} className="text-gray-300 text-sm ml-3 leading-relaxed">{line}</p>;
                  if (!line.trim()) return <div key={i} className="h-2" />;
                  return <p key={i} className="text-gray-300 text-sm leading-relaxed">{line}</p>;
                })
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-800 flex justify-between">
              <button onClick={() => navigator.clipboard?.writeText(viewJob.output)} className="text-xs text-gray-500 hover:text-white transition-colors">Copy output</button>
              <div className="flex items-center gap-2">
                {mediaPreview?.download_ready && mediaPreview.download_url && (
                  <a
                    href={mediaPreview.download_url}
                    download={`${viewJob.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-asset`}
                    className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium rounded-lg transition-colors"
                  >
                    Download
                  </a>
                )}
                <button onClick={() => setViewJob(null)} className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-xs font-medium rounded-lg transition-colors">Close</button>
              </div>
            </div>
          </div>
        </div>
      )}

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
            {loading && (
              <tr><td colSpan={8} className="py-6 px-5"><div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-10 bg-gray-800 rounded animate-pulse"/>)}</div></td></tr>
            )}
            {!loading && visible.length === 0 && (
              <tr><td colSpan={8} className="text-center text-gray-600 text-sm py-10">No agent jobs found.</td></tr>
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
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${jobStatusClass(asset.job_status)}`}>
                    {asset.job_status.replace(/_/g, ' ')}
                  </span>
                  {asset.status !== 'visible' && (
                    <p className="mt-1 text-[10px] text-gray-600">{asset.status}</p>
                  )}
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
                    <button
                      onClick={() => openJob(asset)}
                      disabled={viewLoading}
                      className="text-xs text-violet-400 hover:text-violet-300 disabled:opacity-50 transition-colors"
                    >
                      {viewLoading ? '…' : 'Open'}
                    </button>
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
