'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface BrandProfile {
  business_name: string;
  industry: string;
  products_services: string;
  target_audience: string;
  brand_voice: string;
  brand_colours: string;
  website: string;
  social_links: string;
  preferred_tone: string;
  do_not_use: string;
}

const TONE_OPTIONS = ['Professional', 'Casual', 'Enthusiastic', 'Formal', 'Educational', 'Bold', 'Empathetic'];
const INDUSTRY_OPTIONS = ['E-commerce / Retail', 'SaaS / Tech', 'Health & Wellness', 'Finance', 'Real Estate', 'Food & Beverage', 'Fashion', 'Agency / Consulting', 'Education', 'Entertainment', 'Other'];

export default function BrandProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<BrandProfile>({
    business_name: '', industry: '', products_services: '', target_audience: '',
    brand_voice: '', brand_colours: '', website: '', social_links: '',
    preferred_tone: 'Professional', do_not_use: '',
  });
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    try {
      const stored = localStorage.getItem('vantro_brand_profile');
      if (stored) setProfile(JSON.parse(stored));
    } catch {}
  }, [router]);

  const completedFields = Object.values(profile).filter(v => v.trim().length > 0).length;
  const completionPct = Math.round((completedFields / Object.keys(profile).length) * 100);

  const save = async () => {
    setLoading(true);
    localStorage.setItem('vantro_brand_profile', JSON.stringify(profile));
    await new Promise(r => setTimeout(r, 500));
    setSaved(true); setLoading(false);
    setTimeout(() => setSaved(false), 3000);
  };

  const F = ({ label, field, placeholder, multiline = false, options }: { label: string; field: keyof BrandProfile; placeholder?: string; multiline?: boolean; options?: string[] }) => (
    <div>
      <label className="block text-xs font-medium text-gray-400 mb-1.5">{label}</label>
      {options ? (
        <div className="flex flex-wrap gap-2">
          {options.map(opt => (
            <button key={opt} onClick={() => setProfile(p => ({ ...p, [field]: opt }))}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${profile[field] === opt ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
              {opt}
            </button>
          ))}
        </div>
      ) : multiline ? (
        <textarea value={profile[field]} onChange={e => setProfile(p => ({ ...p, [field]: e.target.value }))} rows={3} placeholder={placeholder}
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500"/>
      ) : (
        <input type="text" value={profile[field]} onChange={e => setProfile(p => ({ ...p, [field]: e.target.value }))} placeholder={placeholder}
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"/>
      )}
    </div>
  );

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Brand Profile</h1>
          <p className="text-gray-500 text-sm">Store your business context so agents produce better, tailored outputs</p>
        </div>
        <button onClick={save} disabled={loading}
          className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white transition-colors">
          {loading ? 'Saving…' : saved ? '✓ Saved' : 'Save profile'}
        </button>
      </div>

      {/* Completion meter */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-gray-400">Profile completion</p>
          <span className="text-xs font-bold text-violet-400">{completionPct}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-1.5">
          <div className="h-1.5 rounded-full bg-violet-600 transition-all" style={{ width: `${completionPct}%` }}/>
        </div>
        <p className="text-[10px] text-gray-600 mt-1.5">The more you fill in, the more context agents have to personalise your outputs.</p>
      </div>

      <div className="space-y-6">
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-white text-sm">Business Details</h2>
          <F label="Business name" field="business_name" placeholder="e.g. Acme Commerce"/>
          <F label="Industry" field="industry" options={INDUSTRY_OPTIONS}/>
          <F label="Products / services" field="products_services" placeholder="What do you sell or offer?" multiline/>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-white text-sm">Audience & Voice</h2>
          <F label="Target audience" field="target_audience" placeholder="Who are your ideal customers?" multiline/>
          <F label="Preferred tone" field="preferred_tone" options={TONE_OPTIONS}/>
          <F label="Brand voice" field="brand_voice" placeholder="How should agents write for your brand?" multiline/>
          <F label="Do not use" field="do_not_use" placeholder="Words, phrases, or topics to avoid" multiline/>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-white text-sm">Brand Identity</h2>
          <F label="Brand colours" field="brand_colours" placeholder="e.g. #6D28D9 violet, #1E40AF blue"/>
          <F label="Website" field="website" placeholder="https://yoursite.com"/>
          <F label="Social links" field="social_links" placeholder="Instagram, TikTok, LinkedIn — paste links" multiline/>
        </div>
      </div>
    </div>
  );
}
