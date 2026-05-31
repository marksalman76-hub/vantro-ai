from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"activation_execution_audit_link_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_activation_execution_audit_link_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.activation_execution_audit_link import (
    get_activation_execution_audit_status,
    list_activation_execution_decisions,
    record_activation_execution_decision,
)
"""

route_block = r'''

@app.get("/activation-execution-audit/status")
async def activation_execution_audit_status():
    return get_activation_execution_audit_status()


@app.get("/activation-execution-audit/decisions")
async def activation_execution_audit_decisions(tenant_id: str = ""):
    return list_activation_execution_decisions(tenant_id)


@app.post("/activation-execution-audit/record")
async def activation_execution_audit_record(request: Request):
    body = await request.json()
    return record_activation_execution_decision(
        tenant_id=body.get("tenant_id", ""),
        requested_agent=body.get("requested_agent", ""),
        actor_role=body.get("actor_role", "system"),
        execution_allowed=bool(body.get("execution_allowed", False)),
        entitlement_check=body.get("entitlement_check", {}),
        source=body.get("source", "manual_record"),
    )
'''

if "from backend.app.runtime.activation_execution_audit_link import" not in text:
    text = import_block + "\n" + text

if "/activation-execution-audit/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

tenant_id = "test-activation-execution-audit-routes-001"

status = client.get("/activation-execution-audit/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["activation_execution_audit_link_ready"] is True
assert status_json["credential_values_exposed"] is False

record = client.post(
    "/activation-execution-audit/record",
    json={
        "tenant_id": tenant_id,
        "requested_agent": "seo_agent",
        "actor_role": "client",
        "execution_allowed": True,
        "source": "route_test",
        "entitlement_check": {
            "success": True,
            "status": "approved",
            "entitlement_source": "governed_activation_persistence",
            "credential_values_exposed": False,
            "customer_safe": True,
        },
    },
)
assert record.status_code == 200
record_json = record.json()
assert record_json["decision_status"] == "approved"
assert record_json["credential_values_exposed"] is False

blocked = client.post(
    "/activation-execution-audit/record",
    json={
        "tenant_id": tenant_id,
        "requested_agent": "head_agent",
        "actor_role": "client",
        "execution_allowed": False,
        "source": "route_test",
        "entitlement_check": {
            "success": False,
            "status": "blocked",
            "error": "requested_agent_not_activated",
            "next_stage": "owner_admin_review_required",
            "entitlement_source": "governed_activation_persistence",
            "credential_values_exposed": False,
            "customer_safe": True,
        },
    },
)
assert blocked.status_code == 200
blocked_json = blocked.json()
assert blocked_json["decision_status"] == "blocked"
assert blocked_json["owner_admin_review_required"] is True

listed = client.get(f"/activation-execution-audit/decisions?tenant_id={tenant_id}")
assert listed.status_code == 200
listed_json = listed.json()
assert listed_json["success"] is True
assert listed_json["event_count"] >= 2
assert listed_json["credential_values_exposed"] is False

print("ACTIVATION_EXECUTION_AUDIT_LINK_ROUTES_TESTS_PASSED")
print("status_ready", status_json["activation_execution_audit_link_ready"])
print("record_status", record_json["decision_status"])
print("blocked_status", blocked_json["decision_status"])
print("listed_event_count", listed_json["event_count"])
''', encoding="utf-8")

print("ACTIVATION_EXECUTION_AUDIT_LINK_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")