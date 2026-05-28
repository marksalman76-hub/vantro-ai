from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"admin_run_selected_live_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

old = '''      for (const agentId of selectedRun) {
        const payload = {
          account_reference: "owner_admin",
          requested_agent: agentId,
          workflow_stage: "admin_internal_execution",
          action_type: "admin_owner_execution",
          actor_role: "owner",
          owner_approved: true,
          admin_execution: true,
          bypass_client_credits: true,
          task,
        };

        const response = await fetch("/api/admin-deployment-control", {
          method: "POST",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
          },
          body: JSON.stringify({
            path: "/run-agent",
            method: "POST",
            payload,
          }),
        });

        const data = await response.json().catch(() => ({
          success: false,
          message: "Invalid admin execution response.",
        }));

        results.push({
          agent_id: agentId,
          http_status: response.status,
          success: data?.success === true,
          status:
            data?.workflow_status ||
            data?.execution_status ||
            data?.status ||
            data?.error ||
            "completed",
          message:
            data?.message ||
            data?.summary ||
            data?.error ||
            "Execution response received.",
        });
      }'''

new = '''      for (const agentId of selectedRun) {
        const response = await fetch("/api/admin-live-execution", {
          method: "POST",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            requested_agent: agentId,
            task,
          }),
        });

        const wrapper = await response.json().catch(() => ({
          success: false,
          message: "Invalid admin live execution response.",
        }));

        const data = wrapper?.data || wrapper;
        const execution = data?.execution || {};
        const adapter = execution?.adapter_result || {};
        const normalised = adapter?.normalised_response || {};
        const safeOutput = normalised?.safe_output || {};

        results.push({
          agent_id: agentId,
          http_status: response.status,
          success: data?.success === true,
          status:
            execution?.execution_status ||
            data?.execution_status ||
            data?.status ||
            data?.error ||
            "completed",
          provider: adapter?.provider_key || "openai",
          live_external_call_executed: adapter?.live_external_call_executed === true,
          latency_ms: adapter?.latency_ms || null,
          credential_values_exposed: adapter?.credential_values_exposed === true,
          customer_safe: adapter?.customer_safe === true,
          output:
            safeOutput?.text ||
            data?.output?.generated_output ||
            data?.output?.output ||
            data?.output?.content ||
            "",
          message:
            data?.message ||
            data?.summary ||
            data?.error ||
            "Live provider execution response received.",
        });
      }'''

if old not in s:
    raise SystemExit("Target admin run-agent block not found. No changes made.")

s = s.replace(old, new)

s = s.replace(
    '"Admin execution completed"',
    '"Live execution completed"'
)

s = s.replace(
    '"Admin execution needs review"',
    '"Live execution needs review"'
)

s = s.replace(
    'showToast(allSucceeded ? "Selected agents completed." : "Some agent runs need review.");',
    'showToast(allSucceeded ? "Selected agents completed live execution." : "Some live agent runs need review.");'
)

p.write_text(s, encoding="utf-8")

print("ADMIN_RUN_SELECTED_AGENTS_NOW_USES_LIVE_EXECUTION")
print(f"Backup: {backup}")
print(f"Updated: {p}")