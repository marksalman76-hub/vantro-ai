'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Settings {
  financial_constraints: {
    agents_may_not_spend: boolean;
    agents_may_not_scale_paid: boolean;
    agents_may_not_sign_agreements: boolean;
    note: string;
  };
  environment: {
    name: string;
    is_production: boolean;
    docs_exposed: boolean;
    server_header_suppressed: boolean;
    csrf_enabled: boolean;
    inline_worker_disabled: boolean;
  };
  rate_limits: Record<string, string>;
  hitl_levels: Record<string, { model: string; trigger: string }>;
  credit_rules: {
    video_credit_interval_seconds: number;
    plan_credits: Record<string, number>;
    plan_max_video_seconds: Record<string, number>;
    agent_task_credit_range: string;
  };
  security_rules: Record<string, boolean>;
  provider_status: Record<string, boolean>;
  admin_config: Record<string, boolean | string>;
}

function BoolBadge({ value }: { value: boolean }) {
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
      value ? 'bg-green-500/15 text-green-400' : 'bg-red-500/10 text-red-400'
    }`}>
      {value ? 'Enabled' : 'Disabled'}
    </span>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden mb-4">
      <div className="px-5 py-3 border-b border-gray-800 bg-gray-900">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest">{title}</h2>
      </div>
      <div className="px-5 py-4 space-y-3">{children}</div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-gray-400">{label}</span>
      <div className="text-sm text-gray-200">{children}</div>
    </div>
  );
}

export default function SettingsGovernancePage() {
  const router = useRouter();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin-login'); return; }

    fetch('/api/admin/settings', { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => { if (r.ok) setSettings(await r.json()); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!settings) return (
    <div className="p-8 text-red-400 text-sm">Failed to load settings.</div>
  );

  const { financial_constraints, environment, rate_limits, hitl_levels, credit_rules, security_rules, provider_status, admin_config } = settings;

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Settings & Governance</h1>
        <p className="text-gray-500 text-sm mt-1">
          Platform-wide operating rules, financial constraints, and security posture
        </p>
      </div>

      <div className="mb-4 bg-amber-500/10 border border-amber-500/20 rounded-xl px-5 py-3 text-xs text-amber-300">
        Financial constraints and security rules are hard-coded platform safety guarantees. They cannot be changed via the admin portal — code changes and a new deployment are required.
      </div>

      {/* Financial Constraints */}
      <Section title="Financial Constraints — Hard-coded">
        <Row label="Agents may not spend money autonomously">
          <BoolBadge value={financial_constraints.agents_may_not_spend} />
        </Row>
        <Row label="Agents may not scale paid infrastructure">
          <BoolBadge value={financial_constraints.agents_may_not_scale_paid} />
        </Row>
        <Row label="Agents may not sign agreements">
          <BoolBadge value={financial_constraints.agents_may_not_sign_agreements} />
        </Row>
        <p className="text-xs text-gray-600 pt-1">{financial_constraints.note}</p>
      </Section>

      {/* Environment */}
      <Section title="Environment">
        <Row label="Environment">
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            environment.is_production ? 'bg-red-500/15 text-red-300' : 'bg-blue-500/10 text-blue-300'
          }`}>
            {environment.name}
          </span>
        </Row>
        <Row label="OpenAPI docs exposed"><BoolBadge value={environment.docs_exposed} /></Row>
        <Row label="Server header suppressed"><BoolBadge value={environment.server_header_suppressed} /></Row>
        <Row label="CSRF protection enabled"><BoolBadge value={environment.csrf_enabled} /></Row>
        <Row label="Inline worker disabled (dedicated ECS)"><BoolBadge value={environment.inline_worker_disabled} /></Row>
      </Section>

      {/* Security Rules */}
      <Section title="Security Rules — Hard-coded">
        {Object.entries(security_rules).map(([k, v]) => (
          <Row key={k} label={k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}>
            <BoolBadge value={v} />
          </Row>
        ))}
      </Section>

      {/* HITL Levels */}
      <Section title="HITL (Human-in-the-Loop) Levels">
        {Object.entries(hitl_levels).map(([level, info]) => (
          <div key={level} className="flex items-start justify-between py-1">
            <div>
              <span className="text-sm text-gray-300 font-medium">Level {level}</span>
              <p className="text-xs text-gray-600 mt-0.5">{info.trigger}</p>
            </div>
            <span className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded">{info.model}</span>
          </div>
        ))}
      </Section>

      {/* Credit Rules */}
      <Section title="Credit Rules">
        <Row label="Video credit interval">
          <span>{credit_rules.video_credit_interval_seconds}s per credit</span>
        </Row>
        <Row label="Agent task credit range">
          <span>{credit_rules.agent_task_credit_range}</span>
        </Row>
        <div className="pt-2">
          <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Plan credits</p>
          {Object.entries(credit_rules.plan_credits).map(([plan, credits]) => (
            <div key={plan} className="flex justify-between text-sm py-0.5">
              <span className="text-gray-400 capitalize">{plan}</span>
              <div className="flex gap-6">
                <span className="text-gray-200 font-mono">{credits} credits</span>
                <span className="text-gray-500 font-mono">
                  max {credit_rules.plan_max_video_seconds[plan]}s video
                </span>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Rate Limits */}
      <Section title="Rate Limits">
        {Object.entries(rate_limits).map(([k, v]) => (
          <Row key={k} label={k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}>
            <span className="font-mono text-xs bg-gray-800 px-2 py-0.5 rounded">{v}</span>
          </Row>
        ))}
      </Section>

      {/* Provider Status */}
      <Section title="Provider Configuration">
        {Object.entries(provider_status).map(([k, v]) => (
          <Row key={k} label={k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}>
            <BoolBadge value={v} />
          </Row>
        ))}
      </Section>

      {/* Admin Config */}
      <Section title="Admin Configuration">
        {Object.entries(admin_config).map(([k, v]) => (
          <Row key={k} label={k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}>
            {typeof v === 'boolean'
              ? <BoolBadge value={v} />
              : <span className="text-xs text-gray-300">{String(v)}</span>
            }
          </Row>
        ))}
      </Section>
    </div>
  );
}
