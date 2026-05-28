from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
page_file = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

backup_dir = ROOT / "backups" / f"admin_live_execution_client_style_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(page_file, backup_dir / "page.tsx")

page_file.write_text(r'''
"use client";

import { useState } from "react";

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
];

export default function AdminLiveExecutionPage() {
  const [agent, setAgent] = useState("marketing_specialist_agent");
  const [task, setTask] = useState("Create a premium ecommerce launch campaign deliverable for a luxury skincare brand targeting women aged 30–50 in Australia.");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [toast, setToast] = useState("");

  const execution = result?.execution || {};
  const adapter = execution?.adapter_result || {};
  const normalised = adapter?.normalised_response || {};
  const safeOutput = normalised?.safe_output || {};
  const outputText =
    safeOutput?.text ||
    result?.output?.generated_output ||
    result?.output?.output ||
    result?.output?.content ||
    "";

  async function runLiveExecution() {
    setRunning(true);
    setToast("Execution started. Generating live admin deliverable...");
    setResult(null);

    try {
      const response = await fetch("/api/admin-live-execution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requested_agent: agent, task }),
      });
      const data = await response.json();
      setResult(data?.data || data);
      setToast(data?.data?.success ? "Live deliverable generated and ready for review." : "Execution completed with a warning.");
    } catch {
      setToast("Execution failed before reaching the backend.");
    } finally {
      setRunning(false);
    }
  }

  const completed = result?.success === true;
  const liveCall = adapter?.live_external_call_executed === true;

  return (
    <main style={{ minHeight: "100vh", background: "#061226", color: "#f8fafc", padding: 36 }}>
      <section style={{ maxWidth: 1500, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 26 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>06</span>
              <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em" }}>Execution Output Viewer</span>
            </div>
            <h1 style={{ fontSize: 38, margin: "14px 0 4px", fontWeight: 950 }}>Admin deliverables</h1>
            <p style={{ color: "#a8b3cf", fontSize: 17 }}>Run live agents and review generated outputs in the same client-style viewer.</p>
          </div>
          <a href="/admin" style={{ color: "#bfdbfe", textDecoration: "none", fontWeight: 900 }}>← Back to admin</a>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22 }}>
          <section style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.35)", borderRadius: 28, padding: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>05</span>
                  <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em" }}>Activity</span>
                </div>
                <h2 style={{ fontSize: 30, margin: "16px 0 4px", fontWeight: 950 }}>Activity</h2>
                <p style={{ color: "#a8b3cf", fontWeight: 800 }}>Latest governed activity</p>
              </div>
              <span style={{ background: "#dcfce7", color: "#047857", padding: "12px 18px", borderRadius: 999, fontWeight: 950 }}>Live tracking</span>
            </div>

            <div style={{ display: "grid", gap: 14 }}>
              {[
                ["✓", completed ? "Deliverable generated" : "Ready for execution", completed ? "Latest admin deliverable is ready for review." : "Run selected agent to generate a live deliverable.", completed ? "Ready" : "Waiting"],
                ["⚡", running ? "Execution running" : completed ? "Execution completed" : "Execution prepared", running ? "Governed execution is currently running." : completed ? "Governed execution completed successfully." : "Governed execution is prepared.", running ? "Running" : completed ? "Complete" : "Prepared"],
                ["○", liveCall ? "Live provider confirmed" : "Provider pending", liveCall ? "OpenAI live provider call completed." : "Provider result will appear after execution.", liveCall ? "Verified" : "Pending"],
              ].map(([icon, title, detail, status]) => (
                <div key={title} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, border: "1px solid rgba(99,102,241,.28)", borderRadius: 22, padding: 18, background: "rgba(15,23,42,.58)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    <span style={{ width: 44, height: 44, borderRadius: 16, background: "#082f49", display: "grid", placeItems: "center", color: "#22c55e", fontSize: 22 }}>{icon}</span>
                    <div>
                      <div style={{ fontWeight: 950, fontSize: 17 }}>{title}</div>
                      <div style={{ color: "#a8b3cf", marginTop: 3, fontWeight: 700 }}>{detail}</div>
                    </div>
                  </div>
                  <span style={{ border: "1px solid rgba(99,102,241,.36)", borderRadius: 999, padding: "9px 14px", color: "#67e8f9", fontWeight: 950 }}>{status}</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 24, border: "1px solid rgba(99,102,241,.28)", borderRadius: 22, padding: 20 }}>
              <div style={{ fontWeight: 950, marginBottom: 10 }}>Execution snapshot</div>
              {[
                ["Generated", completed ? 100 : running ? 65 : 20],
                ["Reviewed", completed ? 55 : 15],
                ["Approved", completed ? 25 : 0],
                ["Pending", completed ? 65 : 35],
              ].map(([label, value]: any) => (
                <div key={label} style={{ display: "grid", gridTemplateColumns: "110px 1fr 50px", gap: 14, alignItems: "center", marginTop: 12 }}>
                  <span style={{ fontWeight: 900 }}>{label}</span>
                  <div style={{ height: 10, borderRadius: 999, background: "#e2e8f0", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${value}%`, background: label === "Generated" ? "#22c55e" : label === "Reviewed" ? "#6366f1" : label === "Approved" ? "#14b8a6" : "#f59e0b" }} />
                  </div>
                  <span style={{ color: "#a8b3cf", fontWeight: 950 }}>{value}%</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 24 }}>
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

          <section style={{ background: "#0b1730", border: "1px solid rgba(99,102,241,.35)", borderRadius: 28, padding: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 999, background: "#e0e7ff", color: "#6366f1", display: "grid", placeItems: "center", fontWeight: 950 }}>06</span>
                  <span style={{ fontSize: 13, fontWeight: 950, color: "#bfdbfe", textTransform: "uppercase", letterSpacing: ".08em", background: "#1d4ed8" }}>Execution Output Viewer</span>
                </div>
                <h2 style={{ fontSize: 30, margin: "16px 0 4px", fontWeight: 950 }}>Admin deliverables</h2>
              </div>
              <span style={{ background: completed ? "#dcfce7" : "#fef3c7", color: completed ? "#047857" : "#92400e", padding: "12px 18px", borderRadius: 999, fontWeight: 950 }}>
                {completed ? "Completed" : "Waiting"}
              </span>
            </div>

            <div style={{ border: "1px solid rgba(99,102,241,.34)", borderRadius: 22, padding: 22 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 44, height: 44, borderRadius: 16, background: "#312e81", display: "grid", placeItems: "center", fontSize: 22 }}>✦</span>
                  <div>
                    <div style={{ fontWeight: 950 }}>Media preview</div>
                    <div style={{ color: "#a8b3cf" }}>Waiting for real generated or uploaded assets</div>
                  </div>
                </div>
                <span style={{ color: "#cbd5e1", fontWeight: 900 }}>Pending media</span>
              </div>

              <div style={{ border: "1px dashed rgba(148,163,184,.3)", borderRadius: 20, minHeight: 170, display: "grid", placeItems: "center", textAlign: "center", color: "#a8b3cf" }}>
                <div>
                  <div style={{ fontSize: 34 }}>🖼️</div>
                  <div style={{ color: "#fff", fontWeight: 950, marginTop: 10 }}>No asset generated yet</div>
                  <p>Generated assets, uploaded brand files, previews, and deliverable media will appear here automatically.</p>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 18, color: "#a8b3cf" }}>
                <span>Secure asset workspace</span>
                <span>Enterprise media pipeline</span>
              </div>
            </div>

            <div style={{ marginTop: 22 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 14 }}>
                <h3 style={{ fontSize: 24, margin: 0 }}>{completed ? "Live admin execution deliverable" : "Ready for execution"}</h3>
                <span style={{ color: "#a8b3cf" }}>{completed ? "Ready for review" : "Waiting"}</span>
              </div>
              <p style={{ color: "#cbd5e1", fontSize: 20, lineHeight: 1.45 }}>
                {completed
                  ? "A live governed admin deliverable has been generated from the selected AI agent."
                  : "Run an agent to generate a live governed admin deliverable."}
              </p>

              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, margin: "14px 0 18px" }}>
                {[
                  "Live output",
                  AGENTS.find(([id]) => id === agent)?.[1] || agent,
                  liveCall ? "OpenAI verified" : "Provider pending",
                  "Admin-ready",
                ].map((tag) => (
                  <span key={tag} style={{ border: "1px solid rgba(148,163,184,.34)", borderRadius: 999, padding: "9px 13px", fontWeight: 900, color: "#e0e7ff" }}>{tag}</span>
                ))}
              </div>

              <pre style={{ whiteSpace: "pre-wrap", maxHeight: 460, overflow: "auto", background: "#020617", border: "1px solid rgba(148,163,184,.2)", borderRadius: 22, padding: 20, color: "#e2e8f0", lineHeight: 1.6, fontSize: 14 }}>
                {outputText || "Generated deliverable output will appear here after execution."}
              </pre>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginTop: 16 }}>
                {[
                  ["Provider", adapter?.provider_key || "—"],
                  ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : "—"],
                  ["Memory", result?.memory?.memory_saved ? "Saved" : "—"],
                  ["Safe", adapter?.customer_safe ? "True" : "—"],
                ].map(([label, value]) => (
                  <div key={label} style={{ border: "1px solid rgba(148,163,184,.22)", borderRadius: 16, padding: 12 }}>
                    <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 950, textTransform: "uppercase" }}>{label}</div>
                    <div style={{ marginTop: 6, fontWeight: 950 }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
'''.lstrip(), encoding="utf-8")

print("ADMIN_LIVE_EXECUTION_REPLACED_WITH_CLIENT_STYLE_VIEWER")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {page_file}")