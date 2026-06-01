from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
CLIENT = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

BACKUP = ROOT / "backups" / f"global_execution_normalizer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

for p in [ADMIN, CLIENT]:
    shutil.copy2(p, BACKUP / p.name.replace(".tsx", f"_{p.parent.name}.tsx"))

normalizer = r'''
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
'''

def install_normalizer(path: Path):
    s = path.read_text(encoding="utf-8")

    if "function normalizeExecutionPacket" not in s:
        anchor = "function safeString"
        idx = s.find(anchor)
        if idx != -1:
            s = s[:idx] + normalizer + "\n\n" + s[idx:]
        else:
            s = normalizer + "\n\n" + s

    # Admin live execution common replacement hooks
    s = s.replace(
        "const liveResult = data?.data || data;",
        "const liveResult = data?.data || data;\n      const normalizedExecution = normalizeExecutionPacket(liveResult);"
    )

    s = s.replace(
        "provider: safeString(liveAdapter?.provider_key),",
        'provider: normalizedExecution.provider || safeString(liveAdapter?.provider_key),'
    )

    s = s.replace(
        'latency: liveAdapter?.latency_ms ? `${liveAdapter.latency_ms}ms` : "—",',
        'latency: normalizedExecution.latency ? `${normalizedExecution.latency}ms` : (liveAdapter?.latency_ms ? `${liveAdapter.latency_ms}ms` : "—"),'
    )

    s = s.replace(
        "output: liveOutput,",
        "output: normalizedExecution.output || liveOutput,"
    )

    s = s.replace(
        "success: liveResult?.success === true,",
        "success: liveResult?.success === true || normalizedExecution.performed,"
    )

    s = s.replace(
        'liveCall ? "Autonomous route verified" : "Route pending"',
        'normalizedExecution?.performed ? "Autonomous route verified" : (liveCall ? "Autonomous route verified" : "Route pending")'
    )

    s = s.replace(
        'completed ? "Completed" : running ? "Running" : "Waiting"',
        'normalizedExecution?.performed ? "Completed" : (completed ? "Completed" : running ? "Running" : "Waiting")'
    )

    s = s.replace(
        'completed ? "Completed" : "Needs review"',
        'normalizedExecution?.performed ? "Completed" : (completed ? "Completed" : "Needs review")'
    )

    path.write_text(s, encoding="utf-8")


install_normalizer(ADMIN)
install_normalizer(CLIENT)

print("GLOBAL_EXECUTION_NORMALIZER_INSTALLED")
print("Backup:", BACKUP)
print("Updated admin:", ADMIN)
print("Updated client:", CLIENT)