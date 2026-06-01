from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
s = p.read_text(encoding="utf-8")

insert = r'''
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
'''

if "function autonomousQualityScore" not in s:
    s = s.replace("function autonomousSafeLabel(result: any): string {", insert + "\nfunction autonomousSafeLabel(result: any): string {")

s = s.replace(
'''  const qualityDisplay = qualityScore ? qualityScore : result?.quality_gate_passed === true ? 100 : result?.quality_gate_passed === false ? 45 : running ? 30 : 0;''',
'''  const qualityDisplay = qualityScore ? qualityScore : autonomousQualityScore(result) || (result?.quality_gate_passed === true ? 100 : result?.quality_gate_passed === false ? 45 : running ? 30 : 0);'''
)

p.write_text(s, encoding="utf-8")
print("ADMIN_AUTONOMOUS_QUALITY_METRIC_FIXED")