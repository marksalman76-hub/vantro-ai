"use client";

import { useEffect, useMemo, useState } from "react";

const AGENTS: [string, string][] = [
  ["marketing_specialist_agent", "Marketing Specialist Agent"],
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["seo_agent", "SEO Agent"],
  ["crm_ai_agent", "CRM AI Agent"],
  ["email_reply_agent", "Email Reply Agent"],
  ["paid_ads_agent", "Paid Ads Agent"],
  ["product_image_agent", "Product Image Agent"],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
  ["head_agent", "Head Agent"],
  ["strategist_agent", "Strategist Agent"],
  ["business_growth_partnerships_agent", "Business Growth & Partnerships Agent"],
  ["lead_generator_appointment_setter_agent", "Lead Generator / Appointment Setter Agent"],
  ["sales_closer_agent", "Sales / Closer Agent"],
  ["receptionist_agent", "Receptionist Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["ecommerce_agent", "Ecommerce Agent"],
  ["product_research_agent", "Product Research Agent"],
  ["competitor_intelligence_agent", "Competitor Intelligence Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["website_landing_apps_agent", "Website / Landing Page / Apps Agent"],
  ["product_development_agent", "Product Development Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
  ["orchestration_agent", "Orchestration Agent"],
  ["security_compliance_agent", "Security & Compliance Agent"],
  ["integration_automation_agent", "Integration / Automation Agent"],
  ["billing_optimisation_agent", "Billing Optimisation Agent"],
  ["training_learning_agent", "Training / Learning Agent"],
];

type HistoryItem = {
  id: string;
  agent: string;
  agentName: string;
  task: string;
  createdAt: string;
  success: boolean;
  provider: string;
  latency: string;
  output: string;
  raw: any;
};

function agentName(agent: string) {
  return AGENTS.find(([id]) => id === agent)?.[1] || agent;
}



function buildVisualDeliverableCards(output: string, agentLabel: string) {
  const text = String(output || "").trim();
  if (!text) return [];

  const lower = `${agentLabel} ${text}`.toLowerCase();

  if (lower.includes("paid ads") || lower.includes("meta ads") || lower.includes("google search") || lower.includes("ad variation")) {
    return [
      { title: "Campaign Board", detail: "Paid ad concepts, hooks, audiences and CTA variants generated." },
      { title: "Meta Ad Preview", detail: "Primary text, headline and CTA structure ready for review." },
      { title: "Google Search Pack", detail: "Search headlines and descriptions prepared for campaign build." },
      { title: "Short-Form Scripts", detail: "TikTok/Reels scripts and hook structure prepared." },
    ];
  }

  if (lower.includes("ugc") || lower.includes("video concept") || lower.includes("shot-by-shot") || lower.includes("creator")) {
    return [
      { title: "UGC Storyboard", detail: "Shot-by-shot video concepts generated for creator production." },
      { title: "Creator Direction", detail: "Casting, wardrobe, lighting and camera guidance prepared." },
      { title: "Retention Map", detail: "Hooks and pacing beats prepared for short-form performance." },
      { title: "Paid Social Variants", detail: "Ad-ready UGC concepts prepared for campaign testing." },
    ];
  }

  if (lower.includes("seo") || lower.includes("meta description") || lower.includes("keyword")) {
    return [
      { title: "SEO Brief", detail: "Title, meta description and keyword structure generated." },
      { title: "Search Intent Map", detail: "Primary and secondary optimisation angles prepared." },
      { title: "Content Blocks", detail: "Page optimisation and content guidance ready for review." },
    ];
  }

  if (lower.includes("email") || lower.includes("subject")) {
    return [
      { title: "Email Draft", detail: "Subject line and email body generated." },
      { title: "Reply Preview", detail: "Client-safe message ready for review or send workflow." },
    ];
  }

  return [
    { title: "Deliverable Preview", detail: "Generated output is ready for review in the live output panel." },
    { title: "Execution Packet", detail: "Autonomous run completed and saved to history." },
  ];
}


function normalizeExecutionPacket(raw: any) {
  const data = raw?.data || raw || {};
  const execution = data?.execution || data?.result?.execution || {};
  const adapter = execution?.adapter_result || data?.adapter_result || data?.result || data || {};
  const completed = Array.isArray(data?.completed_results) ? data.completed_results : [];
  const queued = Array.isArray(data?.queued_results) ? data.queued_results : [];
  const blocked = Array.isArray(data?.blocked_results) ? data.blocked_results : [];
  const first = completed[0] || queued[0] || blocked[0] || adapter || {};

  const performed =
    data?.performed_actual_action === true ||
    adapter?.performed_actual_action === true ||
    first?.performed_actual_action === true ||
    first?.delegate_execution === "executed" ||
    adapter?.execution_status === "adapter_action_executed" ||
    adapter?.execution_status === "website_project_generated";

  const previewUrl =
    data?.preview_url ||
    adapter?.preview_url ||
    adapter?.result?.preview_url ||
    first?.preview_url ||
    first?.deliverable?.preview_url ||
    "";

  const generatedFiles =
    data?.generated_files ||
    adapter?.generated_files ||
    adapter?.result?.generated_files ||
    first?.generated_files ||
    first?.deliverable?.generated_files ||
    [];

  const provider =
    adapter?.provider ||
    adapter?.provider_key ||
    data?.provider ||
    (performed ? "autonomous" : "");

  const latency =
    adapter?.latency_ms ||
    data?.latency_ms ||
    data?.latency ||
    "";

  const agentId =
    first?.assigned_agent ||
    first?.agent ||
    data?.assigned_agent ||
    data?.agent ||
    adapter?.agent_id ||
    "";

  const output =
    adapter?.output ||
    adapter?.result?.output ||
    data?.output ||
    data?.generated_output ||
    first?.completed_output ||
    first?.deliverable?.content?.body ||
    first?.deliverable?.summary ||
    "";

  const status =
    adapter?.execution_status ||
    first?.execution_status ||
    data?.execution_status ||
    data?.status ||
    (performed ? "autonomously_executed" : "autonomous_execution_processed");

  return {
    raw: data,
    performed,
    autonomous: performed || data?.success === true,
    provider,
    latency,
    agentId,
    status,
    previewUrl,
    generatedFiles,
    output,
    safe: data?.safe ?? adapter?.customer_safe ?? true,
    memory: data?.memory_saved || data?.history_persisted || adapter?.history_persisted || false,
  };
}


function safeString(value: unknown, fallback = "—") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}


function extractSellableDeliverable(value: any): string {
  const raw =
    typeof value === "string"
      ? value
      : value?.safe_output?.text ||
        value?.normalized_output ||
        value?.output_text ||
        value?.generated_output ||
        value?.output?.generated_output ||
        value?.output?.output ||
        value?.output?.content ||
        value?.content ||
        "";

  let text = String(raw || "").trim();
  if (!text) return "";

  const markers = [
    "**Final Premium Product Description",
    "Final Premium Product Description",
    "**Final Product Description",
    "Final Product Description",
    "**Final Deliverable",
    "Final Deliverable",
    "**Final Output",
    "Final Output",
    "**Headline:**",
    "Headline:"
  ];

  for (const marker of markers) {
    const index = text.indexOf(marker);
    if (index >= 0) {
      text = text.slice(index).trim();
      break;
    }
  }

  const internalStart = [
    "1. Executive Summary",
    "2. Business/Industry Context Assumptions",
    "3. Specific Opportunity or Problem Diagnosis",
    "4. Execution Plan with Concrete Steps",
    "5. Deliverables/Assets/Actions to Create",
    "6. KPIs or Measurable Success Criteria",
    "7. Risks, Constraints, and Mitigations",
    "8. Owner/Admin Review Points",
    "9. Immediate Next Actions"
  ];

  for (const heading of internalStart) {
    const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    text = text.replace(new RegExp(`(^|\\n)${escaped}[\\s\\S]*?(?=\\n\\s*(\\*\\*Final|Final|\\*\\*Headline|Headline:)|$)`, "i"), "").trim();
  }

  text = text.replace(/^---+\s*/gm, "").trim();

  if (text.startsWith("{") || text.startsWith("[")) {
    try {
      const parsed = JSON.parse(text);
      return extractSellableDeliverable(parsed);
    } catch {
      return "Technical packet returned. Open technical details for raw output.";
    }
  }

  return text;
}

function buildPortalDeliverableTask(task: string): string {
  return `${task}

OUTPUT RULES:
Return only the finished customer-facing deliverable.
Do not include executive summaries, assumptions, diagnosis, execution plans, KPIs, risks, admin review points, JSON, metadata, or internal reasoning.
For product copy, return only headline, description, and call-to-action.`;
}


function clampMetric(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, Math.round(value)));
}

function dynamicExecutionMetrics(result: any, running: boolean, outputText: string, liveCall: boolean) {
  const qualityScore =
    Number(result?.quality?.quality_score) ||
    Number(result?.quality_score) ||
    Number(result?.execution?.quality?.quality_score) ||
    0;

  const latencyMs =
    Number(result?.execution?.adapter_result?.latency_ms) ||
    Number(result?.latency_ms) ||
    0;

  const providerScore = liveCall ? 100 : running ? 45 : result ? 20 : 0;
  const generationScore = running ? 55 : outputText ? 100 : result ? 35 : 0;
  const qualityDisplay = qualityScore ? qualityScore : autonomousQualityScore(result) || (result?.quality_gate_passed === true ? 100 : result?.quality_gate_passed === false ? 45 : running ? 30 : 0);
  const deliveryScore = outputText && result?.success === true ? 100 : outputText ? 70 : running ? 35 : 0;
  const latencyScore = latencyMs ? Math.max(10, 100 - Math.min(90, Math.round(latencyMs / 120))) : running ? 40 : 0;

  return [
    ["Generated", clampMetric(generationScore)],
    ["Provider", clampMetric(providerScore)],
    ["Quality", clampMetric(qualityDisplay)],
    ["Delivery", clampMetric(deliveryScore)],
    ["Speed", clampMetric(latencyScore)],
  ];
}


function buildStrictTaskExecutionContract(task: string, agentName?: string): string {
  return `${task}

STRICT TASK EXECUTION CONTRACT:
You are acting as a task executor, not a consultant.
Fulfil the user's exact requested task only.
Do not expand the task into a campaign, strategy, report, audit, plan, or multi-channel bundle unless the user explicitly asks for that.

OUTPUT REQUIREMENTS:
- Return only the finished deliverable.
- Do not include executive summary, assumptions, diagnosis, execution plan, KPIs, risks, admin review points, next steps, metadata, JSON, or internal reasoning.
- If the user asks for a product description, return only: Headline, Description, Call-to-action.
- If the user asks for an email, return only: Subject and Email body.
- If the user asks for ad copy, return only the requested ad copy variations.
- If the user asks for social captions, return only captions.
- If the task requires a real external action and the integration is not connected or approval is required, clearly state the exact blocker and the required next action.
- Do not invent completed external actions.

QUALITY BAR:
Make the deliverable commercially usable, specific, premium, concise, and ready to copy into the relevant business tool.`;
}



function inferAutonomousActionType(task: string, selectedAgent: string): string {
  const t = `${selectedAgent} ${task}`.toLowerCase();
  if (selectedAgent === "website_landing_apps_agent" || t.includes("landing page") || t.includes("website") || t.includes("web page")) return "website_draft_page";
  if (selectedAgent === "store_builder_agent" || selectedAgent === "ecommerce_agent" || t.includes("shopify") || t.includes("product page") || t.includes("store")) return "store_draft_update";
  if (selectedAgent === "paid_ads_agent" || t.includes("meta ads") || t.includes("google ads") || t.includes("ad campaign") || t.includes("campaign draft")) return "ads_campaign_draft";
  if (selectedAgent === "email_reply_agent" || t.includes("email")) return "email_draft";
  if (selectedAgent === "crm_ai_agent" || t.includes("crm")) return "crm_follow_up";
  if (selectedAgent === "seo_agent" || t.includes("seo")) return "seo_content_plan";
  if (selectedAgent === "product_image_agent" || t.includes("image")) return "product_image_generation";
  if (selectedAgent === "ugc_creative_agent" || t.includes("ugc")) return "ugc_script_draft";
  if (selectedAgent === "customer_support_agent") return "support_response_draft";
  if (selectedAgent === "receptionist_agent") return "reception_response_draft";
  if (selectedAgent === "lead_generator_appointment_setter_agent") return "lead_outreach_sequence";
  if (selectedAgent === "sales_closer_agent") return "sales_follow_up_sequence";
  return "client_deliverable";
}

function integrationsForAutonomousAgent(selectedAgent: string): string[] {
  const map: Record<string, string[]> = {
    website_landing_apps_agent: ["website", "cms"],
    store_builder_agent: ["store", "website", "cms"],
    ecommerce_agent: ["store", "website", "cms"],
    paid_ads_agent: ["ads"],
    email_reply_agent: ["email"],
    crm_ai_agent: ["crm"],
    seo_agent: ["website", "cms", "analytics"],
    product_image_agent: ["media", "asset_storage"],
    ugc_creative_agent: ["media", "asset_storage"],
    influencer_collaboration_agent: ["email", "crm"],
    lead_generator_appointment_setter_agent: ["email", "crm", "calendar"],
    sales_closer_agent: ["email", "crm"],
    receptionist_agent: ["calendar", "email"],
    customer_support_agent: ["email", "support"],
    analytics_optimisation_agent: ["analytics"],
    integration_automation_agent: ["automation"],
    billing_optimisation_agent: ["billing"],
  };
  return map[selectedAgent] || [];
}

function uniqueValues(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean)));
}

function buildAutonomousImplementationPlan(task: string, selectedAgents: string[] | string) {
  const cleanTask = String(task || "").trim();
  const agents = Array.isArray(selectedAgents) && selectedAgents.length ? selectedAgents : [String(selectedAgents || "marketing_specialist_agent")];

  return {
    plan_id: `portal_plan_${Date.now()}`,
    source: "portal_autonomous_execution",
    action_packets: agents.map((selectedAgent, index) => ({
      packet_id: `portal_packet_${Date.now()}_${index}`,
      title: cleanTask,
      implementation_action: inferAutonomousActionType(cleanTask, selectedAgent),
      user_requested_task: cleanTask,
      recommended_agent: selectedAgent || "marketing_specialist_agent",
      risk_level: "low",
      approval_required: false,
      execution_mode: "autonomous_governed",
      expected_output: "completed_action_evidence",
    })),
  };
}

function extractAutonomousDeliverable(result: any): string {
  const data = result?.data || result || {};
  const completed = Array.isArray(data?.completed_results) ? data.completed_results : [];
  const queued = Array.isArray(data?.queued_results) ? data.queued_results : [];
  const blocked = Array.isArray(data?.blocked_results) ? data.blocked_results : [];
  const first = completed[0] || queued[0] || blocked[0] || {};

  const performed = first?.performed_actual_action === true || first?.delegate_execution === "executed";
  const status = first?.execution_status || first?.autonomous_route || data?.profile || "autonomous_execution_processed";
  const output =
    first?.completed_output ||
    first?.deliverable?.content?.body ||
    first?.deliverable?.summary ||
    first?.execution_preview ||
    first?.upgrade_recommendation ||
    "";

  const evidence = [];
  evidence.push(`Execution status: ${status}`);
  evidence.push(`Performed actual action: ${performed ? "Yes" : "No"}`);

  if (first?.external_action_record_count !== undefined) {
    evidence.push(`External action records: ${first.external_action_record_count}`);
  }

  const records = Array.isArray(first?.external_action_records) ? first.external_action_records : [];
  if (records.length) {
    evidence.push("");
    evidence.push("External Action Proof Records:");
    records.forEach((record: any, index: number) => {
      evidence.push(`Record ${index + 1}:`);
      evidence.push(`  - Action type: ${record?.action_type || record?.type || "not provided"}`);
      evidence.push(`  - Adapter: ${record?.adapter || record?.provider || "not provided"}`);
      evidence.push(`  - Status: ${record?.action_status || record?.status || "not provided"}`);
      evidence.push(`  - Target: ${record?.target_system || record?.integration || record?.destination || "not provided"}`);
      evidence.push(`  - Record ID: ${record?.record_id || record?.id || record?.external_id || "not provided"}`);
      evidence.push(`  - Created at: ${record?.created_at || record?.created_at_ms || record?.timestamp || "not provided"}`);
      evidence.push(`  - Summary: ${record?.summary || record?.result || record?.message || "not provided"}`);
    });
  } else if (first?.external_action_record_count > 0) {
    evidence.push("External action record details were not returned to the UI payload. Backend record-detail passthrough is required for full proof display.");
  }

  if (first?.history_persisted !== undefined) {
    evidence.push(`Execution history saved: ${first.history_persisted ? "Yes" : "No"}`);
  }

  if (Array.isArray(data?.connected_integrations)) {
    evidence.push(`Connected integrations: ${data.connected_integrations.length ? data.connected_integrations.join(", ") : "None"}`);
  }

  if (!performed && !output) {
    evidence.push("Result: Autonomous route completed, but no external tool action was performed. Connect the required integration or owner-approve the action if required.");
  }

  return `${output || "Autonomous execution processed. Review evidence below."}

Completion Evidence:
${evidence.map((line) => `- ${line}`).join("\n")}`;
}


function getAutonomousFirstResult(result: any): any {
  const data = result?.data || result || {};
  const completed = Array.isArray(data?.completed_results) ? data.completed_results : [];
  const queued = Array.isArray(data?.queued_results) ? data.queued_results : [];
  const blocked = Array.isArray(data?.blocked_results) ? data.blocked_results : [];
  return completed[0] || queued[0] || blocked[0] || {};
}

function autonomousProviderLabel(result: any): string {
  const data = result?.data || result || {};
  const first = getAutonomousFirstResult(data);
  if (first?.performed_actual_action === true || first?.delegate_execution === "executed") return "autonomous";
  if (first?.execution_status) return "governed";
  return "—";
}

function autonomousLatencyLabel(result: any): string {
  const data = result?.data || result || {};
  const created = Number(data?.created_at_ms || 0);
  const first = getAutonomousFirstResult(data);
  const actionCreated = Number(first?.created_at_ms || 0);
  if (created && actionCreated) return `${Math.max(1, Math.abs(created - actionCreated))}ms`;
  return "—";
}


function autonomousQualityScore(result: any): number {
  const data = result?.data || result || {};
  const first = getAutonomousFirstResult(data);

  if (!result) return 0;

  let score = 0;

  if (data?.success === true || result?.success === true) score += 20;
  if (first?.performed_actual_action === true || first?.delegate_execution === "executed") score += 35;
  if (Number(first?.external_action_record_count || 0) > 0) score += 20;
  if (first?.history_persisted === true) score += 15;
  if (data?.customer_safe !== false) score += 10;

  if (first?.execution_status === "awaiting_owner_approval") score = Math.min(score, 45);
  if (first?.execution_status === "agent_not_owned") score = Math.min(score, 35);

  return Math.max(0, Math.min(100, Math.round(score)));
}

function autonomousSafeLabel(result: any): string {
  const data = result?.data || result || {};
  return data?.customer_safe === false ? "False" : "True";
}

export default function AdminLiveExecutionPage() {
  const [agent, setAgent] = useState("marketing_specialist_agent");
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["website_landing_apps_agent"]);
  const [task, setTask] = useState("Create a custom premium React/Next.js landing page for a luxury Australian skincare brand targeting women aged 30–50. Use advanced glassmorphism, 3D motion visuals, premium animation, cinematic layout, proof sections, offer section, FAQ, sticky CTA, and generate a real previewable React route. Do not return generic copy. Generate the website project.");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const normalizedResult = normalizeExecutionPacket(result);
  const [selectedPreviewCard, setSelectedPreviewCard] = useState<any>(null);
  const visualDeliverableCards = buildVisualDeliverableCards(normalizedResult?.output || "", selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent));
  const [toast, setToast] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState("");

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem("admin_live_execution_history_v1");
      if (stored) setHistory(JSON.parse(stored));
    } catch {
      setHistory([]);
    }
  }, []);

  function persistHistory(next: HistoryItem[]) {
    setHistory(next);
    try {
      window.localStorage.setItem("admin_live_execution_history_v1", JSON.stringify(next.slice(0, 25)));
    } catch {}
  }

  const execution = result?.execution || {};
  const adapter = execution?.adapter_result || {};
  const normalised = adapter?.normalised_response || {};
  const safeOutput = normalised?.safe_output || {};
  const audit = adapter?.audit_asset || {};
  const outputText = result ? extractAutonomousDeliverable(result) : "";

  const completed = result?.success === true;
  const failed = result && result?.success !== true;
  const firstAutonomousResult = getAutonomousFirstResult(result);
  const liveCall = Boolean(result?.completed_results?.length || firstAutonomousResult?.performed_actual_action || firstAutonomousResult?.delegate_execution === "executed");

  const executionMetrics = dynamicExecutionMetrics(result, running, outputText, liveCall);

  const stats = useMemo(() => {
    const total = history.length;
    const successful = history.filter((item) => item.success).length;
    const live = history.filter((item) => item.raw?.execution?.adapter_result?.live_external_call_executed === true).length;
    const avgLatencyRaw = history
      .map((item) => Number(String(item.latency).replace("ms", "")))
      .filter((n) => Number.isFinite(n) && n > 0);
    const avgLatency = avgLatencyRaw.length ? Math.round(avgLatencyRaw.reduce((a, b) => a + b, 0) / avgLatencyRaw.length) : 0;
    return { total, successful, live, avgLatency };
  }, [history]);

  function toggleSelectedAgent(agentId: string) {
    setAgent(agentId);
    setSelectedAgents((prev) => {
      if (prev.includes(agentId)) {
        const next = prev.filter((id) => id !== agentId);
        return next.length ? next : [agentId];
      }
      return [...prev, agentId];
    });
  }

  async function runLiveExecution() {
    setRunning(true);
    setToast("Execution started. Routing through autonomous workforce runtime...");
    setResult(null);
    setSelectedHistoryId("");

    try {
      const response = await fetch("/api/delegated-workforce-execution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          implementation_plan: buildAutonomousImplementationPlan(buildStrictTaskExecutionContract(task, selectedAgents.map(agentName).join(", ")), selectedAgents),
          owner_approved: true,
          client_owned_agents: selectedAgents,
          package_tier: "enterprise",
          connected_integrations: uniqueValues([...selectedAgents.flatMap(integrationsForAutonomousAgent), "task_store"]),
          tenant_id: "owner_admin",
        }),
      });

      const data = await response.json();
      const liveResult = data?.data || data;
      const normalizedExecution = normalizeExecutionPacket(liveResult);
      setResult(liveResult);

      const liveExecution = liveResult?.execution || {};
      const liveAdapter = liveExecution?.adapter_result || {};
      const liveOutput = extractAutonomousDeliverable(liveResult);
      const autonomousProvider = autonomousProviderLabel(liveResult);
      const autonomousLatency = autonomousLatencyLabel(liveResult);

      const item: HistoryItem = {
        id: `${Date.now()}-${agent}`,
        agent,
        agentName: (selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent)),
        task,
        createdAt: new Date().toLocaleString(),
        success: liveResult?.success === true || normalizedResult.performed,
        provider: autonomousProvider,
        latency: autonomousLatency,
        output: normalizedExecution.output || liveOutput,
        raw: liveResult,
      };

      persistHistory([item, ...history].slice(0, 25));
      setSelectedHistoryId(item.id);
      setToast(liveResult?.success ? "Autonomous workforce execution completed and saved to history." : "Autonomous execution completed with a warning.");
    } catch {
      setToast("Execution failed before reaching the backend.");
    } finally {
      setRunning(false);
    }
  }

  function openHistory(item: HistoryItem) {
    setSelectedHistoryId(item.id);
    setAgent(item.agent);
    setTask(item.task);
    setResult(item.raw);
    setToast("Loaded execution from live history.");
  }

  function clearHistory() {
    persistHistory([]);
    setSelectedHistoryId("");
    setToast("Execution history cleared.");
  }

  function exportResult() {
    const payload = result || { history };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `admin-live-execution-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const assetCandidates = [
    normalizedResult?.previewUrl,
    ...(Array.isArray(normalizedResult?.generatedFiles) ? normalizedResult.generatedFiles : []),
    adapter?.asset_url,
    adapter?.image_url,
    adapter?.video_url,
    adapter?.preview_url,
    adapter?.media_url,
    result?.asset_url,
    result?.image_url,
    result?.video_url,
    result?.media_url,
    result?.preview_url,
  ].filter(Boolean);

  return (
    <main style={{ minHeight: "100vh", background: "#061226", color: "#f8fafc", padding: 36 }}>
      <section style={{ maxWidth: 1560, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>06</span>
              <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em" }}>Live Deliverable Viewer</span>
            </div>
            <h1 style={{ fontSize: 38, margin: "14px 0 4px", fontWeight: 950 }}>Admin execution centre</h1>
            <p style={{ color: "#a8b3cf", fontSize: 17 }}>Run live agents, inspect outputs, review media, and keep local operator history.</p>
          </div>
          <a href="/admin" style={{ color: "#bfdbfe", textDecoration: "none", fontWeight: 900 }}>← Back to admin</a>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 20 }}>
          {[
            ["Executions", stats.total],
            ["Successful", stats.successful],
            ["Live provider", stats.live],
            ["Avg latency", stats.avgLatency ? `${stats.avgLatency}ms` : "—"],
          ].map(([label, value]) => (
            <div key={label} style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.3)", borderRadius: 18, padding: 16 }}>
              <div style={{ color: "#94a3b8", fontSize: 12, fontWeight: 950, textTransform: "uppercase" }}>{label}</div>
              <div style={{ fontSize: 24, fontWeight: 950, marginTop: 6 }}>{value}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "0.95fr 1.25fr 0.8fr", gap: 22 }}>
          <section style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.35)", borderRadius: 28, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>05</span>
                  <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em" }}>Activity</span>
                </div>
                <h2 style={{ fontSize: 28, margin: "14px 0 4px", fontWeight: 950 }}>Activity</h2>
                <p style={{ color: "#a8b3cf", fontWeight: 800 }}>Latest governed activity</p>
              </div>
              <span style={{ background: "#dcfce7", color: "#047857", padding: "10px 14px", borderRadius: 999, fontWeight: 950 }}>Live tracking</span>
            </div>

            <div style={{ display: "grid", gap: 12 }}>
              {[
                ["✓", completed ? "Deliverable generated" : "Ready for execution", completed ? "Latest admin deliverable is ready for review." : "Run selected agent to generate a live deliverable.", completed ? "Ready" : "Waiting"],
                ["⚡", running ? "Execution running" : completed ? "Execution completed" : "Execution prepared", running ? "Governed execution is currently running." : completed ? "Governed execution completed successfully." : "Governed execution is prepared.", running ? "Running" : completed ? "Complete" : "Prepared"],
                ["○", liveCall ? "Live provider confirmed" : "Provider pending", liveCall ? "OpenAI live provider call completed." : "Provider result will appear after execution.", liveCall ? "Verified" : "Pending"],
              ].map(([icon, title, detail, status]) => (
                <div key={title} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14, border: "1px solid rgba(99,102,241,.28)", borderRadius: 22, padding: 16, background: "rgba(15,23,42,.58)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <span style={{ width: 42, height: 42, borderRadius: 16, background: "#082f49", display: "grid", placeItems: "center", color: "#22c55e", fontSize: 21 }}>{icon}</span>
                    <div>
                      <div style={{ fontWeight: 950, fontSize: 16 }}>{title}</div>
                      <div style={{ color: "#a8b3cf", marginTop: 3, fontWeight: 700 }}>{detail}</div>
                    </div>
                  </div>
                  <span style={{ border: "1px solid rgba(99,102,241,.36)", borderRadius: 999, padding: "8px 12px", color: "#67e8f9", fontWeight: 950 }}>{status}</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 20, border: "1px solid rgba(99,102,241,.28)", borderRadius: 22, padding: 18 }}>
              <div style={{ fontWeight: 950, marginBottom: 10 }}>Execution snapshot</div>
              {executionMetrics.map(([label, value]: any) => (
                <div key={label} style={{ marginTop: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", color: "#cbd5e1", fontWeight: 900 }}>
                    <span>{label}</span>
                    <span>{value}%</span>
                  </div>
                  <div style={{ height: 10, background: "rgba(226,232,240,.16)", borderRadius: 99, overflow: "hidden", marginTop: 7 }}>
                    <div style={{ height: "100%", width: `${value}%`, background: value >= 80 ? "#22c55e" : value >= 50 ? "#38bdf8" : value > 0 ? "#f59e0b" : "#334155", transition: "width .35s ease" }} />
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 20 }}>
              <div style={{ border: "1px solid rgba(148,163,184,.35)", borderRadius: 16, background: "#020617", padding: 12, marginBottom: 12, maxHeight: 220, overflow: "auto" }}>
                <div style={{ color: "#bfdbfe", fontSize: 12, fontWeight: 950, marginBottom: 10 }}>Select one or more agents</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2,minmax(0,1fr))", gap: 8 }}>
                  {AGENTS.map(([id, name]) => {
                    const active = selectedAgents.includes(id);
                    return (
                      <button
                        key={id}
                        type="button"
                        onClick={() => toggleSelectedAgent(id)}
                        style={{
                          textAlign: "left",
                          border: active ? "1px solid #38bdf8" : "1px solid rgba(148,163,184,.22)",
                          background: active ? "rgba(14,165,233,.18)" : "rgba(15,23,42,.55)",
                          color: "#fff",
                          borderRadius: 12,
                          padding: "9px 10px",
                          fontWeight: 850,
                          cursor: "pointer",
                          fontSize: 12,
                        }}
                      >
                        {active ? "✓ " : "+ "}{name}
                      </button>
                    );
                  })}
                </div>
              </div>
              <textarea value={task} onChange={(e) => setTask(e.target.value)} rows={5} style={{ width: "100%", padding: 14, borderRadius: 16, background: "#020617", color: "#fff", border: "1px solid rgba(148,163,184,.35)", resize: "vertical" }} />
              <button onClick={runLiveExecution} disabled={running} style={{ width: "100%", marginTop: 14, padding: 16, border: 0, borderRadius: 18, background: running ? "#475569" : "linear-gradient(135deg,#2563eb,#06b6d4)", color: "#fff", fontWeight: 950, cursor: running ? "not-allowed" : "pointer" }}>
                {running ? "Generating..." : "✨ Run Agent"}
              </button>
              {toast ? <p style={{ color: "#bfdbfe", fontWeight: 850 }}>{toast}</p> : null}
            </div>
          </section>

          <section style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.35)", borderRadius: 28, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>06</span>
                  <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em", background: "#1d4ed8" }}>Live Deliverable Viewer</span>
                </div>
                <h2 style={{ fontSize: 28, margin: "14px 0 4px", fontWeight: 950 }}>Admin deliverables</h2>
              </div>
              <span style={{ background: completed ? "#dcfce7" : failed ? "#fee2e2" : "#fef3c7", color: completed ? "#047857" : failed ? "#991b1b" : "#92400e", padding: "10px 14px", borderRadius: 999, fontWeight: 950 }}>
                {completed ? "Completed" : failed ? "Needs review" : running ? "Running" : "Waiting"}
              </span>
            </div>

            <div style={{ border: "1px solid rgba(99,102,241,.34)", borderRadius: 22, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 44, height: 44, borderRadius: 16, background: "#312e81", display: "grid", placeItems: "center", fontSize: 22 }}>✦</span>
                  <div>
                    <div style={{ fontWeight: 950 }}>Media preview</div>
                    <div style={{ color: "#a8b3cf" }}>Generated or uploaded execution assets</div>
                  </div>
                </div>
                <span style={{ color: "#cbd5e1", fontWeight: 900 }}>{assetCandidates.length ? "Assets detected" : "Pending media"}</span>
              </div>

              <div style={{ border: "1px dashed rgba(148,163,184,.3)", borderRadius: 20, minHeight: 150, display: "grid", placeItems: "center", textAlign: "center", color: "#a8b3cf", padding: 18 }}>
                {assetCandidates.length ? (
                  <div style={{ width: "100%" }}>
                    {assetCandidates.map((asset: string) => (
                      <div key={asset} style={{ marginBottom: 14 }}>
                        <img src={asset} alt="Generated UGC visual asset" style={{ width: "100%", maxHeight: 360, objectFit: "contain", borderRadius: 16, border: "1px solid rgba(125,211,252,.25)", background: "#020617" }} />
                        <button
                          type="button"
                          onClick={() => {
                            const a = document.createElement("a");
                            a.href = asset;
                            a.download = `ugc-visual-asset-${Date.now()}.svg`;
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                          }}
                          style={{ display: "block", width: "100%", border: "1px solid rgba(125,211,252,.3)", background: "#020617", color: "#bfdbfe", fontWeight: 900, marginTop: 8, padding: "10px 12px", borderRadius: 12, cursor: "pointer" }}
                        >
                          Download generated asset
                        </button>
                      </div>
                    ))}
                  </div>
                ) : visualDeliverableCards.length ? (
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12, width: "100%", textAlign: "left" }}>
                    {visualDeliverableCards.map((card, idx) => (
                      <button type="button" key={`${card.title}-${idx}`} onClick={() => setSelectedPreviewCard(card)} style={{ cursor: "pointer", textAlign: "left", border: "1px solid rgba(125,211,252,.28)", background: "rgba(14,165,233,.08)", borderRadius: 18, padding: 14 }}>
                        <div style={{ fontSize: 12, color: "#67e8f9", fontWeight: 950, marginBottom: 6 }}>PREVIEW {idx + 1}</div>
                        <div style={{ fontWeight: 950, color: "#fff", marginBottom: 6 }}>{card.title}</div>
                        <div style={{ color: "#c7d2fe", fontSize: 13, lineHeight: 1.35 }}>{card.detail}</div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: 34 }}>🖼️</div>
                    <div style={{ color: "#fff", fontWeight: 950, marginTop: 10 }}>Media assets will appear here</div>
                    <p>Generated images, video, uploaded files, and media previews will appear here when an execution includes assets.</p>
                  </div>
                )}
              </div>
            </div>

            <div style={{ marginTop: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 14 }}>
                <h3 style={{ fontSize: 24, margin: 0 }}>
                  {completed ? `${(selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent))} live output` : running ? "Execution running" : "Ready for execution"}
                </h3>
                <span style={{ color: "#a8b3cf" }}>{completed ? "Ready for review" : running ? "Generating" : "Waiting"}</span>
              </div>
              <p style={{ color: "#cbd5e1", fontSize: 18, lineHeight: 1.45 }}>
                {completed && outputText
                  ? outputText.slice(0, 260) + (outputText.length > 260 ? "..." : "")
                  : running
                    ? "Live governed execution is running. The generated output will appear here as soon as the provider response completes."
                    : "No live admin output has been generated in this viewer yet."}
              </p>

              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, margin: "14px 0 18px" }}>
                {["Autonomous output", (selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent)), normalizedResult?.performed ? "Autonomous route verified" : (liveCall ? "Autonomous route verified" : "Route pending"), "Admin-ready"].map((tag) => (
                  <span key={tag} style={{ border: "1px solid rgba(148,163,184,.34)", borderRadius: 999, padding: "9px 13px", fontWeight: 900, color: "#e0e7ff" }}>{tag}</span>
                ))}
              </div>

              <pre style={{ whiteSpace: "pre-wrap", maxHeight: 430, overflow: "auto", background: "#020617", border: "1px solid rgba(148,163,184,.2)", borderRadius: 22, padding: 20, color: "#e2e8f0", lineHeight: 1.6, fontSize: 14 }}>
                {running ? "Generating live governed output..." : outputText || "Run an agent from the left panel. The real live execution output will appear here."}
              </pre>

              <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
                <button onClick={() => navigator.clipboard?.writeText(outputText || "")} style={{ padding: "10px 14px", borderRadius: 14, border: "1px solid rgba(148,163,184,.3)", background: "#020617", color: "#bfdbfe", fontWeight: 900 }}>Copy deliverable</button>
                <button onClick={exportResult} style={{ padding: "10px 14px", borderRadius: 14, border: "1px solid rgba(148,163,184,.3)", background: "#020617", color: "#bfdbfe", fontWeight: 900 }}>Export technical details</button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginTop: 16 }}>
                {[
                  ["Provider", result ? autonomousProviderLabel(result) : running ? "Running" : "—"],
                  ["Latency", result ? autonomousLatencyLabel(result) : running ? "Measuring" : "—"],
                  ["Memory", result?.completed_results?.length || result?.queued_results?.length || result?.blocked_results?.length ? "Saved" : running ? "Pending" : "—"],
                  ["Safe", result ? autonomousSafeLabel(result) : running ? "Pending" : "—"],
                ].map(([label, value]) => (
                  <div key={label} style={{ border: "1px solid rgba(148,163,184,.22)", borderRadius: 16, padding: 12 }}>
                    <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 950, textTransform: "uppercase" }}>{label}</div>
                    <div style={{ marginTop: 6, fontWeight: 950 }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <aside style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.35)", borderRadius: 28, padding: 22, maxHeight: 880, overflow: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 24 }}>Live history</h2>
                <p style={{ color: "#a8b3cf", marginTop: 6 }}>Recent operator runs</p>
              </div>
              <button onClick={clearHistory} style={{ padding: "8px 10px", borderRadius: 12, border: "1px solid rgba(148,163,184,.3)", background: "#020617", color: "#fca5a5", fontWeight: 900 }}>Clear</button>
            </div>

            <div style={{ display: "grid", gap: 12, marginTop: 16 }}>
              {history.length === 0 ? (
                <div style={{ border: "1px dashed rgba(148,163,184,.28)", borderRadius: 18, padding: 18, color: "#a8b3cf" }}>
                  No executions saved yet. Run an agent to populate live history.
                </div>
              ) : history.map((item) => (
                <button key={item.id} onClick={() => openHistory(item)} style={{ textAlign: "left", border: selectedHistoryId === item.id ? "1px solid #38bdf8" : "1px solid rgba(148,163,184,.22)", borderRadius: 18, padding: 14, background: "#020617", color: "#f8fafc", cursor: "pointer" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                    <strong>{item.agentName}</strong>
                    <span style={{ color: item.success ? "#86efac" : "#fca5a5", fontWeight: 900 }}>{item.success ? "Done" : "Review"}</span>
                  </div>
                  <div style={{ color: "#a8b3cf", fontSize: 12, marginTop: 5 }}>{item.createdAt}</div>
                  <div style={{ color: "#cbd5e1", fontSize: 13, marginTop: 8, lineHeight: 1.35 }}>
                    {(item.output || item.task || "").slice(0, 150)}{(item.output || item.task || "").length > 150 ? "..." : ""}
                  </div>
                  <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
                    <span style={{ border: "1px solid rgba(148,163,184,.25)", borderRadius: 999, padding: "5px 8px", color: "#bfdbfe", fontSize: 12 }}>{item.provider}</span>
                    <span style={{ border: "1px solid rgba(148,163,184,.25)", borderRadius: 999, padding: "5px 8px", color: "#bfdbfe", fontSize: 12 }}>{item.latency}</span>
                  </div>
                </button>
              ))}
            </div>
          </aside>
        </div>
      </section>
      {selectedPreviewCard ? (
        <div
          onClick={() => setSelectedPreviewCard(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(2,6,23,.78)",
            backdropFilter: "blur(14px)",
            display: "grid",
            placeItems: "center",
            padding: 24,
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(860px, 94vw)",
              maxHeight: "82vh",
              overflow: "auto",
              border: "1px solid rgba(34,211,238,.35)",
              background: "linear-gradient(135deg, rgba(15,23,42,.98), rgba(8,47,73,.96))",
              borderRadius: 28,
              padding: 28,
              boxShadow: "0 40px 120px rgba(0,0,0,.45)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: 16, marginBottom: 18 }}>
              <div>
                <div style={{ color: "#67e8f9", fontWeight: 950, fontSize: 13, letterSpacing: ".08em", textTransform: "uppercase" }}>
                  Media Preview Detail
                </div>
                <h2 style={{ margin: "8px 0 0", color: "#fff", fontSize: 30 }}>
                  {selectedPreviewCard.title}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setSelectedPreviewCard(null)}
                style={{
                  border: "1px solid rgba(148,163,184,.35)",
                  background: "rgba(15,23,42,.9)",
                  color: "#fff",
                  borderRadius: 999,
                  padding: "10px 14px",
                  cursor: "pointer",
                  fontWeight: 900,
                }}
              >
                Close
              </button>
            </div>

            <div style={{ color: "#dbeafe", lineHeight: 1.55, fontSize: 17, marginBottom: 18 }}>
              {selectedPreviewCard.detail}
            </div>

            <div style={{
              border: "1px solid rgba(125,211,252,.22)",
              background: "rgba(2,6,23,.58)",
              borderRadius: 22,
              padding: 18,
              color: "#e2e8f0",
              whiteSpace: "pre-wrap",
              lineHeight: 1.6,
              fontSize: 14,
            }}>
              {outputText || "No output text available yet."}
            </div>
          </div>
        </div>
      ) : null}

    </main>
  );
}
