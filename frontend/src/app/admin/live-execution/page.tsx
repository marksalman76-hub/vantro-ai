"use client";

import { useEffect, useMemo, useState } from "react";

const AGENTS = [
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
  ["ecommerce_agent", "Ecommerce Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
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
  const qualityDisplay = qualityScore ? qualityScore : result?.quality_gate_passed === true ? 100 : result?.quality_gate_passed === false ? 45 : running ? 30 : 0;
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

export default function AdminLiveExecutionPage() {
  const [agent, setAgent] = useState("marketing_specialist_agent");
  const [task, setTask] = useState("Create a premium ecommerce launch campaign deliverable for a luxury skincare brand targeting women aged 30–50 in Australia.");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
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
  const outputText =
    safeOutput?.text ||
    result?.output?.generated_output ||
    result?.output?.output ||
    result?.output?.content ||
    "";

  const completed = result?.success === true;
  const failed = result && result?.success !== true;
  const liveCall = adapter?.live_external_call_executed === true;

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

  async function runLiveExecution() {
    setRunning(true);
    setToast("Execution started. Generating live admin deliverable...");
    setResult(null);
    setSelectedHistoryId("");

    try {
      const response = await fetch("/api/admin-live-execution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requested_agent: agent, task: buildPortalDeliverableTask(task) }),
      });

      const data = await response.json();
      const liveResult = data?.data || data;
      setResult(liveResult);

      const liveExecution = liveResult?.execution || {};
      const liveAdapter = liveExecution?.adapter_result || {};
      const liveNormalised = liveAdapter?.normalised_response || {};
      const liveSafeOutput = liveNormalised?.safe_output || {};
      const liveOutput =
        liveSafeOutput?.text ||
        liveResult?.output?.generated_output ||
        liveResult?.output?.output ||
        liveResult?.output?.content ||
        "";

      const item: HistoryItem = {
        id: `${Date.now()}-${agent}`,
        agent,
        agentName: agentName(agent),
        task,
        createdAt: new Date().toLocaleString(),
        success: liveResult?.success === true,
        provider: safeString(liveAdapter?.provider_key),
        latency: liveAdapter?.latency_ms ? `${liveAdapter.latency_ms}ms` : "—",
        output: liveOutput,
        raw: liveResult,
      };

      persistHistory([item, ...history].slice(0, 25));
      setSelectedHistoryId(item.id);
      setToast(liveResult?.success ? "Live deliverable generated and saved to execution history." : "Execution completed with a warning.");
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
    adapter?.asset_url,
    adapter?.image_url,
    adapter?.video_url,
    result?.asset_url,
    result?.image_url,
    result?.video_url,
    result?.media_url,
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
              <select value={agent} onChange={(e) => setAgent(e.target.value)} style={{ width: "100%", padding: 14, borderRadius: 16, background: "#020617", color: "#fff", border: "1px solid rgba(148,163,184,.35)", marginBottom: 12 }}>
                {AGENTS.map(([id, name]) => <option key={id} value={id}>{name}</option>)}
              </select>
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
                      <a key={asset} href={asset} target="_blank" rel="noreferrer" style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginBottom: 8, wordBreak: "break-all" }}>
                        Open generated asset
                      </a>
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
                  {completed ? `${agentName(agent)} live output` : running ? "Execution running" : "Ready for execution"}
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
                {["Live output", agentName(agent), liveCall ? "OpenAI verified" : "Provider pending", "Admin-ready"].map((tag) => (
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
                  ["Provider", adapter?.provider_key || (running ? "Running" : "—")],
                  ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : running ? "Measuring" : "—"],
                  ["Memory", result?.memory?.memory_saved ? "Saved" : running ? "Pending" : "—"],
                  ["Safe", adapter?.customer_safe ? "True" : running ? "Pending" : "—"],
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
    </main>
  );
}
