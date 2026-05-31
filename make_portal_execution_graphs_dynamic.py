from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
CLIENT = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups" / f"portal_execution_graphs_dynamic_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [ADMIN, CLIENT]:
    shutil.copy2(path, BACKUP_DIR / path.name)

admin = ADMIN.read_text(encoding="utf-8")
client = CLIENT.read_text(encoding="utf-8")

admin_helper = r'''
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
'''

if "function dynamicExecutionMetrics" not in admin:
    admin = admin.replace("export default function AdminLiveExecutionPage()", admin_helper + "\nexport default function AdminLiveExecutionPage()")

admin = re.sub(
    r'''const executionSteps = \[[\s\S]*?\];''',
    '''const executionMetrics = dynamicExecutionMetrics(result, running, outputText, liveCall);''',
    admin,
    count=1,
)

admin = re.sub(
    r'''\{executionSteps\.map\(\(\[label, state\]: any\) => \([\s\S]*?\)\)\}''',
    r'''{executionMetrics.map(([label, value]: any) => (
                <div key={label} style={{ marginTop: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", color: "#cbd5e1", fontWeight: 900 }}>
                    <span>{label}</span>
                    <span>{value}%</span>
                  </div>
                  <div style={{ height: 10, background: "rgba(226,232,240,.16)", borderRadius: 99, overflow: "hidden", marginTop: 7 }}>
                    <div style={{ height: "100%", width: `${value}%`, background: value >= 80 ? "#22c55e" : value >= 50 ? "#38bdf8" : value > 0 ? "#f59e0b" : "#334155", transition: "width .35s ease" }} />
                  </div>
                </div>
              ))}''',
    admin,
    count=1,
)

if "executionSteps" in admin:
    raise SystemExit("Admin patch incomplete: executionSteps still present.")

CLIENT.write_text(client, encoding="utf-8")  # placeholder no-op before client patch

client_helper = r'''
function clampExecutionMetric(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, Math.round(value)));
}

function clientDynamicExecutionMetrics(params: {
  executionState: string;
  liveDeliverable: any;
  latestDeliverable: any;
  reviewStatus: string;
}) {
  const source = params.liveDeliverable || params.latestDeliverable || {};
  const outputText =
    source?.output_text ||
    source?.output ||
    source?.generated_output ||
    source?.deliverable ||
    source?.content ||
    "";

  const qualityScore =
    Number(source?.quality?.quality_score) ||
    Number(source?.quality_score) ||
    Number(source?.execution?.quality?.quality_score) ||
    0;

  const providerLive =
    source?.provider_execution_attempted === true ||
    source?.raw?.provider_execution_attempted === true ||
    source?.external_action_performed === true ||
    source?.performed_actual_action === true;

  const generatedScore = params.executionState === "running" ? 55 : outputText ? 100 : params.executionState === "completed" ? 85 : 0;
  const providerScore = providerLive ? 100 : params.executionState === "running" ? 45 : params.executionState === "completed" ? 70 : 0;
  const qualityDisplay = qualityScore ? qualityScore : source?.quality_gate_passed === true ? 100 : source?.quality_gate_passed === false ? 45 : params.executionState === "running" ? 30 : 0;
  const reviewScore = params.reviewStatus === "approved" ? 100 : params.reviewStatus === "rejected" ? 35 : params.executionState === "completed" ? 75 : params.executionState === "running" ? 25 : 0;
  const deliveryScore = params.executionState === "completed" && outputText ? 100 : outputText ? 80 : params.executionState === "running" ? 35 : 0;

  return [
    ["Generated", clampExecutionMetric(generatedScore)],
    ["Provider", clampExecutionMetric(providerScore)],
    ["Quality", clampExecutionMetric(qualityDisplay)],
    ["Review", clampExecutionMetric(reviewScore)],
    ["Delivery", clampExecutionMetric(deliveryScore)],
  ];
}
'''

if "function clientDynamicExecutionMetrics" not in client:
    insert_after = client.find("export default function")
    if insert_after == -1:
        raise SystemExit("Could not find client export default function.")
    client = client[:insert_after] + client_helper + "\n" + client[insert_after:]

client = re.sub(
    r'''const pipelineRows = \[[\s\S]*?\];''',
    '''const pipelineRows = clientDynamicExecutionMetrics({
    executionState,
    liveDeliverable,
    latestDeliverable,
    reviewStatus,
  });''',
    client,
    count=1,
)

client = re.sub(
    r'''\{pipelineRows\.map\(\(\[title, status, detail\]: any\) => \([\s\S]*?\)\)\}''',
    r'''{pipelineRows.map(([title, value]: any) => (
                      <div key={title} className="rounded-2xl border border-slate-200 bg-white p-3">
                        <div className="flex items-center justify-between gap-3 text-xs font-black text-slate-700">
                          <span>{title}</span>
                          <span>{value}%</span>
                        </div>
                        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={value >= 80 ? "h-full rounded-full bg-emerald-500 transition-all" : value >= 50 ? "h-full rounded-full bg-sky-500 transition-all" : value > 0 ? "h-full rounded-full bg-amber-500 transition-all" : "h-full rounded-full bg-slate-300 transition-all"}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                      </div>
                    ))}''',
    client,
    count=1,
)

ADMIN.write_text(admin, encoding="utf-8")
CLIENT.write_text(client, encoding="utf-8")

print("PORTAL_EXECUTION_GRAPHS_DYNAMIC_PATCHED")
print("Backup:", BACKUP_DIR)
print("Updated admin:", ADMIN)
print("Updated client:", CLIENT)