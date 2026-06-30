'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface AgentJob { id: string; agent_name: string; status: string; credits_used: number; created_at: string | null; output: string | null; }

interface MediaGenerationOutput {
  type?: string;
  script?: string;
  preview_url?: string;
  download_url?: string;
  real_media_asset_created?: boolean;
  preview_ready?: boolean;
  download_ready?: boolean;
  provider_readiness?: {
    message?: string;
    selected_video_model?: string | null;
    selected_image_model?: string | null;
  };
}

function cleanOutput(output: string) {
  return output.replace(/^<!-- provider:.*? -->\n/, '').trim();
}

function parseMediaGenerationOutput(output: string | null): MediaGenerationOutput | null {
  const clean = cleanOutput(output || '');
  if (!clean.startsWith('{')) return null;
  try {
    const parsed = JSON.parse(clean);
    return parsed?.type === 'media_generation' ? parsed : null;
  } catch {
    return null;
  }
}

const STATUS_STYLE: Record<string, string> = {
  completed: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  running:   'text-blue-400 bg-blue-500/10 border-blue-500/20',
  pending:   'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  failed:    'text-red-400 bg-red-500/10 border-red-500/20',
  pending_approval: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
};

const CLIENT_STATUS: Record<string, string> = {
  completed: 'Ready',
  running: 'In progress',
  pending: 'Waiting to start',
  failed: 'Could not complete',
  pending_approval: 'Needs your approval',
  rejected: 'Declined',
};

export default function AssetsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<AgentJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewJob, setViewJob] = useState<AgentJob | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const mediaPreview = viewJob ? parseMediaGenerationOutput(viewJob.output) : null;

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/agents/jobs', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.jobs) setJobs(d.jobs); })
      .finally(() => setLoading(false));
  }, [router]);

  const completed = jobs.filter(j => j.status === 'completed');
  const inProgress = jobs.filter(j => ['running', 'pending'].includes(j.status));
  const needsAttention = jobs.filter(j => ['failed', 'pending_approval', 'rejected'].includes(j.status));

  if (loading) return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"/></div>;

  return (
    <div className="p-8 max-w-5xl">
      {viewJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
              <div>
                <p className="font-semibold text-white">{viewJob.agent_name}</p>
                <p className="text-xs text-gray-500">{viewJob.credits_used} credits · {viewJob.created_at ? new Date(viewJob.created_at).toLocaleString() : ''}</p>
              </div>
              <button onClick={() => setViewJob(null)} className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">✕</button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-5">
              {mediaPreview ? (
                <div className="space-y-4">
                  <div className="overflow-hidden rounded-xl border border-gray-800 bg-gray-950">
                    {mediaPreview.preview_url ? (
                      mediaPreview.preview_url.includes('.mp4') || mediaPreview.preview_url.startsWith('data:video')
                        ? <video src={mediaPreview.preview_url} controls className="w-full max-h-[420px] bg-black" />
                        : <img src={mediaPreview.preview_url} alt={viewJob.agent_name} className="w-full max-h-[420px] object-contain bg-black" />
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

                  {mediaPreview.script && (
                    <div className="rounded-xl border border-gray-800 bg-gray-950 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-gray-600 mb-2">Generated brief</p>
                      <p className="text-xs leading-relaxed text-gray-300 whitespace-pre-wrap">{mediaPreview.script}</p>
                    </div>
                  )}
                </div>
              ) : (
                cleanOutput(viewJob.output ?? '').split('\n').map((line, i) => {
                  if (/^#{1,3}\s/.test(line)) return <p key={i} className="font-bold text-white text-sm mt-4 mb-1">{line.replace(/^#+\s/, '')}</p>;
                  if (/^[-*]\s|^\d+\.\s/.test(line)) return <p key={i} className="text-gray-300 text-sm ml-3 leading-relaxed">{line}</p>;
                  if (!line.trim()) return <div key={i} className="h-2"/>;
                  return <p key={i} className="text-gray-300 text-sm leading-relaxed">{line}</p>;
                })
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-800 flex justify-between">
              <button onClick={() => navigator.clipboard?.writeText(viewJob.output ?? '')} className="text-xs text-gray-500 hover:text-white">Copy output</button>
              <div className="flex items-center gap-2">
                {mediaPreview?.download_ready && mediaPreview.download_url && (
                  <a
                    href={mediaPreview.download_url}
                    download={`${viewJob.agent_name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-asset`}
                    className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium rounded-lg"
                  >
                    Download
                  </a>
                )}
                <button onClick={() => setViewJob(null)} className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-xs font-medium rounded-lg">Close</button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Assets & Outputs</h1>
        <p className="text-gray-500 text-sm">All your agent deliverables and completed work</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Ready to view', value: completed.length, color: 'text-emerald-400' },
          { label: 'In progress', value: inProgress.length, color: 'text-blue-400' },
          { label: 'Needs attention', value: needsAttention.length, color: 'text-orange-400' },
        ].map(s => (
          <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <p className="text-gray-500 text-xs mb-1">{s.label}</p>
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {jobs.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-12 text-center">
          <p className="text-gray-500 text-sm mb-4">No outputs yet. Run your first agent to see results here.</p>
          <Link href="/dashboard/agents" className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-5 py-2.5 rounded-xl font-medium">Go to My Agents →</Link>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-800">
            <h2 className="font-semibold text-white text-sm">All Outputs</h2>
          </div>
          <div className="divide-y divide-gray-800/60">
            {jobs.map(job => (
              <div key={job.id} className="flex items-center gap-4 px-6 py-4 hover:bg-gray-800/30 transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium">{job.agent_name}</p>
                  <p className="text-xs text-gray-600">{job.created_at ? new Date(job.created_at).toLocaleString() : '—'}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${STATUS_STYLE[job.status] || 'text-gray-400 bg-gray-800 border-gray-700'}`}>
                    {CLIENT_STATUS[job.status] ?? job.status}
                  </span>
                  {job.credits_used > 0 && <span className="text-[10px] text-gray-600">{job.credits_used}cr</span>}
                  {job.status === 'completed' && job.output && (
                    <button onClick={() => setViewJob(job)} className="text-xs text-violet-400 hover:text-violet-300 font-medium">View →</button>
                  )}
                  {job.status === 'failed' && (
                    <Link href="/dashboard/support" className="text-xs text-orange-400 hover:text-orange-300">Get help</Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
