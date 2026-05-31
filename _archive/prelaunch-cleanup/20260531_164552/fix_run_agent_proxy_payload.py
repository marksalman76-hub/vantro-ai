from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/api/run-agent/route.ts")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"run_agent_route_before_payload_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
shutil.copy2(TARGET, backup_file)

old = '''    const backendPayload = {
      ...body,
      agent_id: primaryAgent || selectedAgents[0],
      selected_agents: selectedAgents.length > 0 ? selectedAgents : [primaryAgent],
      task,
      prompt: body?.prompt || task,
      source: "client_workspace",
      execution_surface: "client_page",
    };'''

new = '''    const tenantId =
      request.headers.get("x-tenant-id") ||
      request.cookies.get("tenant_id")?.value ||
      body?.tenant_id ||
      "client_demo_001";

    const backendPayload = {
      ...body,
      tenant_id: body?.tenant_id || tenantId,
      agent_id: primaryAgent || selectedAgents[0],
      requested_agent: body?.requested_agent || primaryAgent || selectedAgents[0],
      selected_agents: selectedAgents.length > 0 ? selectedAgents : [primaryAgent],
      workflow_stage: body?.workflow_stage || "client_workspace_execution",
      action_type: body?.action_type || "agent_execution_request",
      task,
      prompt: body?.prompt || task,
      source: "client_workspace",
      execution_surface: "client_page",
    };'''

if old not in content:
    raise RuntimeError("Could not find backendPayload block.")

content = content.replace(old, new)

old_tenant_block = '''    const tenantId =
      request.headers.get("x-tenant-id") ||
      request.cookies.get("tenant_id")?.value ||
      body?.tenant_id ||
      "client_demo_001";

    const actorRole ='''

new_tenant_block = '''    const actorRole ='''

content = content.replace(old_tenant_block, new_tenant_block)

TARGET.write_text(content, encoding="utf-8")

print("RUN_AGENT_PROXY_PAYLOAD_FIXED")
print("Backup:", backup_file)