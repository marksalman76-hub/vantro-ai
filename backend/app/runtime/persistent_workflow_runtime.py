"""
Persistent workflow runtime foundation.

Purpose:
- Store governed multi-step workflow state durably.
- Support retry/recovery without bypassing governance.
- Preserve owner approval gates for spend, scaling, contracts, publishing, and financial commitments.
- Keep client-safe/white-label behaviour intact.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


OWNER_APPROVAL_ACTIONS = {
    "increase_ad_spend",
    "scale_campaign",
    "change_budget",
    "approve_contract",
    "sign_contract",
    "purchase_media",
    "publish_live_campaign",
    "commit_financial_action",
}

DEFAULT_DB_PATH = Path(
    os.getenv(
        "PERSISTENT_WORKFLOW_DB_PATH",
        "data/persistent_workflows.sqlite3",
    )
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path() -> Path:
    path = Path(os.getenv("PERSISTENT_WORKFLOW_DB_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_persistent_workflow_store() -> Dict[str, Any]:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS governed_workflows (
                workflow_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                actor_role TEXT,
                workflow_type TEXT,
                status TEXT,
                current_step INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                retry_count INTEGER DEFAULT 0,
                owner_approval_required INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                payload_json TEXT,
                result_json TEXT,
                error_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS governed_workflow_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT,
                event_type TEXT,
                event_status TEXT,
                created_at TEXT,
                details_json TEXT
            )
            """
        )
        conn.commit()

    return {
        "success": True,
        "status": "persistent_workflow_store_ready",
        "db_path": str(_db_path()),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def action_requires_owner_approval(action_type: Optional[str]) -> bool:
    return str(action_type or "").strip().lower() in OWNER_APPROVAL_ACTIONS


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(data or {}, ensure_ascii=False, sort_keys=True)


def create_workflow(
    workflow_id: str,
    workflow_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[str] = None,
    actor_role: str = "system",
    max_retries: int = 3,
) -> Dict[str, Any]:
    init_persistent_workflow_store()

    workflow_type_key = str(workflow_type or "").strip().lower()
    now = utc_now_iso()
    approval_required = action_requires_owner_approval(workflow_type_key)

    status = "blocked_pending_owner_approval" if approval_required else "pending"

    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO governed_workflows (
                workflow_id, tenant_id, actor_role, workflow_type, status,
                current_step, max_retries, retry_count, owner_approval_required,
                created_at, updated_at, payload_json, result_json, error_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                tenant_id,
                actor_role,
                workflow_type_key,
                status,
                0,
                int(max_retries),
                0,
                1 if approval_required else 0,
                now,
                now,
                _json(payload),
                _json({}),
                _json({}),
            ),
        )
        conn.execute(
            """
            INSERT INTO governed_workflow_events (
                workflow_id, event_type, event_status, created_at, details_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                "workflow_created",
                status,
                now,
                _json(
                    {
                        "workflow_type": workflow_type_key,
                        "tenant_id": tenant_id,
                        "actor_role": actor_role,
                        "owner_approval_required": approval_required,
                    }
                ),
            ),
        )
        conn.commit()

    return get_workflow(workflow_id)


def get_workflow(workflow_id: str) -> Dict[str, Any]:
    init_persistent_workflow_store()

    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM governed_workflows WHERE workflow_id = ?",
            (workflow_id,),
        ).fetchone()

        if not row:
            return {
                "success": False,
                "status": "workflow_not_found",
                "workflow_id": workflow_id,
            }

        events = conn.execute(
            """
            SELECT event_type, event_status, created_at, details_json
            FROM governed_workflow_events
            WHERE workflow_id = ?
            ORDER BY event_id ASC
            """,
            (workflow_id,),
        ).fetchall()

    return {
        "success": True,
        "status": row["status"],
        "workflow_id": row["workflow_id"],
        "tenant_id": row["tenant_id"],
        "actor_role": row["actor_role"],
        "workflow_type": row["workflow_type"],
        "current_step": row["current_step"],
        "max_retries": row["max_retries"],
        "retry_count": row["retry_count"],
        "owner_approval_required": bool(row["owner_approval_required"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "payload": json.loads(row["payload_json"] or "{}"),
        "result": json.loads(row["result_json"] or "{}"),
        "error": json.loads(row["error_json"] or "{}"),
        "events": [
            {
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


def advance_workflow(
    workflow_id: str,
    step_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    if current["owner_approval_required"]:
        return {
            **current,
            "success": False,
            "status": "blocked_pending_owner_approval",
            "execution_status": "not_advanced",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    now = utc_now_iso()
    next_step = int(current["current_step"]) + 1

    with _connect() as conn:
        conn.execute(
            """
            UPDATE governed_workflows
            SET status = ?, current_step = ?, updated_at = ?, result_json = ?
            WHERE workflow_id = ?
            """,
            (
                "in_progress",
                next_step,
                now,
                _json(step_result),
                workflow_id,
            ),
        )
        conn.execute(
            """
            INSERT INTO governed_workflow_events (
                workflow_id, event_type, event_status, created_at, details_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                "workflow_advanced",
                "in_progress",
                now,
                _json({"current_step": next_step, "step_result": step_result or {}}),
            ),
        )
        conn.commit()

    return get_workflow(workflow_id)


def fail_workflow(
    workflow_id: str,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    now = utc_now_iso()
    retry_count = int(current["retry_count"]) + 1
    max_retries = int(current["max_retries"])

    status = "retry_ready" if retry_count <= max_retries else "failed_manual_review_required"

    with _connect() as conn:
        conn.execute(
            """
            UPDATE governed_workflows
            SET status = ?, retry_count = ?, updated_at = ?, error_json = ?
            WHERE workflow_id = ?
            """,
            (
                status,
                retry_count,
                now,
                _json(error),
                workflow_id,
            ),
        )
        conn.execute(
            """
            INSERT INTO governed_workflow_events (
                workflow_id, event_type, event_status, created_at, details_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                "workflow_failed",
                status,
                now,
                _json({"retry_count": retry_count, "max_retries": max_retries, "error": error or {}}),
            ),
        )
        conn.commit()

    return get_workflow(workflow_id)


def complete_workflow(
    workflow_id: str,
    result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    if current["owner_approval_required"]:
        return {
            **current,
            "success": False,
            "status": "blocked_pending_owner_approval",
            "execution_status": "not_completed",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    now = utc_now_iso()

    with _connect() as conn:
        conn.execute(
            """
            UPDATE governed_workflows
            SET status = ?, updated_at = ?, result_json = ?
            WHERE workflow_id = ?
            """,
            (
                "completed",
                now,
                _json(result),
                workflow_id,
            ),
        )
        conn.execute(
            """
            INSERT INTO governed_workflow_events (
                workflow_id, event_type, event_status, created_at, details_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                "workflow_completed",
                "completed",
                now,
                _json(result or {}),
            ),
        )
        conn.commit()

    return get_workflow(workflow_id)


def readiness() -> Dict[str, Any]:
    store = init_persistent_workflow_store()
    return {
        "success": True,
        "status": "persistent_workflow_runtime_ready",
        "store_status": store["status"],
        "db_path": store["db_path"],
        "supports_persistent_state": True,
        "supports_retry_recovery_foundation": True,
        "spend_scaling_contracts_owner_gated": True,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }
