from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _db_available() -> bool:
    return bool(DATABASE_URL)


def _conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_missing")
    return psycopg.connect(DATABASE_URL)


def _ensure_tables() -> None:
    if not _db_available():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_queue (
                    id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    agent_id TEXT,
                    action_type TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    priority INTEGER DEFAULT 5,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    next_attempt_at TIMESTAMPTZ DEFAULT NOW(),
                    locked_at TIMESTAMPTZ,
                    completed_at TIMESTAMPTZ,
                    failed_at TIMESTAMPTZ,
                    last_error TEXT,
                    payload JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_queue_status_next_attempt
                ON execution_queue (status, next_attempt_at, priority, created_at)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_dead_letter_queue (
                    id BIGSERIAL PRIMARY KEY,
                    queue_id BIGINT,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    agent_id TEXT,
                    action_type TEXT,
                    final_error TEXT,
                    retry_count INTEGER,
                    payload JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        conn.commit()


def enqueue_execution(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not _db_available():
        return {"success": False, "error": "DATABASE_URL_missing"}

    _ensure_tables()

    tenant_id = str(payload.get("tenant_id") or "").strip()
    project_id = str(payload.get("project_id") or "default_project").strip()
    agent_id = str(payload.get("agent_id") or payload.get("requested_agent") or "").strip()
    action_type = str(payload.get("action_type") or "").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO execution_queue
                (tenant_id, project_id, agent_id, action_type, status, priority, max_retries, payload)
                VALUES (%s, %s, %s, %s, 'queued', %s, %s, %s)
                RETURNING id, created_at
                """,
                (
                    tenant_id,
                    project_id,
                    agent_id,
                    action_type,
                    int(payload.get("priority") or 5),
                    int(payload.get("max_retries") or 3),
                    json.dumps(payload),
                ),
            )
            row = cur.fetchone()
        conn.commit()

    return {
        "success": True,
        "queue_id": row[0],
        "status": "queued",
        "created_at": row[1].isoformat() if row and row[1] else _now().isoformat(),
        "storage_mode": "postgres",
    }


def list_execution_queue(tenant_id: str = "", status: str = "", limit: int = 50) -> Dict[str, Any]:
    if not _db_available():
        return {"success": True, "count": 0, "items": [], "storage_mode": "no_database"}

    _ensure_tables()

    clauses = []
    params: List[Any] = []

    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)

    if status:
        clauses.append("status = %s")
        params.append(status)

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""

    params.append(max(1, min(int(limit or 50), 200)))

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, tenant_id, project_id, agent_id, action_type, status,
                       priority, retry_count, max_retries, next_attempt_at,
                       last_error, created_at, updated_at
                FROM execution_queue
                {where_sql}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()

    items = [
        {
            "queue_id": row[0],
            "tenant_id": row[1],
            "project_id": row[2],
            "agent_id": row[3],
            "action_type": row[4],
            "status": row[5],
            "priority": row[6],
            "retry_count": row[7],
            "max_retries": row[8],
            "next_attempt_at": row[9].isoformat() if row[9] else None,
            "last_error": row[10],
            "created_at": row[11].isoformat() if row[11] else None,
            "updated_at": row[12].isoformat() if row[12] else None,
        }
        for row in rows
    ]

    return {"success": True, "count": len(items), "items": items, "storage_mode": "postgres"}


def mark_execution_failed(queue_id: int, error: str) -> Dict[str, Any]:
    if not _db_available():
        return {"success": False, "error": "DATABASE_URL_missing"}

    _ensure_tables()

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT retry_count, max_retries, tenant_id, project_id, agent_id, action_type, payload
                FROM execution_queue
                WHERE id = %s
                """,
                (queue_id,),
            )
            row = cur.fetchone()

            if not row:
                return {"success": False, "error": "queue_item_not_found"}

            retry_count, max_retries, tenant_id, project_id, agent_id, action_type, payload = row
            next_retry_count = int(retry_count or 0) + 1

            if next_retry_count >= int(max_retries or 3):
                cur.execute(
                    """
                    UPDATE execution_queue
                    SET status = 'dead_lettered',
                        retry_count = %s,
                        failed_at = NOW(),
                        last_error = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (next_retry_count, error, queue_id),
                )
                cur.execute(
                    """
                    INSERT INTO execution_dead_letter_queue
                    (queue_id, tenant_id, project_id, agent_id, action_type, final_error, retry_count, payload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        queue_id,
                        tenant_id,
                        project_id,
                        agent_id,
                        action_type,
                        error,
                        next_retry_count,
                        json.dumps(payload or {}),
                    ),
                )
                status = "dead_lettered"
            else:
                delay_minutes = min(60, 5 * next_retry_count)
                cur.execute(
                    """
                    UPDATE execution_queue
                    SET status = 'retry_scheduled',
                        retry_count = %s,
                        next_attempt_at = %s,
                        last_error = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        next_retry_count,
                        _now() + timedelta(minutes=delay_minutes),
                        error,
                        queue_id,
                    ),
                )
                status = "retry_scheduled"

        conn.commit()

    return {
        "success": True,
        "queue_id": queue_id,
        "status": status,
        "retry_count": next_retry_count,
        "storage_mode": "postgres",
    }



def mark_execution_completed(queue_id: int, result: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not _db_available():
        return {"success": False, "error": "DATABASE_URL_missing"}

    _ensure_tables()

    result_payload = result or {}

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE execution_queue
                SET status = 'completed',
                    completed_at = NOW(),
                    last_error = NULL,
                    updated_at = NOW(),
                    payload = COALESCE(payload, '{}'::jsonb) || %s::jsonb
                WHERE id = %s
                RETURNING id, tenant_id, project_id, agent_id, action_type, status, completed_at
                """,
                (
                    json.dumps({"worker_result": result_payload}),
                    queue_id,
                ),
            )
            row = cur.fetchone()

        conn.commit()

    if not row:
        return {"success": False, "error": "queue_item_not_found", "queue_id": queue_id}

    return {
        "success": True,
        "queue_id": row[0],
        "tenant_id": row[1],
        "project_id": row[2],
        "agent_id": row[3],
        "action_type": row[4],
        "status": row[5],
        "completed_at": row[6].isoformat() if row[6] else None,
        "storage_mode": "postgres",
    }


def mark_execution_succeeded(queue_id: int, result: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return mark_execution_completed(queue_id, result)

def queue_readiness() -> Dict[str, Any]:
    if not _db_available():
        return {
            "success": True,
            "queue_ready": False,
            "storage_mode": "no_database",
            "database_url_present": False,
        }

    _ensure_tables()

    return {
        "success": True,
        "queue_ready": True,
        "storage_mode": "postgres",
        "retry_support": True,
        "dead_letter_support": True,
        "max_retries_default": 3,
    }

# queue_completion_persistence_locked = True
