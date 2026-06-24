'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

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

interface MediaRequest {
  type: string;
  brief: string;
  platform: string;
  aspect_ratio: string;
  tone: string;
  use_brand_profile: boolean;
}

const STEPS: Step[] = ['type', 'brief', 'format', 'brand', 'review'];
const STEP_LABELS: Record<Step, string> = {
  type:   'Media type',
  brief:  'Brief',
  format: 'Format',
  brand:  'Brand',
  review: 'Review',
};

export default function CreateMediaPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('type');
  const [req, setReq] = useState<MediaRequest>({
    type: '',
    brief: '',
    platform: '',
    aspect_ratio: '',
    tone: '',
    use_brand_profile: true,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function next() {
    const idx = STEPS.indexOf(step);
    if (idx < STEPS.length - 1) setStep(STEPS[idx + 1]);
  }

  function back() {
    const idx = STEPS.indexOf(step);
    if (idx > 0) setStep(STEPS[idx - 1]);
  }

  async function submit() {
    const token = localStorage.getItem('token');
    if (!token) return;
    setSubmitting(true);
    setError('');
    const task = [
      `Create ${req.type.replace(/_/g, ' ')} media.`,
      req.brief,
      req.platform ? `Platform: ${req.platform}.` : '',
      req.aspect_ratio ? `Format: ${req.aspect_ratio}.` : '',
      req.tone ? `Tone: ${req.tone}.` : '',
      req.use_brand_profile ? 'Use my brand profile for voice, colours, and assets.' : '',
    ].filter(Boolean).join(' ');

    try {
      // Find and run the create_media_agent (or similar agent)
      const agentsRes = await fetch('/api/agents', { headers: { Authorization: `Bearer ${token}` } });
      const agentsData = await agentsRes.json();
      const mediaAgent = (agentsData.agents || []).find(
        (a: { id: string; unlocked: boolean }) =>
          (a.id.includes('media') || a.id.includes('video') || a.id.includes('content')) && a.unlocked
      );

      if (!mediaAgent) {
        setError('No media agent is available on your plan. Upgrade to access Create Media.');
        setSubmitting(false);
        return;
      }

      const res = await fetch(`/api/agents/${mediaAgent.id}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ task }),
      });
      const d = await res.json();
      if (res.ok && d.job_id) {
        router.push('/dashboard/jobs');
      } else {
        setError('Could not start this request. Please try again or contact support.');
      }
    } catch {
      setError('Could not start media request. Please contact support.');
    } finally {
      setSubmitting(false);
    }
  }

  const stepIdx = STEPS.indexOf(step);
  const pct = Math.round(((stepIdx + 1) / STEPS.length) * 100);

  return (
    <div className="p-8 max-w-2xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Link href="/dashboard/create" className="text-xs text-gray-500 hover:text-gray-300">← Back</Link>
        </div>
        <h1 className="text-2xl font-bold">Create Media</h1>
        <p className="text-gray-500 text-sm mt-1">Build video, image, and audio content with your agents</p>
      </div>

      {/* Progress */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {STEPS.map((s, i) => (
            <button
              key={s}
              onClick={() => i < stepIdx && setStep(s)}
              className={`text-[10px] font-medium transition-colors ${
                s === step ? 'text-violet-300' : i < stepIdx ? 'text-gray-400 cursor-pointer' : 'text-gray-700'
              }`}
            >
              {STEP_LABELS[s]}
            </button>
          ))}
        </div>
        <div className="w-full bg-gray-800 rounded-full h-1">
          <div
            className="h-1 rounded-full bg-violet-500 transition-all duration-300"
            style={{ width: `${pct}%`, boxShadow: '0 0 8px rgba(124,58,237,0.5)' }}
          />
        </div>
      </div>

      {/* Step: type */}
      {step === 'type' && (
        <div>
          <h2 className="font-semibold text-sm mb-4">What type of media do you need?</h2>
          <div className="grid grid-cols-1 gap-2">
            {MEDIA_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setReq(r => ({ ...r, type: t.id }))}
                className={`text-left border rounded-2xl px-4 py-3.5 transition-all ${
                  req.type === t.id
                    ? 'border-violet-500/50 bg-violet-500/5'
                    : 'bg-gray-900 border-gray-800 hover:border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">{t.label}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{t.desc}</p>
                  </div>
                  {req.type === t.id && (
                    <span className="w-4 h-4 rounded-full bg-violet-500 flex items-center justify-center text-[9px] text-white font-bold shrink-0">✓</span>
                  )}
                </div>
              </button>
            ))}
          </div>
          <div className="mt-6">
            <button
              onClick={next}
              disabled={!req.type}
              className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl text-sm font-semibold transition-colors"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: brief */}
      {step === 'brief' && (
        <div>
          <h2 className="font-semibold text-sm mb-1">Describe what you need</h2>
          <p className="text-xs text-gray-500 mb-4">Include your goal, key message, target audience, and any specific requirements</p>
          <textarea
            rows={7}
            value={req.brief}
            onChange={e => setReq(r => ({ ...r, brief: e.target.value }))}
            placeholder="e.g. A 30-second product demo showing how our inventory tool saves time. Target audience: small business owners. Key message: reduce admin time by 80%. Include a call to action to book a demo."
            className="w-full bg-gray-900 border border-gray-800 focus:border-violet-500/50 rounded-2xl px-4 py-3 text-sm text-white placeholder-gray-700 outline-none resize-none transition-colors"
          />
          {req.brief.length > 0 && req.brief.length < 30 && (
            <p className="text-[10px] text-amber-400 mt-1.5">More detail = better results</p>
          )}
          <div className="mt-6 flex gap-3">
            <button onClick={back} className="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-2xl text-sm font-medium transition-colors">Back</button>
            <button
              onClick={next}
              disabled={req.brief.trim().length < 10}
              className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl text-sm font-semibold transition-colors"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: format */}
      {step === 'format' && (
        <div>
          <h2 className="font-semibold text-sm mb-4">Format &amp; Platform</h2>

          <div className="mb-5">
            <p className="text-xs text-gray-500 mb-2">Platform <span className="text-gray-700">(optional)</span></p>
            <div className="flex flex-wrap gap-2">
              {PLATFORMS.map(p => (
                <button
                  key={p}
                  onClick={() => setReq(r => ({ ...r, platform: r.platform === p ? '' : p }))}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
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

          <div className="mb-5">
            <p className="text-xs text-gray-500 mb-2">Aspect ratio <span className="text-gray-700">(optional)</span></p>
            <div className="flex flex-wrap gap-2">
              {ASPECT_RATIOS.map(ar => (
                <button
                  key={ar}
                  onClick={() => setReq(r => ({ ...r, aspect_ratio: r.aspect_ratio === ar ? '' : ar }))}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
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

          <div className="mb-5">
            <p className="text-xs text-gray-500 mb-2">Tone <span className="text-gray-700">(optional)</span></p>
            <div className="flex flex-wrap gap-2">
              {TONES.map(t => (
                <button
                  key={t}
                  onClick={() => setReq(r => ({ ...r, tone: r.tone === t ? '' : t }))}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
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

          <div className="flex gap-3">
            <button onClick={back} className="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-2xl text-sm font-medium transition-colors">Back</button>
            <button onClick={next} className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl text-sm font-semibold transition-colors">
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step: brand */}
      {step === 'brand' && (
        <div>
          <h2 className="font-semibold text-sm mb-4">Brand &amp; Assets</h2>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-white">Use my brand profile</p>
                <p className="text-xs text-gray-500 mt-1">
                  Agents will use your brand voice, colours, logo, and audience details from your brand profile
                </p>
              </div>
              <button
                onClick={() => setReq(r => ({ ...r, use_brand_profile: !r.use_brand_profile }))}
                className={`shrink-0 relative w-10 h-5 rounded-full transition-colors ${
                  req.use_brand_profile ? 'bg-violet-600' : 'bg-gray-700'
                }`}
              >
                <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${
                  req.use_brand_profile ? 'left-5' : 'left-0.5'
                }`} />
              </button>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-6">
            <p className="text-sm font-medium text-white mb-1">Upload references</p>
            <p className="text-xs text-gray-500 mb-3">Optional: provide reference images, scripts, or files for this task</p>
            <Link
              href="/dashboard/brand"
              className="text-xs text-violet-400 hover:text-violet-300 font-medium"
            >
              Manage brand assets →
            </Link>
          </div>

          <div className="flex gap-3">
            <button onClick={back} className="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-2xl text-sm font-medium transition-colors">Back</button>
            <button onClick={next} className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl text-sm font-semibold transition-colors">
              Review →
            </button>
          </div>
        </div>
      )}

      {/* Step: review */}
      {step === 'review' && (
        <div>
          <h2 className="font-semibold text-sm mb-5">Review your request</h2>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl divide-y divide-gray-800 mb-6">
            {[
              { label: 'Media type', value: MEDIA_TYPES.find(t => t.id === req.type)?.label || req.type },
              { label: 'Brief', value: req.brief },
              { label: 'Platform', value: req.platform || 'Not specified' },
              { label: 'Aspect ratio', value: req.aspect_ratio || 'Not specified' },
              { label: 'Tone', value: req.tone || 'Not specified' },
              { label: 'Brand profile', value: req.use_brand_profile ? 'Yes — using my brand profile' : 'No' },
            ].map(row => (
              <div key={row.label} className="px-5 py-3 flex gap-4">
                <span className="text-xs text-gray-500 w-24 shrink-0">{row.label}</span>
                <span className="text-xs text-gray-200 flex-1">{row.value}</span>
              </div>
            ))}
          </div>

          {error && (
            <div className="mb-5 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={back} className="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-2xl text-sm font-medium transition-colors">Back</button>
            <button
              onClick={submit}
              disabled={submitting}
              className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-2xl text-sm font-semibold transition-colors"
            >
              {submitting ? 'Starting…' : 'Create media'}
            </button>
          </div>

          <p className="text-[10px] text-gray-600 mt-4">
            Credits will be reserved when the task starts. If the task cannot complete, credits are not charged or will be refunded.
          </p>
        </div>
      )}
    </div>
  );
}
