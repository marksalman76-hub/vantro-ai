from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"action_execution_history_routes_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / main_file.name)

content = main_file.read_text(encoding="utf-8")

import_block = """from backend.app.runtime.persistent_action_execution_history import (
    list_action_execution_history,
    action_execution_history_readiness,
)
"""

if import_block not in content:
    marker = """from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)
"""
    if marker not in content:
        raise SystemExit("IMPORT_MARKER_NOT_FOUND")
    content = content.replace(marker, marker + import_block)

route_block = r'''

@app.get("/admin/action-execution-history")
def admin_action_execution_history(
    tenant_id: str | None = None,
    limit: int = 50,
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return list_action_execution_history(
        tenant_id=tenant_id,
        limit=limit,
    )


@app.get("/admin/action-execution-history/readiness")
def admin_action_execution_history_readiness(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return action_execution_history_readiness()
'''

if "/admin/action-execution-history" not in content:
    content = content + route_block

main_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_action_execution_history_routes.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.persistent_action_execution_history import record_action_execution

client = TestClient(app)

record_action_execution(
    tenant_id="route_test",
    packet_id="route_packet_001",
    assigned_agent="marketing_specialist_agent",
    execution_payload={
        "execution_status": "autonomously_executed",
        "performed_actual_action": True,
        "deliverable": {
            "adapter": "stakeholder_interview_outreach_adapter",
            "actions_performed": [{"type": "email_draft_created", "status": "created"}],
        },
    },
)

blocked = client.get(
    "/admin/action-execution-history?tenant_id=route_test",
    headers={"x-actor-role": "client"},
)
assert blocked.json()["success"] is False

ready = client.get(
    "/admin/action-execution-history/readiness",
    headers={"x-actor-role": "owner_admin"},
)
assert ready.json()["success"] is True

history = client.get(
    "/admin/action-execution-history?tenant_id=route_test&limit=5",
    headers={"x-actor-role": "owner_admin"},
)
body = history.json()
assert body["success"] is True
assert body["count"] >= 1
assert body["records"][0]["tenant_id"] == "route_test"

print("ACTION_EXECUTION_HISTORY_ROUTES_TEST_PASSED")
''', encoding="utf-8")

print("ACTION_EXECUTION_HISTORY_ROUTES_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")