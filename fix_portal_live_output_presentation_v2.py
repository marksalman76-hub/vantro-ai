from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
BACKUP_DIR = ROOT / "backups" / f"portal_live_output_presentation_v2_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / "page.tsx")

text = TARGET.read_text(encoding="utf-8")

helper = r'''
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
'''

if "function extractSellableDeliverable" not in text:
    text = text.replace("export default function AdminLiveExecutionPage()", helper + "\nexport default function AdminLiveExecutionPage()")

text = re.sub(
    r"const outputText =[\s\S]*?result\?\.generated_output \|\|\s*\"\";",
    "const outputText = extractSellableDeliverable(result);",
    text,
    count=1,
)

text = re.sub(
    r"const progress = \{[\s\S]*?\};",
    '''const executionSteps = [
    ["Generation", completed ? "Complete" : running ? "Running" : failed ? "Needs review" : "Waiting"],
    ["Provider", liveCall ? "Live provider confirmed" : running ? "Awaiting provider" : completed ? "Completed" : "Pending"],
    ["Quality", result?.quality_gate_passed === true ? "Passed" : result?.quality_gate_passed === false ? "Review required" : running ? "Checking" : "Pending"],
    ["Final output", completed && outputText ? "Deliverable ready" : running ? "Generating" : failed ? "Needs review" : "Waiting"],
  ];''',
    text,
    count=1,
)

text = text.replace(
    "body: JSON.stringify({ requested_agent: agent, task }),",
    "body: JSON.stringify({ requested_agent: agent, task: buildPortalDeliverableTask(task) }),",
)

text = re.sub(
    r"const liveOutput =[\s\S]*?liveResult\?\.generated_output \|\|\s*\"\";",
    "const liveOutput = extractSellableDeliverable(liveResult);",
    text,
    count=1,
)

text = re.sub(
    r"""\{\[\s*\["Generated", progress\.generated\],[\s\S]*?\]\.map\(\(\[label, value\]: any\) => \([\s\S]*?\)\)\}""",
    r'''{executionSteps.map(([label, state]: any) => (
                <div key={label} style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, border: "1px solid rgba(148,163,184,.22)", borderRadius: 14, padding: "10px 12px", background: "rgba(15,23,42,.55)" }}>
                  <span style={{ color: "#cbd5e1", fontWeight: 900 }}>{label}</span>
                  <span style={{ color: state === "Complete" || state === "Passed" || state === "Deliverable ready" || state === "Live provider confirmed" ? "#34d399" : state === "Needs review" || state === "Review required" ? "#fbbf24" : "#93c5fd", fontWeight: 950 }}>{state}</span>
                </div>
              ))}''',
    text,
    count=1,
)

text = text.replace("Export JSON", "Export technical details")
text = text.replace("Copy output", "Copy deliverable")
text = text.replace("Execution Output Viewer", "Live Deliverable Viewer")

if "progress.generated" in text or "running ? 65" in text or "failed ? 35" in text:
    raise SystemExit("Patch incomplete: hardcoded progress values still found.")

TARGET.write_text(text, encoding="utf-8")

print("PORTAL_LIVE_OUTPUT_PRESENTATION_V2_FIXED")
print("Backup:", BACKUP_DIR)
print("Updated:", TARGET)