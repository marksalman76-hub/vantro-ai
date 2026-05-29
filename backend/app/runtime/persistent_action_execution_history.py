
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
