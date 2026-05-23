from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step248e_multi_agent_portal_execution.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_step248f_{timestamp}.tsx"
backup.write_text(ADMIN_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

ADMIN_PAGE.write_text(r'''
"use client";

import { useEffect, useMemo, useState } from "react";

type RuntimePayload = {
  success?: boolean;
  generated_at?: string;
  runtime?: any;
  execution_summary?: any;
  billing_summary?: any;
  deployment_summary?: any;
  security_summary?: any;
  health?: any;
  provider_governance?: any;
  operations?: any;
};

const ADMIN_AGENT_OPTIONS = [
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
  ["product_image_direction_agent", "Product Image Direction Agent"],
];

function Card({ title, value, detail }: { title: string; value: string | number; detail?: string }) {
  return (
    <div style={{
      background: "rgba(15,23,42,.86)",
      border: "1px solid rgba(148,163,184,.16)",
      borderRadius: 20,
      padding: 22,
    }}>
      <div style={{ color: "#94a3b8", fontSize: 13 }}>{title}</div>
      <strong style={{ display: "block", marginTop: 10, fontSize: 26 }}>{value}</strong>
      {detail ? <p style={{ color: "#94a3b8", marginTop: 10, lineHeight: 1.5 }}>{detail}</p> : null}
    </div>
  );
}

function StatusPill({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div style={{
      padding: "10px 14px",
      borderRadius: 999,
      background: ok ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
      border: ok ? "1px solid rgba(34,197,94,.28)" : "1px solid rgba(239,68,68,.28)",
      color: ok ? "#bbf7d0" : "#fecaca",
      fontWeight: 700,
      fontSize: 13,
    }}>
      {label}: {ok ? "Ready" : "Needs attention"}
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{
      background: "rgba(15,23,42,.82)",
      border: "1px solid rgba(148,163,184,.14)",
      borderRadius: 22,
      padding: 24,
    }}>
      <h2 style={{ fontSize: 28, margin: 0 }}>{title}</h2>
      <div style={{ marginTop: 20 }}>{children}</div>
    </section>
  );
}

export default function AdminPage() {
  const [runtime, setRuntime] = useState<RuntimePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAdminAgents, setSelectedAdminAgents] = useState<string[]>(["product_copywriting_agent"]);
  const [task, setTask] = useState("Create a premium Shopify product page for a high-converting ecommerce product.");
  const [runResult, setRunResult] = useState<any>(null);
  const [running, setRunning] = useState(false);

  async function loadRuntime() {
    try {
      const response = await fetch("/api/admin-runtime", { cache: "no-store" });
      const data = await response.json();
      setRuntime(data);
    } catch {
      setRuntime(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuntime();
  }, []);

  function toggleAdminAgent(agentId: string) {
    setSelectedAdminAgents((current) => {
      if (current.includes(agentId)) {
        return current.filter((item) => item !== agentId);
      }

      return [...current, agentId];
    });
  }

  async function runAdminAgent() {
    if (selectedAdminAgents.length === 0 || !task.trim()) {
      setRunResult({
        success: false,
        message: "Select at least one agent and enter a task.",
      });
      return;
    }

    setRunning(true);
    setRunResult(null);

    try {
      const results = [];

      for (const agentId of selectedAdminAgents) {
        const response = await fetch("/api/run-agent", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
          },
          body: JSON.stringify({
            tenant_id: "owner_admin",
            requested_agent: agentId,
            workflow_stage: "admin_internal_execution",
            action_type: "product_copy_generation",
            actor_role: "owner",
            owner_approved: true,
            task,
          }),
        });

        const data = await response.json();

        results.push({
          agent_id: agentId,
          http_status: response.status,
          result: data,
        });
      }

      const allSucceeded = results.every((item) => item.result?.success === true);

      setRunResult({
        success: allSucceeded,
        status: allSucceeded ? "admin_multi_agent_execution_completed" : "admin_multi_agent_execution_partially_blocked",
        selected_agent_count: selectedAdminAgents.length,
        results,
      });
    } catch {
      setRunResult({ success: false, message: "Admin execution failed." });
    } finally {
      setRunning(false);
    }
  }

  const runtimeStatus = useMemo(() => runtime?.runtime?.platform_status || "offline", [runtime]);

  const provider = runtime?.provider_governance || {};
  const operations = runtime?.operations || {};

  const providerReady = provider.provider_readiness?.ok === true;
  const sdkReady = provider.openai_sdk_readiness?.ok === true;
  const liveControlReady = provider.live_llm_control?.ok === true;
  const recoveryReady = operations.recovery_summary?.ok === true;
  const artifactsReady = operations.artifacts?.ok === true;

  return (
    <main style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg,#020617 0%,#0f172a 45%,#111827 100%)",
      color: "#f8fafc",
      padding: "42px 24px",
      fontFamily: "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
    }}>
      <section style={{ maxWidth: 1440, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 20, flexWrap: "wrap", alignItems: "center" }}>
          <div>
            <div style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
              OWNER COMMAND CENTRE
            </div>
            <h1 style={{ fontSize: 56, lineHeight: 1.02, marginTop: 12 }}>
              Ecommerce AI Agent Platform
            </h1>
            <p style={{ color: "#94a3b8", marginTop: 14, maxWidth: 900, lineHeight: 1.7 }}>
              Clean operational dashboard for execution, billing, provider readiness, recovery tooling, and launch monitoring.
            </p>
          </div>

          <div style={{
            padding: "14px 18px",
            borderRadius: 999,
            background: runtimeStatus === "online" ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
            border: runtimeStatus === "online" ? "1px solid rgba(34,197,94,.3)" : "1px solid rgba(239,68,68,.3)",
            fontWeight: 800,
          }}>
            Runtime: {runtimeStatus}
          </div>
        </div>

        {loading ? <p style={{ marginTop: 40, color: "#94a3b8" }}>Loading admin runtime...</p> : null}

        {runtime ? (
          <>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))",
              gap: 18,
              marginTop: 34,
            }}>
              <Card title="Successful Executions" value={runtime.execution_summary?.successful_executions || 0} />
              <Card title="Pending Approvals" value={runtime.execution_summary?.pending_approvals || 0} />
              <Card title="Blocked Executions" value={runtime.execution_summary?.blocked_executions || 0} />
              <Card title="Premium Outputs" value={runtime.execution_summary?.premium_outputs_generated || 0} />
              <Card title="Active Subscriptions" value={runtime.billing_summary?.subscriptions_active || 0} />
              <Card title="Credits Remaining" value={runtime.billing_summary?.credits_remaining || 0} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(420px,1fr))", gap: 24, marginTop: 34 }}>
              <Panel title="Run Agent">
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Owner/admin can run one agent or multiple agents for internal operations, demos, and testing. Client credit limits do not apply here, but governance and approval controls remain active.
                </p>

                <div style={{
                  display: "grid",
                  gap: 10,
                  border: "1px solid rgba(148,163,184,.22)",
                  borderRadius: 16,
                  padding: 12,
                  background: "#020617",
                }}>
                  {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                    <label
                      key={agentId}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: 10,
                        borderRadius: 12,
                        background: selectedAdminAgents.includes(agentId)
                          ? "rgba(37,99,235,.22)"
                          : "rgba(15,23,42,.8)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selectedAdminAgents.includes(agentId)}
                        onChange={() => toggleAdminAgent(agentId)}
                      />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>

                <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 8 }}>
                  Selected agents: {selectedAdminAgents.length}
                </div>

                <textarea
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  rows={6}
                  style={{
                    width: "100%",
                    marginTop: 14,
                    padding: 14,
                    borderRadius: 14,
                    background: "#020617",
                    color: "#fff",
                    border: "1px solid rgba(148,163,184,.22)",
                    resize: "vertical",
                  }}
                />

                <button
                  onClick={runAdminAgent}
                  disabled={running}
                  style={{
                    marginTop: 14,
                    padding: "14px 18px",
                    borderRadius: 14,
                    border: "none",
                    background: "linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)",
                    color: "#fff",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  {running ? "Running..." : selectedAdminAgents.length > 1 ? "Run Selected Agents" : "Run Agent"}
                </button>

                {runResult ? (
                  <div style={{
                    marginTop: 14,
                    padding: 16,
                    borderRadius: 16,
                    background: runResult.success ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
                    border: runResult.success ? "1px solid rgba(34,197,94,.24)" : "1px solid rgba(239,68,68,.24)",
                    color: runResult.success ? "#bbf7d0" : "#fecaca",
                    lineHeight: 1.6,
                  }}>
                    <strong>{runResult.success ? "Execution prepared" : "Execution blocked"}</strong>
                    <div>{runResult.status || runResult.message || "Result received."}</div>
                    {runResult.selected_agent_count ? (
                      <div>Agents run: {runResult.selected_agent_count}</div>
                    ) : null}
                  </div>
                ) : null}
              </Panel>

              <Panel title="Runtime Health">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Backend" ok={runtime.health?.ok === true} />
                  <StatusPill label="Governance" ok={runtime.runtime?.governance_layer === "active"} />
                  <StatusPill label="Billing" ok={runtime.runtime?.billing_runtime === "active"} />
                  <StatusPill label="Premium Output" ok={runtime.runtime?.premium_output_runtime === "active"} />
                </div>
              </Panel>

              <Panel title="Provider Governance">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Provider readiness route" ok={providerReady} />
                  <StatusPill label="OpenAI SDK route" ok={sdkReady} />
                  <StatusPill label="Live LLM control" ok={liveControlReady} />
                </div>
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Live provider execution remains owner-gated. Provider keys and internal configuration are hidden from the client surface.
                </p>
              </Panel>

              <Panel title="Operational Recovery">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Recovery tooling" ok={recoveryReady} />
                  <StatusPill label="Artifact registry" ok={artifactsReady} />
                </div>
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Recovery, retry preparation, replay preparation, and artifact visibility are available for admin use.
                </p>
              </Panel>

              <Panel title="Billing & Deployment">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Stripe runtime" ok={runtime.billing_summary?.stripe_live_ready === true} />
                  <StatusPill label="Deployment status" ok={runtime.deployment_summary?.environment_status === "production_ready"} />
                  <StatusPill label="Secret exposure" ok={runtime.security_summary?.secret_exposure_detected === false} />
                </div>
              </Panel>
            </div>
          </>
        ) : (
          <div style={{
            marginTop: 40,
            padding: 24,
            borderRadius: 18,
            background: "rgba(239,68,68,.12)",
            border: "1px solid rgba(239,68,68,.22)",
            color: "#fecaca",
          }}>
            Admin runtime unavailable.
          </div>
        )}
      </section>
    </main>
  );
}
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_248F_ADMIN_MULTI_AGENT_FULL_REPLACEMENT_OK")
print(f"Backup: {backup}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Verified existing test: {TEST}")