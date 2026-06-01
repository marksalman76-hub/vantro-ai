from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
BACKUP = ROOT / "backups" / f"admin_autonomous_renderer_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(ADMIN, BACKUP / "page.tsx")

text = ADMIN.read_text(encoding="utf-8")

helper = r'''
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

function autonomousSafeLabel(result: any): string {
  const data = result?.data || result || {};
  return data?.customer_safe === false ? "False" : "True";
}
'''

if "function getAutonomousFirstResult" not in text:
    text = text.replace("export default function AdminLiveExecutionPage()", helper + "\nexport default function AdminLiveExecutionPage()")

text = text.replace(
'''      const liveExecution = liveResult?.execution || {};
      const liveAdapter = liveExecution?.adapter_result || {};
      const liveOutput = extractAutonomousDeliverable(liveResult);
''',
'''      const liveExecution = liveResult?.execution || {};
      const liveAdapter = liveExecution?.adapter_result || {};
      const liveOutput = extractAutonomousDeliverable(liveResult);
      const autonomousProvider = autonomousProviderLabel(liveResult);
      const autonomousLatency = autonomousLatencyLabel(liveResult);
'''
)

text = text.replace(
'''        provider: safeString(liveAdapter?.provider_key),
        latency: liveAdapter?.latency_ms ? `${liveAdapter.latency_ms}ms` : "—",''',
'''        provider: autonomousProvider,
        latency: autonomousLatency,''',
)

text = re.sub(
    r'''\["Provider", adapter\?\.provider_key \|\| \(running \? "Running" : "ΓÇö"\)\],''',
    '''["Provider", autonomousProviderLabel(result) || (running ? "Running" : "—")],''',
    text,
)

text = re.sub(
    r'''\["Latency", adapter\?\.latency_ms \? `\$\{adapter\.latency_ms\}ms` : running \? "Measuring" : "ΓÇö"\],''',
    '''["Latency", autonomousLatencyLabel(result) || (running ? "Measuring" : "—")],''',
    text,
)

text = re.sub(
    r'''\["Memory", result\?\.memory\?\.memory_saved \? "Saved" : running \? "Pending" : "ΓÇö"\],''',
    '''["Memory", result?.completed_results?.length || result?.queued_results?.length || result?.blocked_results?.length ? "Saved" : running ? "Pending" : "—"],''',
    text,
)

text = re.sub(
    r'''\["Safe", adapter\?\.customer_safe \? "True" : running \? "Pending" : "ΓÇö"\],''',
    '''["Safe", result ? autonomousSafeLabel(result) : running ? "Pending" : "—"],''',
    text,
)

ADMIN.write_text(text, encoding="utf-8")

print("ADMIN_AUTONOMOUS_RENDERER_BRIDGE_FIXED")
print("Backup:", BACKUP)
print("Updated:", ADMIN)