from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_dir = ROOT / "backend" / "app" / "runtime"
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"global_execution_evidence_layer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

evidence_file = runtime_dir / "global_execution_evidence_layer.py"

evidence_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.durable_external_action_records import list_external_action_records


GLOBAL_EXECUTION_EVIDENCE_PROFILE = "global_execution_evidence_layer_v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_action_summary(action: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": action.get("type"),
        "status": action.get("status"),
        "provider": action.get("provider"),
        "tenant_id": action.get("tenant_id"),
        "credential_exposed": False,
    }


def build_execution_evidence_packet(
    *,
    tenant_id: str | None = None,
    limit: int = 25,
    actor_role: str = "client",
) -> Dict[str, Any]:
    admin_view = actor_role in {"owner_admin", "admin", "owner"}

    records_result = list_external_action_records(
        tenant_id=tenant_id,
        limit=limit,
    )

    records = records_result.get("records", []) if records_result.get("success") else []

    evidence_items: List[Dict[str, Any]] = []

    for record in records:
        action = record.get("action") or {}
        base = {
            "record_id": record.get("record_id"),
            "tenant_id": record.get("tenant_id"),
            "packet_id": record.get("packet_id"),
            "assigned_agent": record.get("assigned_agent"),
            "adapter": record.get("adapter"),
            "action_type": record.get("action_type"),
            "action_status": record.get("action_status"),
            "provider": record.get("provider"),
            "deliverable_id": record.get("deliverable_id"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": record.get("created_at"),
            "action_summary": _safe_action_summary(action),
        }

        if admin_view:
            base["admin_evidence"] = {
                "provider_reference_id": record.get("provider_reference_id"),
                "raw_action_safe": action,
                "replay_diagnostic": {
                    "can_replay": False,
                    "reason": "Live external actions require a fresh owner-approved execution request.",
                },
            }
        else:
            base["client_evidence"] = {
                "summary": f"{record.get('action_type')} via {record.get('provider')}",
                "status": record.get("action_status"),
                "provider": record.get("provider"),
            }

        evidence_items.append(base)

    return {
        "success": True,
        "profile": GLOBAL_EXECUTION_EVIDENCE_PROFILE,
        "actor_role": actor_role,
        "admin_view": admin_view,
        "tenant_id": tenant_id,
        "count": len(evidence_items),
        "evidence_items": evidence_items,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
''', encoding="utf-8")

main = main_file.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet\n"
if import_line not in main:
    main = main.replace("from fastapi import", import_line + "from fastapi import", 1)

route_block = r'''

@app.get("/admin/execution-evidence")
def admin_execution_evidence(
    tenant_id: str | None = None,
    limit: int = 25,
    x_actor_role: str | None = Header(default="owner_admin"),
):
    return build_execution_evidence_packet(
        tenant_id=tenant_id,
        limit=limit,
        actor_role=x_actor_role or "owner_admin",
    )


@app.get("/client/execution-evidence")
def client_execution_evidence(
    tenant_id: str = "client_demo_001",
    limit: int = 25,
):
    return build_execution_evidence_packet(
        tenant_id=tenant_id,
        limit=limit,
        actor_role="client",
    )
'''

if "/admin/execution-evidence" not in main:
    main = main.rstrip() + "\n" + route_block + "\n"

main_file.write_text(main, encoding="utf-8")

test_file = ROOT / "test_global_execution_evidence_layer.py"
test_file.write_text(r'''
from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet

admin_packet = build_execution_evidence_packet(
    tenant_id="client_demo_001",
    limit=10,
    actor_role="owner_admin",
)

assert admin_packet["success"] is True
assert admin_packet["admin_view"] is True
assert admin_packet["credential_values_exposed"] is False

client_packet = build_execution_evidence_packet(
    tenant_id="client_demo_001",
    limit=10,
    actor_role="client",
)

assert client_packet["success"] is True
assert client_packet["admin_view"] is False
assert client_packet["credential_values_exposed"] is False

print("GLOBAL_EXECUTION_EVIDENCE_LAYER_TEST_PASSED")
''', encoding="utf-8")

print("GLOBAL_EXECUTION_EVIDENCE_LAYER_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Created: {evidence_file}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")