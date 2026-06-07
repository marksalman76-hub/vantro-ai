
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4
import json
import os

from backend.app.runtime.durable_execution_history_evidence_runtime import (
    ensure_execution_history_evidence_tables,
    list_execution_evidence,
    record_execution_evidence,
)


PROFILE = "durable_external_action_records_v1"

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "runtime_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTERNAL_ACTION_FILE = DATA_DIR / "external_action_records.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


def _db_available() -> bool:
    if not _database_url():
        return False
    try:
        import psycopg  # noqa: F401
        return True
    except Exception:
        return False


def _conn():
    import psycopg
    return psycopg.connect(_database_url())


def _ensure_table() -> None:
    if not _db_available():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS external_action_records (
                    record_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    execution_id TEXT,
                    packet_id TEXT,
                    assigned_agent TEXT,
                    adapter TEXT,
                    action_type TEXT,
                    action_status TEXT,
                    provider TEXT,
                    provider_reference_id TEXT,
                    action JSONB DEFAULT '{}'::jsonb,
                    deliverable_id TEXT,
                    customer_safe BOOLEAN DEFAULT TRUE,
                    credential_values_exposed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_external_action_records_tenant_created
                ON external_action_records (tenant_id, created_at DESC)
                """
            )
        conn.commit()


def _build_records(
    *,
    tenant_id: str,
    execution_id: str | None,
    packet_id: str | None,
    assigned_agent: str,
    deliverable: Dict[str, Any] | None,
) -> List[Dict[str, Any]]:
    deliverable = deliverable or {}
    actions = deliverable.get("actions_performed") or []

    records = []
    for action in actions:
        record = {
            "record_id": f"external_record_{uuid4().hex[:12]}",
            "tenant_id": tenant_id or action.get("tenant_id") or "unknown",
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
                or action.get("messageId")
            ),
            "action": action,
            "deliverable_id": deliverable.get("deliverable_id"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": _now(),
        }
        records.append(record)

    return records


def _write_file_records(records: List[Dict[str, Any]]) -> None:
    if not records:
        return

    with EXTERNAL_ACTION_FILE.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_db_records(records: List[Dict[str, Any]]) -> bool:
    if not records or not _db_available():
        return False

    _ensure_table()

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                for record in records:
                    cur.execute(
                        """
                        INSERT INTO external_action_records (
                            record_id, tenant_id, execution_id, packet_id,
                            assigned_agent, adapter, action_type, action_status,
                            provider, provider_reference_id, action, deliverable_id,
                            customer_safe, credential_values_exposed, created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
                        ON CONFLICT (record_id) DO NOTHING
                        """,
                        (
                            record["record_id"],
                            record["tenant_id"],
                            record.get("execution_id"),
                            record.get("packet_id"),
                            record.get("assigned_agent"),
                            record.get("adapter"),
                            record.get("action_type"),
                            record.get("action_status"),
                            record.get("provider"),
                            record.get("provider_reference_id"),
                            json.dumps(record.get("action") or {}),
                            record.get("deliverable_id"),
                            bool(record.get("customer_safe", True)),
                            bool(record.get("credential_values_exposed", False)),
                            record.get("created_at"),
                        ),
                    )
            conn.commit()
        return True
    except Exception:
        return False


def record_external_actions(
    *,
    tenant_id: str,
    execution_id: str | None,
    packet_id: str | None,
    assigned_agent: str,
    deliverable: Dict[str, Any] | None,
) -> Dict[str, Any]:
    records = _build_records(
        tenant_id=tenant_id,
        execution_id=execution_id,
        packet_id=packet_id,
        assigned_agent=assigned_agent,
        deliverable=deliverable,
    )

    persistence_mode = "postgres" if _db_available() else "jsonl_fallback"
    written_to_db = _write_db_records(records)

    if not written_to_db:
        _write_file_records(records)
        persistence_mode = "jsonl_fallback"

    canonical_records = []
    for record in records:
        canonical = record_execution_evidence(
            tenant_id=str(record.get("tenant_id") or tenant_id or "unknown"),
            project_id=str((deliverable or {}).get("project_id") or "default_project"),
            execution_id=str(record.get("execution_id") or ""),
            evidence_type="external_action_record",
            title=str(record.get("action_type") or "External action record"),
            summary=str(record.get("action_status") or "External action recorded."),
            source_type="external_action",
            source_id=str(record.get("record_id") or ""),
            status=str(record.get("action_status") or "recorded"),
            payload=record,
            evidence_id=str(record.get("record_id") or ""),
        )
        if canonical.get("success"):
            canonical_records.append(canonical.get("evidence"))

    return {
        "success": True,
        "profile": PROFILE,
        "persistence_mode": "canonical_durable_runtime",
        "legacy_persistence_mode": persistence_mode,
        "record_count": len(records),
        "records": records,
        "canonical_records": canonical_records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def _read_file_records(*, tenant_id: str | None = None, limit: int = 50) -> List[Dict[str, Any]]:
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

    return records[-max(1, min(limit, 200)):][::-1]


def _read_db_records(*, tenant_id: str | None = None, limit: int = 50) -> List[Dict[str, Any]]:
    if not _db_available():
        return []

    _ensure_table()

    limit = max(1, min(int(limit or 50), 200))

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                if tenant_id:
                    cur.execute(
                        """
                        SELECT record_id, tenant_id, execution_id, packet_id,
                               assigned_agent, adapter, action_type, action_status,
                               provider, provider_reference_id, action, deliverable_id,
                               customer_safe, credential_values_exposed, created_at
                        FROM external_action_records
                        WHERE tenant_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (tenant_id, limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT record_id, tenant_id, execution_id, packet_id,
                               assigned_agent, adapter, action_type, action_status,
                               provider, provider_reference_id, action, deliverable_id,
                               customer_safe, credential_values_exposed, created_at
                        FROM external_action_records
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )

                rows = cur.fetchall()
    except Exception:
        return []

    records = []
    for row in rows:
        created_at = row[14]
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()

        records.append({
            "record_id": row[0],
            "tenant_id": row[1],
            "execution_id": row[2],
            "packet_id": row[3],
            "assigned_agent": row[4],
            "adapter": row[5],
            "action_type": row[6],
            "action_status": row[7],
            "provider": row[8],
            "provider_reference_id": row[9],
            "action": row[10] or {},
            "deliverable_id": row[11],
            "customer_safe": bool(row[12]),
            "credential_values_exposed": bool(row[13]),
            "created_at": created_at,
        })

    return records


def list_external_action_records(
    *,
    tenant_id: str | None = None,
    limit: int = 50,
) -> Dict[str, Any]:
    canonical = list_execution_evidence(tenant_id=tenant_id or "", limit=limit)
    evidence_items = canonical.get("evidence_items", []) if canonical.get("success") else []
    records = []
    for item in evidence_items:
        if item.get("evidence_type") != "external_action_record":
            continue
        payload = item.get("payload") or {}
        record = dict(payload)
        record.setdefault("record_id", item.get("source_id") or item.get("evidence_id"))
        record.setdefault("tenant_id", item.get("tenant_id"))
        record.setdefault("execution_id", item.get("execution_id"))
        record.setdefault("action_type", item.get("title"))
        record.setdefault("action_status", item.get("status"))
        record.setdefault("created_at", item.get("created_at"))
        record.setdefault("credential_values_exposed", False)
        record.setdefault("customer_safe", True)
        records.append(record)

    if records:
        persistence_mode = "canonical_durable_runtime"
    else:
        db_records = _read_db_records(tenant_id=tenant_id, limit=limit)
        file_records = [] if db_records else _read_file_records(tenant_id=tenant_id, limit=limit)
        records = db_records or file_records
        persistence_mode = "postgres" if db_records or _db_available() else "jsonl_fallback"

    return {
        "success": True,
        "profile": PROFILE,
        "tenant_id": tenant_id,
        "persistence_mode": persistence_mode,
        "count": len(records),
        "records": records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def external_action_records_readiness() -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    return {
        **readiness,
        "success": bool(readiness.get("success")),
        "profile": PROFILE,
        "persistence_mode": "canonical_durable_runtime" if readiness.get("success") else "unavailable",
        "legacy_persistence_mode": "postgres" if _db_available() else "jsonl_fallback",
        "database_url_configured": bool(_database_url()),
        "postgres_available": _db_available(),
        "record_file": str(EXTERNAL_ACTION_FILE),
        "record_file_exists": EXTERNAL_ACTION_FILE.exists(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
