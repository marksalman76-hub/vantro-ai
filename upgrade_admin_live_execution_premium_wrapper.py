from pathlib import Path
from datetime import datetime
import shutil

route = Path("frontend/src/app/api/admin-live-execution/route.ts")
backup = Path("backups") / f"admin_live_execution_premium_wrapper_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(route, backup / "route.ts")

s = route.read_text(encoding="utf-8")

old = '''  const payload = {
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
  };'''

new = '''  const requestedAgent = body.requested_agent || "marketing_specialist_agent";
  const userTask =
    body.task ||
    "Produce a commercial-quality governed live execution result.";

  const premiumTask = `
You are executing as: ${requestedAgent}.

Platform standard:
This is a unique multi-agent, multi-industry platform. Do not default to ecommerce unless the task is ecommerce-specific.
Use the industry, business model, market, customer segment, geography, and commercial intent stated in the task.

Output quality requirement:
Produce a premium, client-ready, commercially usable, execution-ready deliverable.
Do not provide generic consulting filler.
Do not merely explain concepts.
Do not say you need more information unless absolutely required; make reasonable explicit assumptions and proceed.

Agent-specific behaviour:
Stay strictly inside the selected agent's specialist role.
Produce the type of deliverable that this agent should produce in a real commercial workflow.

Required structure:
1. Executive summary
2. Business/industry context assumptions
3. Specific opportunity or problem diagnosis
4. Execution plan with concrete steps
5. Deliverables/assets/actions to create
6. KPIs or measurable success criteria
7. Risks, constraints, and mitigations
8. Owner/admin review points
9. Immediate next actions

User task:
${userTask}
`.trim();

  const payload = {
    tenant_id: "owner_admin",
    requested_agent: requestedAgent,
    workflow_stage: "admin_live_execution_premium_multi_industry",
    task: premiumTask,
    action_type: "governed_live_provider_generation",
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
    owner_approved: true,
    execute_real_world_action: true,
    project_id: "admin_live_execution_output_viewer",
    actor_role: "owner_admin",
    requested_credits: 1,
    quality_gate_required: true,
    premium_output_required: true,
    gold_standard_required: true,
    business_context_required: true,
  };'''

if old not in s:
    raise SystemExit("Target payload block not found. No changes made.")

s = s.replace(old, new)

route.write_text(s, encoding="utf-8")

print("ADMIN_LIVE_EXECUTION_PREMIUM_WRAPPER_UPGRADED")
print(f"Backup: {backup}")
print(f"Updated: {route}")