from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.runtime.persistent_workflow_runtime import (
    action_requires_owner_approval,
    create_workflow,
    get_workflow,
)


DEFAULT_DB_PATH = Path(os.getenv("CROSS_AGENT_ORCHESTRATION_DB_PATH", "data/cross_agent_orchestration.sqlite3"))

HEAD_AGENT_IDS = {"head_agent", "ceo_agent", "orchestration_agent"}

SPECIALIST_AGENT_ALLOWLIST = {
    "marketing_specialist_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "seo_agent",
    "social_media_manager_agent",
    "content_creator_agent",
    "product_description_agent",
    "influencer_collaboration_agent",
    "customer_support_agent",
    "analytics_agent",
    "website_builder_agent",
    "shopify_agent",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path() -> Path:
    path = Path(os.getenv("CROSS_AGENT_ORCHESTRATION_DB_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(data or {}, ensure_ascii=False, sort_keys=True)


def init_cross_agent_orchestration_store() -> Dict[str, Any]:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cross_agent_orchestrations (
                orchestration_id TEXT PRIMARY KEY,
                workflow_id TEXT,
                tenant_id TEXT,
                head_agent_id TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                objective_json TEXT,
                final_result_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cross_agent_tasks (
                task_id TEXT PRIMARY KEY,
                orchestration_id TEXT,
                workflow_id TEXT,
                assigned_agent_id TEXT,
                task_type TEXT,
                status TEXT,
                sequence_order INTEGER,
                owner_approval_required INTEGER DEFAULT 0,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                created_at TEXT,
                updated_at TEXT,
                task_payload_json TEXT,
                task_result_json TEXT,
                task_error_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cross_agent_orchestration_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                orchestration_id TEXT,
                task_id TEXT,
                event_type TEXT,
                event_status TEXT,
                created_at TEXT,
                details_json TEXT
            )
        """)
        conn.commit()

    return {
        "success": True,
        "status": "cross_agent_orchestration_store_ready",
        "db_path": str(_db_path()),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def _record_event(
    orchestration_id: str,
    event_type: str,
    event_status: str,
    task_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    with _connect() as conn:
        conn.execute("""
            INSERT INTO cross_agent_orchestration_events (
                orchestration_id, task_id, event_type, event_status, created_at, details_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (orchestration_id, task_id, event_type, event_status, utc_now_iso(), _json(details)))
        conn.commit()


def _normalise_agent(agent_id: str) -> str:
    return str(agent_id or "").strip().lower()


def can_head_agent_orchestrate(head_agent_id: str, active_agent_count: int = 2) -> bool:
    return _normalise_agent(head_agent_id) in HEAD_AGENT_IDS and int(active_agent_count) >= 2


def create_cross_agent_orchestration(
    orchestration_id: str,
    workflow_id: str,
    objective: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    tenant_id: Optional[str] = None,
    head_agent_id: str = "head_agent",
    active_agent_count: int = 2,
) -> Dict[str, Any]:
    init_cross_agent_orchestration_store()

    if not can_head_agent_orchestrate(head_agent_id, active_agent_count):
        return {
            "success": False,
            "status": "head_agent_orchestration_not_allowed",
            "orchestration_id": orchestration_id,
            "head_agent_id": head_agent_id,
            "active_agent_count": active_agent_count,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    workflow_type = str(objective.get("workflow_type") or "cross_agent_orchestration").strip().lower()

    workflow = create_workflow(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        payload={
            "objective": objective,
            "task_count": len(tasks),
            "head_agent_id": head_agent_id,
        },
        tenant_id=tenant_id,
        actor_role=head_agent_id,
        max_retries=int(objective.get("max_retries", 3)),
    )

    now = utc_now_iso()
    orchestration_status = "blocked_pending_owner_approval" if workflow.get("owner_approval_required") else "pending"

    with _connect() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO cross_agent_orchestrations (
                orchestration_id, workflow_id, tenant_id, head_agent_id, status,
                created_at, updated_at, objective_json, final_result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orchestration_id,
            workflow_id,
            tenant_id,
            head_agent_id,
            orchestration_status,
            now,
            now,
            _json(objective),
            _json({}),
        ))

        for index, task in enumerate(tasks, start=1):
            agent_id = _normalise_agent(task.get("assigned_agent_id"))
            task_type = str(task.get("task_type") or "specialist_task").strip().lower()
            approval_required = action_requires_owner_approval(task_type)
            allowed_agent = agent_id in SPECIALIST_AGENT_ALLOWLIST

            status = "blocked_agent_not_allowed"
            if allowed_agent:
                status = "blocked_pending_owner_approval" if approval_required else "pending"

            task_id = task.get("task_id") or f"{orchestration_id}_task_{index:03d}"

            conn.execute("""
                INSERT OR REPLACE INTO cross_agent_tasks (
                    task_id, orchestration_id, workflow_id, assigned_agent_id, task_type,
                    status, sequence_order, owner_approval_required, retry_count, max_retries,
                    created_at, updated_at, task_payload_json, task_result_json, task_error_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                orchestration_id,
                workflow_id,
                agent_id,
                task_type,
                status,
                index,
                1 if approval_required else 0,
                0,
                int(task.get("max_retries", 3)),
                now,
                now,
                _json(task.get("payload", {})),
                _json({}),
                _json({}),
            ))

        conn.commit()

    _record_event(
        orchestration_id,
        "orchestration_created",
        orchestration_status,
        details={
            "workflow_id": workflow_id,
            "tenant_id": tenant_id,
            "head_agent_id": head_agent_id,
            "task_count": len(tasks),
            "workflow_status": workflow.get("status"),
        },
    )

    return get_cross_agent_orchestration(orchestration_id)


def get_cross_agent_orchestration(orchestration_id: str) -> Dict[str, Any]:
    init_cross_agent_orchestration_store()

    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM cross_agent_orchestrations WHERE orchestration_id = ?",
            (orchestration_id,),
        ).fetchone()

        if not row:
            return {
                "success": False,
                "status": "orchestration_not_found",
                "orchestration_id": orchestration_id,
            }

        tasks = conn.execute("""
            SELECT * FROM cross_agent_tasks
            WHERE orchestration_id = ?
            ORDER BY sequence_order ASC
        """, (orchestration_id,)).fetchall()

        events = conn.execute("""
            SELECT task_id, event_type, event_status, created_at, details_json
            FROM cross_agent_orchestration_events
            WHERE orchestration_id = ?
            ORDER BY event_id ASC
        """, (orchestration_id,)).fetchall()

    workflow = get_workflow(row["workflow_id"])

    return {
        "success": True,
        "status": row["status"],
        "orchestration_id": row["orchestration_id"],
        "workflow_id": row["workflow_id"],
        "workflow_status": workflow.get("status"),
        "tenant_id": row["tenant_id"],
        "head_agent_id": row["head_agent_id"],
        "objective": json.loads(row["objective_json"] or "{}"),
        "final_result": json.loads(row["final_result_json"] or "{}"),
        "tasks": [
            {
                "task_id": task["task_id"],
                "assigned_agent_id": task["assigned_agent_id"],
                "task_type": task["task_type"],
                "status": task["status"],
                "sequence_order": task["sequence_order"],
                "owner_approval_required": bool(task["owner_approval_required"]),
                "retry_count": task["retry_count"],
                "max_retries": task["max_retries"],
                "payload": json.loads(task["task_payload_json"] or "{}"),
                "result": json.loads(task["task_result_json"] or "{}"),
                "error": json.loads(task["task_error_json"] or "{}"),
            }
            for task in tasks
        ],
        "events": [
            {
                "task_id": event["task_id"],
                "event_type": event["event_type"],
                "event_status": event["event_status"],
                "created_at": event["created_at"],
                "details": json.loads(event["details_json"] or "{}"),
            }
            for event in events
        ],
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def complete_cross_agent_task(
    orchestration_id: str,
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_cross_agent_orchestration(orchestration_id)
    if not current.get("success"):
        return current

    matched = next((task for task in current["tasks"] if task["task_id"] == task_id), None)
    if not matched:
        return {
            "success": False,
            "status": "task_not_found",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "governance_preserved": True,
        }

    if matched["owner_approval_required"]:
        return {
            "success": False,
            "status": "blocked_pending_owner_approval",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "execution_status": "task_not_completed",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    now = utc_now_iso()

    with _connect() as conn:
        conn.execute("""
            UPDATE cross_agent_tasks
            SET status = ?, updated_at = ?, task_result_json = ?
            WHERE task_id = ? AND orchestration_id = ?
        """, ("completed", now, _json(result), task_id, orchestration_id))
        conn.commit()

    _record_event(orchestration_id, "task_completed", "completed", task_id=task_id, details=result or {})

    updated = get_cross_agent_orchestration(orchestration_id)
    executable_tasks = [
        task for task in updated["tasks"]
        if task["status"] not in {"blocked_pending_owner_approval", "blocked_agent_not_allowed"}
    ]
    all_done = bool(executable_tasks) and all(task["status"] == "completed" for task in executable_tasks)

    if all_done:
        with _connect() as conn:
            conn.execute("""
                UPDATE cross_agent_orchestrations
                SET status = ?, updated_at = ?, final_result_json = ?
                WHERE orchestration_id = ?
            """, ("completed", utc_now_iso(), _json({"all_executable_tasks_completed": True}), orchestration_id))
            conn.commit()

        _record_event(
            orchestration_id,
            "orchestration_completed",
            "completed",
            details={"all_executable_tasks_completed": True},
        )

    return get_cross_agent_orchestration(orchestration_id)


def fail_cross_agent_task(
    orchestration_id: str,
    task_id: str,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_cross_agent_orchestration(orchestration_id)
    if not current.get("success"):
        return current

    matched = next((task for task in current["tasks"] if task["task_id"] == task_id), None)
    if not matched:
        return {
            "success": False,
            "status": "task_not_found",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "governance_preserved": True,
        }

    retry_count = int(matched["retry_count"]) + 1
    max_retries = int(matched["max_retries"])
    status = "retry_ready" if retry_count <= max_retries else "failed_manual_review_required"

    with _connect() as conn:
        conn.execute("""
            UPDATE cross_agent_tasks
            SET status = ?, retry_count = ?, updated_at = ?, task_error_json = ?
            WHERE task_id = ? AND orchestration_id = ?
        """, (status, retry_count, utc_now_iso(), _json(error), task_id, orchestration_id))
        conn.execute("""
            UPDATE cross_agent_orchestrations
            SET status = ?, updated_at = ?
            WHERE orchestration_id = ?
        """, ("requires_recovery" if status == "retry_ready" else "manual_review_required", utc_now_iso(), orchestration_id))
        conn.commit()

    _record_event(
        orchestration_id,
        "task_failed",
        status,
        task_id=task_id,
        details={"retry_count": retry_count, "max_retries": max_retries, "error": error or {}},
    )

    return get_cross_agent_orchestration(orchestration_id)


def readiness() -> Dict[str, Any]:
    store = init_cross_agent_orchestration_store()
    return {
        "success": True,
        "status": "cross_agent_workflow_orchestration_ready",
        "store_status": store["status"],
        "db_path": store["db_path"],
        "head_agent_ids": sorted(HEAD_AGENT_IDS),
        "specialist_agent_count": len(SPECIALIST_AGENT_ALLOWLIST),
        "supports_head_agent_delegation": True,
        "supports_durable_workflow_link": True,
        "supports_task_retry_foundation": True,
        "spend_scaling_contracts_owner_gated": True,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }
