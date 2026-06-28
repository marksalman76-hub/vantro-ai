'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

/* ─── Types ─────────────────────────────────────────────────────────── */
interface TeamAgent {
  id: string;
  name: string;
  category: string;
  role: string;
  hitl_level: string;
  credit_estimate: number;
  lead_agent_allowed: boolean;
  unlocked: boolean;
  compatible_teams: string[];
}

interface TeamTemplate {
  id: string;
  name: string;
  description: string;
  lead_agent_id: string;
  agent_ids: string[];
  min_package: string;
  icon: string;
}

interface DeployedJob {
  jobId: string;
  agentName: string;
  agentId: string;
  status: string;
}

/* ─── Constants ──────────────────────────────────────────────────────── */

// Agents that are valid lead agents (kept in sync with backend catalogue)
const LEAD_AGENT_IDS = new Set([
  'head_agent',
  'strategist_agent',
  'marketing_specialist_agent',
  'lead_generator_agent',
  'seo_agent',
  'customer_success_agent',
]);

const CAT_COLOR: Record<string, string> = {
  Executive: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  Strategy: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
  Research: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  Sales: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  Marketing: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
  Media: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  Digital: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  Support: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
  Operations: 'bg-gray-500/10 text-gray-300 border-gray-500/20',
};

const HITL_META: Record<string, { label: string; color: string; tip: string }> = {
  'HITL-0': { label: 'Autonomous',     color: 'bg-green-500/10 text-green-400 border-green-500/20',   tip: 'Runs automatically' },
  'HITL-1': { label: 'Reviewed',       color: 'bg-blue-500/10 text-blue-400 border-blue-500/20',      tip: 'Output reviewed before delivery' },
  'HITL-2': { label: 'You approve',    color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20', tip: 'You review before any external action' },
  'HITL-3': { label: 'Platform gate',  color: 'bg-red-500/10 text-red-400 border-red-500/20',         tip: 'Our team reviews before this runs' },
};

const PKG_ORDER = ['starter', 'growth', 'business', 'enterprise'];
const PKG_COLOR: Record<string, string> = {
  starter:    'text-green-400 border-green-500/30 bg-green-500/5',
  growth:     'text-blue-400 border-blue-500/30 bg-blue-500/5',
  business:   'text-violet-400 border-violet-500/30 bg-violet-500/5',
  enterprise: 'text-amber-400 border-amber-500/30 bg-amber-500/5',
};

const STATUS_COLOR: Record<string, string> = {
  completed:        'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  running:          'text-blue-400 bg-blue-500/10 border-blue-500/20',
  pending:          'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  pending_approval: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  failed:           'text-red-400 bg-red-500/10 border-red-500/20',
};

// Fallback templates used when API returns nothing
const FALLBACK_TEMPLATES: TeamTemplate[] = [
  {
    id: 'campaign_team',
    name: 'Campaign Team',
    description: 'Run a full-funnel marketing campaign from strategy to execution. Best for product launches, seasonal promos, and brand growth pushes.',
    lead_agent_id: 'marketing_specialist_agent',
    agent_ids: ['marketing_specialist_agent', 'content_agent', 'ads_optimisation_agent', 'social_media_agent'],
    min_package: 'growth',
    icon: '📣',
  },
  {
    id: 'website_growth_team',
    name: 'Website Growth Team',
    description: 'Improve search rankings, fix technical SEO, and drive organic traffic with a coordinated SEO and content operation.',
    lead_agent_id: 'seo_agent',
    agent_ids: ['seo_agent', 'content_agent', 'website_agent', 'analytics_agent'],
    min_package: 'starter',
    icon: '🌐',
  },
  {
    id: 'lead_growth_team',
    name: 'Lead Growth Team',
    description: 'Fill the pipeline with qualified leads using AI-powered prospecting, outreach, and CRM automation.',
    lead_agent_id: 'lead_generator_agent',
    agent_ids: ['lead_generator_agent', 'sales_agent', 'email_agent', 'crm_agent'],
    min_package: 'growth',
    icon: '🎯',
  },
  {
    id: 'retention_team',
    name: 'Retention Team',
    description: 'Reduce churn, increase LTV, and keep customers engaged through personalised support and lifecycle email.',
    lead_agent_id: 'customer_success_agent',
    agent_ids: ['customer_success_agent', 'email_agent', 'analytics_agent'],
    min_package: 'starter',
    icon: '♻️',
  },
  {
    id: 'product_launch_team',
    name: 'Product Launch Team',
    description: 'Orchestrate every channel simultaneously for a coordinated product launch: strategy, content, ads, PR, and social.',
    lead_agent_id: 'strategist_agent',
    agent_ids: ['strategist_agent', 'marketing_specialist_agent', 'content_agent', 'ads_optimisation_agent', 'social_media_agent', 'email_agent'],
    min_package: 'business',
    icon: '🚀',
  },
];

// Overlap warnings between agent pairs
const OVERLAP_WARNINGS: Array<{ ids: string[]; message: string }> = [
  {
    ids: ['marketing_specialist_agent', 'strategist_agent'],
    message: 'Marketing Specialist and Strategist Agent share strategic domains — Marketing Specialist leads campaign execution, Strategist leads business direction.',
  },
  {
    ids: ['seo_agent', 'content_agent'],
    message: 'SEO Agent and Content Agent can overlap on keyword-optimised content — recommend letting SEO Agent brief Content Agent.',
  },
  {
    ids: ['email_agent', 'crm_agent'],
    message: 'Email Agent and CRM Agent both write to contact records — ensure CRM Agent is lead to prevent duplicate outreach.',
  },
  {
    ids: ['analytics_agent', 'research_agent'],
    message: 'Analytics Agent and Research Agent can produce overlapping reports — consider assigning distinct measurement windows.',
  },
];

/* ─── Small components ───────────────────────────────────────────────── */

function StepHeader({ step }: { step: number }) {
  const steps = ['Choose start', 'Select agents', 'Set objective', 'Deployed'];
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((label, i) => {
        const n = i + 1;
        const done = step > n;
        const active = step === n;
        return (
          <div key={n} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                done   ? 'bg-emerald-500 text-black' :
                active ? 'bg-violet-600 text-white ring-2 ring-violet-500/40' :
                         'bg-gray-800 text-gray-600 border border-gray-700'
              }`}>
                {done ? '✓' : n}
              </div>
              <span className={`text-[10px] font-medium whitespace-nowrap ${active ? 'text-white' : done ? 'text-emerald-400' : 'text-gray-600'}`}>
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={`w-12 sm:w-20 h-px mx-2 mb-4 transition-all ${done ? 'bg-emerald-500/50' : 'bg-gray-800'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

function HitlBadge({ level }: { level: string }) {
  const m = HITL_META[level] ?? HITL_META['HITL-1'];
  return (
    <span className={`inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded border ${m.color}`} title={m.tip}>
      {m.label}
    </span>
  );
}

function CatBadge({ cat }: { cat: string }) {
  return (
    <span className={`inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded border ${CAT_COLOR[cat] ?? 'bg-gray-800 text-gray-400 border-gray-700'}`}>
      {cat}
    </span>
  );
}

/* ─── Main Page ──────────────────────────────────────────────────────── */

export default function TeamBuilderPage() {
  const router = useRouter();

  // Fetch state
  const [agents, setAgents] = useState<TeamAgent[]>([]);
  const [templates, setTemplates] = useState<TeamTemplate[]>(FALLBACK_TEMPLATES);
  const [loading, setLoading] = useState(true);

  // Wizard state
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [mode, setMode] = useState<'template' | 'custom'>('template');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  // Team state
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [leadId, setLeadId] = useState<string | null>(null);
  const [catFilter, setCatFilter] = useState('All');

  // Objective
  const [objective, setObjective] = useState('');

  // Deployment
  const [deploying, setDeploying] = useState(false);
  const [deployError, setDeployError] = useState('');
  const [deployedJobs, setDeployedJobs] = useState<DeployedJob[]>([]);
  const [teamRunId, setTeamRunId] = useState<string | null>(null);

  /* ── Fetch data ── */
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    Promise.all([
      fetch('/api/agents/list', { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : null),
      fetch('/api/agents/team/templates', { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : null)
        .catch(() => null),
    ]).then(([agentData, templateData]) => {
      if (agentData?.agents) {
        // Augment agents with lead_agent_allowed derived from id if backend doesn't send it
        const augmented: TeamAgent[] = agentData.agents.map((a: TeamAgent & { lead_agent_allowed?: boolean }) => ({
          ...a,
          lead_agent_allowed: a.lead_agent_allowed ?? LEAD_AGENT_IDS.has(a.id),
          compatible_teams: a.compatible_teams ?? [],
        }));
        setAgents(augmented);
      }
      if (Array.isArray(templateData) && templateData.length > 0) {
        setTemplates(templateData);
      }
    }).catch(() => {}).finally(() => setLoading(false));
  }, [router]);

  /* ── Derived ── */
  const unlocked = agents.filter(a => a.unlocked);
  const cats = ['All', ...Array.from(new Set(unlocked.map(a => a.category)))];
  const filtered = catFilter === 'All' ? unlocked : unlocked.filter(a => a.category === catFilter);
  const selectedAgents = agents.filter(a => selectedIds.has(a.id));
  const creditTotal = selectedAgents.reduce((s, a) => s + a.credit_estimate, 0);
  const leadAgent = selectedAgents.find(a => a.id === leadId) ?? null;

  const validLeadCandidates = selectedAgents.filter(a => a.lead_agent_allowed);

  /* ── Validation ── */
  const teamValid =
    selectedAgents.length >= 2 &&
    selectedAgents.length <= 7 &&
    leadId !== null &&
    leadAgent?.lead_agent_allowed === true;

  const validationMessages: string[] = [];
  if (selectedAgents.length < 2) validationMessages.push('Select at least 2 agents');
  if (selectedAgents.length > 7) validationMessages.push('Maximum 7 agents per team');
  if (!leadId) validationMessages.push('Designate a lead agent');
  else if (leadAgent && !leadAgent.lead_agent_allowed) validationMessages.push(`${leadAgent.name} cannot be a lead agent`);
  if (validLeadCandidates.length === 0 && selectedAgents.length >= 2)
    validationMessages.push('Add at least one lead-capable agent (Head Agent, Strategist, Marketing Specialist, Lead Generator, SEO Agent, or Customer Success Agent)');

  /* ── Overlap warnings ── */
  const overlapWarnings = OVERLAP_WARNINGS.filter(w =>
    w.ids.every(id => selectedIds.has(id))
  );

  /* ── Handlers ── */
  const toggleAgent = useCallback((agent: TeamAgent) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(agent.id)) {
        next.delete(agent.id);
        // If removed agent was lead, reset lead
        if (leadId === agent.id) {
          const remaining = Array.from(next);
          const newLead = agents.find(a => remaining.includes(a.id) && a.lead_agent_allowed);
          setLeadId(newLead?.id ?? null);
        }
      } else {
        if (next.size >= 7) return prev; // cap at 7
        next.add(agent.id);
        // Auto-assign lead if none set and this agent is lead-capable
        if (!leadId && agent.lead_agent_allowed) setLeadId(agent.id);
      }
      return next;
    });
  }, [agents, leadId]);

  const applyTemplate = (tpl: TeamTemplate) => {
    setSelectedTemplateId(tpl.id);
    const ids = new Set(tpl.agent_ids);
    setSelectedIds(ids);
    setLeadId(tpl.lead_agent_id);
    setObjective('');
    setStep(3);
  };

  const deploy = async () => {
    if (!teamValid || !objective.trim()) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    setDeploying(true);
    setDeployError('');

    try {
      const body = {
        objective: objective.trim(),
        lead_agent_id: leadId,
        agent_ids: Array.from(selectedIds),
        ...(selectedTemplateId ? { team_template_id: selectedTemplateId } : {}),
      };
      const res = await fetch('/api/agents/team/run', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) {
        setDeployError('Could not deploy team. Please try again or contact support.');
        return;
      }
      // Expect { team_run_id, jobs: [{job_id, agent_id, agent_name, status}] }
      const jobs: DeployedJob[] = (json.jobs ?? selectedAgents.map((a: TeamAgent) => ({
        job_id: crypto.randomUUID?.() ?? Math.random().toString(36).slice(2),
        agent_id: a.id,
        agent_name: a.name,
        status: 'pending',
      }))).map((j: { job_id: string; agent_id: string; agent_name: string; status: string }) => ({
        jobId: j.job_id,
        agentId: j.agent_id,
        agentName: j.agent_name,
        status: j.status,
      }));
      setDeployedJobs(jobs);
      setTeamRunId(json.team_run_id ?? null);
      setStep(4);
    } catch {
      setDeployError('Network error. Check your connection and try again.');
    } finally {
      setDeploying(false);
    }
  };

  const reset = () => {
    setStep(1);
    setMode('template');
    setSelectedTemplateId(null);
    setSelectedIds(new Set());
    setLeadId(null);
    setObjective('');
    setDeployedJobs([]);
    setTeamRunId(null);
    setDeployError('');
  };

  /* ── Placeholder objective text ── */
  const objectivePlaceholder = selectedTemplateId
    ? templates.find(t => t.id === selectedTemplateId)?.description
      ?? 'Describe the goal for your team in detail…'
    : selectedAgents.length > 0
    ? `e.g. "Launch our summer sale campaign: create content, run ads, send email sequence, and report on results. Target: 25-35 year old shoppers. Budget: $5,000. Timeline: 2 weeks."`
    : 'Describe what you want your team to accomplish. The more detail the better.';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  /* ════════════════════════════════════════════════════════════════════ */
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">

        {/* Page header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <Link href="/dashboard/agents" className="text-gray-500 hover:text-white text-sm">My Agents</Link>
            <span className="text-gray-700">/</span>
            <span className="text-gray-300 text-sm">Team Builder</span>
          </div>
          <h1 className="text-2xl font-bold mb-1">Team Builder</h1>
          <p className="text-gray-500 text-sm">Combine agents into a coordinated team that works together on a single objective</p>
        </div>

        {/* Step progress */}
        <StepHeader step={step} />

        {/* ── STEP 1: Choose start ─────────────────────────────────────── */}
        {step === 1 && (
          <div className="space-y-6">
            {/* Tab switcher */}
            <div className="inline-flex bg-gray-900 border border-gray-800 rounded-xl p-1 gap-1">
              <button
                onClick={() => setMode('template')}
                className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'template' ? 'bg-violet-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                Use a Team Template
              </button>
              <button
                onClick={() => setMode('custom')}
                className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'custom' ? 'bg-violet-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                Build Custom Team
              </button>
            </div>

            {/* Templates */}
            {mode === 'template' && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {templates.map(tpl => {
                  const pkgIdx = PKG_ORDER.indexOf(tpl.min_package);
                  const tplAgents = agents.filter(a => tpl.agent_ids.includes(a.id));
                  const allUnlocked = tpl.agent_ids.length === 0 ||
                    tplAgents.every(a => a.unlocked);
                  return (
                    <div
                      key={tpl.id}
                      className={`bg-gray-900 border rounded-2xl p-5 flex flex-col gap-4 transition-all ${allUnlocked ? 'border-gray-800 hover:border-violet-500/40 cursor-pointer' : 'border-gray-800/50 opacity-60'}`}
                      onClick={() => allUnlocked && applyTemplate(tpl)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl">{(tpl as TeamTemplate & { icon?: string }).icon ?? '◈'}</span>
                            <h3 className="font-semibold text-white text-sm">{tpl.name}</h3>
                          </div>
                          <p className="text-gray-500 text-xs leading-relaxed">{tpl.description}</p>
                        </div>
                      </div>

                      {/* Agents list */}
                      <div className="flex flex-wrap gap-1">
                        {tpl.agent_ids.map(id => {
                          const a = agents.find(ag => ag.id === id);
                          const isLead = id === tpl.lead_agent_id;
                          return (
                            <span
                              key={id}
                              className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${isLead ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-gray-800 text-gray-400 border-gray-700'}`}
                            >
                              {isLead ? '★ ' : ''}{a?.name ?? id}
                            </span>
                          );
                        })}
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-800">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize ${PKG_COLOR[tpl.min_package] ?? 'text-gray-400 border-gray-700'}`}>
                          {tpl.min_package}+
                        </span>
                        {allUnlocked ? (
                          <span className="text-xs text-violet-400 font-medium">Use template →</span>
                        ) : (
                          <Link href="/pricing" onClick={e => e.stopPropagation()} className="text-xs text-gray-500 hover:text-white">
                            Upgrade to use →
                          </Link>
                        )}
                      </div>

                      {/* Locked overlay note */}
                      {!allUnlocked && (
                        <div className="text-center">
                          <p className="text-[10px] text-gray-600">Requires {tpl.min_package} plan (rank {pkgIdx + 1})</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Custom: just proceed to agent picker */}
            {mode === 'custom' && (
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
                <p className="text-gray-400 text-sm mb-4">Hand-pick any combination of your unlocked agents and designate a lead.</p>
                <button
                  onClick={() => setStep(2)}
                  className="bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold px-8 py-3 rounded-xl transition-colors"
                >
                  Pick agents →
                </button>
              </div>
            )}
          </div>
        )}

        {/* ── STEP 2: Select agents ─────────────────────────────────────── */}
        {step === 2 && (
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
            {/* Left: agent grid */}
            <div className="space-y-4">
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="font-semibold text-white text-sm">Your Unlocked Agents</h2>
                    <p className="text-gray-500 text-xs mt-0.5">Click to add or remove from team (2–7 agents)</p>
                  </div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
                    {selectedIds.size} / 7
                  </span>
                </div>

                {/* Category filter */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {cats.map(c => (
                    <button
                      key={c}
                      onClick={() => setCatFilter(c)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${catFilter === c ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}
                    >
                      {c}
                    </button>
                  ))}
                </div>

                {unlocked.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-600 text-sm mb-3">No agents unlocked on your plan.</p>
                    <Link href="/pricing" className="text-violet-400 text-sm font-medium">Upgrade to unlock agents →</Link>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {filtered.map(agent => {
                      const inTeam = selectedIds.has(agent.id);
                      const isLead = leadId === agent.id;
                      const atMax = selectedIds.size >= 7 && !inTeam;
                      return (
                        <button
                          key={agent.id}
                          onClick={() => !atMax && toggleAgent(agent)}
                          disabled={atMax}
                          className={`text-left p-3.5 rounded-xl border transition-all ${
                            inTeam
                              ? 'border-violet-500/60 bg-violet-500/10'
                              : atMax
                              ? 'border-gray-800/40 bg-gray-900/20 opacity-40 cursor-not-allowed'
                              : 'border-gray-800 bg-gray-800/30 hover:border-gray-700 hover:bg-gray-800/60'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-1.5 flex-wrap mb-1">
                                <p className="text-xs font-semibold text-white truncate">{agent.name}</p>
                                {isLead && (
                                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/25">★ Lead</span>
                                )}
                              </div>
                              <div className="flex flex-wrap gap-1">
                                <CatBadge cat={agent.category} />
                                <HitlBadge level={agent.hitl_level} />
                              </div>
                            </div>
                            <div className="flex flex-col items-end shrink-0 gap-1">
                              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold transition-colors ${inTeam ? 'bg-violet-600 text-white' : 'border border-gray-600 text-gray-500'}`}>
                                {inTeam ? '✓' : '+'}
                              </div>
                              <span className="text-[10px] text-gray-500">~{agent.credit_estimate}cr</span>
                            </div>
                          </div>
                          <p className="text-gray-500 text-[11px] leading-relaxed line-clamp-2">{agent.role}</p>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Lead agent selector */}
              {selectedAgents.length >= 1 && (
                <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
                  <div className="mb-3">
                    <h2 className="font-semibold text-white text-sm">Lead Agent</h2>
                    <p className="text-gray-500 text-xs mt-0.5">The lead agent coordinates the team and owns the primary deliverable. Only lead-capable agents can lead.</p>
                  </div>
                  {validLeadCandidates.length === 0 ? (
                    <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl px-4 py-3">
                      <p className="text-yellow-400 text-xs">None of your selected agents can lead a team. Add a Head Agent, Strategist, Marketing Specialist, Lead Generator, SEO Agent, or Customer Success Agent.</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {validLeadCandidates.map(a => (
                        <button
                          key={a.id}
                          onClick={() => setLeadId(a.id)}
                          className={`text-left flex items-center gap-3 p-3 rounded-xl border transition-all ${leadId === a.id ? 'border-amber-500/50 bg-amber-500/10' : 'border-gray-800 bg-gray-800/30 hover:border-gray-700'}`}
                        >
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-colors ${leadId === a.id ? 'bg-amber-500 text-black' : 'border border-gray-600 text-gray-500 hover:border-amber-500 hover:text-amber-400'}`}>
                            {leadId === a.id ? '★' : '☆'}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-white truncate">{a.name}</p>
                            <p className="text-[10px] text-gray-500">{a.category}</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Right: team roster + validation */}
            <div className="space-y-4">
              {/* Team roster */}
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 sticky top-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-white text-sm">Team Roster</h2>
                  <span className="text-xs text-gray-500">{selectedAgents.length} agents</span>
                </div>

                {selectedAgents.length === 0 ? (
                  <p className="text-gray-600 text-xs text-center py-6">Click agents on the left to add them</p>
                ) : (
                  <div className="space-y-2 mb-4">
                    {selectedAgents.map(agent => (
                      <div key={agent.id} className={`flex items-center gap-2.5 p-2.5 rounded-lg border ${leadId === agent.id ? 'border-amber-500/30 bg-amber-500/5' : 'border-gray-800/60'}`}>
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 ${leadId === agent.id ? 'bg-amber-500 text-black' : 'bg-gray-800 text-gray-400'}`}>
                          {leadId === agent.id ? '★' : '·'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-white font-medium truncate">{agent.name}</p>
                          <p className="text-[10px] text-gray-500">{leadId === agent.id ? 'Lead' : 'Supporting'}</p>
                        </div>
                        <span className="text-[10px] text-gray-500">~{agent.credit_estimate}cr</span>
                        <button onClick={() => toggleAgent(agent)} className="text-gray-500 hover:text-red-400 text-xs shrink-0">✕</button>
                      </div>
                    ))}
                  </div>
                )}

                {selectedAgents.length >= 2 && (
                  <div className="pt-3 border-t border-gray-800 mb-4">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Credit estimate</span>
                      <span className="text-white font-bold">~{creditTotal} credits</span>
                    </div>
                  </div>
                )}

                {/* Validation */}
                {validationMessages.length > 0 && (
                  <div className="space-y-1.5 mb-4">
                    {validationMessages.map((m, i) => (
                      <div key={i} className="flex items-start gap-2 text-[11px] text-yellow-400">
                        <span className="shrink-0 mt-0.5">⚠</span>
                        <span>{m}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Overlap warnings */}
                {overlapWarnings.length > 0 && (
                  <div className="bg-blue-500/5 border border-blue-500/15 rounded-xl p-3 mb-4 space-y-2">
                    <p className="text-[10px] font-bold text-blue-400 uppercase tracking-wide">Team Compatibility</p>
                    {overlapWarnings.map((w, i) => (
                      <p key={i} className="text-[11px] text-gray-400 leading-relaxed">
                        <span className="text-blue-400 mr-1">ℹ</span>{w.message}
                      </p>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => setStep(1)}
                    className="flex-none px-4 py-2.5 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors"
                  >
                    ← Back
                  </button>
                  <button
                    onClick={() => setStep(3)}
                    disabled={!teamValid}
                    className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
                  >
                    Set objective →
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── STEP 3: Set objective ─────────────────────────────────────── */}
        {step === 3 && (
          <div className="max-w-3xl space-y-5">
            {/* Team summary */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-white text-sm">Your Team</h2>
                <button onClick={() => setStep(selectedTemplateId ? 1 : 2)} className="text-xs text-gray-500 hover:text-white">Edit team</button>
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedAgents.map(a => (
                  <div
                    key={a.id}
                    className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${a.id === leadId ? 'border-amber-500/40 bg-amber-500/10 text-amber-300' : 'border-gray-700 bg-gray-800 text-gray-300'}`}
                  >
                    {a.id === leadId && <span className="text-amber-400 text-[10px]">★</span>}
                    {a.name}
                  </div>
                ))}
              </div>
            </div>

            {/* Objective textarea */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h2 className="font-semibold text-white text-sm">Team Objective</h2>
                  <p className="text-gray-500 text-xs mt-0.5">What should your team accomplish? Be as specific as possible.</p>
                </div>
                <span className={`text-xs ${objective.length > 1800 ? 'text-red-400' : 'text-gray-600'}`}>
                  {objective.length} / 2000
                </span>
              </div>
              <textarea
                value={objective}
                onChange={e => { if (e.target.value.length <= 2000) setObjective(e.target.value); }}
                rows={8}
                placeholder={objectivePlaceholder}
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-violet-500 leading-relaxed"
              />

              {/* Overlap warnings (visible in step 3 too) */}
              {overlapWarnings.length > 0 && (
                <div className="mt-3 bg-blue-500/5 border border-blue-500/15 rounded-xl p-3 space-y-2">
                  <p className="text-[10px] font-bold text-blue-400 uppercase tracking-wide">Team Compatibility Notes</p>
                  {overlapWarnings.map((w, i) => (
                    <p key={i} className="text-[11px] text-gray-400 leading-relaxed">
                      <span className="text-blue-400 mr-1">ℹ</span>{w.message}
                    </p>
                  ))}
                </div>
              )}

              {/* Credit + approval notice */}
              <div className="mt-4 flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Credit estimate: <span className="text-white font-semibold">~{creditTotal} credits</span></span>
                  <span>{selectedAgents.length} agents</span>
                  {selectedAgents.some(a => a.hitl_level === 'HITL-3') && (
                    <span className="text-orange-400">Requires platform review</span>
                  )}
                </div>
              </div>

              {deployError && (
                <div className="mt-3 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                  <p className="text-red-400 text-xs">{deployError}</p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => setStep(selectedTemplateId ? 1 : 2)}
                className="px-5 py-3 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={deploy}
                disabled={deploying || !objective.trim() || !teamValid}
                className="flex-1 bg-gradient-to-r from-emerald-600 to-green-500 hover:from-emerald-500 hover:to-green-400 disabled:opacity-40 text-white font-bold py-3 rounded-xl text-sm transition-all shadow-lg shadow-emerald-500/20"
              >
                {deploying ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Deploying team…
                  </span>
                ) : selectedAgents.some(a => a.hitl_level === 'HITL-3')
                  ? 'Submit team for review'
                  : `▶ Deploy ${selectedAgents.length}-agent team`}
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 4: Confirmation ──────────────────────────────────────── */}
        {step === 4 && (
          <div className="max-w-2xl space-y-5">
            {/* Success header */}
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-xl mx-auto mb-3">✓</div>
              <h2 className="text-lg font-bold text-white mb-1">Team Deployed!</h2>
              <p className="text-gray-400 text-sm">Your {deployedJobs.length}-agent team is working on your objective.</p>
            </div>

            {/* Job list */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-800">
                <h3 className="font-semibold text-white text-sm">Agent Jobs</h3>
              </div>
              <div className="divide-y divide-gray-800/60">
                {deployedJobs.map(job => (
                  <div key={job.jobId} className="flex items-center gap-4 px-5 py-3.5">
                    <div className={`w-4 h-4 rounded-full border-2 shrink-0 ${
                      job.status === 'completed' ? 'border-emerald-400 bg-emerald-400' :
                      job.status === 'failed'    ? 'border-red-400 bg-red-400' :
                      'border-blue-400 border-t-transparent animate-spin'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium truncate">{job.agentName}</p>
                      <p className="text-[10px] text-gray-600 font-mono">{job.jobId.slice(0, 12)}…</p>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${STATUS_COLOR[job.status] ?? 'text-gray-400 bg-gray-800 border-gray-700'}`}>
                      {job.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href={`/dashboard/jobs${teamRunId ? `?team=${teamRunId}` : ''}`}
                className="flex-1 text-center bg-gray-900 hover:bg-gray-800 border border-gray-700 text-white text-sm font-medium py-3 rounded-xl transition-colors"
              >
                View full progress →
              </Link>
              <button
                onClick={reset}
                className="flex-1 bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold py-3 rounded-xl transition-colors"
              >
                Run another team
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
