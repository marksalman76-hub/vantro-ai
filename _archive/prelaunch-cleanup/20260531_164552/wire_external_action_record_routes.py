from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"external_action_record_routes_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / main_file.name)

content = main_file.read_text(encoding="utf-8")

import_block = """from backend.app.runtime.durable_external_action_records import (
    list_external_action_records,
    external_action_records_readiness,
)
"""

if import_block not in content:
    marker = """from backend.app.runtime.persistent_action_execution_history import (
    list_action_execution_history,
    action_execution_history_readiness,
)
"""
    if marker not in content:
        raise SystemExit("IMPORT_MARKER_NOT_FOUND")
    content = content.replace(marker, marker + import_block)

route_block = r'''

@app.get("/admin/external-action-records")
def admin_external_action_records(
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

    return list_external_action_records(
        tenant_id=tenant_id,
        limit=limit,
    )


@app.get("/admin/external-action-records/readiness")
def admin_external_action_records_readiness(
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

    return external_action_records_readiness()
'''

if "/admin/external-action-records" not in content:
    content = content + route_block

main_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_external_action_record_routes.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.durable_external_action_records import record_external_actions

client = TestClient(app)

record_external_actions(
    tenant_id="route_external_test",
    execution_id="exec_route_test",
    packet_id="packet_route_test",
    assigned_agent="crm_ai_agent",
    deliverable={
        "deliverable_id": "deliverable_route_test",
        "adapter": "stakeholder_interview_outreach_adapter",
        "actions_performed": [
            {
                "type": "crm_task_created",
                "status": "executed",
                "provider": "governed_crm_runtime",
                "task_id": "crm_task_route_test",
            }
        ],
    },
)

blocked = client.get(
    "/admin/external-action-records?tenant_id=route_external_test",
    headers={"x-actor-role": "client"},
)
assert blocked.json()["success"] is False

ready = client.get(
    "/admin/external-action-records/readiness",
    headers={"x-actor-role": "owner_admin"},
)
assert ready.json()["success"] is True

records = client.get(
    "/admin/external-action-records?tenant_id=route_external_test&limit=5",
    headers={"x-actor-role": "owner_admin"},
)
body = records.json()
assert body["success"] is True
assert body["count"] >= 1
assert body["records"][0]["provider_reference_id"] == "crm_task_route_test"

print("EXTERNAL_ACTION_RECORD_ROUTES_TEST_PASSED")
''', encoding="utf-8")

print("EXTERNAL_ACTION_RECORD_ROUTES_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")