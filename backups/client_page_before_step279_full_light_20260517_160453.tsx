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
  product_copywriting_agent: "Product Copywriting Agent",
  ugc_creative_agent: "UGC Creative Agent",
  product_image_agent: "Product Image Agent",
  product_image_direction_agent: "Product Image Direction Agent",
  influencer_collaboration_agent: "Influencer Collaboration Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  general_ecommerce_agent: "General Ecommerce Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
  email_marketing_agent: "Email Marketing Agent",
  seo_agent: "SEO Agent",
  customer_support_agent: "Customer Support Agent",
  ad_creative_agent: "Ad Creative Agent",
};

function cleanOutput(value: any): string {
  if (!value) return "No visible output returned.";

  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);

  return text
    .replace(/client_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/tenant_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/sk_live_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/sk_test_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/whsec_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/postgresql:\/\/[^ ]+/g, "[protected]");
}

const fieldStyle = {
  width: "100%",
  minHeight: 58,
  padding: "11px 12px",
  borderRadius: 14,
  border: "1px solid rgba(148,163,184,.10)",
  background: "rgba(2,6,23,.55)",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
};

const softPanel = {
  background: "linear-gradient(135deg,rgba(15,23,42,.58),rgba(15,23,42,.30))",
  border: "1px solid rgba(148,163,184,.09)",
  boxShadow: "0 22px 70px rgba(0,0,0,.18)",
  backdropFilter: "blur(18px)",
};

export default function ClientWorkspacePage() {
  const [account, setAccount] = useState<ClientAccount | null>(null);
  const [health, setHealth] = useState("Checking...");
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
      const me = await fetch("/api/client-me", {
        credentials: "include",
        cache: "no-store",
      });

      if (me.ok) {
        const data = await me.json();

        if (data?.account) {
          setAccount(data.account);

          if (data.account.active_agents?.length > 0) {
            setSelectedAgents([data.account.active_agents[0]]);
          }
        }
      }

      if (!API_BASE) {
        setHealth("Local workspace");
        return;
      }

      const healthRes = await fetch(`${API_BASE}/health`, { cache: "no-store" });
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

  function toggleAgent(agentId: string) {
    setSelectedAgents((current) =>
      current.includes(agentId)
        ? current.filter((item) => item !== agentId)
        : [...current, agentId]
    );
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
        const response = await fetch("/api/run-agent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
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
    ["Goals", "goals", "Sales, launches, retention, growth"],
  ];

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left,rgba(14,165,233,.12),transparent 34%),linear-gradient(135deg,#020617 0%,#08111f 45%,#0f172a 100%)",
        color: "#e2e8f0",
        padding: "30px 22px 60px",
        fontFamily:
          "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
      }}
    >
      <section style={{ maxWidth: 1160, margin: "0 auto" }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 24,
            alignItems: "flex-start",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "#38bdf8",
                fontWeight: 900,
                fontSize: 13,
                letterSpacing: 1.7,
              }}
            >
              CLIENT WORKSPACE
            </div>

            <h1
              style={{
                fontSize: 44,
                lineHeight: 1.02,
                margin: "10px 0 0",
                letterSpacing: "-0.04em",
              }}
            >
              {account?.company_name || "Ecommerce AI Agent Platform"}
            </h1>

            <p
              style={{
                color: "#9fb0c7",
                maxWidth: 760,
                lineHeight: 1.55,
                marginTop: 12,
                fontSize: 15,
              }}
            >
              Run premium ecommerce AI agents, generate governed outputs, monitor usage,
              and review client-safe deliverables.
            </p>
          </div>

          <div
            style={{
              borderRadius: 999,
              padding: "11px 17px",
              background: "rgba(56,189,248,.10)",
              border: "1px solid rgba(56,189,248,.18)",
              color: "#e0f2fe",
              fontWeight: 800,
              fontSize: 14,
            }}
          >
            {health}
          </div>
        </header>

        <section
          style={{
            marginTop: 22,
            padding: "12px 16px",
            borderRadius: 24,
            background: "rgba(15,23,42,.38)",
            border: "1px solid rgba(148,163,184,.08)",
            display: "flex",
            justifyContent: "space-between",
            gap: 16,
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
                  borderRadius: 999,
                  background: "#38bdf8",
                  boxShadow: "0 0 14px rgba(56,189,248,.70)",
                }}
              />
              <span style={{ color: "#64748b", fontSize: 11 }}>{label}</span>
              <strong style={{ color: "#fff", fontSize: 15 }}>{value}</strong>
            </div>
          ))}
        </section>

        <section
          style={{
            ...softPanel,
            marginTop: 22,
            borderRadius: 28,
            padding: 22,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 18,
              alignItems: "flex-start",
              flexWrap: "wrap",
              marginBottom: 18,
            }}
          >
            <div>
              <div
                style={{
                  color: "#38bdf8",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.5,
                }}
              >
                BUSINESS PROFILE INTELLIGENCE
              </div>

              <h2 style={{ margin: "7px 0 0", fontSize: 23 }}>
                Store context for smarter agent outputs
              </h2>

              <p
                style={{
                  margin: "7px 0 0",
                  color: "#9fb0c7",
                  fontSize: 14,
                  lineHeight: 1.55,
                  maxWidth: 820,
                }}
              >
                Add context once so every active agent can tailor strategy, copy,
                creative, competitor analysis, and execution to the client.
              </p>
            </div>

            <div
              style={{
                borderRadius: 999,
                padding: "8px 12px",
                background: "rgba(56,189,248,.10)",
                border: "1px solid rgba(56,189,248,.18)",
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
              gap: 12,
            }}
          >
            {businessFields.map(([label, key, placeholder]) => (
              <label key={key}>
                <div style={{ color: "#64748b", fontSize: 11, marginBottom: 6 }}>
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
                  style={fieldStyle}
                />
              </label>
            ))}
          </div>
        </section>

        <section
          style={{
            marginTop: 22,
            display: "grid",
            gridTemplateColumns: "minmax(410px,.95fr) minmax(460px,1.05fr)",
            gap: 20,
            alignItems: "start",
          }}
        >
          <div
            style={{
              ...softPanel,
              borderRadius: 28,
              padding: 22,
            }}
          >
            <h2 style={{ margin: 0, fontSize: 25 }}>Run AI Agent</h2>

            <div style={{ marginTop: 18 }}>
              <div style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>
                Active agents
              </div>

              <div
                style={{
                  display: "grid",
                  gap: 8,
                  maxHeight: 212,
                  overflow: "auto",
                  borderRadius: 18,
                  padding: 10,
                  background: "#ffffff",
                }}
              >
                {(account?.active_agents || []).map((agent) => (
                  <label
                    key={agent}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "9px 10px",
                      borderRadius: 14,
                      background: selectedAgents.includes(agent)
                        ? "rgba(37,99,235,.24)"
                        : "rgba(15,23,42,.54)",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(agent)}
                      onChange={() => toggleAgent(agent)}
                    />
                    <span>{SAFE_AGENT_LABELS[agent] || agent}</span>
                  </label>
                ))}
              </div>

              <div style={{ color: "#64748b", fontSize: 12, marginTop: 8 }}>
                Selected agents: {selectedAgents.length}. Only active paid agents are shown.
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <div style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>
                Task
              </div>

              <textarea
                value={task}
                onChange={(event) => setTask(event.target.value)}
                rows={5}
                style={{
                  ...fieldStyle,
                  minHeight: 132,
                  fontSize: 14,
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
                background: loading
                  ? "linear-gradient(135deg,#475569,#334155)"
                  : "linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)",
                color: "#fff",
                fontWeight: 900,
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: "0 14px 30px rgba(14,165,233,.20)",
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
                  marginTop: 14,
                  padding: 13,
                  borderRadius: 14,
                  background: "rgba(239,68,68,.12)",
                  border: "1px solid rgba(239,68,68,.18)",
                  color: "#fecaca",
                  fontSize: 13,
                }}
              >
                {error}
              </div>
            ) : null}
          </div>

          <div
            style={{
              ...softPanel,
              borderRadius: 28,
              padding: 22,
              minHeight: 410,
            }}
          >
            <h2 style={{ margin: 0, fontSize: 25 }}>Execution Output Viewer</h2>

            {!result ? (
              <div
                style={{
                  marginTop: 18,
                  minHeight: 270,
                  borderRadius: 22,
                  background:
                    "linear-gradient(135deg,rgba(2,6,23,.42),rgba(15,23,42,.22))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  padding: 30,
                  color: "#64748b",
                  lineHeight: 1.7,
                }}
              >
                <div>
                  <div
                    style={{
                      color: "#e2e8f0",
                      fontSize: 20,
                      fontWeight: 900,
                      marginBottom: 8,
                    }}
                  >
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
                    gap: 10,
                  }}
                >
                  <div
                    style={{
                      padding: "9px 13px",
                      borderRadius: 999,
                      background: result.success
                        ? "rgba(34,197,94,.12)"
                        : "rgba(239,68,68,.12)",
                      border: result.success
                        ? "1px solid rgba(34,197,94,.18)"
                        : "1px solid rgba(239,68,68,.18)",
                    }}
                  >
                    Status: {result.status || "unknown"}
                  </div>
                </div>

                <pre
                  style={{
                    marginTop: 18,
                    background: "rgba(2,6,23,.52)",
                    borderRadius: 18,
                    padding: 20,
                    overflow: "auto",
                    maxHeight: 700,
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    border: "1px solid rgba(148,163,184,.08)",
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
        </section>
      </section>
    </main>
  );
}
