'use client';

import { useState } from 'react';

interface Template {
  title: string;
  prompt: string;
}

// ─── Template data ────────────────────────────────────────────────────────────

const TEMPLATES: Record<string, Template[]> = {
  email_marketing_agent: [
    {
      title: 'Welcome sequence',
      prompt:
        'Write a 3-email welcome sequence for new customers who just purchased [product]. Brand tone: [tone]. Include: Day 1 thank you, Day 3 product tips, Day 7 review request.',
    },
    {
      title: 'Abandoned cart',
      prompt:
        'Write 2 abandoned cart recovery emails for [product category] store. First email: 1 hour after abandonment (gentle reminder). Second: 24 hours (add 10% discount urgency).',
    },
    {
      title: 'Re-engagement campaign',
      prompt:
        'Write a win-back email for customers who haven\'t purchased in 90 days. Product: [product]. Offer: [offer]. Keep it personal and not pushy.',
    },
  ],
  seo_agent: [
    {
      title: 'Product page SEO audit',
      prompt:
        'Audit and rewrite the SEO for this product page: [URL or product name]. Target keyword: [keyword]. Include: title tag, meta description, H1, 3 H2s, schema markup recommendation.',
    },
    {
      title: 'Blog post outline',
      prompt:
        'Create an SEO-optimised blog post outline for [topic]. Target keyword: [keyword]. Monthly search volume: [volume]. Competitor articles to beat: [URLs].',
    },
    {
      title: 'Category page copy',
      prompt:
        'Write SEO-optimised copy for a category page: [category name]. Target keywords: [keywords]. Include: hero paragraph, 3 buying guides, FAQs.',
    },
  ],
  social_media_agent: [
    {
      title: 'Product launch posts',
      prompt:
        'Write 5 social media posts (2x Instagram, 2x Twitter/X, 1x LinkedIn) announcing [product]. Key benefit: [benefit]. Launch date: [date]. CTA: [CTA].',
    },
    {
      title: 'Weekly content calendar',
      prompt:
        'Create a 7-day social media content calendar for [brand]. Products: [products]. Themes: educational Mon/Wed, entertaining Tue/Thu, promotional Fri, UGC Sat, behind-scenes Sun.',
    },
    {
      title: 'Viral hook formula',
      prompt:
        'Write 10 hook variations for a social video about [topic/product]. Mix formats: question hooks, stat hooks, story hooks, controversy hooks.',
    },
  ],
  content_strategy_agent: [
    {
      title: '90-day content plan',
      prompt:
        'Build a 90-day content strategy for [brand] in [industry]. Target audience: [audience]. Goals: [goals]. Include blog, social, email, and video content pillars.',
    },
    {
      title: 'Competitor content gap',
      prompt:
        'Analyse content gaps vs competitors for [brand]. Our site: [URL]. Top 3 competitors: [URLs]. Find topics they rank for that we don\'t cover.',
    },
    {
      title: 'Content repurposing',
      prompt:
        'Take this blog post and create 10 pieces of derivative content: [paste article or URL]. Formats needed: Twitter thread, LinkedIn post, email newsletter, 3 Instagram captions, YouTube description, podcast talking points.',
    },
  ],
  paid_ads_agent: [
    {
      title: 'Google Ads campaign',
      prompt:
        'Build a Google Search campaign for [product/service]. Budget: $[budget]/day. Target CPA: $[CPA]. Audience: [audience]. Include: 5 ad groups, 15 keywords each, 3 RSA ads per group, negative keyword list.',
    },
    {
      title: 'Meta ads creative brief',
      prompt:
        'Write ad copy + creative brief for a Meta (Facebook/Instagram) campaign for [product]. Objective: [conversions/traffic/awareness]. Budget: $[budget]/day. Target audience: [age, interests, behaviours]. Include 3 ad variations.',
    },
    {
      title: 'Ad copy A/B test',
      prompt:
        'Write 5 headline variations and 5 body copy variations for [product] ad. Test angle 1: benefit-led. Angle 2: pain-point. Angle 3: social proof. Angle 4: urgency. Angle 5: curiosity.',
    },
  ],
};

const DEFAULT_TEMPLATES: Template[] = [
  {
    title: 'Quick analysis',
    prompt:
      'Analyse [topic] for my [business type] business. Key context: [context]. Deliverable: [what you need].',
  },
  {
    title: 'Strategy plan',
    prompt:
      'Create a strategy for [goal] for [business]. Current situation: [situation]. Target outcome: [outcome]. Timeline: [timeline].',
  },
  {
    title: 'Content creation',
    prompt:
      'Create [content type] for [purpose]. Brand: [brand name]. Tone: [tone]. Key message: [message]. CTA: [CTA].',
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

interface AgentTemplateLibraryProps {
  agentId: string;
  agentName?: string;
  onSelect: (prompt: string) => void;
}

export default function AgentTemplateLibrary({
  agentId,
  agentName,
  onSelect,
}: AgentTemplateLibraryProps) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  const templates = TEMPLATES[agentId] ?? DEFAULT_TEMPLATES;

  const handleSelect = (template: Template) => {
    setSelected(template.title);
    onSelect(template.prompt);
    setOpen(false);
    // Reset selection indicator after a moment
    setTimeout(() => setSelected(null), 2000);
  };

  return (
    <div className="mb-3">
      {/* Toggle button */}
      <div className="flex items-center justify-between mb-2">
        {agentName && (
          <p className="text-xs text-gray-500 font-medium">{agentName}</p>
        )}
        <button
          type="button"
          onClick={() => setOpen(v => !v)}
          className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
            open
              ? 'border-violet-500/40 bg-violet-600/10 text-violet-300'
              : 'border-gray-700 text-gray-400 hover:text-white hover:border-gray-600'
          }`}
        >
          <span className="text-[11px]">◉</span>
          Templates
          <span className="text-gray-600">{open ? '▲' : '▼'}</span>
        </button>
      </div>

      {/* Template grid */}
      {open && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 p-3 bg-gray-800/50 border border-gray-700 rounded-xl mb-2">
          {templates.map(tmpl => (
            <button
              key={tmpl.title}
              type="button"
              onClick={() => handleSelect(tmpl)}
              className={`text-left p-3 rounded-xl border transition-all group ${
                selected === tmpl.title
                  ? 'border-emerald-500/40 bg-emerald-600/10'
                  : 'border-gray-700 bg-gray-800/60 hover:border-violet-500/40 hover:bg-violet-600/5'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <p
                  className={`text-xs font-semibold leading-tight ${
                    selected === tmpl.title
                      ? 'text-emerald-400'
                      : 'text-white group-hover:text-violet-300'
                  }`}
                >
                  {selected === tmpl.title ? '✓ ' : ''}{tmpl.title}
                </p>
                <span className="text-gray-600 text-[10px] shrink-0 mt-0.5 group-hover:text-violet-400">
                  Use →
                </span>
              </div>
              <p className="text-[10px] text-gray-500 leading-relaxed line-clamp-3">
                {tmpl.prompt}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
