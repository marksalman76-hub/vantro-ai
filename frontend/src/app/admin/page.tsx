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
  ["trial_trial_agent", "Trial / Trial Agent"],
];

function Card({ title, value, detail }: { title: string; value: string | number; detail?: string }) {
  return (
    <div style={{
      background: "#ffffff",
      border: "1px solid var(--color-border)",
      borderRadius: 22,
      padding: 22,
      boxShadow: "0 18px 40px rgba(15,23,42,.06)",
    }}>
      <div style={{ color: "var(--color-muted)", fontSize: 13, fontWeight: 800 }}>{title}</div>
      <strong style={{ display: "block", marginTop: 10, fontSize: 28, color: "var(--color-dark)" }}>{value}</strong>
      {detail ? <p style={{ color: "var(--color-muted)", marginTop: 10, lineHeight: 1.5 }}>{detail}</p> : null}
    </div>
  );
}

function StatusPill({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div style={{
      padding: "10px 14px",
      borderRadius: 999,
      background: ok ? "#ecfdf5" : "#fef2f2",
      border: ok ? "1px solid #bbf7d0" : "1px solid #fecaca",
      color: ok ? "#166534" : "#991b1b",
      fontWeight: 800,
      fontSize: 13,
    }}>
      {label}: {ok ? "Ready" : "Needs attention"}
    </div>
  );
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow?: string; children: React.ReactNode }) {
  return (
    <section style={{
      background: "#ffffff",
      border: "1px solid var(--color-border)",
      borderRadius: 26,
      padding: 26,
      boxShadow: "0 22px 55px rgba(15,23,42,.07)",
      minHeight: "100%",
    }}>
      {eyebrow ? <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 900, letterSpacing: 1, textTransform: "uppercase" }}>{eyebrow}</div> : null}
      <h2 style={{ fontSize: 28, margin: eyebrow ? "8px 0 0" : 0, color: "var(--color-dark)" }}>{title}</h2>
      <div style={{ marginTop: 20 }}>{children}</div>
    </section>
  );
}

function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{
        padding: 14,
        borderRadius: 14,
        background: "var(--color-bg-light)",
        color: "var(--color-dark)",
        border: "1px solid var(--color-border)",
        outline: "none",
        ...(props.style || {}),
      }}
    />
  );
}

function PrimaryButton(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      style={{
        padding: "14px 18px",
        borderRadius: 14,
        border: "none",
        background: "linear-gradient(135deg,var(--color-brand) 0%,#06b6d4 100%)",
        color: "#fff",
        fontWeight: 900,
        cursor: props.disabled ? "not-allowed" : "pointer",
        opacity: props.disabled ? 0.7 : 1,
        ...(props.style || {}),
      }}
    />
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
  const [businessName, setBusinessName] = useState("Owner Admin Workspace");
  const [businessNiche, setBusinessNiche] = useState("Ecommerce growth, automation, product marketing, UGC, paid ads, SEO, and operations.");
  const [targetMarket, setTargetMarket] = useState("Global ecommerce brands, Shopify stores, online retailers, and fast-scaling product businesses.");
  const [runResult, setRunResult] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [deployCompany, setDeployCompany] = useState("Create Client Workspace");
  const [deployEmail, setDeployEmail] = useState("manual-client@example.com");
  const [deployTenant, setDeployTenant] = useState("client_manual_admin");
  const [deploymentResult, setDeploymentResult] = useState<any>(null);
  const [clientRegistry, setClientRegistry] = useState<any[]>([]);
  const [clientRegistrySummary, setClientRegistrySummary] = useState<any>(null);
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false);

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
    setSelectedAdminAgents((current) =>
      current.includes(agentId) ? current.filter((item) => item !== agentId) : [...current, agentId]
    );
  }

  function toggleDeploymentAgent(agentId: string) {
    setSelectedDeploymentAgents((current) =>
      current.includes(agentId) ? current.filter((item) => item !== agentId) : [...current, agentId]
    );
  }

  function selectAllDeploymentAgents() {
    setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map(([agentId]) => agentId));
  }

  function clearDeploymentAgents() {
    setSelectedDeploymentAgents([]);
  }

  async function runAdminAgent() {
    if (selectedAdminAgents.length === 0 || !task.trim()) {
      setRunResult({ success: false, message: "Select at least one agent and enter a task." });
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
            account_reference: "owner_admin",
            requested_agent: agentId,
            workflow_stage: "admin_internal_execution",
            action_type: "premium_admin_workspace_execution",
            actor_role: "owner",
            owner_approved: true,
            business_context: {
              business_name: businessName,
              niche: businessNiche,
              target_market: targetMarket,
            },
            task,
          }),
        });

        const data = await response.json();
        results.push({ agent_id: agentId, http_status: response.status, result: data });
      }

      const allSucceeded = results.every((item) => item.result?.success === true);
      setRunResult({
        success: allSucceeded,
        status: allSucceeded ? "admin_workspace_execution_completed" : "admin_workspace_execution_partially_blocked",
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
        body: JSON.stringify({ path: "/admin/deployment-control/list?limit=25", method: "GET" }),
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
        body: JSON.stringify({ path: "/admin/deployment-control/summary", method: "GET" }),
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
      background: "linear-gradient(135deg,var(--color-bg-light) 0%,#eef6ff 42%,var(--color-bg-light) 100%)",
      color: "var(--color-dark)",
      padding: "42px 24px",
      fontFamily: "Inter, sans-serif",
    }}>
      <section style={{ maxWidth: 1480, margin: "0 auto" }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "minmax(0,1.4fr) minmax(320px,.6fr)",
          gap: 24,
          alignItems: "stretch",
        }}>
          <div style={{
            background: "#ffffff",
            border: "1px solid var(--color-border)",
            borderRadius: 32,
            padding: 34,
            boxShadow: "0 28px 70px rgba(37,99,235,.10)",
          }}>
            <div style={{ color: "var(--color-brand)", fontWeight: 900, letterSpacing: 1 }}>
              OWNER WORKSPACE + ADMIN COMMAND CENTRE
            </div>
            <h1 style={{ fontSize: 58, lineHeight: 1.02, margin: "14px 0 0", color: "var(--color-dark)" }}>
              Ecommerce AI Agent Platform
            </h1>
            <p style={{ color: "var(--color-mid)", marginTop: 16, maxWidth: 920, lineHeight: 1.75, fontSize: 16 }}>
              Admin now mirrors the premium client workspace experience while preserving elevated owner controls for deployments, client access, runtime health, billing, recovery, and governance.
            </p>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 24 }}>
              <StatusPill label="Client workspace mirror" ok={true} />
              <StatusPill label="Owner controls" ok={true} />
              <StatusPill label="Runtime" ok={runtimeStatus === "online"} />
            </div>
          </div>

          <div style={{
            background: "#ffffff",
            border: "1px solid var(--color-border)",
            borderRadius: 32,
            padding: 28,
            color: "var(--color-dark)",
            boxShadow: "0 28px 70px rgba(37,99,235,.08)",
          }}>
            <div style={{ color: "var(--color-brand)", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>PLATFORM STATUS</div>
            <div style={{ fontSize: 34, fontWeight: 950, marginTop: 12, color: "#047857" }}>{runtimeStatus}</div>
            <p style={{ color: "var(--color-mid)", lineHeight: 1.7 }}>
              Owner/admin access is unrestricted by client credits. Governance, auditability, and high-risk approval boundaries remain preserved.
            </p>
          </div>
        </div>

        {loading ? <p style={{ marginTop: 40, color: "var(--color-muted)" }}>Loading admin runtime...</p> : null}

        {runtime ? (
          <>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
              gap: 18,
              marginTop: 28,
            }}>
              <Card title="Successful Executions" value={runtime.execution_summary?.successful_executions || 0} />
              <Card title="Pending Approvals" value={runtime.execution_summary?.pending_approvals || 0} />
              <Card title="Blocked Executions" value={runtime.execution_summary?.blocked_executions || 0} />
              <Card title="Premium Outputs" value={runtime.execution_summary?.premium_outputs_generated || 0} />
              <Card title="Active Subscriptions" value={runtime.billing_summary?.subscriptions_active || 0} />
              <Card title="Credits Remaining" value={runtime.billing_summary?.credits_remaining || 0} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)", gap: 24, marginTop: 28 }}>
              <Panel title="Business Context" eyebrow="Client portal mirror">
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  This mirrors the client workspace context layer so the owner can test, operate, and validate agent output using the same business-first experience.
                </p>
                <div style={{ display: "grid", gap: 12, marginTop: 14 }}>
                  <TextInput value={businessName} onChange={(event) => setBusinessName(event.target.value)} placeholder="Business name" />
                  <TextInput value={businessNiche} onChange={(event) => setBusinessNiche(event.target.value)} placeholder="Niche / offer / products" />
                  <TextInput value={targetMarket} onChange={(event) => setTargetMarket(event.target.value)} placeholder="Target market / country / audience" />
                </div>
              </Panel>

              <Panel title="Workspace Guardrails" eyebrow="Owner rules">
                <div style={{ display: "grid", gap: 10 }}>
                  <StatusPill label="Client credits bypassed for admin" ok={true} />
                  <StatusPill label="High-risk actions governed" ok={true} />
                  <StatusPill label="Internal configuration hidden" ok={true} />
                  <StatusPill label="Tenant isolation preserved" ok={true} />
                </div>
              </Panel>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(440px,1fr))", gap: 24, marginTop: 28 }}>
              <Panel title="Premium Agent Workspace" eyebrow="Client portal mirror">
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  Run one or multiple agents using the same premium workspace pattern clients experience, with owner/admin execution authority.
                </p>

                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                  gap: 8,
                  maxHeight: "none",
                  overflow: "visible",
                  border: "1px solid var(--color-border)",
                  borderRadius: 18,
                  padding: 12,
                  background: "var(--color-bg-light)",
                }}>
                  {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                    <label key={agentId} style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "12px 16px",
                      borderRadius: 14,
                      background: selectedAdminAgents.includes(agentId) ? "var(--color-border)" : "#ffffff",
                      border: selectedAdminAgents.includes(agentId) ? "1px solid #93c5fd" : "1px solid var(--color-border)",
                      cursor: "pointer",
                      color: "var(--color-dark)",
                    }}>
                      <input type="checkbox" checked={selectedAdminAgents.includes(agentId)} onChange={() => toggleAdminAgent(agentId)} style={{ display: "none" }} />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>

                <div style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 8 }}>
                  Selected agents: {selectedAdminAgents.length}
                </div>

                <textarea
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  rows={8}
                  style={{
                    width: "100%",
                    marginTop: 14,
                    padding: 16,
                    borderRadius: 18,
                    background: "var(--color-bg-light)",
                    color: "var(--color-dark)",
                    border: "1px solid var(--color-border)",
                    resize: "vertical",
                    minHeight: 128,
                    outline: "none",
                  }}
                />

                <PrimaryButton onClick={runAdminAgent} disabled={running} style={{ marginTop: 16, minWidth: 220 }}>
                  {running ? "Running..." : selectedAdminAgents.length > 1 ? "Run Selected Agents" : "Run Agent"}
                </PrimaryButton>

                {runResult ? (
                  <div style={{
                    marginTop: 16,
                    padding: 18,
                    borderRadius: 18,
                    background: runResult.success ? "#ecfdf5" : "#fef2f2",
                    border: runResult.success ? "1px solid #bbf7d0" : "1px solid #fecaca",
                    color: runResult.success ? "#166534" : "#991b1b",
                    lineHeight: 1.6,
                  }}>
                    <strong>{runResult.success ? "Execution completed" : "Execution blocked"}</strong>
                    <div>{runResult.status || runResult.message || "Result received."}</div>
                    {runResult.selected_agent_count ? <div>Agents run: {runResult.selected_agent_count}</div> : null}
                  </div>
                ) : null}
              </Panel>

              <Panel title="Deploy / Suspend / Cancel Client System" eyebrow="Admin capability">
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  Owner/admin controls for manual deployment, unlimited-credit client systems, suspension, cancellation, and reactivation.
                </p>

                <div style={{ display: "grid", gap: 12 }}>
                  <TextInput value={deployTenant} onChange={(event) => setDeployTenant(event.target.value)} placeholder="Account Reference" />
                  <TextInput value={deployCompany} onChange={(event) => setDeployCompany(event.target.value)} placeholder="Company name" />
                  <TextInput value={deployEmail} onChange={(event) => setDeployEmail(event.target.value)} placeholder="Client email" />

                  <div style={{ border: "1px solid var(--color-border)", borderRadius: 18, padding: 14, background: "var(--color-bg-light)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                      <div>
                        <strong>Deploy client agents</strong>
                        <div style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 4 }}>
                          Select exactly which agents this client can access.
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <PrimaryButton type="button" onClick={selectAllDeploymentAgents} style={{ padding: "9px 11px", background: "var(--color-teal)" }}>Select all</PrimaryButton>
                        <PrimaryButton type="button" onClick={clearDeploymentAgents} style={{ padding: "9px 11px", background: "var(--color-red)" }}>Clear</PrimaryButton>
                      </div>
                    </div>

                    <div style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                      gap: 8,
                      maxHeight: "none",
                      overflow: "visible",
                      marginTop: 14,
                    }}>
                      {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                        <label key={`deploy-${agentId}`} style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          padding: "12px 16px",
                          borderRadius: 14,
                          background: selectedDeploymentAgents.includes(agentId) ? "#dcfce7" : "#ffffff",
                          border: selectedDeploymentAgents.includes(agentId) ? "1px solid #86efac" : "1px solid var(--color-border)",
                          cursor: "pointer",
                        }}>
                          <input type="checkbox" checked={selectedDeploymentAgents.includes(agentId)} onChange={() => toggleDeploymentAgent(agentId)} style={{ display: "none" }} />
                          <span>{label}</span>
                        </label>
                      ))}
                    </div>

                    <div style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 10 }}>
                      Deployment agents selected: {selectedDeploymentAgents.length}
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                    <PrimaryButton onClick={() => callDeploymentControl("/admin/deployment-control/manual-deploy", {
                      account_reference: deployTenant,
                      company_name: deployCompany,
                      contact_email: deployEmail,
                      package: "Manual Unlimited",
                      active_agents: selectedDeploymentAgents,
                      unlimited_credits: true,
                    })} style={{ background: "var(--color-teal)" }}>
                      Deploy
                    </PrimaryButton>

                    <PrimaryButton onClick={() => callDeploymentControl("/admin/deployment-control/suspend", {
                      account_reference: deployTenant,
                      reason: "Suspended from admin portal.",
                    })} style={{ background: "var(--color-amber)" }}>
                      Suspend
                    </PrimaryButton>

                    <PrimaryButton onClick={() => callDeploymentControl("/admin/deployment-control/reactivate", {
                      account_reference: deployTenant,
                      reason: "Reactivated from admin portal.",
                    })} style={{ background: "#0284c7" }}>
                      Reactivate
                    </PrimaryButton>

                    <button type="button" onClick={() => setCancelConfirmOpen(true)} style={{ background: "transparent", border: "none", color: "var(--color-red)", fontSize: 14, fontWeight: 700, cursor: "pointer", padding: "10px 0", textAlign: "left" }}>Cancel System <span style={{ color: "var(--color-muted)", fontWeight: 500 }}>(Permanent — requires confirmation)</span></button>
                  </div>

                  {deploymentResult ? (
                    <div style={{
                      padding: 16,
                      borderRadius: 14,
                      background: deploymentResult.success ? "#ecfdf5" : "#fef2f2",
                      border: deploymentResult.success ? "1px solid #bbf7d0" : "1px solid #fecaca",
                      color: deploymentResult.success ? "#166534" : "#991b1b",
                      lineHeight: 1.6,
                    }}>
                      <strong>{deploymentResult.success ? "Action completed" : "Action failed"}</strong>
                      <div>{deploymentResult.status || deploymentResult.message || deploymentResult.error || "Result received."}</div>
                      {deploymentResult.tenant?.activation_link ? <div>Activation link: {deploymentResult.tenant.activation_link}</div> : null}
                    </div>
                  ) : null}
                </div>
              </Panel>

              <Panel title="Client Registry" eyebrow="Admin capability">
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  Track active, suspended, cancelled, and previously deployed client systems.
                </p>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12 }}>
                  <Card title="Total Clients" value={clientRegistrySummary?.tenant_count || clientRegistry.length || 0} />
                  <Card title="Active" value={clientRegistrySummary?.active_count || 0} />
                  <Card title="Suspended" value={clientRegistrySummary?.suspended_count || 0} />
                  <Card title="Cancelled" value={clientRegistrySummary?.cancelled_count || 0} />
                </div>

                <div style={{ marginTop: 16, display: "grid", gap: 10, maxHeight: 360, overflow: "auto" }}>
                  {clientRegistry.length === 0 ? (
                    <div style={{ color: "var(--color-muted)" }}>No deployed clients found yet.</div>
                  ) : clientRegistry.map((client) => (
                    <div key={client.account_reference} style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "var(--color-bg-light)",
                      border: "1px solid var(--color-border)",
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                        <strong>{client.company_name || "Client"}</strong>
                        <span style={{
                          padding: "6px 10px",
                          borderRadius: 999,
                          background: client.access_status === "active" ? "#dcfce7" : client.access_status === "suspended" ? "#ffedd5" : "#fee2e2",
                          color: client.access_status === "active" ? "#166534" : client.access_status === "suspended" ? "#9a3412" : "#991b1b",
                          fontSize: 12,
                          fontWeight: 900,
                        }}>
                          {client.access_status || client.status || "unknown"}
                        </span>
                      </div>
                      <div style={{ color: "var(--color-muted)", fontSize: 13, marginTop: 8 }}>
                        {client.contact_email || "No email"} · {client.package || "No package"} · Agents: {(client.active_agents || []).length}
                      </div>
                      <div style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 6 }}>
                        Credits: {client.unlimited_credits ? "Unlimited" : client.credit_state?.credits_remaining || "Limited"}
                      </div>
                    </div>
                  ))}
                </div>
              </Panel>

              <Panel title="Runtime, Billing & Governance" eyebrow="Admin capability">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Backend" ok={runtime.health?.ok === true} />
                  <StatusPill label="Governance" ok={runtime.runtime?.governance_layer === "active"} />
                  <StatusPill label="Billing" ok={runtime.runtime?.billing_runtime === "active"} />
                  <StatusPill label="Premium Output" ok={runtime.runtime?.premium_output_runtime === "active"} />
                  <StatusPill label="Stripe runtime" ok={runtime.billing_summary?.stripe_live_ready === true} />
                  <StatusPill label="Deployment" ok={runtime.deployment_summary?.environment_status === "production_ready"} />
                  <StatusPill label="Protected data exposure" ok={runtime.security_summary?.secret_exposure_detected === false} />
                </div>
              </Panel>

              <Panel title="Provider Governance" eyebrow="Admin capability">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Provider readiness route" ok={providerReady} />
                  <StatusPill label="OpenAI SDK route" ok={sdkReady} />
                  <StatusPill label="Live LLM control" ok={liveControlReady} />
                </div>
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  Live provider execution remains owner-gated. Provider keys and internal platform settings are hidden from client surfaces.
                </p>
              </Panel>

              <Panel title="Operational Recovery" eyebrow="Admin capability">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                  <StatusPill label="Recovery tooling" ok={recoveryReady} />
                  <StatusPill label="Artifact registry" ok={artifactsReady} />
                </div>
                <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                  Recovery, retry preparation, replay preparation, and artifact visibility are available for owner/admin use.
                </p>
              </Panel>
            </div>
          </>
        ) : (
          <div style={{
            marginTop: 40,
            padding: 22,
            borderRadius: 18,
            background: "#fef2f2",
            border: "1px solid #fecaca",
            color: "#991b1b",
          }}>
            Admin runtime unavailable.
          </div>
        )}
        {cancelConfirmOpen ? (
          <div style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.55)",
            display: "grid",
            placeItems: "center",
            zIndex: 1000,
            padding: 22,
          }}>
            <div style={{
              width: "100%",
              maxWidth: 480,
              background: "#ffffff",
              border: "1px solid var(--color-border)",
              borderRadius: 18,
              padding: 22,
              boxShadow: "0 24px 80px rgba(15,23,42,.24)",
            }}>
              <h3 style={{ margin: 0, color: "var(--color-dark)", fontSize: 22 }}>Cancel this client system?</h3>
              <p style={{ color: "var(--color-muted)", lineHeight: 1.7 }}>
                This is a destructive admin action. It should only be used when the client system must be cancelled. Suspension is safer if access only needs to be paused.
              </p>
              <div style={{ display: "flex", gap: 12, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 20 }}>
                <button
                  type="button"
                  onClick={() => setCancelConfirmOpen(false)}
                  style={{
                    border: "1px solid var(--color-border)",
                    background: "transparent",
                    color: "var(--color-mid)",
                    borderRadius: 8,
                    padding: "12px 18px",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  Go back
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setCancelConfirmOpen(false);
                    callDeploymentControl("/admin/deployment-control/cancel", {
                      account_reference: deployTenant,
                      reason: "Cancelled from admin portal.",
                    });
                  }}
                  style={{
                    border: "none",
                    background: "var(--color-red)",
                    color: "#fff",
                    borderRadius: 8,
                    padding: "12px 18px",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  Confirm cancellation
                </button>
              </div>
            </div>
          </div>
        ) : null}

      </section>
    </main>
  );
}
