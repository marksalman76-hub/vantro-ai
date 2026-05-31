from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
page_dir = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution"
api_dir = ROOT / "frontend" / "src" / "app" / "api" / "admin-live-execution"
page_file = page_dir / "page.tsx"
api_file = api_dir / "route.ts"

backup_dir = ROOT / "backups" / f"admin_live_execution_output_viewer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for f in [page_file, api_file]:
    if f.exists():
        shutil.copy2(f, backup_dir / f.name)

page_dir.mkdir(parents=True, exist_ok=True)
api_dir.mkdir(parents=True, exist_ok=True)

api_file.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function POST(req: NextRequest) {
  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const body = await req.json();

  const payload = {
    tenant_id: "owner_admin",
    requested_agent: body.requested_agent || "marketing_specialist_agent",
    workflow_stage: "admin_live_execution_output_viewer",
    task:
      body.task ||
      "Produce a commercial-quality governed live execution result.",
    action_type: "governed_live_provider_generation",
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
    owner_approved: true,
    execute_real_world_action: true,
    project_id: "admin_live_execution_output_viewer",
    actor_role: "owner_admin",
    requested_credits: 1,
  };

  const response = await fetch(`${BACKEND_URL}/run-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "admin-live-execution-output-viewer",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://trance-formation.com.au",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  const data = await response.json();

  return NextResponse.json({
    success: response.ok,
    backend_status: response.status,
    data,
  });
}
'''.lstrip(), encoding="utf-8")

page_file.write_text(r'''
"use client";

import { useState } from "react";

const AGENTS = [
  "head_agent",
  "strategist_agent",
  "marketing_specialist_agent",
  "social_media_manager_content_creator_agent",
  "seo_agent",
  "email_reply_agent",
  "crm_ai_agent",
  "sales_closer_agent",
  "customer_support_agent",
  "ecommerce_agent",
  "product_research_agent",
  "competitor_intelligence_agent",
  "brand_strategy_agent",
  "store_builder_agent",
  "website_landing_apps_agent",
  "product_development_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "paid_ads_agent",
  "analytics_optimisation_agent",
  "influencer_collaboration_agent",
  "orchestration_agent",
  "security_compliance_agent",
  "integration_automation_agent",
];

function text(value: unknown) {
  if (value === null || value === undefined) return "—";
  return String(value);
}

export default function AdminLiveExecutionPage() {
  const [agent, setAgent] = useState("marketing_specialist_agent");
  const [task, setTask] = useState("Create a premium ecommerce execution plan with clear actions, risks, owner review points, and measurable next steps.");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function runLiveExecution() {
    setBusy(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/admin-live-execution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requested_agent: agent, task }),
      });

      const data = await response.json();

      if (!response.ok || !data?.data?.success) {
        setError(data?.data?.message || data?.data?.error || data?.error || "Live execution failed.");
      }

      setResult(data?.data || data);
    } catch {
      setError("Admin live execution request failed before reaching the backend.");
    } finally {
      setBusy(false);
    }
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

  return (
    <main style={{ minHeight: "100vh", background: "#020617", color: "#f8fafc", padding: 32 }}>
      <section style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", marginBottom: 24 }}>
          <div>
            <p style={{ color: "#38bdf8", fontSize: 12, fontWeight: 900, letterSpacing: "0.16em", textTransform: "uppercase" }}>
              Admin Command Centre
            </p>
            <h1 style={{ fontSize: 36, margin: "8px 0", fontWeight: 950 }}>Live Execution Output Viewer</h1>
            <p style={{ color: "#94a3b8", maxWidth: 760 }}>
              Run real governed AI agent executions and inspect provider output, persistence, latency, safety, and governance state.
            </p>
          </div>
          <a href="/admin" style={{ color: "#bfdbfe", textDecoration: "none", fontWeight: 800 }}>← Back to admin</a>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 18 }}>
          <section style={{ background: "rgba(15,23,42,.92)", border: "1px solid rgba(148,163,184,.22)", borderRadius: 24, padding: 20 }}>
            <label style={{ fontSize: 12, fontWeight: 900, color: "#94a3b8" }}>Agent</label>
            <select value={agent} onChange={(e) => setAgent(e.target.value)} style={{ width: "100%", marginTop: 8, padding: 12, borderRadius: 14, background: "#020617", color: "#fff", border: "1px solid rgba(148,163,184,.35)" }}>
              {AGENTS.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>

            <label style={{ display: "block", marginTop: 18, fontSize: 12, fontWeight: 900, color: "#94a3b8" }}>Execution task</label>
            <textarea value={task} onChange={(e) => setTask(e.target.value)} rows={10} style={{ width: "100%", marginTop: 8, padding: 12, borderRadius: 14, background: "#020617", color: "#fff", border: "1px solid rgba(148,163,184,.35)", resize: "vertical" }} />

            <button onClick={runLiveExecution} disabled={busy} style={{ width: "100%", marginTop: 18, padding: "14px 16px", borderRadius: 16, border: 0, background: busy ? "#475569" : "linear-gradient(135deg,#2563eb,#06b6d4)", color: "#fff", fontWeight: 950, cursor: busy ? "not-allowed" : "pointer" }}>
              {busy ? "Running governed execution..." : "Run live execution"}
            </button>

            {error ? <p style={{ marginTop: 14, color: "#fca5a5", fontWeight: 800 }}>{error}</p> : null}
          </section>

          <section style={{ display: "grid", gap: 18 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
              {[
                ["Status", execution?.execution_status || result?.status],
                ["Provider", adapter?.provider_key],
                ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : "—"],
                ["Live call", adapter?.live_external_call_executed === true ? "TRUE" : "FALSE"],
                ["Customer safe", adapter?.customer_safe === true ? "TRUE" : "—"],
                ["Credentials exposed", adapter?.credential_values_exposed === false ? "FALSE" : "—"],
                ["Memory", result?.memory?.memory_saved === true ? "Saved" : "—"],
                ["SQLite", result?.sqlite?.sqlite_saved === true ? "Saved" : "—"],
              ].map(([label, value]) => (
                <div key={label} style={{ background: "rgba(15,23,42,.92)", border: "1px solid rgba(148,163,184,.22)", borderRadius: 18, padding: 14 }}>
                  <p style={{ margin: 0, color: "#94a3b8", fontSize: 11, fontWeight: 900, textTransform: "uppercase" }}>{label}</p>
                  <p style={{ margin: "8px 0 0", fontWeight: 950, color: value === "FALSE" || value === "TRUE" || value === "Saved" ? "#86efac" : "#f8fafc" }}>{text(value)}</p>
                </div>
              ))}
            </div>

            <div style={{ background: "rgba(15,23,42,.92)", border: "1px solid rgba(148,163,184,.22)", borderRadius: 24, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <h2 style={{ margin: 0, fontSize: 20 }}>Execution Output</h2>
                <button onClick={() => navigator.clipboard?.writeText(outputText || JSON.stringify(result, null, 2))} style={{ padding: "9px 12px", borderRadius: 12, border: "1px solid rgba(148,163,184,.3)", background: "#020617", color: "#bfdbfe", fontWeight: 800 }}>
                  Copy
                </button>
              </div>
              <pre style={{ whiteSpace: "pre-wrap", marginTop: 16, maxHeight: 520, overflow: "auto", background: "#020617", border: "1px solid rgba(148,163,184,.16)", borderRadius: 18, padding: 18, color: "#e2e8f0", lineHeight: 1.55 }}>
                {outputText || "Run a live execution to view output here."}
              </pre>
            </div>

            <details style={{ background: "rgba(15,23,42,.92)", border: "1px solid rgba(148,163,184,.22)", borderRadius: 24, padding: 20 }}>
              <summary style={{ cursor: "pointer", fontWeight: 950 }}>Runtime metadata</summary>
              <pre style={{ whiteSpace: "pre-wrap", marginTop: 16, maxHeight: 420, overflow: "auto", background: "#020617", borderRadius: 18, padding: 18, color: "#cbd5e1" }}>
                {JSON.stringify({
                  execution,
                  adapter_result: adapter,
                  persistence: {
                    execution: audit?.execution_bridge?.persistence_mode,
                    event: audit?.event_bridge?.persistence_mode,
                    latency: audit?.latency_bridge?.persistence_mode,
                  },
                }, null, 2)}
              </pre>
            </details>
          </section>
        </div>
      </section>
    </main>
  );
}
'''.lstrip(), encoding="utf-8")

print("ADMIN_LIVE_EXECUTION_OUTPUT_VIEWER_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {page_file}")
print(f"Created/updated: {api_file}")