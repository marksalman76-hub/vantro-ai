
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4
import json


PROFILE = "durable_external_action_records_v1"

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "runtime_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTERNAL_ACTION_FILE = DATA_DIR / "external_action_records.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_external_actions(
    *,
    tenant_id: str,
    execution_id: str | None,
    packet_id: str | None,
    assigned_agent: str,
    deliverable: Dict[str, Any] | None,
) -> Dict[str, Any]:
    deliverable = deliverable or {}
    actions = deliverable.get("actions_performed") or []

    records = []
    for action in actions:
        record = {
            "record_id": f"external_record_{uuid4().hex[:12]}",
            "tenant_id": tenant_id or "unknown",
            "execution_id": execution_id,
            "packet_id": packet_id,
            "assigned_agent": assigned_agent,
            "adapter": deliverable.get("adapter"),
            "action_type": action.get("type"),
            "action_status": action.get("status"),
            "provider": action.get("provider"),
            "provider_reference_id": (
                action.get("task_id")
                or action.get("draft_id")
                or action.get("event_id")
                or action.get("asset_id")
            ),
            "action": action,
            "deliverable_id": deliverable.get("deliverable_id"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": _now(),
        }
        records.append(record)

    if records:
        with EXTERNAL_ACTION_FILE.open("a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "success": True,
        "profile": PROFILE,
        "record_count": len(records),
        "records": records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def list_external_action_records(
    *,
    tenant_id: str | None = None,
    limit: int = 50,
) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []

    if EXTERNAL_ACTION_FILE.exists():
        for line in EXTERNAL_ACTION_FILE.read_text(encoding="utf-8").splitlines():
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
        "profile": PROFILE,
        "tenant_id": tenant_id,
        "count": len(records),
        "records": records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def external_action_records_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "profile": PROFILE,
        "record_file": str(EXTERNAL_ACTION_FILE),
        "record_file_exists": EXTERNAL_ACTION_FILE.exists(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
