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
  influencer_collaboration_agent: "Influencer Collaboration Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  general_ecommerce_agent: "General Ecommerce Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
};

function cleanOutput(value: any): string {
  if (!value) return "No visible output returned.";
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);

  return text
    .replace(/client_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/tenant_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/sk_live_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/sk_test_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/whsec_[a-zA-Z0-9]+/g, "[protected]");
}

const panel = {
  background: "#ffffff",
  border: "1px solid #e5eaf2",
  borderRadius: 24,
  boxShadow: "0 18px 45px rgba(15,23,42,.06)",
};

const input = {
  width: "100%",
  minHeight: 58,
  padding: "12px 14px",
  borderRadius: 12,
  border: "1px solid #dbe3ee",
  background: "#ffffff",
  color: "#0f172a",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
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
          "radial-gradient(circle at top left,rgba(37,99,235,.08),transparent 28%),#f6f8fb",
        color: "#0f172a",
        padding: "32px 24px 70px",
        fontFamily:
          "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
      }}
    >
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 24,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "#2563eb",
                fontWeight: 900,
                fontSize: 13,
                letterSpacing: 1.7,
              }}
            >
              CLIENT WORKSPACE
            </div>

            <h1
              style={{
                margin: "10px 0 0",
                fontSize: 42,
                lineHeight: 1.05,
                letterSpacing: "-0.04em",
              }}
            >
              {account?.company_name || "Ecommerce AI Agent Platform"}
            </h1>

            <p
              style={{
                marginTop: 12,
                color: "#64748b",
                maxWidth: 760,
                lineHeight: 1.6,
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
              padding: "11px 18px",
              background: "#ffffff",
              border: "1px solid #dbe3ee",
              boxShadow: "0 10px 28px rgba(15,23,42,.06)",
              fontWeight: 800,
              color: "#334155",
            }}
          >
            ● {health}
          </div>
        </header>

        <section
          style={{
            ...panel,
            marginTop: 22,
            padding: "16px 20px",
            display: "grid",
            gridTemplateColumns: "repeat(4,1fr)",
            gap: 18,
          }}
        >
          {[
            ["Package", account?.package || account?.package_name || "Not assigned"],
            ["Credits Remaining", String(creditsRemaining)],
            ["Status", account?.status || account?.package_status || "Unknown"],
            ["Active Agents", String(account?.active_agents?.length || 0)],
          ].map(([label, value]) => (
            <div key={label}>
              <div style={{ color: "#64748b", fontSize: 12 }}>{label}</div>
              <strong style={{ display: "block", marginTop: 6, fontSize: 17 }}>
                {value}
              </strong>
            </div>
          ))}
        </section>

        <section style={{ ...panel, marginTop: 18, padding: 24 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: 18,
              flexWrap: "wrap",
              marginBottom: 18,
            }}
          >
            <div>
              <div
                style={{
                  color: "#2563eb",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.4,
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
                  color: "#64748b",
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
                padding: "9px 13px",
                background: "#eff6ff",
                border: "1px solid #bfdbfe",
                color: "#2563eb",
                fontSize: 12,
                fontWeight: 800,
              }}
            >
              ✓ Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
              gap: 14,
            }}
          >
            {businessFields.map(([label, key, placeholder]) => (
              <label key={key}>
                <div style={{ color: "#334155", fontSize: 12, marginBottom: 6 }}>
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
                  style={input}
                />
              </label>
            ))}
          </div>
        </section>

        <section
          style={{
            marginTop: 18,
            display: "grid",
            gridTemplateColumns: "minmax(420px,.95fr) minmax(460px,1.05fr)",
            gap: 18,
            alignItems: "start",
          }}
        >
          <div style={{ ...panel, padding: 24 }}>
            <h2 style={{ margin: 0, fontSize: 24 }}>Run AI Agent</h2>

            <div style={{ marginTop: 18 }}>
              <div style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>
                Active agents
              </div>

              <div
                style={{
                  display: "grid",
                  gap: 8,
                  maxHeight: 210,
                  overflow: "auto",
                }}
              >
                {(account?.active_agents || []).map((agent) => (
                  <label
                    key={agent}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "10px 12px",
                      borderRadius: 12,
                      border: "1px solid #e5eaf2",
                      background: selectedAgents.includes(agent)
                        ? "#eff6ff"
                        : "#ffffff",
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
                style={{ ...input, minHeight: 132, fontSize: 14 }}
              />
            </div>

            <button
              onClick={runAgent}
              disabled={loading}
              style={{
                marginTop: 18,
                width: "100%",
                padding: "14px 18px",
                borderRadius: 14,
                border: "none",
                background: loading
                  ? "#94a3b8"
                  : "linear-gradient(135deg,#2563eb,#06b6d4)",
                color: "#fff",
                fontWeight: 900,
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: "0 14px 28px rgba(37,99,235,.20)",
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
                  background: "#fef2f2",
                  border: "1px solid #fecaca",
                  color: "#991b1b",
                  fontSize: 13,
                }}
              >
                {error}
              </div>
            ) : null}
          </div>

          <div style={{ ...panel, padding: 24, minHeight: 410 }}>
            <h2 style={{ margin: 0, fontSize: 24 }}>Execution Output Viewer</h2>

            {!result ? (
              <div
                style={{
                  marginTop: 18,
                  minHeight: 270,
                  borderRadius: 18,
                  border: "1px dashed #cbd5e1",
                  background: "#f8fafc",
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
                      color: "#0f172a",
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
              <pre
                style={{
                  marginTop: 18,
                  background: "#f8fafc",
                  borderRadius: 18,
                  padding: 20,
                  overflow: "auto",
                  maxHeight: 700,
                  lineHeight: 1.6,
                  whiteSpace: "pre-wrap",
                  border: "1px solid #e5eaf2",
                }}
              >
                {cleanOutput(result.output || result.workflow || result.message || result)}
              </pre>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}
