from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
CLIENT = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

BACKUP = ROOT / "backups" / f"wire_portals_to_autonomous_workforce_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

for p in [ADMIN, CLIENT]:
    shutil.copy2(p, BACKUP / p.name)

admin = ADMIN.read_text(encoding="utf-8")
client = CLIENT.read_text(encoding="utf-8")

helper = r'''
function buildAutonomousImplementationPlan(task: string, selectedAgent: string) {
  const cleanTask = String(task || "").trim();

  return {
    plan_id: `portal_plan_${Date.now()}`,
    source: "portal_autonomous_execution",
    action_packets: [
      {
        packet_id: `portal_packet_${Date.now()}`,
        title: cleanTask,
        implementation_action: cleanTask,
        recommended_agent: selectedAgent || "marketing_specialist_agent",
        risk_level: "low",
        approval_required: false,
        execution_mode: "autonomous_governed",
        expected_output: "completed_action_evidence",
      },
    ],
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
'''

if "function buildAutonomousImplementationPlan" not in admin:
    admin = admin.replace("export default function AdminLiveExecutionPage()", helper + "\nexport default function AdminLiveExecutionPage()")

admin = admin.replace(
    'const response = await fetch("/api/admin-live-execution", {',
    'const response = await fetch("/api/delegated-workforce-execution", {'
)

admin = admin.replace(
    'body: JSON.stringify({ requested_agent: agent, task: buildStrictTaskExecutionContract(task, agentName(agent)) }),',
    '''body: JSON.stringify({
          implementation_plan: buildAutonomousImplementationPlan(buildStrictTaskExecutionContract(task, agentName(agent)), agent),
          owner_approved: true,
          client_owned_agents: [agent],
          package_tier: "enterprise",
          connected_integrations: ["email", "crm", "calendar"],
          tenant_id: "owner_admin",
        }),'''
)

admin = re.sub(
    r'''const liveExecution = liveResult\?\.execution \|\| \{\};[\s\S]*?const liveOutput =[\s\S]*?;\n''',
    '''const liveExecution = liveResult?.execution || {};
      const liveAdapter = liveExecution?.adapter_result || {};
      const liveOutput = extractAutonomousDeliverable(liveResult);
''',
    admin,
    count=1,
)

admin = admin.replace(
    'setToast(liveResult?.success ? "Live deliverable generated and saved to execution history." : "Execution completed with a warning.");',
    'setToast(liveResult?.success ? "Autonomous workforce execution completed and saved to history." : "Autonomous execution completed with a warning.");'
)

admin = admin.replace(
    'setToast("Execution started. Generating live admin deliverable...");',
    'setToast("Execution started. Routing through autonomous workforce runtime...");'
)

if "function buildAutonomousImplementationPlan" not in client:
    idx = client.find("export default function")
    if idx == -1:
        raise SystemExit("Could not find client export default function.")
    client = client[:idx] + helper + "\n" + client[idx:]

client = client.replace('/api/run-agent', '/api/delegated-workforce-execution')

client = re.sub(
    r'''body:\s*JSON\.stringify\(\{\s*requested_agent:\s*selectedAgent,\s*task:\s*buildStrictTaskExecutionContract\(taskInput,\s*selectedAgent\),\s*\}\)''',
    '''body: JSON.stringify({
                          implementation_plan: buildAutonomousImplementationPlan(buildStrictTaskExecutionContract(taskInput, selectedAgent), selectedAgent),
                          owner_approved: false,
                          client_owned_agents: [selectedAgent],
                          package_tier: packageTier || "starter",
                          connected_integrations: ["email", "crm", "calendar"],
                          tenant_id: clientSession?.tenant_id || "client_demo_001",
                        })''',
    client,
    count=1,
    flags=re.S,
)

client = client.replace("Client deliverable generated.", "Autonomous workforce execution completed.")
client = client.replace("Execution completed", "Autonomous execution completed")

ADMIN.write_text(admin, encoding="utf-8")
CLIENT.write_text(client, encoding="utf-8")

print("PORTALS_WIRED_TO_AUTONOMOUS_WORKFORCE")
print("Backup:", BACKUP)
print("Updated admin:", ADMIN)
print("Updated client:", CLIENT)