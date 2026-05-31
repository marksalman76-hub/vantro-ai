from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"persistent_action_execution_history_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

store_file = runtime_dir / "persistent_action_execution_history.py"
if store_file.exists():
    shutil.copy2(store_file, BACKUP / store_file.name)

store_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "runtime_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "action_execution_history.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_action_execution(
    *,
    tenant_id: str,
    packet_id: str | None,
    assigned_agent: str,
    execution_payload: Dict[str, Any],
) -> Dict[str, Any]:
    record = {
        "history_id": f"history_{uuid4().hex[:12]}",
        "tenant_id": tenant_id or "unknown",
        "packet_id": packet_id,
        "assigned_agent": assigned_agent,
        "execution_status": execution_payload.get("execution_status"),
        "autonomous_route": execution_payload.get("autonomous_route"),
        "performed_actual_action": execution_payload.get("performed_actual_action", False),
        "adapter": (
            execution_payload.get("adapter")
            or execution_payload.get("deliverable", {}).get("adapter")
        ),
        "actions_performed": (
            execution_payload.get("actions_performed")
            or execution_payload.get("deliverable", {}).get("actions_performed", [])
        ),
        "deliverable": execution_payload.get("deliverable"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }

    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def list_action_execution_history(
    *,
    tenant_id: str | None = None,
    limit: int = 50,
) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []

    if HISTORY_FILE.exists():
        for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue

            if tenant_id and item.get("tenant_id") != tenant_id:
                continue

            records.append(item)

    records = records[-max(1, min(limit, 200)):][::-1]

    return {
        "success": True,
        "profile": "persistent_action_execution_history_v1",
        "tenant_id": tenant_id,
        "count": len(records),
        "records": records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def action_execution_history_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "profile": "persistent_action_execution_history_v1",
        "history_file": str(HISTORY_FILE),
        "history_file_exists": HISTORY_FILE.exists(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
''', encoding="utf-8")

test_file = ROOT / "test_persistent_action_execution_history.py"
test_file.write_text(r'''
from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
    list_action_execution_history,
    action_execution_history_readiness,
)

payload = {
    "execution_status": "autonomously_executed",
    "performed_actual_action": True,
    "deliverable": {
        "adapter": "stakeholder_interview_outreach_adapter",
        "actions_performed": [
            {"type": "email_draft_created", "status": "created"},
            {"type": "crm_task_created", "status": "created"},
        ],
    },
}

record = record_action_execution(
    tenant_id="tenant_test",
    packet_id="packet_test_001",
    assigned_agent="marketing_specialist_agent",
    execution_payload=payload,
)

assert record["performed_actual_action"] is True
assert record["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(record["actions_performed"]) == 2

history = list_action_execution_history(tenant_id="tenant_test", limit=10)
assert history["success"] is True
assert history["count"] >= 1
assert history["records"][0]["tenant_id"] == "tenant_test"

readiness = action_execution_history_readiness()
assert readiness["success"] is True

print("PERSISTENT_ACTION_EXECUTION_HISTORY_TEST_PASSED")
''', encoding="utf-8")

print("PERSISTENT_ACTION_EXECUTION_HISTORY_INSTALLED")
print(f"Backup: {BACKUP}")
print(f"Created/updated: {store_file}")
print(f"Created/updated: {test_file}")