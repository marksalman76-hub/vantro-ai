
"use client";

import { useEffect, useMemo, useState } from "react";

const API_BASE = "";

type ExecutionResult = {
  success?: boolean;
  status?: string;
  workflow?: any;
  output?: any;
  approval?: any;
  message?: string;
  selected_agent_count?: number;
  results?: any[];
};

type ClientAccount = {
  tenant_id?: string;
  email?: string;
  company_name?: string;
  package?: string;
  package_name?: string;
  active_agents?: string[];
  monthly_credits?: number;
  credits_monthly?: number;
  credits_used?: number;
  credits_remaining?: number;
  status?: string;
  package_status?: string;
};

const SAFE_AGENT_LABELS: Record<string, string> = {
  master_orchestrator_agent: "Master Orchestrator Agent",
  product_research_agent: "Product Research Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
  brand_strategy_agent: "Brand Strategy Agent",
  store_builder_agent: "Store Builder Agent",
  website_landing_page_agent: "Website / Landing Page Agent",
  product_copywriting_agent: "Product Copywriting Agent",
  ugc_creative_agent: "UGC Creative Agent",
  product_image_direction_agent: "Product Image Direction Agent",
  product_image_agent: "Product Image Agent",
  ad_creative_agent: "Ad Creative Agent",
  campaign_launch_agent: "Campaign Launch Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  creative_rotation_agent: "Creative Rotation Agent",
  email_marketing_agent: "Email Marketing Agent",
  customer_support_agent: "Customer Support Agent",
  fulfilment_agent: "Fulfilment Agent",
  influencer_collaboration_agent: "Influencer Collaboration Agent",
  seo_agent: "SEO Agent",
  marketplace_agent: "Marketplace Agent",
  billing_licence_agent: "Billing & Licence Agent",
  reporting_agent: "Reporting Agent",
  quality_assurance_agent: "Quality Assurance Agent",
  integration_agent: "Integration Agent",
  security_compliance_agent: "Security & Compliance Agent",
  demo_trial_agent: "Demo / Trial Agent",
  general_ecommerce_agent: "General Ecommerce Agent",
};

function cleanOutput(value: any): string {
  if (!value) return "No visible output returned.";

  const text =
    typeof value === "string"
      ? value
      : JSON.stringify(value, null, 2);

  return text
    .replace(/client_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/tenant_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/sk_live_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/sk_test_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/whsec_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/postgresql:\/\/[^ ]+/g, "[protected]");
}

const cardStyle = {
  background: "linear-gradient(135deg,rgba(15,23,42,.56),rgba(15,23,42,.34))",
  border: "1px solid rgba(148,163,184,.08)",
  borderRadius: 26,
  boxShadow: "0 24px 70px rgba(0,0,0,.18)",
  backdropFilter: "blur(18px)",
};

const inputStyle = {
  width: "100%",
  padding: 12,
  borderRadius: 16,
  border: "1px solid rgba(148,163,184,.07)",
  background: "rgba(2,6,23,.48)",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
};

export default function ClientWorkspacePage() {
  const [account, setAccount] = useState<ClientAccount | null>(null);
  const [health, setHealth] = useState("Checking...");
  const [selectedAgent, setSelectedAgent] = useState("");
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  const [businessProfile, setBusinessProfile] = useState({
    niche: "",
    products_services: "",
    target_audience: "",
    competitors: "",
    offers: "",
    brand_voice: "",
    positioning: "",
    goals: "",
  });

  const [task, setTask] = useState(
    "Create premium ecommerce campaign assets for a luxury skincare product launch."
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadWorkspace();
  }, []);

  async function loadWorkspace() {
    try {
      const me = await fetch(`/api/client-me`, {
        credentials: "include",
        cache: "no-store",
      });

      if (me.ok) {
        const data = await me.json();

        if (data?.account) {
          setAccount(data.account);

          if (data.account.active_agents?.length > 0) {
            setSelectedAgent(data.account.active_agents[0]);
            setSelectedAgents([data.account.active_agents[0]]);
          }
        }
      }

      if (!API_BASE) {
        setHealth("Local workspace");
        return;
      }

      const healthRes = await fetch(`${API_BASE}/health`, {
        cache: "no-store",
      });

      setHealth(healthRes.ok ? "Platform online" : "Platform unavailable");
    } catch {
      setHealth("Platform unavailable");
    }
  }

  const creditsRemaining = useMemo(() => {
    if (!account) return 0;

    return (
      account.credits_remaining ??
      Math.max(
        (account.monthly_credits || account.credits_monthly || 0) -
          (account.credits_used || 0),
        0
      )
    );
  }, [account]);

  function toggleClientAgent(agentId: string) {
    setSelectedAgents((current) => {
      if (current.includes(agentId)) {
        const next = current.filter((item) => item !== agentId);
        setSelectedAgent(next[0] || "");
        return next;
      }

      const next = [...current, agentId];
      setSelectedAgent(next[0] || agentId);
      return next;
    });
  }

  async function runAgent() {
    if (selectedAgents.length === 0 || !task.trim()) {
      setError("Select at least one active paid agent and enter a task.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const results = [];

      for (const agentId of selectedAgents) {
        const response = await fetch(`/api/run-agent`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            requested_agent: agentId,
            task,
            business_profile: businessProfile,
          }),
        });

        const data = await response.json();

        results.push({
          agent_id: agentId,
          agent_label: SAFE_AGENT_LABELS[agentId] || agentId,
          http_status: response.status,
          result: data,
        });
      }

      const allSucceeded = results.every((item) => item.result?.success === true);

      setResult({
        success: allSucceeded,
        status: allSucceeded
          ? "multi_agent_execution_completed"
          : "multi_agent_execution_partially_blocked",
        selected_agent_count: selectedAgents.length,
        results,
      });

      if (!allSucceeded) {
        setError("One or more selected agents were blocked or failed.");
      }
    } catch {
      setError("Execution failed.");
    } finally {
      setLoading(false);
    }
  }

  const businessFields: Array<[string, keyof typeof businessProfile, string]> = [
    ["Business niche", "niche", "Luxury skincare, supplements, fashion, pet products"],
    ["Products & services", "products_services", "Main products, bundles, offers"],
    ["Target audience", "target_audience", "Customer type, location, needs"],
    ["Competitors", "competitors", "Competitor names, websites, market examples"],
    ["Offers", "offers", "Current promotions, bundles, guarantees"],
    ["Brand voice", "brand_voice", "Premium, playful, clinical, bold, friendly"],
    ["Positioning", "positioning", "Why customers should choose you"],
    ["Goals", "goals", "Sales, leads, launches, retention, growth"],
  ];

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#020617 0%,#0f172a 45%,#111827 100%)",
        color: "#e2e8f0",
        padding: "26px 22px",
        fontFamily:
          "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
      }}
    >
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 16,
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
              CLIENT WORKSPACE
            </div>

            <h1 style={{ fontSize: 44, marginTop: 8, lineHeight: 1.02 }}>
              {account?.company_name || "Ecommerce AI Agent Platform"}
            </h1>

            <p
              style={{
                color: "#94a3b8",
                maxWidth: 760,
                lineHeight: 1.55,
                marginTop: 10,
              }}
            >
              Run premium ecommerce AI agents, generate governed outputs,
              monitor usage, and review client-safe deliverables.
            </p>
          </div>

          <div
            style={{
              padding: "14px 18px",
              borderRadius: 24,
              background:
                health === "Platform online"
                  ? "rgba(34,197,94,.12)"
                  : "rgba(239,68,68,.12)",
              border:
                health === "Platform online"
                  ? "1px solid rgba(34,197,94,.3)"
                  : "1px solid rgba(239,68,68,.3)",
              fontWeight: 700,
            }}
          >
            {health}
          </div>
        </div>

        <div
          style={{
            marginTop: 18,
            padding: "12px 16px",
            borderRadius: 24,
            background: "rgba(15,23,42,.34)",
            border: "1px solid rgba(148,163,184,.07)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 18,
            flexWrap: "wrap",
          }}
        >
          {[
            ["Package", account?.package || account?.package_name || "Not assigned"],
            ["Credits", String(creditsRemaining)],
            ["Status", account?.status || account?.package_status || "Unknown"],
            ["Agents", String(account?.active_agents?.length || 0)],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 9,
                minWidth: 130,
              }}
            >
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: 24,
                  background: "#38bdf8",
                  boxShadow: "0 0 16px rgba(56,189,248,.75)",
                }}
              />
              <div>
                <span style={{ color: "#94a3b8", fontSize: 11 }}>
                  {label}
                </span>
                <strong style={{ marginLeft: 8, fontSize: 15 }}>
                  {value}
                </strong>
              </div>
            </div>
          ))}
        </div>

                <div style={{ ...cardStyle, padding: 22, marginTop: 18 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 18,
              flexWrap: "wrap",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <div>
              <div
                style={{
                  color: "#38bdf8",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.2,
                }}
              >
                BUSINESS PROFILE INTELLIGENCE
              </div>

              <h2 style={{ fontSize: 18, marginTop: 5 }}>
                Store context for smarter agent outputs
              </h2>

              <p
                style={{
                  color: "#94a3b8",
                  maxWidth: 760,
                  lineHeight: 1.45,
                  marginTop: 5,
                  fontSize: 14,
                }}
              >
                Add this once so every active agent can tailor strategy, copy,
                creative, competitor analysis, and execution to the client.
              </p>
            </div>

            <div
              style={{
                borderRadius: 24,
                padding: "8px 12px",
                background: "rgba(56,189,248,.10)",
                border: "1px solid rgba(56,189,248,.22)",
                color: "#bae6fd",
                fontSize: 12,
                fontWeight: 800,
              }}
            >
              Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
              gap: 11,
            }}
          >
            {businessFields.map(([label, key, placeholder]) => (
              <label key={key}>
                <div style={{ color: "#94a3b8", fontSize: 11, marginBottom: 6 }}>
                  {label}
                </div>

                <textarea
                  value={businessProfile[key]}
                  onChange={(event) =>
                    setBusinessProfile({
                      ...businessProfile,
                      [key]: event.target.value,
                    })
                  }
                  rows={2}
                  placeholder={placeholder}
                  style={{
                    ...inputStyle,
                    minHeight: 52,
                    padding: 11,
                    borderRadius: 13,
                    fontSize: 12,
                  }}
                />
              </label>
            ))}
          </div>
        </div>

<div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(340px,400px) 1fr",
            gap: 24,
            marginTop: 18,
            alignItems: "start",
          }}
        >
          <div style={{ ...cardStyle, padding: 24 }}>
            <h2 style={{ fontSize: 26 }}>Run AI Agent</h2>

            <div style={{ marginTop: 20 }}>
              <div style={{ color: "#94a3b8", fontSize: 13, marginBottom: 8 }}>
                Active Agent
              </div>

              <div
                style={{
                  display: "grid",
                  gap: 8,
                  maxHeight: 210,
                  overflow: "auto",
                  border: "1px solid rgba(148,163,184,.08)",
                  borderRadius: 16,
                  padding: 12,
                  background: "rgba(2,6,23,.52)",
                }}
              >
                {(account?.active_agents || []).map((agent) => (
                  <label
                    key={agent}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: 8,
                      borderRadius: 12,
                      background: selectedAgents.includes(agent)
                        ? "rgba(37,99,235,.22)"
                        : "rgba(15,23,42,.8)",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(agent)}
                      onChange={() => toggleClientAgent(agent)}
                    />
                    <span>{SAFE_AGENT_LABELS[agent] || agent}</span>
                  </label>
                ))}
              </div>

              <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 8 }}>
                Selected agents: {selectedAgents.length}. Only active paid agents are shown.
              </div>
            </div>

            <div style={{ marginTop: 18 }}>
              <div style={{ color: "#94a3b8", fontSize: 13, marginBottom: 8 }}>
                Task
              </div>

              <textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                rows={5}
                style={{
                  width: "100%",
                  padding: 16,
                  borderRadius: 16,
                  border: "1px solid rgba(148,163,184,.08)",
                  background: "rgba(2,6,23,.52)",
                  color: "#fff",
                  resize: "vertical",
                }}
              />
            </div>

            <button
              onClick={runAgent}
              disabled={loading}
              style={{
                marginTop: 18,
                width: "100%",
                padding: "14px 18px",
                borderRadius: 16,
                border: "none",
                background: "linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)",
                color: "#fff",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              {loading
                ? "Running..."
                : selectedAgents.length > 1
                  ? "Run Selected Agents"
                  : "Run Agent"}
            </button>

            {error ? (
              <div
                style={{
                  marginTop: 16,
                  padding: 14,
                  borderRadius: 14,
                  background: "rgba(239,68,68,.12)",
                  border: "1px solid rgba(239,68,68,.24)",
                  color: "#fecaca",
                }}
              >
                {error}
              </div>
            ) : null}
          </div>

          <div style={{ ...cardStyle, padding: 20, minHeight: 430 }}>
            <h2 style={{ fontSize: 26 }}>Execution Output Viewer</h2>

            {!result ? (
              <div
                style={{
                  marginTop: 20,
                  minHeight: 230,
                  borderRadius: 20,
                  border: "1px dashed rgba(148,163,184,.10)",
                  background: "linear-gradient(135deg,rgba(2,6,23,.35),rgba(15,23,42,.20))"
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  padding: 26,
                  color: "#94a3b8",
                  lineHeight: 1.7,
                }}
              >
                <div>
                  <div style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 800, marginBottom: 6 }}>
                    Ready for premium execution
                  </div>
                  <div>
                    Select active agents, add the task, then run execution.
                    Deliverables, approvals, billing blocks, and workflow results will appear here.
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div
                  style={{
                    marginTop: 18,
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 12,
                  }}
                >
                  <div
                    style={{
                      padding: "10px 14px",
                      borderRadius: 24,
                      background: result.success
                        ? "rgba(34,197,94,.12)"
                        : "rgba(239,68,68,.12)",
                      border: result.success
                        ? "1px solid rgba(34,197,94,.24)"
                        : "1px solid rgba(239,68,68,.24)",
                    }}
                  >
                    Status: {result.status || "unknown"}
                  </div>

                  {result.approval?.status ? (
                    <div
                      style={{
                        padding: "10px 14px",
                        borderRadius: 24,
                        background: "rgba(59,130,246,.12)",
                        border: "1px solid rgba(59,130,246,.24)",
                      }}
                    >
                      Approval: {result.approval.status}
                    </div>
                  ) : null}
                </div>

                <pre
                  style={{
                    marginTop: 18,
                    background: "rgba(2,6,23,.52)",
                    borderRadius: 18,
                    padding: 22,
                    overflow: "auto",
                    maxHeight: 700,
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    border: "1px solid rgba(148,163,184,.07)",
                  }}
                >
                  {cleanOutput(
                    result.output ||
                      result.workflow ||
                      result.message ||
                      result
                  )}
                </pre>
              </>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}