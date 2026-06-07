from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DURABLE_EXECUTION_HISTORY_EVIDENCE_PROFILE = "durable_execution_history_evidence_runtime_v1"

_DEV_HISTORY: Dict[str, Dict[str, Any]] = {}
_DEV_EVENTS: Dict[str, Dict[str, Any]] = {}
_DEV_EVIDENCE: Dict[str, Dict[str, Any]] = {}
_DEV_DELIVERABLES: Dict[str, Dict[str, Any]] = {}
_DEV_APPROVAL_AUDITS: Dict[str, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _database_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or ""


def _is_production() -> bool:
    values = [
        os.getenv("ENVIRONMENT"),
        os.getenv("APP_ENV"),
        os.getenv("FASTAPI_ENV"),
        os.getenv("NODE_ENV"),
        os.getenv("RENDER"),
        os.getenv("VERCEL_ENV"),
        os.getenv("PRODUCTION"),
    ]
    return any(str(value or "").strip().lower() in {"1", "true", "prod", "production"} for value in values)


def _psycopg():
    try:
        import psycopg  # type: ignore

        return psycopg
    except Exception:
        return None


def _connect():
    psycopg = _psycopg()
    if psycopg is None:
        raise RuntimeError("psycopg_unavailable")
    if not _database_url():
        raise RuntimeError("DATABASE_URL_missing")
    timeout = max(1, min(int(os.getenv("EXECUTION_HISTORY_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("execution_history_evidence_profile", DURABLE_EXECUTION_HISTORY_EVIDENCE_PROFILE)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="execution_history_evidence_store_unavailable",
        execution_history_evidence_ready=False,
        durable=False,
        storage_mode="postgres_unavailable",
        production_fail_closed=_is_production(),
        dev_only=False,
        not_production_durable=False,
        reason=reason,
    )


def _using_dev(readiness: Dict[str, Any]) -> bool:
    return readiness.get("storage_mode") == "dev_memory"


def _limit(value: int, default: int = 50, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


def _clean(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def _scrub_sensitive(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in (data or {}).items():
        key_lower = str(key).lower()
        if any(marker in key_lower for marker in ("secret", "token", "api_key", "password", "credential")):
            continue
        if isinstance(value, dict):
            safe[key] = _scrub_sensitive(value)
            continue
        if isinstance(value, list):
            safe[key] = [_scrub_sensitive(item) if isinstance(item, dict) else item for item in value]
            continue
        safe[key] = value
    return safe


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(_scrub_sensitive(deepcopy(data or {})), ensure_ascii=False, sort_keys=True)


def _parse_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return _scrub_sensitive(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return _scrub_sensitive(parsed) if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _dt(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _history_columns() -> List[str]:
    return [
        "history_id",
        "tenant_id",
        "project_id",
        "execution_id",
        "agent_id",
        "workflow_id",
        "orchestration_id",
        "provider_execution_id",
        "queue_job_id",
        "action_type",
        "status",
        "summary",
        "payload_json",
        "created_at",
        "updated_at",
        "completed_at",
        "failed_at",
        "credential_values_exposed",
    ]


def _event_columns() -> List[str]:
    return ["event_id", "tenant_id", "project_id", "execution_id", "event_type", "source_type", "source_id", "payload_json", "created_at"]


def _evidence_columns() -> List[str]:
    return ["evidence_id", "tenant_id", "project_id", "execution_id", "evidence_type", "title", "summary", "source_type", "source_id", "status", "payload_json", "created_at"]


def _deliverable_columns() -> List[str]:
    return ["deliverable_id", "tenant_id", "project_id", "execution_id", "agent_id", "title", "summary", "deliverable_type", "status", "payload_json", "created_at", "updated_at"]


def _approval_columns() -> List[str]:
    return ["audit_id", "tenant_id", "project_id", "execution_id", "action_id", "action_type", "decision", "actor_role", "payload_json", "created_at"]


def _row(row: Any, columns: List[str]) -> Dict[str, Any]:
    result = dict(zip(columns, row))
    if "payload_json" in result:
        result["payload"] = _parse_json(result.pop("payload_json", None))
    for key, value in list(result.items()):
        result[key] = _dt(value)
    result["credential_values_exposed"] = False
    result["customer_safe"] = True
    return result


def ensure_execution_history_evidence_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_execution_history_evidence_ready",
            execution_history_evidence_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
        )

    if _psycopg() is None:
        if _is_production():
            return _unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_execution_history_evidence_ready",
            execution_history_evidence_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_driver_unavailable=True,
        )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_history_records (
                        history_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        agent_id TEXT,
                        workflow_id TEXT,
                        orchestration_id TEXT,
                        provider_execution_id TEXT,
                        queue_job_id TEXT,
                        action_type TEXT,
                        status TEXT NOT NULL DEFAULT 'recorded',
                        summary TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_execution_history_tenant_created ON execution_history_records (tenant_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_execution_history_execution ON execution_history_records (execution_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_events (
                        event_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        event_type TEXT NOT NULL,
                        source_type TEXT,
                        source_id TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_execution_events_tenant_project ON execution_events (tenant_id, project_id, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_evidence_items (
                        evidence_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        evidence_type TEXT NOT NULL,
                        title TEXT,
                        summary TEXT,
                        source_type TEXT,
                        source_id TEXT,
                        status TEXT NOT NULL DEFAULT 'recorded',
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_execution_evidence_tenant_created ON execution_evidence_items (tenant_id, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_deliverable_records (
                        deliverable_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        agent_id TEXT,
                        title TEXT,
                        summary TEXT,
                        deliverable_type TEXT,
                        status TEXT NOT NULL DEFAULT 'ready',
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_latest_deliverable_tenant_created ON latest_deliverable_records (tenant_id, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS approval_action_audit_records (
                        audit_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        action_id TEXT,
                        action_type TEXT,
                        decision TEXT,
                        actor_role TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_approval_action_audit_tenant_created ON approval_action_audit_records (tenant_id, created_at DESC)")
            conn.commit()
        return _safe_response(success=True, status="execution_history_evidence_ready", execution_history_evidence_ready=True, durable=True, storage_mode="postgres", persistence_mode="postgres", dev_only=False, not_production_durable=False)
    except Exception as exc:
        if _is_production():
            return _unavailable(str(exc))
        return _safe_response(success=True, status="dev_only_execution_history_evidence_ready", execution_history_evidence_ready=True, durable=False, storage_mode="dev_memory", persistence_mode="dev_only", dev_only=True, not_production_durable=True, postgres_error=str(exc))


def record_execution_history(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    agent_id: str = "",
    workflow_id: str = "",
    orchestration_id: str = "",
    provider_execution_id: str = "",
    queue_job_id: str = "",
    action_type: str = "",
    status: str = "recorded",
    summary: str = "",
    payload: Optional[Dict[str, Any]] = None,
    history_id: str = "",
    completed: bool = False,
    failed: bool = False,
) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    now = _now_iso()
    record = {
        "history_id": _clean(history_id) or f"history_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "agent_id": _clean(agent_id),
        "workflow_id": _clean(workflow_id),
        "orchestration_id": _clean(orchestration_id),
        "provider_execution_id": _clean(provider_execution_id),
        "queue_job_id": _clean(queue_job_id),
        "action_type": _clean(action_type),
        "status": _clean(status, "recorded"),
        "summary": str(summary or "")[:2000],
        "payload": _scrub_sensitive(payload or {}),
        "created_at": now,
        "updated_at": now,
        "completed_at": now if completed else None,
        "failed_at": now if failed else None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_HISTORY[record["history_id"]] = deepcopy(record)
        return _safe_response(success=True, status="recorded", history=deepcopy(record), record=deepcopy(record), history_id=record["history_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO execution_history_records
                (history_id, tenant_id, project_id, execution_id, agent_id, workflow_id,
                 orchestration_id, provider_execution_id, queue_job_id, action_type,
                 status, summary, payload_json, completed_at, failed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                RETURNING history_id, tenant_id, project_id, execution_id, agent_id,
                          workflow_id, orchestration_id, provider_execution_id,
                          queue_job_id, action_type, status, summary, payload_json,
                          created_at, updated_at, completed_at, failed_at,
                          credential_values_exposed
                """,
                (record["history_id"], record["tenant_id"], record["project_id"], record["execution_id"] or None, record["agent_id"] or None, record["workflow_id"] or None, record["orchestration_id"] or None, record["provider_execution_id"] or None, record["queue_job_id"] or None, record["action_type"] or None, record["status"], record["summary"] or None, _json(record["payload"]), record["completed_at"], record["failed_at"]),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _history_columns())
    return _safe_response(success=True, status="recorded", history=item, record=item, history_id=item["history_id"], storage_mode="postgres", durable=True)


def list_execution_history(*, tenant_id: str = "", project_id: str = "", execution_id: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        records = list(_DEV_HISTORY.values())
        if tenant_id:
            records = [item for item in records if item.get("tenant_id") == tenant_id]
        if project_id:
            records = [item for item in records if item.get("project_id") == project_id]
        if execution_id:
            records = [item for item in records if item.get("execution_id") == execution_id]
        records = sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(records), records=deepcopy(records), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_history_columns())} FROM execution_history_records {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    records = [_row(row, _history_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(records), records=records, storage_mode="postgres", durable=True)


def record_execution_event(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    event_type: str,
    source_type: str = "",
    source_id: str = "",
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    event = {
        "event_id": _clean(event_id) or f"exec_event_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "event_type": _clean(event_type, "execution_event"),
        "source_type": _clean(source_type),
        "source_id": _clean(source_id),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_EVENTS[event["event_id"]] = deepcopy(event)
        return _safe_response(success=True, status="recorded", event=deepcopy(event), event_id=event["event_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO execution_events
                (event_id, tenant_id, project_id, execution_id, event_type, source_type, source_id, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING event_id, tenant_id, project_id, execution_id, event_type, source_type, source_id, payload_json, created_at
                """,
                (event["event_id"], event["tenant_id"], event["project_id"], event["execution_id"] or None, event["event_type"], event["source_type"] or None, event["source_id"] or None, _json(event["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _event_columns())
    return _safe_response(success=True, status="recorded", event=item, event_id=item["event_id"], storage_mode="postgres", durable=True)


def list_execution_events(*, tenant_id: str = "", project_id: str = "", execution_id: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        events = list(_DEV_EVENTS.values())
        if tenant_id:
            events = [item for item in events if item.get("tenant_id") == tenant_id]
        if project_id:
            events = [item for item in events if item.get("project_id") == project_id]
        if execution_id:
            events = [item for item in events if item.get("execution_id") == execution_id]
        events = sorted(events, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(events), events=deepcopy(events), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_event_columns())} FROM execution_events {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    events = [_row(row, _event_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(events), events=events, storage_mode="postgres", durable=True)


def record_execution_evidence(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    evidence_type: str = "execution_evidence",
    title: str = "",
    summary: str = "",
    source_type: str = "",
    source_id: str = "",
    status: str = "recorded",
    payload: Optional[Dict[str, Any]] = None,
    evidence_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    item = {
        "evidence_id": _clean(evidence_id) or f"evidence_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "evidence_type": _clean(evidence_type, "execution_evidence"),
        "title": str(title or "")[:500],
        "summary": str(summary or "")[:2000],
        "source_type": _clean(source_type),
        "source_id": _clean(source_id),
        "status": _clean(status, "recorded"),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_EVIDENCE[item["evidence_id"]] = deepcopy(item)
        return _safe_response(success=True, status="recorded", evidence=item, evidence_id=item["evidence_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO execution_evidence_items
                (evidence_id, tenant_id, project_id, execution_id, evidence_type, title,
                 summary, source_type, source_id, status, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING evidence_id, tenant_id, project_id, execution_id, evidence_type,
                          title, summary, source_type, source_id, status, payload_json, created_at
                """,
                (item["evidence_id"], item["tenant_id"], item["project_id"], item["execution_id"] or None, item["evidence_type"], item["title"] or None, item["summary"] or None, item["source_type"] or None, item["source_id"] or None, item["status"], _json(item["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    evidence = _row(row, _evidence_columns())
    return _safe_response(success=True, status="recorded", evidence=evidence, evidence_id=evidence["evidence_id"], storage_mode="postgres", durable=True)


def list_execution_evidence(*, tenant_id: str = "", project_id: str = "", execution_id: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        items = list(_DEV_EVIDENCE.values())
        if tenant_id:
            items = [item for item in items if item.get("tenant_id") == tenant_id]
        if project_id:
            items = [item for item in items if item.get("project_id") == project_id]
        if execution_id:
            items = [item for item in items if item.get("execution_id") == execution_id]
        items = sorted(items, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(items), evidence_items=deepcopy(items), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_evidence_columns())} FROM execution_evidence_items {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    items = [_row(row, _evidence_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(items), evidence_items=items, storage_mode="postgres", durable=True)


def record_latest_deliverable(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    agent_id: str = "",
    title: str = "",
    summary: str = "",
    deliverable_type: str = "deliverable",
    status: str = "ready",
    payload: Optional[Dict[str, Any]] = None,
    deliverable_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    record = {
        "deliverable_id": _clean(deliverable_id) or f"deliverable_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "agent_id": _clean(agent_id),
        "title": str(title or "")[:500],
        "summary": str(summary or "")[:2000],
        "deliverable_type": _clean(deliverable_type, "deliverable"),
        "status": _clean(status, "ready"),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_DELIVERABLES[record["deliverable_id"]] = deepcopy(record)
        return _safe_response(success=True, status="recorded", deliverable=deepcopy(record), latest_deliverable=deepcopy(record), deliverable_id=record["deliverable_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO latest_deliverable_records
                (deliverable_id, tenant_id, project_id, execution_id, agent_id, title,
                 summary, deliverable_type, status, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING deliverable_id, tenant_id, project_id, execution_id, agent_id,
                          title, summary, deliverable_type, status, payload_json,
                          created_at, updated_at
                """,
                (record["deliverable_id"], record["tenant_id"], record["project_id"], record["execution_id"] or None, record["agent_id"] or None, record["title"] or None, record["summary"] or None, record["deliverable_type"], record["status"], _json(record["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _deliverable_columns())
    return _safe_response(success=True, status="recorded", deliverable=item, latest_deliverable=item, deliverable_id=item["deliverable_id"], storage_mode="postgres", durable=True)


def get_latest_deliverable(*, tenant_id: str, project_id: str = "") -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    if _using_dev(readiness):
        items = [item for item in _DEV_DELIVERABLES.values() if item.get("tenant_id") == tenant_id]
        if project_id:
            items = [item for item in items if item.get("project_id") == project_id]
        items = sorted(items, key=lambda item: str(item.get("created_at") or ""), reverse=True)
        if not items:
            return _safe_response(success=True, status="not_found", latest_deliverable=None, has_real_output=False, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", latest_deliverable=deepcopy(items[0]), deliverable=deepcopy(items[0]), has_real_output=True, storage_mode="dev_memory", dev_only=True)
    clauses = ["tenant_id = %s"]
    params: List[Any] = [tenant_id]
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    where = "WHERE " + " AND ".join(clauses)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_deliverable_columns())} FROM latest_deliverable_records {where} ORDER BY created_at DESC LIMIT 1", params)
            row = cur.fetchone()
    if not row:
        return _safe_response(success=True, status="not_found", latest_deliverable=None, has_real_output=False, storage_mode="postgres", durable=True)
    item = _row(row, _deliverable_columns())
    return _safe_response(success=True, status="found", latest_deliverable=item, deliverable=item, has_real_output=True, storage_mode="postgres", durable=True)


def record_approval_action_audit(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    action_id: str = "",
    action_type: str = "",
    decision: str = "",
    actor_role: str = "",
    payload: Optional[Dict[str, Any]] = None,
    audit_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    audit = {
        "audit_id": _clean(audit_id) or f"approval_audit_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "action_id": _clean(action_id),
        "action_type": _clean(action_type),
        "decision": _clean(decision),
        "actor_role": _clean(actor_role),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_APPROVAL_AUDITS[audit["audit_id"]] = deepcopy(audit)
        return _safe_response(success=True, status="recorded", audit=deepcopy(audit), audit_id=audit["audit_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO approval_action_audit_records
                (audit_id, tenant_id, project_id, execution_id, action_id, action_type,
                 decision, actor_role, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING audit_id, tenant_id, project_id, execution_id, action_id,
                          action_type, decision, actor_role, payload_json, created_at
                """,
                (audit["audit_id"], audit["tenant_id"], audit["project_id"], audit["execution_id"] or None, audit["action_id"] or None, audit["action_type"] or None, audit["decision"] or None, audit["actor_role"] or None, _json(audit["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _approval_columns())
    return _safe_response(success=True, status="recorded", audit=item, audit_id=item["audit_id"], storage_mode="postgres", durable=True)


def get_execution_evidence_summary(tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    if not readiness.get("success"):
        return readiness
    history = list_execution_history(tenant_id=tenant_id, limit=200)
    events = list_execution_events(tenant_id=tenant_id, limit=200)
    evidence = list_execution_evidence(tenant_id=tenant_id, limit=200)
    return _safe_response(
        success=True,
        status="ready",
        execution_history_evidence_ready=True,
        storage_mode=readiness.get("storage_mode"),
        durable=readiness.get("durable", False),
        dev_only=readiness.get("dev_only", False),
        not_production_durable=readiness.get("not_production_durable", False),
        history_count=history.get("count", 0),
        event_count=events.get("count", 0),
        evidence_count=evidence.get("count", 0),
        history_records=history.get("records", [])[:20],
        execution_events=events.get("events", [])[:20],
        evidence_items=evidence.get("evidence_items", [])[:20],
    )


def reset_dev_execution_history_evidence_for_tests() -> Dict[str, Any]:
    _DEV_HISTORY.clear()
    _DEV_EVENTS.clear()
    _DEV_EVIDENCE.clear()
    _DEV_DELIVERABLES.clear()
    _DEV_APPROVAL_AUDITS.clear()
    return _safe_response(success=True, reset=True, status="dev_execution_history_evidence_reset", storage_mode="dev_memory", dev_only=True, not_production_durable=True)
