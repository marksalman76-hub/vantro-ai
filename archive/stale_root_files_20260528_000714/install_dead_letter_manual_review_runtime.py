from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

DEAD_LETTER = RUNTIME_DIR / "dead_letter_manual_review_runtime.py"
TEST_FILE = ROOT / "test_dead_letter_manual_review_runtime.py"
IMPORT_TEST = ROOT / "test_dead_letter_manual_review_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if MAIN.exists():
    backup = BACKUPS / f"main_before_dead_letter_manual_review_{ts}.py"
    backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")
else:
    raise FileNotFoundError("backend/app/main.py not found")

DEAD_LETTER.write_text(r'''
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid

DATA_DIR = Path("data") / "manual_review"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEAD_LETTER_EVENTS = DATA_DIR / "dead_letter_events.jsonl"
MANUAL_REVIEW_QUEUE = DATA_DIR / "manual_review_queue.jsonl"
MANUAL_REVIEW_DECISIONS = DATA_DIR / "manual_review_decisions.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({
                "record_type": "corrupt_jsonl_line",
                "raw": line,
                "loaded_at": _now(),
            })
    return rows


@dataclass
class DeadLetterRecord:
    dead_letter_id: str
    tenant_id: str
    workflow_id: Optional[str]
    agent_id: str
    action_type: str
    failure_reason: str
    payload: Dict[str, Any]
    retry_count: int
    severity: str
    status: str
    created_at: str
    owner_review_required: bool
    governance_preserved: bool
    no_autonomous_spend_or_scaling: bool


def create_dead_letter_record(
    *,
    tenant_id: str,
    agent_id: str,
    action_type: str,
    failure_reason: str,
    payload: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[str] = None,
    retry_count: int = 0,
    severity: str = "medium",
) -> Dict[str, Any]:
    record = DeadLetterRecord(
        dead_letter_id=f"dlq_{uuid.uuid4().hex[:16]}",
        tenant_id=tenant_id,
        workflow_id=workflow_id,
        agent_id=agent_id,
        action_type=action_type,
        failure_reason=failure_reason,
        payload=payload or {},
        retry_count=retry_count,
        severity=severity,
        status="dead_lettered",
        created_at=_now(),
        owner_review_required=True,
        governance_preserved=True,
        no_autonomous_spend_or_scaling=True,
    )
    item = asdict(record)
    _append_jsonl(DEAD_LETTER_EVENTS, item)
    enqueue_manual_review(item)
    return item


def enqueue_manual_review(dead_letter_record: Dict[str, Any]) -> Dict[str, Any]:
    review = {
        "review_id": f"review_{uuid.uuid4().hex[:16]}",
        "dead_letter_id": dead_letter_record.get("dead_letter_id"),
        "tenant_id": dead_letter_record.get("tenant_id"),
        "agent_id": dead_letter_record.get("agent_id"),
        "action_type": dead_letter_record.get("action_type"),
        "failure_reason": dead_letter_record.get("failure_reason"),
        "severity": dead_letter_record.get("severity", "medium"),
        "status": "pending_owner_review",
        "created_at": _now(),
        "owner_review_required": True,
        "allowed_decisions": ["retry", "mark_resolved", "reject", "escalate"],
        "blocked_decisions": ["increase_spend", "scale_campaign", "approve_contract"],
        "customer_safe_status": "Needs review",
    }
    _append_jsonl(MANUAL_REVIEW_QUEUE, review)
    return review


def list_dead_letters(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(DEAD_LETTER_EVENTS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "dead_letters": rows,
        "governance_preserved": True,
        "owner_review_required": True,
    }


def list_manual_review_queue(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(MANUAL_REVIEW_QUEUE)
    decisions = _read_jsonl(MANUAL_REVIEW_DECISIONS)
    decided_ids = {d.get("review_id") for d in decisions if d.get("review_id")}
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    if status == "pending_owner_review":
        rows = [r for r in rows if r.get("review_id") not in decided_ids]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "manual_review_items": rows,
        "governance_preserved": True,
        "customer_safe_ui_required": True,
    }


def record_manual_review_decision(
    *,
    review_id: str,
    decision: str,
    actor_role: str,
    notes: str = "",
) -> Dict[str, Any]:
    allowed = {"retry", "mark_resolved", "reject", "escalate"}
    if actor_role not in {"owner", "admin"}:
        return {
            "status": "blocked",
            "reason": "manual_review_decision_requires_owner_or_admin",
            "governance_preserved": True,
        }
    if decision not in allowed:
        return {
            "status": "blocked",
            "reason": "unsupported_or_high_risk_decision",
            "allowed_decisions": sorted(allowed),
            "governance_preserved": True,
            "no_autonomous_spend_or_scaling": True,
        }

    payload = {
        "decision_id": f"decision_{uuid.uuid4().hex[:16]}",
        "review_id": review_id,
        "decision": decision,
        "actor_role": actor_role,
        "notes": notes,
        "decided_at": _now(),
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "customer_safe_status": "Review updated",
    }
    _append_jsonl(MANUAL_REVIEW_DECISIONS, payload)
    return {
        "status": "ok",
        "decision": payload,
    }


def dead_letter_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "dead_letter_manual_review_runtime",
        "dead_letter_events_path": str(DEAD_LETTER_EVENTS),
        "manual_review_queue_path": str(MANUAL_REVIEW_QUEUE),
        "manual_review_decisions_path": str(MANUAL_REVIEW_DECISIONS),
        "owner_review_required": True,
        "governance_preserved": True,
        "entitlement_isolation_preserved": True,
        "customer_safe_ui_required": True,
        "no_autonomous_spend_or_scaling": True,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.dead_letter_manual_review_runtime import create_dead_letter_record, dead_letter_readiness, list_dead_letters, list_manual_review_queue, record_manual_review_decision\n"
if import_line not in main_text:
    insert_at = 0
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    if import_matches:
        insert_at = import_matches[-1].end() + 1
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/dead-letter/readiness")
def admin_dead_letter_readiness():
    return dead_letter_readiness()


@app.post("/admin/dead-letter/create")
def admin_create_dead_letter(payload: dict):
    return create_dead_letter_record(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=payload.get("workflow_id"),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        action_type=str(payload.get("action_type", "unknown_action")),
        failure_reason=str(payload.get("failure_reason", "unspecified_failure")),
        payload=dict(payload.get("payload", {})),
        retry_count=int(payload.get("retry_count", 0)),
        severity=str(payload.get("severity", "medium")),
    )


@app.get("/admin/dead-letter/list")
def admin_list_dead_letters(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_dead_letters(tenant_id=tenant_id, status=status, limit=limit)


@app.get("/admin/manual-review/list")
def admin_list_manual_review_queue(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_manual_review_queue(tenant_id=tenant_id, status=status, limit=limit)


@app.post("/admin/manual-review/decision")
def admin_record_manual_review_decision(payload: dict):
    return record_manual_review_decision(
        review_id=str(payload.get("review_id", "")),
        decision=str(payload.get("decision", "")),
        actor_role=str(payload.get("actor_role", "")),
        notes=str(payload.get("notes", "")),
    )
'''

if "/admin/dead-letter/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.dead_letter_manual_review_runtime import (
    create_dead_letter_record,
    dead_letter_readiness,
    list_dead_letters,
    list_manual_review_queue,
    record_manual_review_decision,
)


def main():
    readiness = dead_letter_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    record = create_dead_letter_record(
        tenant_id="tenant_test",
        workflow_id="workflow_test",
        agent_id="marketing_specialist_agent",
        action_type="provider_execution",
        failure_reason="provider_timeout_after_retries",
        payload={"safe": True},
        retry_count=3,
        severity="high",
    )
    assert record["status"] == "dead_lettered"
    assert record["owner_review_required"] is True
    assert record["no_autonomous_spend_or_scaling"] is True

    listed = list_dead_letters(tenant_id="tenant_test")
    assert listed["count"] >= 1

    queue = list_manual_review_queue(tenant_id="tenant_test")
    assert queue["count"] >= 1
    review_id = queue["manual_review_items"][-1]["review_id"]

    blocked = record_manual_review_decision(
        review_id=review_id,
        decision="retry",
        actor_role="client",
        notes="client should not be able to approve manual recovery",
    )
    assert blocked["status"] == "blocked"

    approved = record_manual_review_decision(
        review_id=review_id,
        decision="retry",
        actor_role="owner",
        notes="safe retry approved after review",
    )
    assert approved["status"] == "ok"

    bad_decision = record_manual_review_decision(
        review_id=review_id,
        decision="scale_campaign",
        actor_role="owner",
        notes="must remain blocked by governance",
    )
    assert bad_decision["status"] == "blocked"

    print("DEAD_LETTER_MANUAL_REVIEW_RUNTIME_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/dead-letter/readiness",
        "/admin/dead-letter/create",
        "/admin/dead-letter/list",
        "/admin/manual-review/list",
        "/admin/manual-review/decision",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("DEAD_LETTER_MANUAL_REVIEW_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("DEAD_LETTER_MANUAL_REVIEW_RUNTIME_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {DEAD_LETTER}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/dead-letter/readiness")
print("/admin/dead-letter/create")
print("/admin/dead-letter/list")
print("/admin/manual-review/list")
print("/admin/manual-review/decision")