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
  ["master_orchestrator_agent", "Master Orchestrator Agent"],
  ["product_research_agent", "Product Research Agent"],
  ["competitor_intelligence_agent", "Competitor Intelligence Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["website_landing_page_agent", "Website / Landing Page Agent"],
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["product_image_direction_agent", "Product Image Direction Agent"],
  ["ad_creative_agent", "Ad Creative Agent"],
  ["campaign_launch_agent", "Campaign Launch Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
  ["creative_rotation_agent", "Creative Rotation Agent"],
  ["email_marketing_agent", "Email Marketing Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["fulfilment_agent", "Fulfilment Agent"],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
  ["seo_agent", "SEO Agent"],
  ["marketplace_agent", "Marketplace Agent"],
  ["billing_licence_agent", "Billing and Licence Agent"],
  ["reporting_agent", "Reporting Agent"],
  ["quality_assurance_agent", "Quality Assurance Agent"],
  ["integration_agent", "Integration Agent"],
  ["security_compliance_agent", "Security and Compliance Agent"],
  ["demo_trial_agent", "Demo / Trial Agent"],
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
  const [selectedDeploymentAgents, setSelectedDeploymentAgents] = useState<string[]>(
    ADMIN_AGENT_OPTIONS.map(([agentId]) => agentId)
  );
  const [task, setTask] = useState("Create a premium Shopify product page for a high-converting ecommerce product.");
  const [runResult, setRunResult] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [deployCompany, setDeployCompany] = useState("Manual Deploy Client");
  const [deployEmail, setDeployEmail] = useState("manual-client@example.com");
  const [deployTenant, setDeployTenant] = useState("client_manual_admin");
  const [deploymentResult, setDeploymentResult] = useState<any>(null);
  const [clientRegistry, setClientRegistry] = useState<any[]>([]);
  const [clientRegistrySummary, setClientRegistrySummary] = useState<any>(null);

  async function loadRuntime() {
    try {
      const response = await fetch("/api/admin-runtime", { cache: "no-store" });
      const data = await response.json();
      setRuntime(data);
      await loadClientRegistry();
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

  function selectAllDeploymentAgents() {
    setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map((agent) => agent.id));
  }

  function clearDeploymentAgents() {
    setSelectedDeploymentAgents([]);
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



  async function loadClientRegistry() {
    try {
      const response = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/list?limit=25",
          method: "GET",
        }),
      });

      const data = await response.json();
      setClientRegistry(data.tenants || []);
    } catch {
      setClientRegistry([]);
    }

    try {
      const response = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/summary",
          method: "GET",
        }),
      });

      const data = await response.json();
      setClientRegistrySummary(data);
    } catch {
      setClientRegistrySummary(null);
    }
  }

  async function callDeploymentControl(path: string, payload: any) {
    try {
      const response = await fetch("/api/admin-deployment-control", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },
        body: JSON.stringify({ path, method: "POST", payload }),
      });

      const data = await response.json();
      setDeploymentResult(data);
      await loadClientRegistry();
    } catch {
      setDeploymentResult({ success: false, message: "Deployment control action failed." });
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
                  Owner/admin can run one agent, multiple selected agents, or any agent from the full 25-agent catalogue for internal operations, demos, and testing. Client credit limits do not apply here, but governance and approval controls remain active.
                </p>

                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                  gap: 8,
                  maxHeight: 260,
                  overflow: "auto",
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


              <Panel title="Deploy / Suspend / Cancel Client System">
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Owner/admin controls to manually deploy a client system with unlimited credits, suspend access, cancel access, or reactivate a system.
                </p>

                <div style={{ display: "grid", gap: 12 }}>
                  <input
                    value={deployTenant}
                    onChange={(event) => setDeployTenant(event.target.value)}
                    placeholder="Tenant ID"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <input
                    value={deployCompany}
                    onChange={(event) => setDeployCompany(event.target.value)}
                    placeholder="Company name"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <input
                    value={deployEmail}
                    onChange={(event) => setDeployEmail(event.target.value)}
                    placeholder="Client email"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <div
                    style={{
                      border: "1px solid rgba(148,163,184,.22)",
                      borderRadius: 16,
                      padding: 14,
                      background: "#020617",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                      <div>
                        <strong>Deploy client agents</strong>
                        <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 4 }}>
                          Select exactly which agents this client can access. Manual Unlimited defaults to all agents.
                        </div>
                      </div>

                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <button
                          type="button"
                          onClick={selectAllDeploymentAgents}
                          style={{
                            border: "1px solid rgba(34,197,94,.35)",
                            background: "rgba(34,197,94,.14)",
                            color: "#bbf7d0",
                            borderRadius: 10,
                            padding: "8px 10px",
                            fontWeight: 800,
                            cursor: "pointer",
                          }}
                        >
                          Select all
                        </button>

                        <button
                          type="button"
                          onClick={clearDeploymentAgents}
                          style={{
                            border: "1px solid rgba(248,113,113,.35)",
                            background: "rgba(248,113,113,.12)",
                            color: "#fecaca",
                            borderRadius: 10,
                            padding: "8px 10px",
                            fontWeight: 800,
                            cursor: "pointer",
                          }}
                        >
                          Clear
                        </button>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                        gap: 8,
                        maxHeight: 260,
                        overflow: "auto",
                        marginTop: 14,
                      }}
                    >
                      {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                        <label
                          key={`deploy-${agentId}`}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 10,
                            padding: 10,
                            borderRadius: 12,
                            background: selectedDeploymentAgents.includes(agentId)
                              ? "rgba(34,197,94,.18)"
                              : "rgba(15,23,42,.8)",
                            cursor: "pointer",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={selectedDeploymentAgents.includes(agentId)}
                            onChange={() => toggleDeploymentAgent(agentId)}
                          />
                          <span>{label}</span>
                        </label>
                      ))}
                    </div>

                    <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 10 }}>
                      Deployment agents selected: {selectedDeploymentAgents.length}
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/manual-deploy", {
                        tenant_id: deployTenant,
                        company_name: deployCompany,
                        contact_email: deployEmail,
                        package: "Manual Unlimited",
                        active_agents: selectedDeploymentAgents,
                        unlimited_credits: true,
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#22c55e",
                        color: "#052e16",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Deploy With Unlimited Credits
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/suspend", {
                        tenant_id: deployTenant,
                        reason: "Suspended from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#f97316",
                        color: "#fff7ed",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Suspend System
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/reactivate", {
                        tenant_id: deployTenant,
                        reason: "Reactivated from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#0ea5e9",
                        color: "#eff6ff",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Reactivate System
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/cancel", {
                        tenant_id: deployTenant,
                        reason: "Cancelled from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#ef4444",
                        color: "#fef2f2",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Cancel System
                    </button>
                  </div>

                  {deploymentResult ? (
                    <div style={{
                      padding: 16,
                      borderRadius: 16,
                      background: deploymentResult.success ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
                      border: deploymentResult.success ? "1px solid rgba(34,197,94,.24)" : "1px solid rgba(239,68,68,.24)",
                      color: deploymentResult.success ? "#bbf7d0" : "#fecaca",
                      lineHeight: 1.6,
                    }}>
                      <strong>{deploymentResult.success ? "Action completed" : "Action failed"}</strong>
                      <div>{deploymentResult.status || deploymentResult.message || deploymentResult.error || "Result received."}</div>
                      {deploymentResult.tenant?.activation_link ? (
                        <div>Activation link: {deploymentResult.tenant.activation_link}</div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
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


              <Panel title="Client Registry">
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Track active, suspended, cancelled, and previously deployed client systems.
                </p>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 12 }}>
                  <Card title="Total Clients" value={clientRegistrySummary?.tenant_count || clientRegistry.length || 0} />
                  <Card title="Active" value={clientRegistrySummary?.active_count || 0} />
                  <Card title="Suspended" value={clientRegistrySummary?.suspended_count || 0} />
                  <Card title="Cancelled" value={clientRegistrySummary?.cancelled_count || 0} />
                </div>

                <div style={{
                  marginTop: 16,
                  display: "grid",
                  gap: 10,
                  maxHeight: 360,
                  overflow: "auto",
                }}>
                  {clientRegistry.length === 0 ? (
                    <div style={{ color: "#94a3b8" }}>No deployed clients found yet.</div>
                  ) : clientRegistry.map((client) => (
                    <div
                      key={client.tenant_id}
                      style={{
                        padding: 14,
                        borderRadius: 16,
                        background: "#020617",
                        border: "1px solid rgba(148,163,184,.16)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                        <strong>{client.company_name || "Client"}</strong>
                        <span style={{
                          padding: "6px 10px",
                          borderRadius: 999,
                          background:
                            client.access_status === "active"
                              ? "rgba(34,197,94,.14)"
                              : client.access_status === "suspended"
                                ? "rgba(249,115,22,.14)"
                                : "rgba(239,68,68,.14)",
                          color:
                            client.access_status === "active"
                              ? "#bbf7d0"
                              : client.access_status === "suspended"
                                ? "#fed7aa"
                                : "#fecaca",
                          fontSize: 12,
                          fontWeight: 800,
                        }}>
                          {client.access_status || client.status || "unknown"}
                        </span>
                      </div>

                      <div style={{ color: "#94a3b8", fontSize: 13, marginTop: 8 }}>
                        {client.contact_email || "No email"} · {client.package || "No package"} · Agents: {(client.active_agents || []).length}
                      </div>

                      <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 6 }}>
                        Credits: {client.unlimited_credits ? "Unlimited" : client.credit_state?.credits_remaining || "Limited"}
                      </div>
                    </div>
                  ))}
                </div>
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
