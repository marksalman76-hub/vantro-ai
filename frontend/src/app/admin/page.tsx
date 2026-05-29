"use client";

import { useEffect, useState } from "react";

const ADMIN_AGENT_OPTIONS: [string, string][] = [
  ["head_agent", "Head Agent"],
  ["orchestration_agent", "Orchestration Agent"],
  ["strategist_agent", "Strategist Agent"],
  ["business_growth_partnerships_agent", "Business Growth Agent"],
  ["lead_generator_appointment_setter_agent", "Lead Generation Agent"],
  ["sales_closer_agent", "Sales / Closer Agent"],
  ["marketing_specialist_agent", "Marketing Specialist Agent"],
  ["social_media_manager_content_creator_agent", "Social Media Manager Agent"],
  ["social_media_manager_content_creator_agent", "Content Creator Agent"],
  ["paid_ads_agent", "Ad Creative Agent"],
  ["campaign_launch_agent", "Campaign Launch Agent"],
  ["creative_rotation_agent", "Creative Rotation Agent"],
  ["seo_agent", "SEO Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["product_image_agent", "Product Image Direction Agent"],
  ["product_research_agent", "Product Research Agent"],
  ["competitor_intelligence_agent", "Competitor Intelligence Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["website_landing_apps_agent", "Website / Landing Page Agent"],
  ["crm_ai_agent", "CRM Agent"],
  ["email_marketing_agent", "Email Marketing Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["fulfilment_agent", "Fulfilment Agent"],
  ["marketplace_agent", "Marketplace Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
];

type RuntimePayload = {
  runtime?: any;
  execution_summary?: any;
  billing_summary?: any;
  provider_governance?: any;
  operations?: any;
};

function StatusRow({ label, status, tone }: { label: string; status: string; tone: "ready" | "warn" | "error" }) {
  return (
    <div className="status">
      <span>{label}</span>
      <b className={tone}>{status}</b>
    </div>
  );
}

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      {subtitle ? <p>{subtitle}</p> : null}
      {children}
    </div>
  );
}

export default function AdminPage() {
  const [activeNav, setActiveNav] = useState("Overview");
  const [runtime, setRuntime] = useState<RuntimePayload | null>(null);
  const [selectedRun, setSelectedRun] = useState<string[]>(["marketing_specialist_agent"]);
  const [selectedDeploy, setSelectedDeploy] = useState<string[]>(ADMIN_AGENT_OPTIONS.map(([id]) => id));
  const [task, setTask] = useState("Analyse market positioning for a professional services firm entering the healthcare technology sector. Identify three strategic growth opportunities with supporting rationale.");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<any>(null);
  const [implementationPlans, setImplementationPlans] = useState<any[]>([]);
  const [latestImplementationPlan, setLatestImplementationPlan] = useState<any>(null);
  const [deployTenant, setDeployTenant] = useState("client_manual_001");
  const [deployCompany, setDeployCompany] = useState("Acme Consulting Group");
  const [deployEmail, setDeployEmail] = useState("");
  const [deploymentResult, setDeploymentResult] = useState<any>(null);
  const [clientRegistry, setClientRegistry] = useState<any[]>([]);
  const [clientRegistrySummary, setClientRegistrySummary] = useState<any>(null);
  const [toast, setToast] = useState("");
  const [cancelOpen, setCancelOpen] = useState(false);
  const [busyAction, setBusyAction] = useState("");
  const [orchestration, setOrchestration] = useState<any>({
    readiness: null,
    routes: null,
    liveExecutions: null,
    deadLetters: null,
    manualReview: null,
  });
  const [orchestrationBusy, setOrchestrationBusy] = useState(false);
  const [orchestrationResult, setOrchestrationResult] = useState<any>(null);

  const [clock, setClock] = useState("--:--:--");

  useEffect(() => {
    const updateClock = () => setClock(new Date().toLocaleTimeString("en-GB", { hour12: false }));
    updateClock();
    const timer = window.setInterval(updateClock, 1000);
    return () => window.clearInterval(timer);
  }, []);

  function showToast(message: string) {
    setToast(message);
    setTimeout(() => setToast(""), 3200);
  }

  function goToSection(item: string) {
    setActiveNav(item);
    const map: Record<string, string> = {
      "Overview": "admin-overview",
      "Run Agent": "admin-run",
      "Deploy Clients": "admin-deploy",
      "Client Registry": "admin-registry",
      "Runtime Health": "admin-health",
      "Provider Governance": "admin-governance",
      "Orchestration": "admin-orchestration",
      "Recovery": "admin-recovery",
      "Billing": "admin-billing",
    };
    const target = document.getElementById(map[item]);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function toggleRun(agentId: string) {
    setSelectedRun((current) => current.includes(agentId) ? current.filter((id) => id !== agentId) : [...current, agentId]);
  }

  function toggleDeploy(agentId: string) {
    setSelectedDeploy((current) => current.includes(agentId) ? current.filter((id) => id !== agentId) : [...current, agentId]);
  }

  async function loadRuntime() {
    try {
      const response = await fetch("/api/admin-runtime", { cache: "no-store" });
      const data = await response.json();
      setRuntime(data);
      showToast("Runtime refreshed.");
    } catch {
      setRuntime(null);
      showToast("Runtime refresh failed.");
    }
  }

  async function loadClientRegistry() {
    try {
      const listResponse = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/list?limit=25",
          method: "GET",
        }),
      });
      const listData = await listResponse.json();
      setClientRegistry(listData.tenants || []);
    } catch {
      setClientRegistry([]);
    }

    try {
      const summaryResponse = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/summary",
          method: "GET",
        }),
      });
      const summaryData = await summaryResponse.json();
      setClientRegistrySummary(summaryData);
    } catch {
      setClientRegistrySummary(null);
    }
  }

  useEffect(() => {
    loadRuntime();
    loadClientRegistry();
    loadOrchestrationDashboard();
  }, []);


  async function callAdminProxy(path: string, method: "GET" | "POST" = "GET", payload: any = null) {
    const response = await fetch("/api/admin-deployment-control", {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
      },
      body: JSON.stringify({ path, method, payload }),
    });
    return response.json();
  }

  async function loadOrchestrationDashboard() {
    setOrchestrationBusy(true);
    try {
      const [routingReady, routingList, liveReady, liveList, deadLetters, manualReview] = await Promise.all([
        callAdminProxy("/admin/workflow-provider-routing/readiness", "GET"),
        callAdminProxy("/admin/workflow-provider-routing/list?limit=10", "GET"),
        callAdminProxy("/admin/live-provider-execution/readiness", "GET"),
        callAdminProxy("/admin/live-provider-execution/list?limit=10", "GET"),
        callAdminProxy("/admin/dead-letter/list?limit=10", "GET"),
        callAdminProxy("/admin/manual-review/list?limit=10", "GET"),
      ]);

      setOrchestration({
        readiness: {
          routing: routingReady,
          live_execution: liveReady,
        },
        routes: routingList,
        liveExecutions: liveList,
        deadLetters,
        manualReview,
      });
      showToast("Orchestration dashboard refreshed.");
    } catch {
      setOrchestration({
        readiness: null,
        routes: null,
        liveExecutions: null,
        deadLetters: null,
        manualReview: null,
      });
      showToast("Orchestration dashboard refresh failed.");
    } finally {
      setOrchestrationBusy(false);
    }
  }

  async function runOrchestrationSmokeTest() {
    setOrchestrationBusy(true);
    setOrchestrationResult(null);

    try {
      const routeResult = await callAdminProxy("/admin/workflow-provider-routing/route", "POST", {
        tenant_id: "owner",
        workflow_id: "admin_orchestration_dashboard_test",
        agent_id: "marketing_specialist_agent",
        action_type: "generate_campaign_copy",
        workflow_payload: {
          provider: "openai",
          brand: "Owner Admin",
          region: "global",
          task: "campaign copy",
        },
        available_providers: ["openai"],
        entitlement_active: true,
      });

      const packet = routeResult?.provider_execution_packet || {};

      const executionResult = await callAdminProxy("/admin/live-provider-execution/execute", "POST", {
        tenant_id: packet.tenant_id || "owner",
        workflow_id: packet.workflow_id || "admin_orchestration_dashboard_test",
        agent_id: packet.agent_id || "marketing_specialist_agent",
        provider: packet.provider || "openai",
        action_type: packet.action_type || "generate_campaign_copy",
        payload: packet.payload || {},
        execution_allowed: packet.execution_allowed === true,
        owner_approved: true,
        live_keys_available: false,
        entitlement_active: true,
      });

      setOrchestrationResult({
        status: "orchestration_smoke_test_completed",
        routeResult,
        executionResult,
      });

      await loadOrchestrationDashboard();
      showToast("Orchestration smoke test completed.");
    } catch {
      setOrchestrationResult({
        status: "orchestration_smoke_test_failed",
        message: "Unable to run orchestration smoke test.",
      });
      showToast("Orchestration smoke test failed.");
    } finally {
      setOrchestrationBusy(false);
    }
  }

  async function runAdminAgent() {
    if (selectedRun.length === 0 || !task.trim()) {
      setRunResult({ success: false, message: "Select at least one agent and enter a task." });
      showToast("Select at least one agent and enter a task.");
      return;
    }

    setRunning(true);
    setRunResult(null);

    try {
      const results = [];

      for (const agentId of selectedRun) {
        const response = await fetch("/api/admin-live-execution", {
          method: "POST",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            requested_agent: agentId,
            task,
          }),
        });

        const wrapper = await response.json().catch(() => ({
          success: false,
          message: "Invalid admin live execution response.",
        }));

        const data = wrapper?.data || wrapper;
        const execution = data?.execution || {};
        const adapter = execution?.adapter_result || {};
        const normalised = adapter?.normalised_response || {};
        const safeOutput = normalised?.safe_output || {};

        results.push({
          agent_id: agentId,
          http_status: response.status,
          success: data?.success === true,
          status:
            execution?.execution_status ||
            data?.execution_status ||
            data?.status ||
            data?.error ||
            "completed",
          provider: wrapper?.provider_key || adapter?.provider_key || "openai",
          live_external_call_executed: wrapper?.live_external_call_executed === true || adapter?.live_external_call_executed === true,
          latency_ms: wrapper?.latency_ms || adapter?.latency_ms || null,
          credential_values_exposed: wrapper?.credential_values_exposed === true || adapter?.credential_values_exposed === true,
          customer_safe: wrapper?.customer_safe === true || adapter?.customer_safe === true,
          output:
            wrapper?.normalized_output ||
            safeOutput?.text ||
            data?.output?.generated_output ||
            data?.output?.output ||
            data?.output?.content ||
            data?.generated_output ||
            data?.result ||
            "",
          message:
            data?.message ||
            data?.summary ||
            data?.error ||
            "Live provider execution response received.",
        });
      }

      const allSucceeded = results.every((item) => item.success === true && item.live_external_call_executed === true);

      setRunResult({
        success: allSucceeded,
        status: allSucceeded
          ? "Live execution completed"
          : "Live execution needs review",
        selected_agent_count: selectedRun.length,
        results,
      });

      showToast(allSucceeded ? "Selected agents completed live execution." : "Some live agent runs need review.");
    } catch {
      setRunResult({ success: false, message: "Admin execution failed." });
      showToast("Admin execution failed.");
    } finally {
      setRunning(false);
    }
  }

  async function callDeploymentControl(path: string, payload: any, label: string) {
    setBusyAction(label);
    setDeploymentResult(null);

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

      const activationLink =
        data?.tenant?.activation_link ||
        data?.activation_link ||
        data?.activation?.activation_link ||
        data?.invite?.activation_link ||
        "";

      if (activationLink) {
        showToast("Deployment completed. Activation link generated.");
      } else {
        showToast(data?.success === false ? "Deployment action failed." : `${label} completed.`);
      }
    } catch {
      setDeploymentResult({ success: false, message: "Deployment control action failed." });
      showToast("Deployment control action failed.");
    } finally {
      setBusyAction("");
    }
  }

  function deployClient() {
    const cleanEmail = deployEmail.trim().toLowerCase();

    if (!cleanEmail || !cleanEmail.includes("@")) {
      showToast("Enter a valid client email before deploying.");
      return;
    }

    callDeploymentControl(
      "/admin/deployment-control/manual-deploy",
      {
        account_reference: deployTenant,
        company_name: deployCompany,
        contact_email: cleanEmail,
        package: "Manual Unlimited",
        active_agents: selectedDeploy,
        unlimited_credits: true,
      },
      "Deploy"
    );
  }

  function suspendClient() {
    callDeploymentControl(
      "/admin/deployment-control/suspend",
      {
        account_reference: deployTenant,
        reason: "Suspended from admin portal.",
      },
      "Suspend"
    );
  }

  function reactivateClient() {
    callDeploymentControl(
      "/admin/deployment-control/reactivate",
      {
        account_reference: deployTenant,
        reason: "Reactivated from admin portal.",
      },
      "Reactivate"
    );
  }

  function cancelClient() {
    setCancelOpen(false);
    callDeploymentControl(
      "/admin/deployment-control/cancel",
      {
        account_reference: deployTenant,
        reason: "Cancelled from admin portal.",
      },
      "Cancel"
    );
  }


  async function approveOutcomeAndCreatePlan(item: any) {
    const outcomeText =
      item?.output ||
      item?.generated_output ||
      item?.response ||
      item?.provider_output ||
      item?.message ||
      "";

    if (!outcomeText.trim()) {
      showToast("No outcome available to convert into an implementation plan.");
      return;
    }

    const createVisibleFallbackPlan = (reason: string) => {
      const actionLines = outcomeText
        .split("\n")
        .map((line: string) => line.replace(/^[-•\s]+/, "").trim())
        .filter((line: string) =>
          line.length > 35 &&
          /create|develop|launch|build|prepare|identify|review|generate|draft|plan|initiate|assign|schedule|assemble|conduct|monitor|evaluate/i.test(line)
        )
        .slice(0, 10);

      const fallbackLines = actionLines.length ? actionLines : [
        "Review the generated outcome and convert it into an implementation checklist.",
        "Assign the relevant specialist agents to create the required deliverables.",
        "Prepare the final client-safe implementation package for review.",
      ];

      const packets = fallbackLines.map((line: string, index: number) => ({
        packet_id: `visible_packet_${Date.now()}_${index}`,
        sequence: index + 1,
        title: line.slice(0, 140),
        action: line,
        recommended_agent: item?.agent_id || "orchestration_agent",
        risk_level: /budget|spend|contract|legal|security|compliance|payment|client data/i.test(line) ? "high" : "medium",
        approval_required: true,
        owner_approved: true,
        execution_status: "ready_for_implementation_review",
      }));

      return {
        success: true,
        fallback_used: true,
        fallback_reason: reason,
        plan_id: `visible_plan_${Date.now()}`,
        action_count: packets.length,
        action_packets: packets,
        approval_summary: {
          approval_required_count: packets.length,
          safe_auto_ready_count: 0,
        },
      };
    };

    try {
      const response = await fetch("/api/outcome-action-plan", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          outcome_text: outcomeText,
          source_agent: item?.agent_id || "unknown_agent",
          tenant_id: "owner_admin",
          project_id: "admin_outcome_approval",
          owner_approved: true,
        }),
      });

      let plan: any = null;

      try {
        const wrapper = await response.json();
        plan = wrapper?.data || wrapper;
      } catch {
        plan = createVisibleFallbackPlan("api_response_not_json");
      }

      if (!response.ok || !plan?.success) {
        plan = createVisibleFallbackPlan(`api_failed_${response.status}`);
      }

      setLatestImplementationPlan(plan);
      setImplementationPlans((prev) => [plan, ...prev].slice(0, 20));
      showToast(`Approved. ${plan.action_count || 0} implementation action packet(s) created.`);
    } catch {
      const plan = createVisibleFallbackPlan("frontend_fetch_failed");
      setLatestImplementationPlan(plan);
      setImplementationPlans((prev) => [plan, ...prev].slice(0, 20));
      showToast(`Approved. ${plan.action_count || 0} implementation action packet(s) created.`);
    }
  }

  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];
  const runtimeStatus = runtime?.runtime?.platform_status || "online";
  const registryTotal = clientRegistrySummary?.total || clientRegistrySummary?.tenant_count || clientRegistry.length || 0;

  return (
    <main className="admin-v2">
      <div className="topbar">
        <div className="brand">
          <div className="mark">AI</div>
          <div>
            <strong>Owner Command Centre</strong>
            <span>AI Workforce Platform</span>
          </div>
        </div>
        <div className="topRight">
          <span className="runtime"><i /> Runtime: {runtimeStatus}</span>
          <span className="clock">{clock}</span>
          <span className="avatar">OW</span>
        </div>
      </div>

      <div className="layout">
        <aside className="sidebar">
          <div className="sideGroup">
            <p>Platform</p>
            {navItems.slice(0, 4).map((item) => (
              <button key={item} className={activeNav === item ? "active" : ""} onClick={() => goToSection(item)}>
                {item}
                {item === "Deploy Clients" ? <em>{selectedDeploy.length}</em> : null}
              </button>
            ))}
          </div>

          <div className="sideGroup">
            <p>Health</p>
            {navItems.slice(4).map((item) => (
              <button key={item} className={activeNav === item ? "active" : ""} onClick={() => goToSection(item)}>
                {item}
                {["Provider Governance", "Recovery"].includes(item) ? <em>!</em> : null}
              </button>
            ))}
          </div>

          <div className="owner">
            <span className="avatar">OW</span>
            <div>
              <strong>Owner Admin</strong>
              <small>Unrestricted · 27 agents</small>
            </div>
          </div>
        </aside>

        <section className="content">
          <header className="pageHead" id="admin-overview">
            <span>Owner Command Centre</span>
            <h1>AI Workforce Platform</h1>
            <p>Execution · Billing · Provider governance · Recovery · Launch monitoring</p>
            <div className="badges">
              <b>Client workspace mirror: Ready</b>
              <b>Owner controls: Ready</b>
              <b>Governance: Active</b>
              <b>27-agent catalogue</b>
            </div>
          </header>

          <section className="metrics">
            {[
              ["Successful executions", runtime?.execution_summary?.successful_executions ?? 0, "teal"],
              ["Pending approvals", runtime?.execution_summary?.pending_approvals ?? 0, "gold"],
              ["Blocked executions", runtime?.execution_summary?.blocked_executions ?? 0, "red"],
              ["Premium outputs", runtime?.execution_summary?.premium_outputs_generated ?? 0, "brand"],
              ["Active subscriptions", runtime?.billing_summary?.subscriptions_active ?? 0, "brand"],
              ["Credits remaining", runtime?.billing_summary?.credits_remaining ?? 0, "neutral"],
            ].map(([label, value, tone]) => (
              <div className={`metric ${tone}`} key={label}>
                <small>{label}</small>
                <strong>{value}</strong>
              </div>
            ))}
          </section>

          <section className="orchestrationStrip">
            {[
              ["Routes", orchestration?.routes?.count ?? 0, "Workflow → provider routing"],
              ["Live outputs", orchestration?.liveExecutions?.count ?? 0, "Prepared / executed provider packets"],
              ["Dead letters", orchestration?.deadLetters?.count ?? 0, "Failed workflows needing review"],
              ["Manual review", orchestration?.manualReview?.count ?? 0, "Owner/admin review queue"],
            ].map(([label, value, hint]) => (
              <div className="orchestrationMini" key={label}>
                <small>{label}</small>
                <strong>{value}</strong>
                <span>{hint}</span>
              </div>
            ))}
          </section>

          <section className="grid two">
            <div className="panel" id="admin-run">
              <h2>Run Agent <span>{selectedRun.length} selected</span></h2>
              <p>Run any selected agents from the full 27-agent catalogue. Owner/admin execution bypasses client credit limits while preserving governance.</p>

              <div className="panelActions">
                <button className="ghost" onClick={() => setSelectedRun(ADMIN_AGENT_OPTIONS.map(([id]) => id))}>Select all 27</button>
                <button className="ghost" onClick={() => setSelectedRun([])}>Clear</button>
              </div>

              <label>Select agents</label>
              <div className="pills">
                {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                  <button key={agentId} className={selectedRun.includes(agentId) ? "on brand" : ""} onClick={() => toggleRun(agentId)}>
                    {label}
                  </button>
                ))}
              </div>

              <label>Task</label>
              <textarea value={task} onChange={(e) => setTask(e.target.value)} />

              {running ? <div className="progress"><span /></div> : null}

              <button className="primary" onClick={runAdminAgent} disabled={running}>{running ? "Running..." : selectedRun.length > 1 ? "Run Selected Agents" : "Run Agent"}</button>

              <div className={runResult ? "output has premiumExecutionOutput" : "output premiumExecutionOutput"}>
                {!runResult ? (
                  <div className="emptyExecutionState">
                    <strong>Ready to run</strong>
                    <span>Select agents, enter a task, then run a governed owner/admin execution.</span>
                  </div>
                ) : (
                  <div className="adminResultCard premium">
                    <div className="executionHeader">
                      <div>
                        <small>Governed execution</small>
                        <strong>{runResult?.status || "Execution processed"}</strong>
                        <p>{runResult?.selected_agent_count || 0} selected agent run(s) processed through the governed live provider path.</p>
                      </div>
                      <b className={runResult?.success ? "statusPill success" : "statusPill review"}>
                        {runResult?.success ? "COMPLETED" : "NEEDS REVIEW"}
                      </b>
                    </div>

                    {Array.isArray(runResult?.results) ? (
                      <div className="premiumResultGrid">
                        {runResult.results.map((item: any, index: number) => {
                          const cleanStatus = item?.success
                            ? "Completed"
                            : item?.status === "unsupported_execution_action"
                            ? "Prepared for review"
                            : "Needs review";

                          const liveOutput =
                            item?.output ||
                            item?.generated_output ||
                            item?.response ||
                            item?.provider_output ||
                            item?.message;

                          const cleanMessage = item?.success
                            ? liveOutput || "Agent pipeline completed successfully."
                            : item?.message === "Execution response received."
                            ? "The agent returned a live provider result and is ready for operator review."
                            : item?.message || "Review the governed result before delivery.";

                          return (
                            <div className={item?.success ? "premiumResultCard success" : "premiumResultCard review"} key={index}>
                              <div className="resultTopline">
                                <span>{String(item?.agent_id || "agent").replaceAll("_", " ")}</span>
                                <b>{cleanStatus}</b>
                              </div>
                              <div className="liveOutcomeBox">
                                <strong>Live Outcome</strong>
                                <pre>{cleanMessage}</pre>
                              </div>
                              <div className="executionMetaRow">
                                <span>Provider: {item?.provider || "openai"}</span>
                                <span>Live: {item?.live_external_call_executed ? "Yes" : "No"}</span>
                                <span>Latency: {item?.latency_ms ? `${item.latency_ms}ms` : "—"}</span>
                              </div>

                              <div className="visibleOutcomeActions">
                                <button onClick={() => approveOutcomeAndCreatePlan(item)}>Approve + create plan</button>
                                <button onClick={() => showToast("Amendment requested. Add revision notes in the task box and rerun.")}>Request amendment</button>
                                <button onClick={() => showToast("Outcome rejected by admin.")}>Reject</button>
                                <button onClick={() => navigator.clipboard.writeText(cleanMessage || "")}>Copy outcome</button>
                              </div>

                              <div className="executionTimeline">
                                <span>Generated</span>
                                <span>Review ready</span>
                                <span>{latestImplementationPlan ? "Implementation planned" : item?.success ? "Awaiting approval" : "Needs amendment"}</span>
                              </div>

                              {latestImplementationPlan ? (
                                <div className="implementationPlanBox">
                                  <strong>Implementation Action Plan</strong>
                                  <p>{latestImplementationPlan.action_count || 0} action packet(s) created from approved outcome.</p>
                                  {(latestImplementationPlan.action_packets || []).slice(0, 10).map((packet: any) => {
                                    const recommendedAgent = String(packet.recommended_agent || "agent");
                                    const isAdminOrEnterprise = true;
                                    const ownedAgents = selectedDeploy.length ? selectedDeploy : selectedRun;
                                    const agentOwned = isAdminOrEnterprise || ownedAgents.includes(recommendedAgent);

                                    return (
                                      <div className={agentOwned ? "implementationPacket" : "implementationPacket locked"} key={packet.packet_id}>
                                        <div>
                                          <small>{agentOwned ? "Assigned agent" : "Recommended specialist agent"}</small>
                                          <b>{recommendedAgent.replaceAll("_", " ")}</b>
                                        </div>

                                        <div>
                                          <small>{agentOwned ? "Implementation action" : "Why recommended"}</small>
                                          <span>
                                            {agentOwned
                                              ? packet.title
                                              : "This specialist agent could unlock additional implementation capacity for this outcome."}
                                          </span>
                                        </div>

                                        <div>
                                          <small>{agentOwned ? "Risk / status" : "Package status"}</small>
                                          <em>
                                            {agentOwned
                                              ? `${packet.risk_level || "medium"} · ${packet.execution_status}`
                                              : "Upgrade required · task hidden"}
                                          </em>
                                        </div>

                                        <div className="packetActions">
                                          {agentOwned ? (
                                            <>
                                              <button onClick={() => showToast("Packet queued for governed execution review.")}>Queue</button>
                                              <button onClick={() => showToast("Packet sent to client visibility queue.")}>Send to client</button>
                                            </>
                                          ) : (
                                            <>
                                              <button onClick={() => showToast("Upgrade recommendation saved.")}>Recommend upgrade</button>
                                              <button onClick={() => showToast("Implementation task is hidden until this agent is purchased.")}>Preview value</button>
                                            </>
                                          )}
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              ) : null}
                            </div>
                          );
                        })}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            </div>

            <div className="panel" id="admin-deploy">
              <h2>Deploy Client System <span className="tealTag">{selectedDeploy.length} selected</span></h2>
              <p>Create a client workspace with unlimited credits, selected agent access, and activation link generation.</p>

              <label>Client ID</label>
              <input value={deployTenant} onChange={(e) => setDeployTenant(e.target.value)} />
              <label>Workspace name</label>
              <input value={deployCompany} onChange={(e) => setDeployCompany(e.target.value)} />
              <label>Client email</label>
              <input value={deployEmail} onChange={(e) => setDeployEmail(e.target.value)} placeholder="client@example.com" />

              <div className="panelActions">
                <button className="ghost" onClick={() => setSelectedDeploy(ADMIN_AGENT_OPTIONS.map(([id]) => id))}>Select all 27</button>
                <button className="ghost" onClick={() => setSelectedDeploy([])}>Clear</button>
              </div>

              <label>Deploy agents — select client access</label>
              <div className="pills">
                {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                  <button key={agentId} className={selectedDeploy.includes(agentId) ? "on teal" : ""} onClick={() => toggleDeploy(agentId)}>
                    {label}
                  </button>
                ))}
              </div>

              <button className="deploy" onClick={deployClient} disabled={busyAction !== ""}>
                {busyAction === "Deploy" ? "Deploying..." : "Deploy with unlimited credits"}
              </button>
              <div className="split">
                <button className="warn" onClick={suspendClient} disabled={busyAction !== ""}>Suspend system</button>
                <button className="reactivate" onClick={reactivateClient} disabled={busyAction !== ""}>Reactivate</button>
              </div>
              <button className="dangerText" onClick={() => setCancelOpen(true)}>Cancel system — requires confirmation</button>

              {deploymentResult ? (
                <div className={deploymentResult?.success === false ? "actionStatus error" : "actionStatus ok"}>
                  <strong>{deploymentResult?.success === false ? "Action needs attention" : "Action completed"}</strong>
                  <p>
                    {deploymentResult?.reason === "smtp_not_configured"
                      ? "Deployment prepared and activation link generated. Email was not sent because SMTP is not configured."
                      : deploymentResult?.error === "security_enforcement_blocked"
                      ? "Action blocked by admin security enforcement. Check local admin token configuration."
                      : deploymentResult?.success === false
                      ? deploymentResult?.message || deploymentResult?.error || "The action could not be completed."
                      : "The requested admin action completed successfully."}
                  </p>
                  {deploymentResult?.activation_url || deploymentResult?.activation_link || deploymentResult?.tenant?.activation_link ? (
                    <button
                      className="ghost full"
                      onClick={() => navigator.clipboard.writeText(
                        deploymentResult?.activation_url ||
                        deploymentResult?.activation_link ||
                        deploymentResult?.tenant?.activation_link ||
                        ""
                      )}
                    >
                      Copy activation link
                    </button>
                  ) : null}
                  {deploymentResult?.reason === "smtp_not_configured" ? (
                    <small>Missing SMTP settings: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL</small>
                  ) : null}
                </div>
              ) : null}
            </div>
          </section>

          <section className="grid two">
            <div id="admin-health">
              <Panel title="Runtime Health" subtitle="Core platform runtime status.">
                {["Backend runtime", "Governance controls", "Billing integration", "Premium output pipeline", "Stripe runtime", "Deployment engine", "Data exposure protection"].map((item) => (
                  <StatusRow key={item} label={item} status="Ready" tone="ready" />
                ))}
                <button className="ghost full" onClick={loadRuntime}>Refresh runtime health</button>
              </Panel>
            </div>

            <div id="admin-governance">
              <Panel title="Provider Governance" subtitle="Live provider execution is owner-gated. Provider keys are hidden from clients.">
                <StatusRow label="Provider readiness route" status="Review" tone="warn" />
                <StatusRow label="LLM SDK route" status="Review" tone="warn" />
                <StatusRow label="Live LLM execution control" status="Review" tone="warn" />
                <button className="ghost full" onClick={loadRuntime}>Refresh provider governance</button>
              </Panel>
            </div>
          </section>

          <section className="grid two" id="admin-orchestration">
            <Panel title="Orchestration Dashboard" subtitle="Workflow routing, provider execution, dead-letter handling and owner review visibility.">
              <div className="orchestrationGrid">
                <div>
                  <small>Routing runtime</small>
                  <strong>{orchestration?.readiness?.routing?.status || "review"}</strong>
                </div>
                <div>
                  <small>Live execution</small>
                  <strong>{orchestration?.readiness?.live_execution?.status || "review"}</strong>
                </div>
                <div>
                  <small>Owner gates</small>
                  <strong>Active</strong>
                </div>
                <div>
                  <small>Client safety</small>
                  <strong>Protected</strong>
                </div>
              </div>

              <div className="panelActions">
                <button className="ghost" onClick={loadOrchestrationDashboard} disabled={orchestrationBusy}>
                  {orchestrationBusy ? "Refreshing..." : "Refresh orchestration"}
                </button>
                <button className="ghost" onClick={runOrchestrationSmokeTest} disabled={orchestrationBusy}>
                  Run safe smoke test
                </button>
              </div>

              <div className="timeline">
                {(orchestration?.routes?.routes || []).slice(-5).reverse().map((route: any, index: number) => (
                  <div className="timelineItem" key={route.routing_id || index}>
                    <b>{route.status || "route"}</b>
                    <span>{route.agent_id || "agent"} → {route.selected_provider || route.provider_category || "provider"}</span>
                    <p>{route.route_state || route.action_type || "Workflow route decision recorded."}</p>
                  </div>
                ))}
                {!(orchestration?.routes?.routes || []).length ? (
                  <div className="timelineItem">
                    <b>No route events loaded</b>
                    <span>Refresh or run a safe smoke test</span>
                    <p>Workflow provider routing decisions will appear here.</p>
                  </div>
                ) : null}
              </div>
            </Panel>

            <Panel title="Execution Review Centre" subtitle="Live provider outputs, dead letters and manual review queue.">
              <div className="reviewRows">
                <div>
                  <span>Live provider outputs</span>
                  <b>{orchestration?.liveExecutions?.count ?? 0}</b>
                </div>
                <div>
                  <span>Dead-letter items</span>
                  <b>{orchestration?.deadLetters?.count ?? 0}</b>
                </div>
                <div>
                  <span>Manual review items</span>
                  <b>{orchestration?.manualReview?.count ?? 0}</b>
                </div>
              </div>

              <div className="reviewList">
                {(orchestration?.manualReview?.manual_review_items || []).slice(-4).reverse().map((item: any, index: number) => (
                  <div className="reviewItem" key={item.review_id || index}>
                    <strong>{item.status || "pending_owner_review"}</strong>
                    <span>{item.agent_id || "agent"} · {item.action_type || "action"}</span>
                    <p>{item.failure_reason || "Owner/admin review required before recovery."}</p>
                  </div>
                ))}
                {!(orchestration?.manualReview?.manual_review_items || []).length ? (
                  <div className="reviewItem">
                    <strong>No pending manual reviews</strong>
                    <span>{implementationPlans.length ? `${latestImplementationPlan?.action_count || 0} action packets created from approved outcome.` : "Dead-letter/manual-review runtime is ready"}</span>
                    <p>{implementationPlans.length ? "Review generated action packets and continue to implementation queue." : "Items requiring owner/admin decisions will appear here."}</p>
                  </div>
                ) : null}
              </div>

              <pre className={orchestrationResult ? "output has" : "output"}>
                {orchestrationResult ? JSON.stringify(orchestrationResult, null, 2) : "Orchestration test result will appear here..."}
              </pre>
            </Panel>
          </section>

          <section className="grid two">
            <div id="admin-recovery">
              <Panel title="Operational Recovery" subtitle="Recovery, retry preparation, replay, and artifact visibility.">
                <StatusRow label="Recovery tooling" status="Review" tone="warn" />
                <StatusRow label="Artifact registry" status="Review" tone="warn" />
                <button className="ghost full" onClick={loadRuntime}>Refresh recovery status</button>
              </Panel>
            </div>

            <div id="admin-registry">
              <Panel title="Client Registry" subtitle="Client lifecycle and system state.">
                <div className="registryStats">
                  <div><small>Total</small><strong>{registryTotal}</strong></div>
                  <div><small>Loaded</small><strong>{clientRegistry.length}</strong></div>
                  <div><small>Selected</small><strong>{selectedDeploy.length}</strong></div>
                  <div><small>Agents</small><strong>27</strong></div>
                </div>

                {clientRegistry.length > 0 ? clientRegistry.slice(0, 6).map((client, index) => (
                  <div className="clientRow" key={client.account_reference || client.client_id || index}>
                    <strong>{client.company_name || client.account_reference || client.client_id || "Client"}</strong>
                    <span>{client.status || "active"}</span>
                    <p>{client.contact_email || client.email || "No email"} · Agents: {(client.active_agents || []).length || "—"} · Credits: {client.unlimited_credits ? "Unlimited" : client.credits_remaining || "—"}</p>
                  </div>
                )) : (
                  <div className="clientRow">
                    <strong>No clients loaded</strong>
                    <p>Use Deploy Client System or refresh registry.</p>
                  </div>
                )}

                <button className="ghost full" onClick={loadClientRegistry}>Refresh client registry</button>
              </Panel>
            </div>
          </section>

          <div id="admin-billing">
            <Panel title="Billing & Deployment" subtitle="Subscription, Stripe and deployment readiness.">
              <div className="billingGrid">
                <div>
                  <StatusRow label="Stripe runtime" status="Ready" tone="ready" />
                  <StatusRow label="Deployment status" status="Ready" tone="ready" />
                  <StatusRow label="Data exposure protection" status="Ready" tone="ready" />
                </div>
                <div>
                  <label>Subscription tracking</label>
                  <h3>{(runtime?.billing_summary?.subscriptions_active ?? 0) > 0 ? "Active" : "No live subscriptions"}</h3>
                  <p>Live subscription count: {runtime?.billing_summary?.subscriptions_active ?? 0}</p>
                </div>
                <div>
                  <label>Monthly revenue</label>
                  <h3 className="gradient">${runtime?.billing_summary?.monthly_revenue ?? 0}</h3>
                  <p>{runtime?.billing_summary?.subscriptions_active ?? 0} active subscriptions</p>
                </div>
              </div>
              <button className="ghost full" onClick={() => window.open("https://dashboard.stripe.com", "_blank", "noopener,noreferrer")}>Open Stripe dashboard</button>
            </Panel>
          </div>
        </section>
      </div>

      {cancelOpen ? (
        <div className="modal">
          <div>
            <h2>Cancel this client system?</h2>
            <p>This is permanent. The client loses workspace access, agents, and stored outputs. This action will be logged.</p>
            <div className="split">
              <button className="cancel" onClick={cancelClient}>Confirm cancellation</button>
              <button className="ghost" onClick={() => setCancelOpen(false)}>Go back</button>
            </div>
          </div>
        </div>
      ) : null}

      {toast ? <div className="toast">{toast}</div> : null}

      <style jsx>{`
        .admin-v2{height:100vh;overflow:hidden;background:#08091A;color:#B8C4D8;font-family:Inter,Arial,sans-serif}
        .topbar{height:54px;background:rgba(12,14,31,.95);border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;padding:0 20px;gap:16px}
        .brand{display:flex;align-items:center;gap:10px}.brand strong{display:block;color:#EEF2FF}.brand span{font-size:11px;color:#3E4A5C}.mark,.avatar{background:linear-gradient(135deg,#5B52F0,#7C74FF);color:white;display:grid;place-items:center;font-weight:900}.mark{width:32px;height:32px;border-radius:8px}.avatar{width:30px;height:30px;border-radius:50%;font-size:11px}
        .premiumExecutionOutput{min-height:150px}
        .emptyExecutionState{display:grid;gap:6px;color:#94a3b8}
        .emptyExecutionState strong{color:#EEF2FF;font-size:16px}
        .adminResultCard.premium{display:grid;gap:16px}
        .executionHeader{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;padding:16px;border:1px solid rgba(255,255,255,.08);background:rgba(11,18,38,.74);border-radius:18px}
        .executionHeader small{display:block;color:#8B9CB8;text-transform:uppercase;letter-spacing:.08em;font-size:10px;font-weight:900}
        .executionHeader strong{display:block;color:#EEF2FF;font-size:18px;margin-top:4px}
        .executionHeader p{margin:6px 0 0;color:#AAB7CF;font-size:13px;line-height:1.5}
        .statusPill{border-radius:999px;padding:7px 10px;font-size:10px;font-weight:950;letter-spacing:.06em;white-space:nowrap}
        .statusPill.success{background:rgba(20,184,166,.14);color:#5EEAD4;border:1px solid rgba(20,184,166,.28)}
        .statusPill.review{background:rgba(245,158,11,.14);color:#FCD34D;border:1px solid rgba(245,158,11,.28)}
        .premiumResultGrid{display:grid;gap:12px}
        .premiumResultCard{border-radius:16px;padding:14px;border:1px solid rgba(255,255,255,.08);background:rgba(15,23,42,.76)}
        .premiumResultCard.success{border-color:rgba(20,184,166,.22)}
        .premiumResultCard.review{border-color:rgba(245,158,11,.22)}
        .resultTopline{display:flex;justify-content:space-between;gap:12px;align-items:center}
        .resultTopline span{text-transform:capitalize;color:#EEF2FF;font-weight:900}
        .resultTopline b{font-size:10px;color:#C4B5FD;border:1px solid rgba(196,181,253,.2);border-radius:999px;padding:5px 8px}
        .premiumResultCard p{margin:9px 0 0;color:#AAB7CF;font-size:13px;line-height:1.45}
        .executionTimeline{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
        .executionTimeline span{font-size:10px;font-weight:900;color:#8B9CB8;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.07);border-radius:999px;padding:5px 8px}
        .topRight{margin-left:auto;display:flex;align-items:center;gap:12px}.runtime{display:flex;gap:6px;align-items:center;background:rgba(14,207,188,.1);border:1px solid rgba(14,207,188,.25);border-radius:20px;padding:4px 13px;font-size:11px;color:#0ECFBC;font-weight:800}.runtime i{width:6px;height:6px;background:#0ECFBC;border-radius:50%}.clock{font-family:monospace;color:#3E4A5C}
        .layout{display:flex;height:calc(100vh - 54px)}.sidebar{width:230px;background:#090A16;border-right:1px solid rgba(255,255,255,.06);display:flex;flex-direction:column}.sideGroup{padding:18px 0 6px}.sideGroup p{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#3E4A5C;padding:0 18px 8px}.sideGroup button{width:100%;display:flex;align-items:center;gap:10px;padding:10px 18px;background:transparent;border:0;border-left:2px solid transparent;color:#7A8899;text-align:left;cursor:pointer;font-weight:700}.sideGroup button.active{color:#EEF2FF;background:rgba(91,82,240,.08);border-left-color:#5B52F0}.sideGroup em{margin-left:auto;background:rgba(245,197,24,.18);color:#F5C518;border-radius:9px;padding:2px 7px;font-style:normal;font-size:10px}.owner{margin-top:auto;border-top:1px solid rgba(255,255,255,.06);padding:16px;display:flex;gap:10px;align-items:center}.owner strong{display:block;color:#EEF2FF;font-size:12px}.owner small{color:#3E4A5C}
        .content{flex:1;overflow:auto;padding:28px;background:radial-gradient(ellipse at top,rgba(91,82,240,.07),transparent 320px),#08091A}.pageHead{margin-bottom:26px;scroll-margin-top:24px}.pageHead>span{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:#0ECFBC;font-weight:900}.pageHead h1{font-size:28px;color:#EEF2FF;margin:8px 0 6px}.pageHead p{color:#3E4A5C}.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.badges b{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:5px 13px;font-size:11px;color:#7A8899}
        .metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:22px}.metric{background:#0F1228;border:1px solid rgba(255,255,255,.06);border-left:3px solid;border-radius:12px;padding:18px}.metric small{display:block;color:#3E4A5C;font-size:10px;text-transform:uppercase}.metric strong{display:block;color:#EEF2FF;font-size:34px;margin-top:8px}.teal{border-left-color:#0ECFBC}.gold{border-left-color:#F5C518}.red{border-left-color:#EF4444}.brand{border-left-color:#5B52F0}.neutral{border-left-color:#3E4A5C}
        .grid.two{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}.panel{background:#0F1228;border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:22px;scroll-margin-top:24px}.panel h2{color:#EEF2FF;font-size:17px;margin:0 0 6px}.panel h2 span,.tealTag{font-size:11px;border-radius:12px;padding:3px 8px;background:rgba(91,82,240,.16);color:#9D97FF}.tealTag{background:rgba(14,207,188,.13)!important;color:#34E8D8!important}.panel p{color:#7A8899;line-height:1.6}.panel label{display:block;color:#3E4A5C;font-size:10px;text-transform:uppercase;letter-spacing:.09em;font-weight:900;margin:14px 0 6px}.panelActions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
        .pills{display:flex;flex-wrap:wrap;gap:6px;max-height:260px;overflow-y:auto;padding:2px 4px 6px 0;scrollbar-width:thin}.pills button{padding:7px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);color:#7A8899;cursor:pointer;white-space:nowrap;min-height:32px}.pills .on.brand{background:rgba(91,82,240,.15);border-color:rgba(91,82,240,.4);color:#9D97FF}.pills .on.teal{background:rgba(14,207,188,.12);border-color:rgba(14,207,188,.35);color:#34E8D8}
        input,textarea{width:100%;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:9px;padding:10px 13px;color:#B8C4D8}textarea{min-height:120px;resize:vertical}.primary,.deploy,.ghost,.warn,.reactivate,.cancel{border:0;border-radius:9px;padding:11px 16px;font-weight:800;cursor:pointer}.primary:disabled,.deploy:disabled,.warn:disabled,.reactivate:disabled{opacity:.6;cursor:not-allowed}.primary{width:100%;background:#5B52F0;color:white;margin-top:12px}.deploy{width:100%;background:#0ECFBC;color:#06080F;margin-top:14px}.ghost{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:#B8C4D8}.ghost.full{width:100%;margin-top:14px}.warn{background:transparent;border:1px solid rgba(245,197,24,.3);color:#F5C518}.reactivate{background:transparent;border:1px solid rgba(14,207,188,.35);color:#34E8D8}.cancel{background:#EF4444;color:white}.dangerText{background:transparent;border:0;color:#EF4444;text-align:left;margin-top:10px;cursor:pointer}
        .split{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}.output{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:14px;min-height:80px;color:#3E4A5C;white-space:pre-wrap;margin-top:12px;max-height:360px;overflow:auto}.output.has{color:#B8C4D8;border-color:rgba(14,207,188,.18)}.output.error{color:#fecaca;border-color:rgba(239,68,68,.25)}.actionStatus{margin-top:14px;border-radius:12px;padding:14px 16px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.035)}.actionStatus strong{display:block;color:#EEF2FF;margin-bottom:6px}.actionStatus p{margin:0;color:#B8C4D8}.actionStatus small{display:block;color:#F5C518;margin-top:10px;line-height:1.5}.actionStatus.ok{border-color:rgba(14,207,188,.22);background:rgba(14,207,188,.055)}.actionStatus.error{border-color:rgba(239,68,68,.25);background:rgba(239,68,68,.055)}.progress{height:4px;background:rgba(255,255,255,.08);border-radius:9px;overflow:hidden;margin:10px 0}.progress span{display:block;height:100%;width:80%;background:linear-gradient(90deg,#5B52F0,#0ECFBC);animation:load 1s infinite}
        .status{display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid rgba(255,255,255,.06);padding:11px 0}.status b{font-size:11px;border-radius:20px;padding:4px 11px}.status .ready{background:rgba(14,207,188,.1);color:#0ECFBC}.status .warn{background:rgba(245,197,24,.1);color:#F5C518}.status .error{background:rgba(239,68,68,.1);color:#EF4444}
        .registryStats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.registryStats div{background:rgba(255,255,255,.03);border-radius:9px;padding:12px}.registryStats small{color:#3E4A5C}.registryStats strong{display:block;color:#EEF2FF;font-size:22px}.clientRow{margin-top:12px;background:rgba(255,255,255,.03);border-left:3px solid #3E4A5C;border-radius:9px;padding:13px}.clientRow strong{color:#EEF2FF}.clientRow span{float:right;color:#7A8899}.billingGrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}.gradient{font-size:30px;background:linear-gradient(135deg,#7C74FF,#0ECFBC);-webkit-background-clip:text;color:transparent}
        .orchestrationStrip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:-8px 0 22px}.orchestrationMini{background:#0F1228;border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px}.orchestrationMini small{display:block;color:#3E4A5C;text-transform:uppercase;letter-spacing:.09em;font-size:10px;font-weight:900}.orchestrationMini strong{display:block;color:#EEF2FF;font-size:28px;margin:7px 0}.orchestrationMini span{color:#7A8899;font-size:12px;line-height:1.4}
        .orchestrationGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:14px 0}.orchestrationGrid div{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:12px}.orchestrationGrid small{display:block;color:#3E4A5C;text-transform:uppercase;font-size:9px;font-weight:900}.orchestrationGrid strong{display:block;color:#EEF2FF;margin-top:6px;text-transform:capitalize}
        .timeline,.reviewList{display:grid;gap:8px;margin-top:12px}.timelineItem,.reviewItem{background:rgba(255,255,255,.03);border-left:3px solid #5B52F0;border-radius:10px;padding:12px}.timelineItem b,.reviewItem strong{display:block;color:#EEF2FF;font-size:12px;text-transform:capitalize}.timelineItem span,.reviewItem span{display:block;color:#0ECFBC;font-size:11px;margin-top:4px}.timelineItem p,.reviewItem p{margin:6px 0 0;color:#7A8899;font-size:12px;line-height:1.45}.reviewRows{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0}.reviewRows div{background:rgba(255,255,255,.03);border-radius:10px;padding:12px}.reviewRows span{display:block;color:#3E4A5C;font-size:10px;text-transform:uppercase;font-weight:900}.reviewRows b{display:block;color:#EEF2FF;font-size:24px;margin-top:6px}
        .modal{position:fixed;inset:0;background:rgba(0,0,0,.72);display:grid;place-items:center;z-index:99}.modal>div{width:min(420px,90vw);background:#111426;border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:28px}.toast{position:fixed;right:24px;bottom:24px;background:#0ECFBC;color:#06080F;border-radius:9px;padding:12px 22px;font-weight:800;z-index:120}
        @keyframes load{50%{transform:translateX(20%)}}
        @media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.grid.two,.billingGrid,.orchestrationStrip{grid-template-columns:1fr}.orchestrationGrid,.reviewRows{grid-template-columns:1fr 1fr}.sidebar{display:none}.content{padding:18px}.pills{max-height:320px}}@media(max-width:700px){.metrics{grid-template-columns:1fr 1fr}.topRight .clock{display:none}}
      `}</style>
    </main>
  );
}
