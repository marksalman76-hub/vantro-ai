from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
                CREATE TABLE IF NOT EXISTS execution_event_log (
                    id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    title TEXT,
                    agent_id TEXT,
                    payload JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        conn.commit()


def add_execution_event(
    tenant_id: str,
    project_id: str,
    event_type: str,
    title: str,
    agent_id: str = "",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = payload or {}

    if not _db_available():
        return {
            "success": False,
            "error": "DATABASE_URL_missing",
        }

    _ensure_tables()

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO execution_event_log
                (
                    tenant_id,
                    project_id,
                    event_type,
                    title,
                    agent_id,
                    payload
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
                """,
                (
                    tenant_id,
                    project_id,
                    event_type,
                    title,
                    agent_id,
                    json.dumps(payload),
                ),
            )

            row = cur.fetchone()

        conn.commit()

    return {
        "success": True,
        "event_id": row[0],
        "created_at": row[1].isoformat() if row and row[1] else _now(),
        "storage_mode": "postgres",
    }


def list_execution_events(
    tenant_id: str,
    project_id: str,
    limit: int = 20,
) -> Dict[str, Any]:
    if not _db_available():
        return {
            "success": True,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "count": 0,
            "events": [],
            "storage_mode": "no_database",
        }

    _ensure_tables()

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    event_type,
                    title,
                    agent_id,
                    payload,
                    created_at
                FROM execution_event_log
                WHERE tenant_id = %s
                AND project_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    tenant_id,
                    project_id,
                    limit,
                ),
            )

            rows = cur.fetchall()

    events: List[Dict[str, Any]] = []

    for row in rows:
        events.append(
            {
                "event_type": row[0],
                "title": row[1],
                "agent_id": row[2],
                "payload": row[3] or {},
                "created_at": row[4].isoformat() if row[4] else None,
            }
        )

    return {
        "success": True,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "count": len(events),
        "events": events,
        "storage_mode": "postgres",
    }