from pathlib import Path
import re

p = Path("frontend/src/app/admin/live-execution/page.tsx")
text = p.read_text(encoding="utf-8")

new_fn = r'''function extractAutonomousDeliverable(result: any): string {
  const data = result?.data || result || {};
  const completed = Array.isArray(data?.completed_results) ? data.completed_results : [];
  const queued = Array.isArray(data?.queued_results) ? data.queued_results : [];
  const blocked = Array.isArray(data?.blocked_results) ? data.blocked_results : [];
  const first = completed[0] || queued[0] || blocked[0] || {};

  const isGenericReceipt = (value: any) => {
    const text = String(value || "").trim().toLowerCase();
    return !text ||
      text === "created operational execution task." ||
      text === "operational task created" ||
      text === "autonomous execution processed." ||
      text.startsWith("created operational execution task.");
  };

  const pickText = (...values: any[]) => {
    for (const value of values) {
      if (typeof value === "string" && !isGenericReceipt(value)) return value.trim();
      if (value && typeof value === "object") {
        for (const key of ["body", "content", "summary", "text", "output", "generated_output", "completed_output"]) {
          const nested = value?.[key];
          if (typeof nested === "string" && !isGenericReceipt(nested)) return nested.trim();
        }
      }
    }
    return "";
  };

  const output = pickText(
    first?.deliverable?.content?.body,
    first?.deliverable?.body,
    first?.deliverable?.content,
    first?.deliverable?.summary,
    first?.generated_output,
    first?.output,
    data?.generated_output,
    data?.output,
    result?.generated_output,
    result?.output,
    first?.completed_output
  );

  const performed = first?.performed_actual_action === true || first?.delegate_execution === "executed";
  const status = first?.execution_status || first?.autonomous_route || data?.profile || "autonomous_execution_processed";

  const evidence = [];
  evidence.push(`Execution status: ${status}`);
  evidence.push(`Performed actual action: ${performed ? "Yes" : "No"}`);

  if (first?.external_action_record_count !== undefined) {
    evidence.push(`External action records: ${first.external_action_record_count}`);
  }

  if (first?.history_persisted !== undefined) {
    evidence.push(`Execution history saved: ${first.history_persisted ? "Yes" : "No"}`);
  }

  if (Array.isArray(data?.connected_integrations)) {
    evidence.push(`Connected integrations: ${data.connected_integrations.length ? data.connected_integrations.join(", ") : "None"}`);
  }

  return `${output || "Autonomous execution processed. Review evidence below."}

Completion Evidence:
${evidence.map((line) => `- ${line}`).join("\n")}`;
}'''

text = re.sub(
    r"function extractAutonomousDeliverable\(result: any\): string \{[\s\S]*?\n\}\n\nfunction getAutonomousFirstResult",
    new_fn + "\n\nfunction getAutonomousFirstResult",
    text,
    count=1,
)

p.write_text(text, encoding="utf-8")
print("ADMIN_LIVE_EXECUTION_DELIVERABLE_PRIORITY_FIXED")