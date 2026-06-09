from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


DURABLE_QUEUE_PROFILE = "durable_execution_queue_runtime_v1"
TERMINAL_STATUSES = {"completed", "dead_letter"}
CLAIMABLE_STATUSES = {"queued", "retry_scheduled", "leased"}

_DEV_JOBS: Dict[str, Dict[str, Any]] = {}
_DEV_EVENTS: List[Dict[str, Any]] = []


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


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("queue_profile", DURABLE_QUEUE_PROFILE)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _durable_unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="durable_queue_unavailable",
        queue_ready=False,
        durable=False,
        storage_mode="postgres_unavailable",
        production_fail_closed=_is_production(),
        dev_only=False,
        reason=reason,
    )


def _psycopg():
    try:
        import psycopg  # type: ignore

        return psycopg
    except Exception:
        return None


def _postgres_ready() -> bool:
    return bool(_database_url()) and _psycopg() is not None


def _connect():
    psycopg = _psycopg()
    if psycopg is None:
        raise RuntimeError("psycopg_unavailable")
    if not _database_url():
        raise RuntimeError("DATABASE_URL_missing")
    try:
        connect_timeout = max(1, min(int(os.getenv("DURABLE_QUEUE_CONNECT_TIMEOUT_SECONDS", "3")), 10))
    except Exception:
        connect_timeout = 3
    try:
        statement_timeout_ms = max(1000, min(int(os.getenv("DURABLE_QUEUE_STATEMENT_TIMEOUT_MS", "3000")), 10000))
    except Exception:
        statement_timeout_ms = 3000
    return psycopg.connect(
        _database_url(),
        connect_timeout=connect_timeout,
        options=f"-c statement_timeout={statement_timeout_ms}",
    )


def _json_payload(payload: Optional[Dict[str, Any]]) -> str:
    safe_payload = deepcopy(payload or {})
    return json.dumps(safe_payload, ensure_ascii=False, sort_keys=True)


def _parse_payload(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _row_to_job(row: Any, columns: List[str]) -> Dict[str, Any]:
    data = dict(zip(columns, row))
    payload = _parse_payload(data.get("payload"))
    job = {
        **data,
        "payload": payload,
        "queue_id": data.get("job_id"),
        "attempt_count": int(data.get("attempt_count") or 0),
        "max_attempts": int(data.get("max_attempts") or 0),
        "credential_values_exposed": bool(data.get("credential_values_exposed", False)),
    }
    for key, value in list(job.items()):
        if isinstance(value, datetime):
            job[key] = value.isoformat()
    job["credential_values_exposed"] = False
    return job


def _select_columns() -> str:
    return """
        job_id, queue_name, tenant_id, project_id, agent_id, action_type,
        payload, status, idempotency_key, attempt_count, max_attempts,
        run_after, leased_by, lease_expires_at, heartbeat_at, created_at,
        updated_at, started_at, completed_at, failed_at, dead_lettered_at,
        last_error, credential_values_exposed
    """


def _columns() -> List[str]:
    return [
        "job_id",
        "queue_name",
        "tenant_id",
        "project_id",
        "agent_id",
        "action_type",
        "payload",
        "status",
        "idempotency_key",
        "attempt_count",
        "max_attempts",
        "run_after",
        "leased_by",
        "lease_expires_at",
        "heartbeat_at",
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "failed_at",
        "dead_lettered_at",
        "last_error",
        "credential_values_exposed",
    ]


def _select_columns_for_alias(alias: str) -> str:
    safe_alias = "".join(ch for ch in str(alias or "") if ch.isalnum() or ch == "_")
    if not safe_alias:
        return _select_columns()
    return ", ".join(f"{safe_alias}.{column}" for column in _columns())


def _record_dev_event(job_id: str, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    _DEV_EVENTS.append(
        {
            "event_id": f"dev_evt_{uuid.uuid4().hex[:16]}",
            "job_id": job_id,
            "event_type": event_type,
            "details": details or {},
            "created_at": _now_iso(),
            "credential_values_exposed": False,
        }
    )


def _record_postgres_event(conn: Any, job_id: str, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO durable_execution_queue_events
            (event_id, job_id, event_type, details)
            VALUES (%s, %s, %s, %s)
            """,
            (f"evt_{uuid.uuid4().hex[:20]}", job_id, event_type, _json_payload(details)),
        )


def ensure_execution_queue_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _durable_unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_queue_ready",
            queue_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
        )

    if _psycopg() is None:
        if _is_production():
            return _durable_unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_queue_ready",
            queue_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_driver_unavailable=True,
        )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS durable_execution_queue_jobs (
                        job_id TEXT PRIMARY KEY,
                        queue_name TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        agent_id TEXT,
                        action_type TEXT,
                        payload JSONB DEFAULT '{}'::jsonb,
                        status TEXT NOT NULL DEFAULT 'queued',
                        idempotency_key TEXT,
                        attempt_count INTEGER NOT NULL DEFAULT 0,
                        max_attempts INTEGER NOT NULL DEFAULT 3,
                        run_after TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        leased_by TEXT,
                        lease_expires_at TIMESTAMPTZ,
                        heartbeat_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        started_at TIMESTAMPTZ,
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        dead_lettered_at TIMESTAMPTZ,
                        last_error TEXT,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_durable_execution_queue_idempotency
                    ON durable_execution_queue_jobs (queue_name, idempotency_key)
                    WHERE idempotency_key IS NOT NULL AND idempotency_key <> ''
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_durable_execution_queue_claimable
                    ON durable_execution_queue_jobs (queue_name, status, run_after, lease_expires_at, created_at)
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_durable_execution_queue_tenant
                    ON durable_execution_queue_jobs (tenant_id, status, created_at)
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS durable_execution_queue_events (
                        event_id TEXT PRIMARY KEY,
                        job_id TEXT NOT NULL REFERENCES durable_execution_queue_jobs(job_id) ON DELETE CASCADE,
                        event_type TEXT NOT NULL,
                        details JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_durable_execution_queue_events_job
                    ON durable_execution_queue_events (job_id, created_at)
                    """
                )
            conn.commit()
    except Exception:
        if _is_production():
            return _durable_unavailable("postgres_connection_or_schema_initialisation_failed")
        return _safe_response(
            success=True,
            status="dev_only_queue_ready",
            queue_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_unavailable=True,
        )

    return _safe_response(
        success=True,
        status="durable_queue_ready",
        queue_ready=True,
        durable=True,
        storage_mode="postgres",
        dev_only=False,
        not_production_durable=False,
    )


def _dev_job_copy(job: Dict[str, Any]) -> Dict[str, Any]:
    copied = deepcopy(job)
    copied["queue_id"] = copied.get("job_id")
    copied["credential_values_exposed"] = False
    return copied


def _using_dev_fallback() -> bool:
    return not _postgres_ready() and not _is_production()


def enqueue_execution_job(
    *,
    queue_name: str = "execution_queue",
    tenant_id: str,
    project_id: str = "default_project",
    agent_id: str = "",
    action_type: str = "",
    payload: Optional[Dict[str, Any]] = None,
    idempotency_key: str = "",
    max_attempts: int = 3,
    run_after: Optional[datetime] = None,
) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    tenant_id = str(tenant_id or "").strip()
    if not tenant_id:
        return _safe_response(success=False, status="tenant_id_required", error="tenant_id_required")

    queue_name = str(queue_name or "execution_queue").strip()
    project_id = str(project_id or "default_project").strip()
    job_payload = deepcopy(payload or {})
    job_payload.setdefault("tenant_id", tenant_id)
    job_payload.setdefault("project_id", project_id)
    job_payload.setdefault("agent_id", agent_id)
    job_payload.setdefault("action_type", action_type)
    job_id = f"exec_job_{uuid.uuid4().hex}"
    run_after_value = run_after or _now()
    safe_max_attempts = max(1, min(int(max_attempts or 3), 25))

    if readiness.get("storage_mode") == "dev_memory":
        if idempotency_key:
            for existing in _DEV_JOBS.values():
                if existing.get("queue_name") == queue_name and existing.get("idempotency_key") == idempotency_key:
                    return _safe_response(
                        success=True,
                        status=existing.get("status"),
                        job=_dev_job_copy(existing),
                        job_id=existing.get("job_id"),
                        queue_id=existing.get("job_id"),
                        idempotent_replay=True,
                        storage_mode="dev_memory",
                        dev_only=True,
                        not_production_durable=True,
                    )

        job = {
            "job_id": job_id,
            "queue_name": queue_name,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "agent_id": str(agent_id or ""),
            "action_type": str(action_type or ""),
            "payload": job_payload,
            "status": "queued",
            "idempotency_key": idempotency_key or None,
            "attempt_count": 0,
            "max_attempts": safe_max_attempts,
            "run_after": run_after_value.isoformat(),
            "leased_by": None,
            "lease_expires_at": None,
            "heartbeat_at": None,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "started_at": None,
            "completed_at": None,
            "failed_at": None,
            "dead_lettered_at": None,
            "last_error": None,
            "credential_values_exposed": False,
        }
        _DEV_JOBS[job_id] = job
        _record_dev_event(job_id, "job_enqueued", {"queue_name": queue_name})
        return _safe_response(
            success=True,
            status="queued",
            job=_dev_job_copy(job),
            job_id=job_id,
            queue_id=job_id,
            idempotent_replay=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
        )

    with _connect() as conn:
        with conn.cursor() as cur:
            if idempotency_key:
                cur.execute(
                    f"""
                    SELECT {_select_columns()}
                    FROM durable_execution_queue_jobs
                    WHERE queue_name = %s AND idempotency_key = %s
                    """,
                    (queue_name, idempotency_key),
                )
                existing = cur.fetchone()
                if existing:
                    job = _row_to_job(existing, _columns())
                    return _safe_response(
                        success=True,
                        status=job.get("status"),
                        job=job,
                        job_id=job.get("job_id"),
                        queue_id=job.get("job_id"),
                        idempotent_replay=True,
                        storage_mode="postgres",
                        durable=True,
                    )

            cur.execute(
                """
                INSERT INTO durable_execution_queue_jobs
                (job_id, queue_name, tenant_id, project_id, agent_id, action_type,
                 payload, status, idempotency_key, max_attempts, run_after)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'queued', %s, %s, %s)
                RETURNING
                """
                + _select_columns(),
                (
                    job_id,
                    queue_name,
                    tenant_id,
                    project_id,
                    str(agent_id or ""),
                    str(action_type or ""),
                    _json_payload(job_payload),
                    idempotency_key or None,
                    safe_max_attempts,
                    run_after_value,
                ),
            )
            row = cur.fetchone()
            _record_postgres_event(conn, job_id, "job_enqueued", {"queue_name": queue_name})
        conn.commit()

    job = _row_to_job(row, _columns())
    return _safe_response(
        success=True,
        status="queued",
        job=job,
        job_id=job_id,
        queue_id=job_id,
        idempotent_replay=False,
        storage_mode="postgres",
        durable=True,
    )


def release_expired_execution_leases(queue_name: str = "", now: Optional[datetime] = None) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    now_value = now or _now()
    if readiness.get("storage_mode") == "dev_memory":
        released = 0
        for job in _DEV_JOBS.values():
            if queue_name and job.get("queue_name") != queue_name:
                continue
            expires_raw = job.get("lease_expires_at")
            if job.get("status") == "leased" and expires_raw and datetime.fromisoformat(str(expires_raw)) <= now_value:
                job["status"] = "retry_scheduled"
                job["leased_by"] = None
                job["lease_expires_at"] = None
                job["updated_at"] = _now_iso()
                released += 1
                _record_dev_event(str(job["job_id"]), "lease_expired")
        return _safe_response(success=True, released_count=released, storage_mode="dev_memory", dev_only=True)

    params: List[Any] = [now_value]
    queue_filter = ""
    if queue_name:
        queue_filter = "AND queue_name = %s"
        params.append(queue_name)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE durable_execution_queue_jobs
                SET status = 'retry_scheduled',
                    leased_by = NULL,
                    lease_expires_at = NULL,
                    updated_at = NOW()
                WHERE status = 'leased'
                  AND lease_expires_at IS NOT NULL
                  AND lease_expires_at <= %s
                  {queue_filter}
                RETURNING job_id
                """,
                params,
            )
            released = [row[0] for row in cur.fetchall()]
            for job_id in released:
                _record_postgres_event(conn, job_id, "lease_expired")
        conn.commit()

    return _safe_response(success=True, released_count=len(released), released_job_ids=released, storage_mode="postgres", durable=True)


def claim_next_execution_job(
    *,
    queue_name: str = "execution_queue",
    worker_id: str = "",
    lease_seconds: int = 300,
) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    queue_name = str(queue_name or "execution_queue").strip()
    worker_id = str(worker_id or f"worker_{uuid.uuid4().hex[:12]}")
    safe_lease_seconds = max(30, min(int(lease_seconds or 300), 3600))
    now_value = _now()
    lease_expires = now_value + timedelta(seconds=safe_lease_seconds)

    release_expired_execution_leases(queue_name=queue_name, now=now_value)

    if readiness.get("storage_mode") == "dev_memory":
        claimable = [
            job
            for job in _DEV_JOBS.values()
            if job.get("queue_name") == queue_name
            and job.get("status") in {"queued", "retry_scheduled"}
            and datetime.fromisoformat(str(job.get("run_after"))) <= now_value
        ]
        claimable.sort(key=lambda job: (str(job.get("run_after")), str(job.get("created_at"))))
        if not claimable:
            return _safe_response(success=True, status="empty", job=None, storage_mode="dev_memory", dev_only=True)
        job = claimable[0]
        job["status"] = "leased"
        job["leased_by"] = worker_id
        job["lease_expires_at"] = lease_expires.isoformat()
        job["heartbeat_at"] = now_value.isoformat()
        job["started_at"] = job.get("started_at") or now_value.isoformat()
        job["updated_at"] = now_value.isoformat()
        _record_dev_event(str(job["job_id"]), "job_claimed", {"worker_id": worker_id})
        return _safe_response(success=True, status="leased", job=_dev_job_copy(job), job_id=job["job_id"], queue_id=job["job_id"], storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                WITH candidate AS (
                    SELECT job_id
                    FROM durable_execution_queue_jobs
                    WHERE queue_name = %s
                      AND status IN ('queued', 'retry_scheduled')
                      AND run_after <= NOW()
                    ORDER BY run_after ASC, created_at ASC
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                )
                UPDATE durable_execution_queue_jobs job
                SET status = 'leased',
                    leased_by = %s,
                    lease_expires_at = %s,
                    heartbeat_at = NOW(),
                    started_at = COALESCE(started_at, NOW()),
                    updated_at = NOW()
                FROM candidate
                WHERE job.job_id = candidate.job_id
                RETURNING {_select_columns_for_alias("job")}
                """,
                (queue_name, worker_id, lease_expires),
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return _safe_response(success=True, status="empty", job=None, storage_mode="postgres", durable=True)
            job = _row_to_job(row, _columns())
            _record_postgres_event(conn, str(job["job_id"]), "job_claimed", {"worker_id": worker_id})
        conn.commit()

    return _safe_response(success=True, status="leased", job=job, job_id=job["job_id"], queue_id=job["job_id"], storage_mode="postgres", durable=True)


def heartbeat_execution_job(job_id: str, worker_id: str = "", lease_seconds: int = 300) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    safe_lease_seconds = max(30, min(int(lease_seconds or 300), 3600))
    lease_expires = _now() + timedelta(seconds=safe_lease_seconds)
    worker_id = str(worker_id or "")

    if readiness.get("storage_mode") == "dev_memory":
        job = _DEV_JOBS.get(str(job_id))
        if not job:
            return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="dev_memory", dev_only=True)
        if worker_id and job.get("leased_by") != worker_id:
            return _safe_response(success=False, status="worker_lease_mismatch", error="worker_lease_mismatch", storage_mode="dev_memory", dev_only=True)
        job["heartbeat_at"] = _now_iso()
        job["lease_expires_at"] = lease_expires.isoformat()
        job["updated_at"] = _now_iso()
        _record_dev_event(str(job_id), "job_heartbeat", {"worker_id": worker_id})
        return _safe_response(success=True, status="heartbeat_recorded", job=_dev_job_copy(job), storage_mode="dev_memory", dev_only=True)

    params: List[Any] = [lease_expires, job_id]
    worker_filter = ""
    if worker_id:
        worker_filter = "AND leased_by = %s"
        params.append(worker_id)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE durable_execution_queue_jobs
                SET heartbeat_at = NOW(),
                    lease_expires_at = %s,
                    updated_at = NOW()
                WHERE job_id = %s
                  AND status = 'leased'
                  {worker_filter}
                RETURNING {_select_columns()}
                """,
                params,
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return _safe_response(success=False, status="job_not_found_or_not_leased", error="job_not_found_or_not_leased", storage_mode="postgres", durable=True)
            job = _row_to_job(row, _columns())
            _record_postgres_event(conn, str(job_id), "job_heartbeat", {"worker_id": worker_id})
        conn.commit()

    return _safe_response(success=True, status="heartbeat_recorded", job=job, storage_mode="postgres", durable=True)


def complete_execution_job(job_id: str, worker_id: str = "", result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    worker_id = str(worker_id or "")
    if readiness.get("storage_mode") == "dev_memory":
        job = _DEV_JOBS.get(str(job_id))
        if not job:
            return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="dev_memory", dev_only=True)
        if worker_id and job.get("leased_by") != worker_id:
            return _safe_response(success=False, status="worker_lease_mismatch", error="worker_lease_mismatch", storage_mode="dev_memory", dev_only=True)
        job["status"] = "completed"
        job["completed_at"] = _now_iso()
        job["lease_expires_at"] = None
        job["leased_by"] = None
        job["updated_at"] = _now_iso()
        _record_dev_event(str(job_id), "job_completed", result or {})
        return _safe_response(success=True, status="completed", job=_dev_job_copy(job), storage_mode="dev_memory", dev_only=True)

    params: List[Any] = [job_id]
    worker_filter = ""
    if worker_id:
        worker_filter = "AND leased_by = %s"
        params.append(worker_id)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE durable_execution_queue_jobs
                SET status = 'completed',
                    completed_at = NOW(),
                    leased_by = NULL,
                    lease_expires_at = NULL,
                    updated_at = NOW()
                WHERE job_id = %s
                  AND status = 'leased'
                  {worker_filter}
                RETURNING {_select_columns()}
                """,
                params,
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return _safe_response(success=False, status="job_not_found_or_not_leased", error="job_not_found_or_not_leased", storage_mode="postgres", durable=True)
            job = _row_to_job(row, _columns())
            _record_postgres_event(conn, str(job_id), "job_completed", result or {})
        conn.commit()

    return _safe_response(success=True, status="completed", job=job, storage_mode="postgres", durable=True)


def dead_letter_execution_job(job_id: str, error: str = "", worker_id: str = "") -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    if readiness.get("storage_mode") == "dev_memory":
        job = _DEV_JOBS.get(str(job_id))
        if not job:
            return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="dev_memory", dev_only=True)
        job["status"] = "dead_letter"
        job["failed_at"] = _now_iso()
        job["dead_lettered_at"] = _now_iso()
        job["last_error"] = str(error or "dead_lettered")
        job["leased_by"] = None
        job["lease_expires_at"] = None
        job["updated_at"] = _now_iso()
        _record_dev_event(str(job_id), "job_dead_lettered", {"error": str(error or "")[:1000], "worker_id": worker_id})
        return _safe_response(success=True, status="dead_letter", job=_dev_job_copy(job), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE durable_execution_queue_jobs
                SET status = 'dead_letter',
                    failed_at = NOW(),
                    dead_lettered_at = NOW(),
                    last_error = %s,
                    leased_by = NULL,
                    lease_expires_at = NULL,
                    updated_at = NOW()
                WHERE job_id = %s
                RETURNING {_select_columns()}
                """,
                (str(error or "dead_lettered")[:2000], job_id),
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="postgres", durable=True)
            job = _row_to_job(row, _columns())
            _record_postgres_event(conn, str(job_id), "job_dead_lettered", {"error": str(error or "")[:1000], "worker_id": worker_id})
        conn.commit()

    return _safe_response(success=True, status="dead_letter", job=job, storage_mode="postgres", durable=True)


def retry_execution_job(
    job_id: str,
    error: str = "",
    worker_id: str = "",
    retry_delay_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    delay = retry_delay_seconds
    if delay is None:
        delay = 60
    delay = max(0, min(int(delay), 86400))
    run_after = _now() + timedelta(seconds=delay)
    worker_id = str(worker_id or "")

    if readiness.get("storage_mode") == "dev_memory":
        job = _DEV_JOBS.get(str(job_id))
        if not job:
            return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="dev_memory", dev_only=True)
        next_attempt = int(job.get("attempt_count") or 0) + 1
        job["attempt_count"] = next_attempt
        if next_attempt >= int(job.get("max_attempts") or 1):
            return dead_letter_execution_job(job_id, error=error, worker_id=worker_id)
        job["status"] = "retry_scheduled"
        job["failed_at"] = _now_iso()
        job["last_error"] = str(error or "retry_scheduled")[:2000]
        job["run_after"] = run_after.isoformat()
        job["leased_by"] = None
        job["lease_expires_at"] = None
        job["updated_at"] = _now_iso()
        _record_dev_event(str(job_id), "job_retry_scheduled", {"error": str(error or "")[:1000], "worker_id": worker_id})
        return _safe_response(success=True, status="retry_scheduled", job=_dev_job_copy(job), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT attempt_count, max_attempts
                FROM durable_execution_queue_jobs
                WHERE job_id = %s
                FOR UPDATE
                """,
                (job_id,),
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return _safe_response(success=False, status="job_not_found", error="job_not_found", storage_mode="postgres", durable=True)
            next_attempt = int(row[0] or 0) + 1
            max_attempts = int(row[1] or 1)
            if next_attempt >= max_attempts:
                conn.commit()
                return dead_letter_execution_job(job_id, error=error, worker_id=worker_id)

            cur.execute(
                f"""
                UPDATE durable_execution_queue_jobs
                SET status = 'retry_scheduled',
                    attempt_count = %s,
                    failed_at = NOW(),
                    last_error = %s,
                    run_after = %s,
                    leased_by = NULL,
                    lease_expires_at = NULL,
                    updated_at = NOW()
                WHERE job_id = %s
                RETURNING {_select_columns()}
                """,
                (next_attempt, str(error or "retry_scheduled")[:2000], run_after, job_id),
            )
            updated = cur.fetchone()
            job = _row_to_job(updated, _columns())
            _record_postgres_event(conn, str(job_id), "job_retry_scheduled", {"error": str(error or "")[:1000], "worker_id": worker_id})
        conn.commit()

    return _safe_response(success=True, status="retry_scheduled", job=job, storage_mode="postgres", durable=True)


def fail_execution_job(
    job_id: str,
    error: str = "",
    worker_id: str = "",
    retry_delay_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    return retry_execution_job(
        job_id=job_id,
        error=error,
        worker_id=worker_id,
        retry_delay_seconds=retry_delay_seconds,
    )


def list_execution_jobs(
    *,
    queue_name: str = "",
    tenant_id: str = "",
    status: str = "",
    limit: int = 50,
) -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    safe_limit = max(1, min(int(limit or 50), 500))
    if readiness.get("storage_mode") == "dev_memory":
        jobs = list(_DEV_JOBS.values())
        if queue_name:
            jobs = [job for job in jobs if job.get("queue_name") == queue_name]
        if tenant_id:
            jobs = [job for job in jobs if job.get("tenant_id") == tenant_id]
        if status:
            jobs = [job for job in jobs if job.get("status") == status]
        jobs = sorted(jobs, key=lambda job: str(job.get("created_at")), reverse=True)[:safe_limit]
        items = [_dev_job_copy(job) for job in jobs]
        return _safe_response(success=True, status="ok", count=len(items), items=items, jobs=items, storage_mode="dev_memory", dev_only=True, not_production_durable=True)

    clauses = []
    params: List[Any] = []
    if queue_name:
        clauses.append("queue_name = %s")
        params.append(queue_name)
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if status:
        clauses.append("status = %s")
        params.append(status)
    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT {_select_columns()}
                FROM durable_execution_queue_jobs
                {where_sql}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()

    jobs = [_row_to_job(row, _columns()) for row in rows]
    return _safe_response(success=True, status="ok", count=len(jobs), items=jobs, jobs=jobs, storage_mode="postgres", durable=True)


def get_execution_queue_status(queue_name: str = "") -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    if readiness.get("storage_mode") == "dev_memory":
        jobs = list(_DEV_JOBS.values())
        if queue_name:
            jobs = [job for job in jobs if job.get("queue_name") == queue_name]
        counts: Dict[str, int] = {}
        for job in jobs:
            counts[str(job.get("status"))] = counts.get(str(job.get("status")), 0) + 1
        return _safe_response(
            success=True,
            status="dev_only_queue_ready",
            queue_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
            queue_name=queue_name or "all",
            counts=counts,
            total_jobs=len(jobs),
            atomic_claiming=False,
            lease_expiry_enabled=True,
            retry_scheduling_enabled=True,
            dead_letter_enabled=True,
            idempotency_keys_enabled=True,
        )

    params: List[Any] = []
    queue_filter = ""
    if queue_name:
        queue_filter = "WHERE queue_name = %s"
        params.append(queue_name)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT status, COUNT(*)
                FROM durable_execution_queue_jobs
                {queue_filter}
                GROUP BY status
                """,
                params,
            )
            counts = {str(row[0]): int(row[1]) for row in cur.fetchall()}

    return _safe_response(
        success=True,
        status="durable_queue_ready",
        queue_ready=True,
        durable=True,
        storage_mode="postgres",
        dev_only=False,
        queue_name=queue_name or "all",
        counts=counts,
        total_jobs=sum(counts.values()),
        atomic_claiming=True,
        atomic_claiming_strategy="postgres_for_update_skip_locked",
        lease_expiry_enabled=True,
        worker_heartbeat_enabled=True,
        retry_scheduling_enabled=True,
        dead_letter_enabled=True,
        idempotency_keys_enabled=True,
        production_fail_closed_if_unavailable=True,
    )


def get_latest_execution_job_event(job_id: str, event_type: str = "job_completed") -> Dict[str, Any]:
    readiness = ensure_execution_queue_tables()
    if not readiness.get("success"):
        return readiness

    job_id = str(job_id or "").strip()
    event_type = str(event_type or "").strip() or "job_completed"
    if not job_id:
        return _safe_response(success=False, status="job_id_required", event=None)

    if readiness.get("storage_mode") == "dev_memory":
        events = [
            event
            for event in _DEV_EVENTS
            if event.get("job_id") == job_id and event.get("event_type") == event_type
        ]
        event = events[-1] if events else None
        return _safe_response(
            success=True,
            status="ok" if event else "empty",
            event=deepcopy(event) if event else None,
            details=deepcopy(event.get("details")) if event else {},
            storage_mode="dev_memory",
            dev_only=True,
        )

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id, job_id, event_type, details, created_at, credential_values_exposed
                FROM durable_execution_queue_events
                WHERE job_id = %s AND event_type = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (job_id, event_type),
            )
            row = cur.fetchone()

    if not row:
        return _safe_response(success=True, status="empty", event=None, details={}, storage_mode="postgres", durable=True)

    details = _parse_payload(row[3])
    event = {
        "event_id": row[0],
        "job_id": row[1],
        "event_type": row[2],
        "details": details,
        "created_at": row[4].isoformat() if isinstance(row[4], datetime) else row[4],
        "credential_values_exposed": False,
    }
    return _safe_response(success=True, status="ok", event=event, details=details, storage_mode="postgres", durable=True)


def reset_dev_execution_queue_for_tests() -> Dict[str, Any]:
    _DEV_JOBS.clear()
    _DEV_EVENTS.clear()
    return _safe_response(success=True, status="dev_queue_reset", storage_mode="dev_memory", dev_only=True)
