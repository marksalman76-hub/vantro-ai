'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface MediaStatusResult {
  status: 'processing' | 'completed' | 'failed';
  video_url: string | null;
  task_id: string | null;
}

const POLL_INTERVAL_MS = 10000;
const POLL_MAX = 36; // 6 min cap

interface BrandAsset {
  id: string;
  name: string;
  filename: string;
  mime_type: string;
  size: number;
  created_at: string;
}

type Step = 'type' | 'brief' | 'format' | 'brand' | 'review';

const MEDIA_TYPES = [
  { id: 'product_demo',    label: 'Product Demo',      desc: 'Showcase a product or feature'           },
  { id: 'service_promo',   label: 'Service Promo',      desc: 'Promote a service or offer'              },
  { id: 'social_ad',       label: 'Social Ad',          desc: 'Short-form social media content'          },
  { id: 'brand_story',     label: 'Brand Story',        desc: 'Tell your brand story'                   },
  { id: 'testimonial',     label: 'Testimonial',        desc: 'Customer success or review'               },
  { id: 'explainer',       label: 'Explainer',          desc: 'Educational or how-to content'            },
  { id: 'campaign',        label: 'Campaign',           desc: 'Multi-platform campaign asset'            },
  { id: 'image',           label: 'Image / Graphic',    desc: 'Static image, banner, or graphic'        },
  { id: 'script',          label: 'Script Only',        desc: 'Video or ad script without media render'  },
];

const PLATFORMS = ['Instagram', 'TikTok', 'YouTube', 'LinkedIn', 'Facebook', 'Email', 'Website', 'Other'];
const ASPECT_RATIOS = ['9:16 (vertical)', '1:1 (square)', '16:9 (landscape)', '4:5 (portrait)'];
const TONES = ['Professional', 'Friendly', 'Urgent', 'Inspirational', 'Playful', 'Authoritative'];
const AGE_RANGES = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
const GENDERS = ['Female', 'Male', 'Non-binary', 'Not specified'];
const ETHNICITIES = ['Caucasian', 'African', 'Asian', 'Hispanic', 'Middle Eastern', 'Mixed', 'Other'];
const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Mandarin', 'Japanese', 'Arabic', 'Other'];
const VIDEO_QUALITIES = ['720p', '1080p', '4K'];

export interface MediaRequest {
  type: string;
  brief: string;
  platform: string;
  aspect_ratio: string;
  tone: string;
  age_range: string;
  gender: string;
  ethnicity: string;
  language: string;
  video_quality: string;
  use_brand_profile: boolean;
}

export const CREATIVE_AGENT_OPTIONS = [
  {
    id: 'ugc_media_agent',
    label: 'UGC / AI Media Agent',
    desc: 'Default video and creator-led media',
    videoModels: ['720p', '1080p'],
    imageTiers: ['standard'],
  },
  {
    id: 'ugc_creative_agent',
    label: 'UGC Creative Agent',
    desc: 'Premium UGC, 4K, and pro creative routes',
    videoModels: ['720p', '1080p', '4K'],
    imageTiers: ['standard', 'pro'],
  },
  {
    id: 'product_image_agent',
    label: 'Product Image Agent',
    desc: 'Static image, banner, and product visuals',
    videoModels: [],
    imageTiers: ['standard', 'pro'],
  },
  {
    id: 'ad_creative_agent',
    label: 'Ad Creative Agent',
    desc: 'Paid social creative and campaign assets',
    videoModels: ['720p', '1080p'],
    imageTiers: ['standard', 'pro'],
  },
  {
    id: 'creative_rotation_agent',
    label: 'Creative Rotation Agent',
    desc: 'Fast creative variants and testing angles',
    videoModels: ['720p'],
    imageTiers: ['standard'],
  },
  {
    id: 'social_media_content_agent',
    label: 'Social Media Content Agent',
    desc: 'Organic social content and platform posts',
    videoModels: ['720p'],
    imageTiers: ['standard'],
  },
  {
    id: 'ads_optimisation_agent',
    label: 'Ads Optimisation Agent',
    desc: 'Ad account creative support and image routes',
    videoModels: [],
    imageTiers: ['standard'],
  },
];

const STEPS: Step[] = ['type', 'brief', 'format', 'brand', 'review'];
const STEP_LABELS: Record<Step, string> = {
  type:   'Media type',
  brief:  'Brief',
  format: 'Format',
  brand:  'Brand',
  review: 'Review',
};

export const BRIEF_STEP_FIELD_ORDER = [
  'creative_agent',
  'brief_text',
  'reference_files',
];

function recommendedCreativeAgentId(req: MediaRequest) {
  if (req.type === 'image') return 'product_image_agent';
  if (req.video_quality === '4K') return 'ugc_creative_agent';
  return 'ugc_media_agent';
}

export function resolveCreateMediaAgentId(req: MediaRequest, selectedAgentId: string) {
  return selectedAgentId || recommendedCreativeAgentId(req);
}

function requestedCreativeMediaType(req: MediaRequest) {
  return req.type === 'image' ? 'image' : 'video';
}

function requestedVideoQuality(req: MediaRequest) {
  return req.video_quality || '1080p';
}

export function getCreativeAgentBoundaryLabel(agentId: string) {
  const agent = CREATIVE_AGENT_OPTIONS.find(option => option.id === agentId);
  if (!agent) return '';
  const video = agent.videoModels.length
    ? `Video: ${agent.videoModels.length === 1 ? `${agent.videoModels[0]} only` : agent.videoModels.join(', ')}.`
    : 'Video: none.';
  const image = agent.imageTiers.length
    ? `Image: ${agent.imageTiers.join(', ')}.`
    : 'Image: none.';
  return `${video} ${image}`;
}

export function isCreativeAgentOptionAllowed(agentId: string, req: MediaRequest): { allowed: boolean; reason: string } {
  const agent = CREATIVE_AGENT_OPTIONS.find(option => option.id === agentId);
  if (!agent) return { allowed: false, reason: 'Unknown creative agent.' };

  if (requestedCreativeMediaType(req) === 'image') {
    if (agent.imageTiers.length === 0) {
      return { allowed: false, reason: 'Media boundary: video assets only.' };
    }
    return { allowed: true, reason: '' };
  }

  if (agent.videoModels.length === 0) {
    return { allowed: false, reason: 'Media boundary: image assets only.' };
  }

  const quality = requestedVideoQuality(req);
  if (!agent.videoModels.includes(quality)) {
    return {
      allowed: false,
      reason: `Video model boundary: supports ${agent.videoModels.length === 1 ? `${agent.videoModels[0]} only` : `${agent.videoModels.slice(0, -1).join(', ')} and ${agent.videoModels.at(-1)} only`}.`,
    };
  }

  return { allowed: true, reason: '' };
}

function getStoredAdminToken() {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('admin_token') || localStorage.getItem('token') || '';
}

function authHeaders(token: string, extra?: Record<string, string>) {
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(extra || {}),
  };
}

function clearStoredAdminTokens() {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('token');
}

function redirectToAdminLogin(router: ReturnType<typeof useRouter>) {
  clearStoredAdminTokens();
  router.replace('/admin-login');
}

export default function AdminCreateMediaPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('type');
  const [req, setReq] = useState<MediaRequest>({
    type: '',
    brief: '',
    platform: '',
    aspect_ratio: '',
    tone: '',
    age_range: '',
    gender: '',
    ethnicity: '',
    language: '',
    video_quality: '',
    use_brand_profile: true,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [refFiles, setRefFiles] = useState<File[]>([]);
  const [brandAssets, setBrandAssets] = useState<BrandAsset[]>([]);
  const [selectedAssetIds, setSelectedAssetIds] = useState<Set<string>>(new Set());
  const [selectedCreativeAgentId, setSelectedCreativeAgentId] = useState('ugc_media_agent');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const submitLockRef = useRef(false);
  const selectedAgentRule = isCreativeAgentOptionAllowed(selectedCreativeAgentId, req);

  // Post-submit result state
  const [jobId, setJobId] = useState<string | null>(null);
  const [mediaStatus, setMediaStatus] = useState<MediaStatusResult | null>(null);
  const [pollCount, setPollCount] = useState(0);
  const pollTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollCountRef = useRef(0);

  useEffect(() => {
    const token = getStoredAdminToken();
    fetch('/api/admin/brand-assets', { headers: authHeaders(token), credentials: 'include' })
      .then(r => r.json())
      .then(d => setBrandAssets(d.assets || []))
      .catch(() => {});
  }, []);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }, []);

  const pollMediaStatus = useCallback((id: string, token: string) => {
    if (pollCountRef.current >= POLL_MAX) { stopPolling(); return; }
    fetch(`/api/admin/agents/jobs/${id}/media-status`, {
      headers: authHeaders(token),
      credentials: 'include',
    })
      .then(r => r.ok ? r.json() : null)
      .then((data: MediaStatusResult | null) => {
        if (!data) return;
        setMediaStatus(data);
        pollCountRef.current += 1;
        setPollCount(pollCountRef.current);
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling();
        } else {
          pollTimerRef.current = setTimeout(() => pollMediaStatus(id, token), POLL_INTERVAL_MS);
        }
      })
      .catch(() => {
        pollCountRef.current += 1;
        setPollCount(pollCountRef.current);
        pollTimerRef.current = setTimeout(() => pollMediaStatus(id, token), POLL_INTERVAL_MS);
      });
  }, [stopPolling]);

  useEffect(() => () => stopPolling(), [stopPolling]);

  function toggleAsset(id: string) {
    setSelectedAssetIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function assetThumb(asset: BrandAsset) {
    if (asset.mime_type.startsWith('image/')) return '▧';
    if (asset.mime_type.startsWith('video/')) return '▶';
    if (asset.mime_type === 'application/pdf') return '📄';
    return '✎';
  }

  function next() {
    const idx = STEPS.indexOf(step);
    if (idx < STEPS.length - 1) setStep(STEPS[idx + 1]);
  }

  function back() {
    const idx = STEPS.indexOf(step);
    if (idx > 0) setStep(STEPS[idx - 1]);
  }

  async function submit() {
    if (submitLockRef.current) return;
    submitLockRef.current = true;
    const token = getStoredAdminToken();
    const selectedAgentId = resolveCreateMediaAgentId(req, selectedCreativeAgentId);
    const selectedAgentAllowed = isCreativeAgentOptionAllowed(selectedAgentId, req);
    if (!selectedAgentAllowed.allowed) {
      submitLockRef.current = false;
      setError(selectedAgentAllowed.reason);
      setStep('brief');
      return;
    }
    setSubmitting(true);
    setError('');
    const task = [
      `Create ${req.type.replace(/_/g, ' ')} media.`,
      req.brief,
      req.platform ? `Platform: ${req.platform}.` : '',
      req.aspect_ratio ? `Format: ${req.aspect_ratio}.` : '',
      req.tone ? `Tone: ${req.tone}.` : '',
      req.age_range ? `Creator age: ${req.age_range}.` : '',
      req.gender ? `Creator gender: ${req.gender}.` : '',
      req.ethnicity ? `Creator ethnicity: ${req.ethnicity}.` : '',
      req.language ? `Language: ${req.language}.` : '',
      req.video_quality ? `Video quality: ${req.video_quality}.` : '',
      req.use_brand_profile ? 'Use my brand profile for voice, colours, and assets.' : '',
    ].filter(Boolean).join(' ');

    try {
      const agentsRes = await fetch('/api/agents', { headers: authHeaders(token), credentials: 'include' });
      const agentsData = await agentsRes.json();
      if (agentsRes.status === 401) {
        setError('Your admin session expired. Please sign in again, then rerun this media request.');
        redirectToAdminLogin(router);
        return;
      }
      // Admin bypasses credit/unlock checks on backend — don't filter by unlocked here
      const agents = agentsData.agents || [];
      const mediaAgent = agents.find((a: { id: string }) => a.id === selectedAgentId) || { id: selectedAgentId };
      const selectedAssets = brandAssets.filter((asset) => selectedAssetIds.has(asset.id));

      const res = await fetch('/api/admin-run-agent', {
        method: 'POST',
        headers: {
          ...authHeaders(token, { 'Content-Type': 'application/json' }),
        },
        credentials: 'include',
        body: JSON.stringify({
          agent_id: mediaAgent.id,
          prompt: task,
          context: {
            media_request: req,
            selected_creative_agent_id: selectedAgentId,
            requested_creative_agent_id: selectedAgentId,
            reference_files: refFiles.map((file) => ({
              name: file.name,
              type: file.type,
              size: file.size,
            })),
            brand_asset_ids: Array.from(selectedAssetIds),
            brand_assets: selectedAssets.map((asset) => ({
              id: asset.id,
              name: asset.name,
              mime_type: asset.mime_type,
              size: asset.size,
            })),
            creative_provider_route: {
              video: { provider: 'higgsfield', model: 'ugc_pro' },
            },
          },
        }),
      });
      const d = await res.json();
      if (res.ok && d.job_id) {
        // Stay on page — show inline result + poll for video
        setJobId(d.job_id);
        setMediaStatus(null);
        setPollCount(0);
        pollCountRef.current = 0;
        stopPolling();
        setTimeout(() => pollMediaStatus(d.job_id, token), POLL_INTERVAL_MS);
      } else {
        if (res.status === 401) {
          setError('Your admin session expired. Please sign in again, then rerun this media request.');
          redirectToAdminLogin(router);
          return;
        }
        const rawErr = d.detail || d.error;
        const errMsg = typeof rawErr === 'string' ? rawErr
          : typeof rawErr === 'object' && rawErr !== null
            ? ((rawErr as Record<string, unknown>).reason as string) || JSON.stringify(rawErr)
            : 'Could not start this request. Please try again or contact support.';
        setError(errMsg);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not start media request. Please contact support.');
    } finally {
      submitLockRef.current = false;
      setSubmitting(false);
    }
  }

  const stepIdx = STEPS.indexOf(step);
  const pct = Math.round(((stepIdx + 1) / STEPS.length) * 100);

  return (
    <div className="p-6" style={{ paddingTop: '5rem', maxWidth: '1000px', margin: '0 auto' }}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-3">
          <Link href="/admin/assets" className="text-xs text-gray-500 hover:text-gray-300">← Back</Link>
        </div>
        <h1 className="text-xl font-bold">Create Media</h1>
        <p className="text-gray-500 text-xs mt-1">Build video, image, and audio content with your agents</p>
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between mb-1.5">
          {STEPS.map((s, i) => (
            <button
              key={s}
              onClick={() => i < stepIdx && setStep(s)}
              className={`text-[9px] font-medium transition-colors ${
                s === step ? 'text-violet-300' : i < stepIdx ? 'text-gray-400 cursor-pointer' : 'text-gray-700'
              }`}
            >
              {STEP_LABELS[s]}
            </button>
          ))}
        </div>
        <div className="w-full bg-gray-800 rounded-full h-0.5">
          <div
            className="h-0.5 rounded-full bg-violet-500 transition-all duration-300"
            style={{ width: `${pct}%`, boxShadow: '0 0 8px rgba(124,58,237,0.5)' }}
          />
        </div>
      </div>

      {/* Step: type */}
      {step === 'type' && (
        <div>
          <h2 className="font-semibold text-xs mb-3">What type of media do you need?</h2>
          <div className="grid grid-cols-4 gap-1.5">
            {MEDIA_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setReq(r => ({ ...r, type: t.id }))}
                className={`text-left border rounded-xl px-3.5 py-3 transition-all ${
                  req.type === t.id
                    ? 'border-violet-500/50 bg-violet-500/5'
                    : 'bg-gray-900 border-gray-800 hover:border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-white">{t.label}</p>
                    <p className="text-[11px] text-gray-600 mt-0.5">{t.desc}</p>
                  </div>
                  {req.type === t.id && (
                    <span className="w-3.5 h-3.5 rounded-full bg-violet-500 flex items-center justify-center text-[8px] text-white font-bold shrink-0">✓</span>
                  )}
                </div>
              </button>
            ))}
          </div>
          <div className="mt-4">
            <button
              onClick={next}
              disabled={!req.type}
              className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-xs font-semibold transition-colors"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: brief */}
      {step === 'brief' && (
        <div>
          <h2 className="font-semibold text-xs mb-1">Describe what you need</h2>
          <p className="text-[11px] text-gray-500 mb-3">Include your goal, key message, target audience, and any specific requirements</p>

          <div className="bg-gray-900 border border-violet-500/30 rounded-xl p-4 mb-4" data-brief-field={BRIEF_STEP_FIELD_ORDER[0]}>
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <label htmlFor="creative-agent-selector" className="text-xs font-medium text-white">
                  Select creative agent
                </label>
                <p className="text-[11px] text-gray-500 mt-0.5">
                  Required routing control. Choose exactly which agent should handle this media brief.
                </p>
              </div>
              <span className="text-[10px] text-gray-600 shrink-0">
                Suggested: {CREATIVE_AGENT_OPTIONS.find(agent => agent.id === recommendedCreativeAgentId(req))?.label}
              </span>
            </div>
            <select
              id="creative-agent-selector"
              aria-label="Select creative agent"
              value={selectedCreativeAgentId}
              onChange={(event) => setSelectedCreativeAgentId(event.target.value)}
              className="w-full bg-gray-950 border border-gray-800 focus:border-violet-500/50 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none transition-colors"
            >
              {CREATIVE_AGENT_OPTIONS.map(agent => {
                const rule = isCreativeAgentOptionAllowed(agent.id, req);
                return (
                <option key={agent.id} value={agent.id} disabled={!rule.allowed}>
                  {agent.label} - {agent.desc}{rule.allowed ? '' : ` (Unavailable: ${rule.reason})`}
                </option>
                );
              })}
            </select>
            <p className={`text-[10px] mt-2 ${selectedAgentRule.allowed ? 'text-gray-500' : 'text-red-300'}`}>
              {selectedAgentRule.allowed ? getCreativeAgentBoundaryLabel(selectedCreativeAgentId) : selectedAgentRule.reason}
            </p>
          </div>

          <textarea
            rows={6}
            value={req.brief}
            onChange={e => setReq(r => ({ ...r, brief: e.target.value }))}
            placeholder="e.g. A 30-second product demo showing how our inventory tool saves time. Target audience: small business owners. Key message: reduce admin time by 80%. Include a call to action to book a demo."
            className="w-full bg-gray-900 border border-gray-800 focus:border-violet-500/50 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-700 outline-none resize-none transition-colors"
            data-brief-field={BRIEF_STEP_FIELD_ORDER[1]}
          />
          {req.brief.length > 0 && req.brief.length < 30 && (
            <p className="text-[9px] text-amber-400 mt-1">More detail = better results</p>
          )}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-4 mt-4" data-brief-field={BRIEF_STEP_FIELD_ORDER[2]}>
            <div className="flex items-center justify-between mb-0.5">
              <p className="text-xs font-medium text-white">Reference files</p>
              <Link href="/admin/brand-assets" className="text-[10px] text-violet-400 hover:text-violet-300">
                Manage brand assets →
              </Link>
            </div>
            <p className="text-[11px] text-gray-500 mb-3">Select saved brand assets or upload new files for this request</p>

            {/* Saved brand assets */}
            {brandAssets.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-1.5">Saved assets</p>
                <div className="space-y-1 max-h-36 overflow-y-auto pr-1">
                  {brandAssets.map(asset => {
                    const selected = selectedAssetIds.has(asset.id);
                    return (
                      <button
                        key={asset.id}
                        type="button"
                        onClick={() => toggleAsset(asset.id)}
                        className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-left transition-colors ${
                          selected
                            ? 'bg-violet-500/10 border border-violet-500/30'
                            : 'bg-gray-800/50 border border-transparent hover:border-gray-700'
                        }`}
                      >
                        <span className="text-sm">{assetThumb(asset)}</span>
                        <span className="flex-1 text-[11px] text-gray-300 truncate">{asset.name}</span>
                        <span className="text-[10px] text-gray-600 shrink-0">{formatSize(asset.size)}</span>
                        {selected && <span className="text-violet-400 text-[10px] font-bold shrink-0">✓</span>}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Fresh upload */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                type="button"
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 text-[11px] font-medium transition-colors"
              >
                <span className="text-violet-400">+</span> Upload file
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*,application/pdf,.doc,.docx,.txt"
                className="hidden"
                onChange={(e) => {
                  const picked = e.target.files ? Array.from(e.target.files) : [];
                  e.target.value = '';
                  if (picked.length > 0) setRefFiles(prev => [...prev, ...picked]);
                }}
              />
              {(refFiles.length > 0 || selectedAssetIds.size > 0) && (
                <span className="text-[10px] text-gray-500">
                  {refFiles.length + selectedAssetIds.size} file{refFiles.length + selectedAssetIds.size !== 1 ? 's' : ''} selected
                </span>
              )}
            </div>

            {refFiles.length > 0 && (
              <div className="mt-2 space-y-1">
                {refFiles.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between px-2.5 py-1 rounded-lg bg-gray-800/50 text-[11px] text-gray-400">
                    <span className="truncate">{file.name}</span>
                    <button
                      onClick={() => setRefFiles(prev => prev.filter((_, i) => i !== idx))}
                      className="text-gray-600 hover:text-red-400 transition-colors ml-2 shrink-0"
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            {brandAssets.length === 0 && refFiles.length === 0 && (
              <p className="text-[10px] text-gray-700 mt-2">
                No saved brand assets yet.{' '}
                <Link href="/admin/brand-assets" className="text-violet-500 hover:text-violet-400">Upload assets →</Link>
              </p>
            )}
          </div>

          <div className="mt-4 flex gap-2">
            <button onClick={back} className="px-3.5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-medium transition-colors">Back</button>
            <button
              onClick={next}
              disabled={req.brief.trim().length < 10}
              className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-xs font-semibold transition-colors"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: format */}
      {step === 'format' && (
        <div>
          <h2 className="font-semibold text-xs mb-3">Format &amp; Platform</h2>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Platform <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {PLATFORMS.map(p => (
                <button
                  key={p}
                  onClick={() => setReq(r => ({ ...r, platform: r.platform === p ? '' : p }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.platform === p
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Aspect ratio <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {ASPECT_RATIOS.map(ar => (
                <button
                  key={ar}
                  onClick={() => setReq(r => ({ ...r, aspect_ratio: r.aspect_ratio === ar ? '' : ar }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.aspect_ratio === ar
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {ar}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Tone <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-6 gap-1.5">
              {TONES.map(t => (
                <button
                  key={t}
                  onClick={() => setReq(r => ({ ...r, tone: r.tone === t ? '' : t }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.tone === t
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Creator age <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {AGE_RANGES.map(ar => (
                <button
                  key={ar}
                  onClick={() => setReq(r => ({ ...r, age_range: r.age_range === ar ? '' : ar }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.age_range === ar
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {ar}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Creator gender <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {GENDERS.map(g => (
                <button
                  key={g}
                  onClick={() => setReq(r => ({ ...r, gender: r.gender === g ? '' : g }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.gender === g
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Creator ethnicity <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {ETHNICITIES.map(e => (
                <button
                  key={e}
                  onClick={() => setReq(r => ({ ...r, ethnicity: r.ethnicity === e ? '' : e }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.ethnicity === e
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Language <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {LANGUAGES.map(l => (
                <button
                  key={l}
                  onClick={() => setReq(r => ({ ...r, language: r.language === l ? '' : l }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.language === l
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[11px] text-gray-500 mb-1.5">Video quality <span className="text-gray-700">(optional)</span></p>
            <div className="grid grid-cols-4 gap-1.5">
              {VIDEO_QUALITIES.map(vq => (
                <button
                  key={vq}
                  onClick={() => setReq(r => ({ ...r, video_quality: r.video_quality === vq ? '' : vq }))}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                    req.video_quality === vq
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {vq}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            <button onClick={back} className="px-3.5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-medium transition-colors">Back</button>
            <button onClick={next} className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold transition-colors">
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: brand */}
      {step === 'brand' && (
        <div>
          <h2 className="font-semibold text-xs mb-3">Brand &amp; Assets</h2>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-medium text-white">Use my brand profile</p>
                <p className="text-[11px] text-gray-500 mt-0.5">
                  Agents will use your brand voice, colours, logo, and audience details from your brand profile
                </p>
              </div>
              <button
                onClick={() => setReq(r => ({ ...r, use_brand_profile: !r.use_brand_profile }))}
                className={`shrink-0 relative w-9 h-5 rounded-full transition-colors ${
                  req.use_brand_profile ? 'bg-violet-600' : 'bg-gray-700'
                }`}
              >
                <span className={`absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white shadow transition-all ${
                  req.use_brand_profile ? 'left-4.5' : 'left-0.5'
                }`} />
              </button>
            </div>
          </div>

          <div className="flex gap-2">
            <button onClick={back} className="px-3.5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-medium transition-colors">Back</button>
            <button onClick={next} className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold transition-colors">
              Review →
            </button>
          </div>
        </div>
      )}

      {/* Step: review */}
      {step === 'review' && (
        <div>
          <h2 className="font-semibold text-xs mb-3">Review your request</h2>

          <div className="bg-gray-900 border border-gray-800 rounded-xl divide-y divide-gray-800 mb-4">
            {[
              { label: 'Media type', value: MEDIA_TYPES.find(t => t.id === req.type)?.label || req.type },
              { label: 'Creative agent', value: CREATIVE_AGENT_OPTIONS.find(agent => agent.id === resolveCreateMediaAgentId(req, selectedCreativeAgentId))?.label || selectedCreativeAgentId },
              { label: 'Brief', value: req.brief },
              { label: 'Platform', value: req.platform || 'Not specified' },
              { label: 'Aspect ratio', value: req.aspect_ratio || 'Not specified' },
              { label: 'Tone', value: req.tone || 'Not specified' },
              { label: 'Creator age', value: req.age_range || 'Not specified' },
              { label: 'Creator gender', value: req.gender || 'Not specified' },
              { label: 'Creator ethnicity', value: req.ethnicity || 'Not specified' },
              { label: 'Language', value: req.language || 'Not specified' },
              { label: 'Video quality', value: req.video_quality || 'Not specified' },
              { label: 'Brand profile', value: req.use_brand_profile ? 'Yes — using my brand profile' : 'No' },
            ].map(row => (
              <div key={row.label} className="px-4 py-2.5 flex gap-3">
                <span className="text-[11px] text-gray-500 w-20 shrink-0">{row.label}</span>
                <span className="text-[11px] text-gray-200 flex-1">{row.value}</span>
              </div>
            ))}
          </div>

          {error && (
            <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2.5">
              <p className="text-red-300 text-xs">{error}</p>
            </div>
          )}

          {!jobId ? (
            <>
              <div className="flex gap-2">
                <button onClick={back} className="px-3.5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-medium transition-colors">Back</button>
                <button
                  onClick={submit}
                  disabled={submitting}
                  className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  {submitting ? 'Starting…' : 'Create media'}
                </button>
              </div>
              <p className="text-[9px] text-gray-600 mt-2.5">
                Credits will be reserved when the task starts. If the task cannot complete, credits are not charged or will be refunded.
              </p>
            </>
          ) : (
            /* ── Inline result panel ── */
            <div className="mt-6 border border-gray-800 rounded-2xl overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-gray-900 border-b border-gray-800">
                <div className="flex items-center gap-2">
                  {mediaStatus?.status !== 'completed' && mediaStatus?.status !== 'failed' && (
                    <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
                  )}
                  {mediaStatus?.status === 'completed' && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  )}
                  {mediaStatus?.status === 'failed' && (
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                  )}
                  <span className="text-xs font-semibold text-white">
                    {!mediaStatus ? 'Generating your media…' :
                     mediaStatus.status === 'completed' ? 'Media ready — review & approve' :
                     mediaStatus.status === 'failed' ? 'Generation failed' :
                     `Rendering video… check ${pollCount}/${POLL_MAX}`}
                  </span>
                </div>
                <Link
                  href={`/admin/agent-jobs?highlight=${jobId}`}
                  className="text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
                >
                  View job →
                </Link>
              </div>

              {/* Video preview */}
              <div className="bg-black" style={{ minHeight: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {mediaStatus?.video_url ? (
                  <video
                    src={mediaStatus.video_url}
                    controls
                    autoPlay
                    loop
                    style={{ maxHeight: '420px', maxWidth: '100%', width: '100%' }}
                  />
                ) : mediaStatus?.status === 'failed' ? (
                  <p className="text-red-400 text-xs text-center px-6">
                    Video generation failed. Try adjusting your brief and regenerating.
                  </p>
                ) : (
                  <div className="flex flex-col items-center gap-3 py-12">
                    <div className="w-8 h-8 border-2 border-violet-500/40 border-t-violet-500 rounded-full animate-spin" />
                    <p className="text-gray-500 text-xs">
                      {!mediaStatus ? 'Agent is working on your brief…' : 'Video rendering on Higgsfield servers…'}
                    </p>
                    <p className="text-gray-700 text-[10px]">
                      {!mediaStatus ? 'First check in 10 seconds' : `Checked ${pollCount} time${pollCount !== 1 ? 's' : ''}`}
                    </p>
                  </div>
                )}
              </div>

              {/* Approve / regenerate CTAs */}
              <div className="px-4 py-3 bg-gray-900 border-t border-gray-800 flex items-center gap-2">
                {mediaStatus?.status === 'completed' && mediaStatus.video_url && (
                  <>
                    <a
                      href={mediaStatus.video_url}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold transition-colors"
                    >
                      Approve &amp; Download
                    </a>
                    <Link
                      href="/admin/assets"
                      className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold transition-colors"
                    >
                      View in Assets →
                    </Link>
                  </>
                )}
                <button
                  onClick={() => {
                    stopPolling();
                    setJobId(null);
                    setMediaStatus(null);
                    setPollCount(0);
                    pollCountRef.current = 0;
                    setStep('review');
                  }}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-medium transition-colors"
                >
                  {mediaStatus?.status === 'failed' ? 'Try again' : 'Regenerate'}
                </button>
                {!mediaStatus || mediaStatus.status === 'processing' ? (
                  <span className="text-[10px] text-gray-600 ml-auto">
                    Higgsfield videos take 30–120s to render
                  </span>
                ) : null}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
