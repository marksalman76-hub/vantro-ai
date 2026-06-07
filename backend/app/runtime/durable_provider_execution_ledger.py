from __future__ import annotations

import hashlib
import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


DURABLE_PROVIDER_LEDGER_PROFILE = "durable_provider_execution_ledger_v1"

_DEV_EXECUTIONS: Dict[str, Dict[str, Any]] = {}
_DEV_JOBS: Dict[str, Dict[str, Any]] = {}
_DEV_JOB_EVENTS: List[Dict[str, Any]] = []
_DEV_DISPATCH_ATTEMPTS: List[Dict[str, Any]] = []
_DEV_RETRIES: List[Dict[str, Any]] = []
_DEV_POLLING: Dict[str, Dict[str, Any]] = {}
_DEV_RESULTS: List[Dict[str, Any]] = []
_DEV_DELIVERY_PACKETS: Dict[str, Dict[str, Any]] = {}
_DEV_LATENCY: List[Dict[str, Any]] = []


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
    timeout = max(1, min(int(os.getenv("PROVIDER_LEDGER_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("ledger_profile", DURABLE_PROVIDER_LEDGER_PROFILE)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="provider_ledger_unavailable",
        provider_ledger_ready=False,
        durable=False,
        storage_mode="postgres_unavailable",
        production_fail_closed=_is_production(),
        dev_only=False,
        reason=reason,
    )


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(deepcopy(data or {}), ensure_ascii=False, sort_keys=True)


def _parse_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _dt(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _hash_request(payload: Optional[Dict[str, Any]]) -> str:
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()[:32]


def _default_idempotency_key(
    *,
    tenant_id: str,
    provider: str,
    action_type: str = "",
    capability: str = "",
    request_hash: str = "",
) -> str:
    base = "|".join([tenant_id, provider, action_type or capability, request_hash])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:40]


def _using_dev(readiness: Dict[str, Any]) -> bool:
    return readiness.get("storage_mode") == "dev_memory"


def _limit(value: int, default: int = 100, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


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


def _execution_columns() -> List[str]:
    return [
        "execution_id",
        "tenant_id",
        "project_id",
        "agent_id",
        "provider",
        "capability",
        "action_type",
        "status",
        "request_hash",
        "idempotency_key",
        "created_at",
        "updated_at",
        "credential_values_exposed",
        "request_id",
        "provider_key",
        "task_type",
        "execution_status",
        "worker_job_id",
        "provider_job_id",
        "extra_json",
        "live_external_call_executed",
        "customer_safe",
        "created_at_ms",
        "updated_at_ms",
    ]


def _execution_select() -> str:
    return ", ".join(_execution_columns())


def _job_columns() -> List[str]:
    return [
        "provider_job_id",
        "execution_id",
        "provider",
        "provider_external_job_id",
        "tenant_id",
        "project_id",
        "status",
        "polling_status",
        "attempt_count",
        "max_attempts",
        "next_poll_at",
        "next_retry_at",
        "last_error",
        "created_at",
        "updated_at",
        "completed_at",
        "failed_at",
        "credential_values_exposed",
    ]


def _job_select() -> str:
    return ", ".join(_job_columns())


def _row(row: Any, columns: List[str]) -> Dict[str, Any]:
    result = dict(zip(columns, row))
    for key, value in list(result.items()):
        if key.endswith("_json"):
            result[key] = _parse_json(value)
        else:
            result[key] = _dt(value)
    if "extra_json" in result:
        result["extra"] = result.get("extra_json") or {}
    result["credential_values_exposed"] = False
    return result


def ensure_provider_ledger_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_provider_ledger_ready",
            provider_ledger_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
        )

    if _psycopg() is None:
        if _is_production():
            return _unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_provider_ledger_ready",
            provider_ledger_ready=True,
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
                    CREATE TABLE IF NOT EXISTS provider_execution_records (
                        execution_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        agent_id TEXT,
                        provider TEXT NOT NULL,
                        capability TEXT,
                        action_type TEXT,
                        status TEXT NOT NULL,
                        request_hash TEXT,
                        idempotency_key TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                for statement in [
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS project_id TEXT NOT NULL DEFAULT 'default_project'",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS request_id TEXT NOT NULL DEFAULT 'unknown_request'",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS provider_key TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS task_type TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS execution_status TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS agent_id TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS provider TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS capability TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS action_type TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS status TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS request_hash TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS idempotency_key TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS worker_job_id TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS provider_job_id TEXT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS extra_json JSONB DEFAULT '{}'::jsonb",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS live_external_call_executed BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS customer_safe BOOLEAN DEFAULT TRUE",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS created_at_ms BIGINT",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS updated_at_ms BIGINT",
                    "ALTER TABLE provider_execution_records ALTER COLUMN created_at_ms SET DEFAULT ((EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT)",
                    "ALTER TABLE provider_execution_records ALTER COLUMN updated_at_ms SET DEFAULT ((EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT)",
                    "UPDATE provider_execution_records SET created_at_ms = COALESCE(created_at_ms, (EXTRACT(EPOCH FROM created_at) * 1000)::BIGINT)",
                    "UPDATE provider_execution_records SET updated_at_ms = COALESCE(updated_at_ms, (EXTRACT(EPOCH FROM updated_at) * 1000)::BIGINT)",
                    "ALTER TABLE provider_execution_records ADD COLUMN IF NOT EXISTS credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE",
                    "UPDATE provider_execution_records SET provider = COALESCE(provider, provider_key) WHERE provider IS NULL",
                    "UPDATE provider_execution_records SET provider_key = COALESCE(provider_key, provider) WHERE provider_key IS NULL",
                    "UPDATE provider_execution_records SET status = COALESCE(status, execution_status, 'created') WHERE status IS NULL",
                    "UPDATE provider_execution_records SET execution_status = COALESCE(execution_status, status) WHERE execution_status IS NULL",
                ]:
                    cur.execute(statement)
                cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_provider_execution_idempotency
                    ON provider_execution_records (tenant_id, provider, idempotency_key)
                    WHERE idempotency_key IS NOT NULL AND idempotency_key <> ''
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_execution_records_tenant_id ON provider_execution_records (tenant_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_execution_records_provider ON provider_execution_records (provider)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_jobs (
                        provider_job_id TEXT PRIMARY KEY,
                        execution_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        provider_external_job_id TEXT,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        status TEXT NOT NULL,
                        polling_status TEXT,
                        attempt_count INTEGER NOT NULL DEFAULT 0,
                        max_attempts INTEGER NOT NULL DEFAULT 3,
                        next_poll_at TIMESTAMPTZ,
                        next_retry_at TIMESTAMPTZ,
                        last_error TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_jobs_execution ON provider_jobs (execution_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_jobs_tenant_status ON provider_jobs (tenant_id, status, created_at)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_job_events (
                        event_id TEXT PRIMARY KEY,
                        provider_job_id TEXT,
                        execution_id TEXT,
                        event_type TEXT NOT NULL,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_job_events_execution ON provider_job_events (execution_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_dispatch_attempts (
                        dispatch_attempt_id TEXT PRIMARY KEY,
                        execution_id TEXT NOT NULL,
                        provider_job_id TEXT,
                        provider TEXT NOT NULL,
                        status TEXT NOT NULL,
                        idempotency_key TEXT,
                        latency_ms INTEGER DEFAULT 0,
                        error TEXT,
                        attempt_number INTEGER,
                        allowed_by_policy BOOLEAN,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                for statement in [
                    "ALTER TABLE provider_dispatch_attempts ADD COLUMN IF NOT EXISTS attempt_number INTEGER",
                    "ALTER TABLE provider_dispatch_attempts ADD COLUMN IF NOT EXISTS allowed_by_policy BOOLEAN",
                    "ALTER TABLE provider_dispatch_attempts ADD COLUMN IF NOT EXISTS credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE",
                ]:
                    cur.execute(statement)
                cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_provider_dispatch_idempotency
                    ON provider_dispatch_attempts (provider, idempotency_key)
                    WHERE idempotency_key IS NOT NULL AND idempotency_key <> ''
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_dispatch_attempts_execution ON provider_dispatch_attempts (execution_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_retry_history (
                        retry_id TEXT PRIMARY KEY,
                        provider_job_id TEXT,
                        execution_id TEXT NOT NULL,
                        retry_reason TEXT NOT NULL,
                        attempt_number INTEGER NOT NULL,
                        scheduled_for TIMESTAMPTZ,
                        retry_allowed BOOLEAN,
                        next_action TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                for statement in [
                    "ALTER TABLE provider_retry_history ADD COLUMN IF NOT EXISTS retry_allowed BOOLEAN",
                    "ALTER TABLE provider_retry_history ADD COLUMN IF NOT EXISTS next_action TEXT",
                    "ALTER TABLE provider_retry_history ADD COLUMN IF NOT EXISTS credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE",
                ]:
                    cur.execute(statement)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_retry_history_execution ON provider_retry_history (execution_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_polling_state (
                        provider_job_id TEXT PRIMARY KEY,
                        execution_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        polling_status TEXT NOT NULL,
                        next_poll_at TIMESTAMPTZ,
                        last_poll_at TIMESTAMPTZ,
                        provider_status TEXT,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_result_records (
                        result_id TEXT PRIMARY KEY,
                        provider_job_id TEXT,
                        execution_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        result_status TEXT NOT NULL,
                        result_summary TEXT,
                        asset_id TEXT,
                        asset_url TEXT,
                        metadata_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_delivery_packets (
                        delivery_packet_id TEXT PRIMARY KEY,
                        provider_job_id TEXT,
                        execution_id TEXT NOT NULL,
                        asset_id TEXT,
                        delivery_status TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS provider_latency_metrics (
                        metric_id TEXT PRIMARY KEY,
                        tenant_id TEXT,
                        request_id TEXT,
                        execution_id TEXT,
                        provider TEXT NOT NULL,
                        capability TEXT,
                        latency_ms INTEGER NOT NULL,
                        status TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                for statement in [
                    "ALTER TABLE provider_latency_metrics ADD COLUMN IF NOT EXISTS tenant_id TEXT",
                    "ALTER TABLE provider_latency_metrics ADD COLUMN IF NOT EXISTS request_id TEXT",
                    "ALTER TABLE provider_latency_metrics ADD COLUMN IF NOT EXISTS execution_id TEXT",
                    "ALTER TABLE provider_latency_metrics ADD COLUMN IF NOT EXISTS credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE",
                ]:
                    cur.execute(statement)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_provider_latency_metrics_tenant_provider ON provider_latency_metrics (tenant_id, provider)")
            conn.commit()
    except Exception:
        if _is_production():
            return _unavailable("postgres_connection_or_schema_initialisation_failed")
        return _safe_response(
            success=True,
            status="dev_only_provider_ledger_ready",
            provider_ledger_ready=True,
            durable=False,
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_unavailable=True,
        )

    return _safe_response(
        success=True,
        status="durable_provider_ledger_ready",
        provider_ledger_ready=True,
        durable=True,
        storage_mode="postgres",
        dev_only=False,
        not_production_durable=False,
    )


def create_provider_execution_record(
    *,
    tenant_id: str,
    provider: str = "",
    provider_key: str = "",
    project_id: str = "default_project",
    agent_id: str = "",
    capability: str = "",
    action_type: str = "",
    status: str = "created",
    execution_status: str = "",
    request_payload: Optional[Dict[str, Any]] = None,
    request_hash: str = "",
    idempotency_key: str = "",
    execution_id: str = "",
    worker_job_id: str = "",
    provider_job_id: str = "",
    extra: Optional[Dict[str, Any]] = None,
    **_: Any,
) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness

    provider_name = str(provider or provider_key or "unknown").strip().lower()
    tenant = str(tenant_id or "").strip()
    if not tenant:
        return _safe_response(success=False, status="tenant_id_required", error="tenant_id_required")

    req_hash = request_hash or _hash_request(request_payload or {})
    request_id = str((request_payload or {}).get("request_id") or f"request_{req_hash[:12]}")
    idem = idempotency_key or _default_idempotency_key(
        tenant_id=tenant,
        provider=provider_name,
        action_type=action_type,
        capability=capability,
        request_hash=req_hash,
    )
    clean_status = str(execution_status or status or "created").strip()

    if _using_dev(readiness):
        for record in _DEV_EXECUTIONS.values():
            if record.get("tenant_id") == tenant and record.get("provider") == provider_name and record.get("idempotency_key") == idem:
                return _safe_response(success=True, status=record["status"], record=deepcopy(record), execution=deepcopy(record), execution_id=record["execution_id"], idempotent_replay=True, storage_mode="dev_memory", dev_only=True, not_production_durable=True)
        record_id = execution_id or f"provider_execution_{uuid.uuid4().hex[:16]}"
        now = _now()
        record = {
            "execution_id": record_id,
            "tenant_id": tenant,
            "project_id": str(project_id or "default_project"),
            "agent_id": str(agent_id or ""),
            "provider": provider_name,
            "provider_key": provider_name,
            "capability": str(capability or ""),
            "action_type": str(action_type or ""),
            "status": clean_status,
            "execution_status": clean_status,
            "request_hash": req_hash,
            "idempotency_key": idem,
            "request_id": request_id,
            "task_type": str(capability or action_type or "provider_execution"),
            "worker_job_id": str(worker_job_id or ""),
            "provider_job_id": str(provider_job_id or ""),
            "extra": _scrub_sensitive(extra),
            "extra_json": _scrub_sensitive(extra),
            "live_external_call_executed": False,
            "customer_safe": True,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "created_at_ms": int(now.timestamp() * 1000),
            "updated_at_ms": int(now.timestamp() * 1000),
            "credential_values_exposed": False,
        }
        _DEV_EXECUTIONS[record_id] = record
        return _safe_response(success=True, status=clean_status, record=deepcopy(record), execution=deepcopy(record), execution_id=record_id, idempotent_replay=False, storage_mode="dev_memory", dev_only=True, not_production_durable=True)

    now_ms = int(_now().timestamp() * 1000)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {_execution_select()} FROM provider_execution_records WHERE tenant_id = %s AND provider = %s AND idempotency_key = %s",
                (tenant, provider_name, idem),
            )
            existing = cur.fetchone()
            if existing:
                record = _row(existing, _execution_columns())
                return _safe_response(success=True, status=record["status"], record=record, execution=record, execution_id=record["execution_id"], idempotent_replay=True, storage_mode="postgres", durable=True)
            record_id = execution_id or f"provider_execution_{uuid.uuid4().hex[:16]}"
            cur.execute(
                f"""
                INSERT INTO provider_execution_records
                (execution_id, tenant_id, project_id, agent_id, provider, capability,
                 action_type, status, request_hash, idempotency_key, request_id,
                 provider_key, task_type, execution_status, worker_job_id, provider_job_id,
                 extra_json, live_external_call_executed, customer_safe,
                 credential_values_exposed, created_at_ms, updated_at_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING {_execution_select()}
                """,
                (
                    record_id,
                    tenant,
                    str(project_id or "default_project"),
                    str(agent_id or ""),
                    provider_name,
                    str(capability or ""),
                    str(action_type or ""),
                    clean_status,
                    req_hash,
                    idem,
                    request_id,
                    provider_name,
                    str(capability or action_type or "provider_execution"),
                    clean_status,
                    str(worker_job_id or ""),
                    str(provider_job_id or ""),
                    _json(_scrub_sensitive(extra)),
                    False,
                    True,
                    False,
                    now_ms,
                    now_ms,
                ),
            )
            record = _row(cur.fetchone(), _execution_columns())
        conn.commit()

    return _safe_response(success=True, status=clean_status, record=record, execution=record, execution_id=record["execution_id"], idempotent_replay=False, storage_mode="postgres", durable=True)


def update_provider_execution_status(execution_id: str, status: str, **kwargs: Any) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    clean_status = str(status or "updated")
    worker_job_id = kwargs.get("worker_job_id")
    provider_job_id = kwargs.get("provider_job_id")
    extra = kwargs.get("extra")
    has_extra = extra is not None
    if _using_dev(readiness):
        record = _DEV_EXECUTIONS.get(str(execution_id))
        if not record:
            return _safe_response(success=False, status="not_found", execution_id=execution_id, storage_mode="dev_memory", dev_only=True)
        record["status"] = clean_status
        record["execution_status"] = clean_status
        if worker_job_id is not None:
            record["worker_job_id"] = worker_job_id
        if provider_job_id is not None:
            record["provider_job_id"] = provider_job_id
        if has_extra:
            record["extra"] = _scrub_sensitive(extra)
            record["extra_json"] = _scrub_sensitive(extra)
        now = _now()
        record["updated_at"] = now.isoformat()
        record["updated_at_ms"] = int(now.timestamp() * 1000)
        return _safe_response(success=True, status=clean_status, record=deepcopy(record), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE provider_execution_records
                SET status = %s,
                    execution_status = %s,
                    worker_job_id = COALESCE(%s, worker_job_id),
                    provider_job_id = COALESCE(%s, provider_job_id),
                    extra_json = CASE WHEN %s THEN %s ELSE extra_json END,
                    updated_at_ms = (EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT,
                    updated_at = NOW()
                WHERE execution_id = %s
                RETURNING {_execution_select()}
                """,
                (
                    clean_status,
                    clean_status,
                    worker_job_id,
                    provider_job_id,
                    has_extra,
                    _json(_scrub_sensitive(extra)),
                    execution_id,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="not_found", execution_id=execution_id, storage_mode="postgres", durable=True)
    return _safe_response(success=True, status=clean_status, record=_row(row, _execution_columns()), storage_mode="postgres", durable=True)


def get_provider_execution_record(execution_id: str) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    key = str(execution_id or "")
    if _using_dev(readiness):
        record = _DEV_EXECUTIONS.get(key)
        if not record:
            return _safe_response(success=False, status="not_found", execution_id=key, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", record=deepcopy(record), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_execution_select()} FROM provider_execution_records WHERE execution_id = %s", (key,))
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="not_found", execution_id=key, storage_mode="postgres", durable=True)
    return _safe_response(success=True, status="found", record=_row(row, _execution_columns()), storage_mode="postgres", durable=True)


def list_provider_execution_records(tenant_id: str = "", provider: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    clean_provider = str(provider or "").strip().lower()
    if _using_dev(readiness):
        records = list(_DEV_EXECUTIONS.values())
        if tenant_id:
            records = [record for record in records if record.get("tenant_id") == tenant_id]
        if clean_provider:
            records = [record for record in records if record.get("provider") == clean_provider or record.get("provider_key") == clean_provider]
        records = sorted(records, key=lambda record: str(record.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(
            success=True,
            status="listed",
            records=deepcopy(records),
            count=len(records),
            storage_mode="dev_memory",
            dev_only=True,
            not_production_durable=True,
        )
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if clean_provider:
        clauses.append("provider = %s")
        params.append(clean_provider)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_execution_select()} FROM provider_execution_records {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    records = [_row(row, _execution_columns()) for row in rows]
    return _safe_response(success=True, status="listed", records=records, count=len(records), storage_mode="postgres", durable=True)


def create_provider_job(
    payload: Optional[Dict[str, Any]] = None,
    *,
    execution_id: str = "",
    provider: str = "",
    provider_key: str = "",
    tenant_id: str = "",
    project_id: str = "default_project",
    status: str = "queued",
    max_attempts: int = 3,
    provider_job_id: str = "",
    provider_external_job_id: str = "",
    provider_job_reference: str = "",
    **_: Any,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness

    provider_name = str(provider or provider_key or payload.get("provider") or payload.get("provider_id") or "unknown").strip().lower()
    tenant = str(tenant_id or payload.get("tenant_id") or payload.get("client_id") or "").strip()
    project = str(project_id or payload.get("project_id") or "default_project")
    exec_id = str(execution_id or payload.get("execution_id") or payload.get("workflow_id") or "")
    if not exec_id:
        created = create_provider_execution_record(
            tenant_id=tenant or "unknown",
            provider=provider_name,
            project_id=project,
            action_type=str(payload.get("action_type") or payload.get("job_type") or payload.get("type") or "provider_job"),
            capability=str(payload.get("capability") or payload.get("job_type") or ""),
            request_payload=payload,
        )
        if not created.get("success"):
            return created
        exec_id = str(created["execution_id"])
    job_id = str(provider_job_id or payload.get("job_id") or f"provider_job_{uuid.uuid4().hex[:14]}")
    external_id = str(provider_external_job_id or provider_job_reference or payload.get("provider_job_reference") or payload.get("provider_external_job_id") or "")
    safe_max = max(1, min(int(max_attempts or payload.get("max_attempts") or 3), 25))
    clean_status = str(status or payload.get("status") or "queued").lower()

    if _using_dev(readiness):
        job = {
            "provider_job_id": job_id,
            "job_id": job_id,
            "execution_id": exec_id,
            "provider": provider_name,
            "provider_external_job_id": external_id or None,
            "provider_job_reference": external_id or None,
            "tenant_id": tenant or "unknown",
            "project_id": project,
            "status": clean_status,
            "polling_status": None,
            "attempt_count": int(payload.get("attempt_count") or 0),
            "max_attempts": safe_max,
            "next_poll_at": None,
            "next_retry_at": None,
            "last_error": None,
            "result_payload": {},
            "asset_records": [],
            "requested_asset_type": payload.get("requested_asset_type") or payload.get("asset_type"),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "completed_at": None,
            "failed_at": None,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        _DEV_JOBS[job_id] = job
        record_provider_job_event(provider_job_id=job_id, execution_id=exec_id, event_type="provider_job_created", payload=job)
        return _safe_response(success=True, status=clean_status, job=deepcopy(job), provider_job_id=job_id, storage_mode="dev_memory", dev_only=True, not_production_durable=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO provider_jobs
                (provider_job_id, execution_id, provider, provider_external_job_id,
                 tenant_id, project_id, status, attempt_count, max_attempts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider_job_id) DO UPDATE SET updated_at = NOW()
                RETURNING {_job_select()}
                """,
                (job_id, exec_id, provider_name, external_id or None, tenant or "unknown", project, clean_status, int(payload.get("attempt_count") or 0), safe_max),
            )
            job = _row(cur.fetchone(), _job_columns())
        conn.commit()
    record_provider_job_event(provider_job_id=job_id, execution_id=exec_id, event_type="provider_job_created", payload=job)
    job["job_id"] = job["provider_job_id"]
    return _safe_response(success=True, status=clean_status, job=job, provider_job_id=job_id, storage_mode="postgres", durable=True)


def get_provider_job(job_id: str) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    key = str(job_id or "")
    if _using_dev(readiness):
        job = _DEV_JOBS.get(key)
        if not job:
            return _safe_response(success=False, status="not_found", error="provider_job_not_found", job_id=key, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", job=deepcopy(job), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_job_select()} FROM provider_jobs WHERE provider_job_id = %s", (key,))
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="not_found", error="provider_job_not_found", job_id=key, storage_mode="postgres", durable=True)
    job = _row(row, _job_columns())
    job["job_id"] = job["provider_job_id"]
    job["provider_job_reference"] = job.get("provider_external_job_id")
    return _safe_response(success=True, status="found", job=job, storage_mode="postgres", durable=True)


def list_provider_jobs(status: str = "", tenant_id: str = "", provider: str = "", limit: int = 100, execution_id: str = "") -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    if _using_dev(readiness):
        jobs = list(_DEV_JOBS.values())
        if status:
            jobs = [j for j in jobs if j.get("status") == status]
        if tenant_id:
            jobs = [j for j in jobs if j.get("tenant_id") == tenant_id]
        if provider:
            jobs = [j for j in jobs if j.get("provider") == provider]
        if execution_id:
            jobs = [j for j in jobs if j.get("execution_id") == execution_id]
        jobs = sorted(jobs, key=lambda j: str(j.get("created_at")), reverse=True)[: max(1, min(int(limit or 100), 500))]
        return _safe_response(success=True, status="listed", job_count=len(jobs), jobs=deepcopy(jobs), storage_mode="dev_memory", dev_only=True, not_production_durable=True)
    clauses: List[str] = []
    params: List[Any] = []
    if status:
        clauses.append("status = %s")
        params.append(status)
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if provider:
        clauses.append("provider = %s")
        params.append(provider)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(max(1, min(int(limit or 100), 500)))
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_job_select()} FROM provider_jobs {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    jobs = [_row(r, _job_columns()) for r in rows]
    for job in jobs:
        job["job_id"] = job["provider_job_id"]
        job["provider_job_reference"] = job.get("provider_external_job_id")
    return _safe_response(success=True, status="listed", job_count=len(jobs), jobs=jobs, storage_mode="postgres", durable=True)


def update_provider_job_status(
    job_id: str,
    status: str,
    *,
    result_payload: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    provider_job_reference: Optional[str] = None,
    asset_records: Optional[List[Dict[str, Any]]] = None,
    next_retry_at: Optional[str] = None,
    polling_status: Optional[str] = None,
    next_poll_at: Optional[str] = None,
) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    key = str(job_id or "")
    clean_status = str(status or "updated").lower()
    terminal_completed = clean_status == "completed"
    terminal_failed = clean_status in {"failed", "dead_letter", "manual_review_required", "cancelled", "timed_out"}

    if _using_dev(readiness):
        job = _DEV_JOBS.get(key)
        if not job:
            return _safe_response(success=False, status="not_found", error="provider_job_not_found", job_id=key, storage_mode="dev_memory", dev_only=True)
        if clean_status in {"running", "retry_scheduled", "polling"}:
            job["attempt_count"] = int(job.get("attempt_count") or 0) + 1 if clean_status == "running" else int(job.get("attempt_count") or 0)
        job["status"] = clean_status
        job["updated_at"] = _now_iso()
        if provider_job_reference:
            job["provider_external_job_id"] = provider_job_reference
            job["provider_job_reference"] = provider_job_reference
        if next_retry_at is not None:
            job["next_retry_at"] = next_retry_at
        if error is not None:
            job["last_error"] = error
            job["error"] = error
        if result_payload is not None:
            job["result_payload"] = deepcopy(result_payload)
        if asset_records is not None:
            job["asset_records"] = deepcopy(asset_records)
        if polling_status is not None:
            job["polling_status"] = polling_status
        if next_poll_at is not None:
            job["next_poll_at"] = next_poll_at
        if terminal_completed:
            job["completed_at"] = _now_iso()
        if terminal_failed:
            job["failed_at"] = _now_iso()
        record_provider_job_event(provider_job_id=key, execution_id=job["execution_id"], event_type="provider_job_status_updated", payload=job)
        return _safe_response(success=True, status=clean_status, job=deepcopy(job), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE provider_jobs
                SET status = %s,
                    provider_external_job_id = COALESCE(%s, provider_external_job_id),
                    polling_status = COALESCE(%s, polling_status),
                    attempt_count = attempt_count + CASE WHEN %s = 'running' THEN 1 ELSE 0 END,
                    next_poll_at = COALESCE(%s, next_poll_at),
                    next_retry_at = %s,
                    last_error = %s,
                    completed_at = CASE WHEN %s THEN NOW() ELSE completed_at END,
                    failed_at = CASE WHEN %s THEN NOW() ELSE failed_at END,
                    updated_at = NOW()
                WHERE provider_job_id = %s
                RETURNING {_job_select()}
                """,
                (clean_status, provider_job_reference, polling_status, clean_status, next_poll_at, next_retry_at, error, terminal_completed, terminal_failed, key),
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="not_found", error="provider_job_not_found", job_id=key, storage_mode="postgres", durable=True)
    job = _row(row, _job_columns())
    job["job_id"] = job["provider_job_id"]
    job["provider_job_reference"] = job.get("provider_external_job_id")
    if result_payload is not None:
        record_provider_result(provider_job_id=key, execution_id=job["execution_id"], provider=job["provider"], result_status=clean_status, metadata=result_payload)
    if asset_records:
        for asset in asset_records:
            record_provider_delivery_packet(provider_job_id=key, execution_id=job["execution_id"], asset_id=str(asset.get("asset_id") or ""), delivery_status=str(asset.get("delivery_status") or "ready"))
    record_provider_job_event(provider_job_id=key, execution_id=job["execution_id"], event_type="provider_job_status_updated", payload=job)
    return _safe_response(success=True, status=clean_status, job=job, storage_mode="postgres", durable=True)


def record_provider_job_event(*, provider_job_id: str = "", execution_id: str = "", event_type: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_payload = _scrub_sensitive(payload or {})
    event = {
        "event_id": f"provider_job_event_{uuid.uuid4().hex[:14]}",
        "provider_job_id": provider_job_id,
        "job_id": provider_job_id,
        "execution_id": execution_id,
        "event_type": event_type,
        "created_at": _now_iso(),
        "payload": deepcopy(safe_payload),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_JOB_EVENTS.append(event)
        return _safe_response(success=True, status="recorded", event=deepcopy(event), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_job_events
                (event_id, provider_job_id, execution_id, event_type, payload_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event["event_id"], provider_job_id or None, execution_id or None, event_type, _json(safe_payload)),
            )
        conn.commit()
    return _safe_response(success=True, status="recorded", event=event, storage_mode="postgres", durable=True)


def list_provider_job_events(job_id: str = "", limit: int = 100, tenant_id: str = "", execution_id: str = "") -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        events = list(_DEV_JOB_EVENTS)
        if job_id:
            events = [event for event in events if event.get("provider_job_id") == job_id]
        if execution_id:
            events = [event for event in events if event.get("execution_id") == execution_id]
        if tenant_id:
            events = [
                event
                for event in events
                if (event.get("payload") or {}).get("tenant_id") == tenant_id
                or _DEV_EXECUTIONS.get(str(event.get("execution_id")), {}).get("tenant_id") == tenant_id
            ]
        events = sorted(events, key=lambda event: str(event.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", event_count=len(events), events=deepcopy(events), storage_mode="dev_memory", dev_only=True)
    params: List[Any] = []
    clauses: List[str] = []
    if job_id:
        clauses.append("e.provider_job_id = %s")
        params.append(job_id)
    if execution_id:
        clauses.append("e.execution_id = %s")
        params.append(execution_id)
    if tenant_id:
        clauses.append("COALESCE(r.tenant_id, e.payload_json->>'tenant_id') = %s")
        params.append(tenant_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT e.event_id, e.provider_job_id, e.execution_id, e.event_type, e.payload_json, e.created_at
                FROM provider_job_events e
                LEFT JOIN provider_execution_records r ON r.execution_id = e.execution_id
                {where}
                ORDER BY e.created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    events = [
        {
            "event_id": r[0],
            "provider_job_id": r[1],
            "job_id": r[1],
            "execution_id": r[2],
            "event_type": r[3],
            "payload": _parse_json(r[4]),
            "created_at": _dt(r[5]),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        for r in rows
    ]
    return _safe_response(success=True, status="listed", event_count=len(events), events=events, storage_mode="postgres", durable=True)


def record_provider_dispatch_attempt(
    *,
    execution_id: str,
    provider: str = "",
    provider_key: str = "",
    provider_job_id: str = "",
    status: str,
    idempotency_key: str = "",
    latency_ms: int = 0,
    error: Optional[str] = None,
    attempt_number: Optional[int] = None,
    allowed_by_policy: Optional[bool] = None,
    reason: Optional[str] = None,
    **_: Any,
) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    provider_name = str(provider or provider_key or "unknown").lower()
    idem = idempotency_key or f"{execution_id}:{provider_job_id}:{provider_name}:{status}"
    if _using_dev(readiness):
        for attempt in _DEV_DISPATCH_ATTEMPTS:
            if attempt.get("provider") == provider_name and attempt.get("idempotency_key") == idem:
                return _safe_response(success=True, status=attempt["status"], attempt=deepcopy(attempt), idempotent_replay=True, storage_mode="dev_memory", dev_only=True)
        attempt = {
            "dispatch_attempt_id": f"provider_dispatch_{uuid.uuid4().hex[:16]}",
            "attempt_id": None,
            "execution_id": execution_id,
            "provider_job_id": provider_job_id,
            "worker_job_id": provider_job_id,
            "provider": provider_name,
            "provider_key": provider_name,
            "status": status,
            "result_status": status,
            "idempotency_key": idem,
            "latency_ms": int(latency_ms or 0),
            "error": error or reason,
            "reason": error or reason,
            "attempt_number": attempt_number,
            "allowed_by_policy": allowed_by_policy,
            "live_external_call_executed": False,
            "created_at": _now_iso(),
            "created_at_ms": int(_now().timestamp() * 1000),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        attempt["attempt_id"] = attempt["dispatch_attempt_id"]
        _DEV_DISPATCH_ATTEMPTS.append(attempt)
        return _safe_response(success=True, status=status, attempt=deepcopy(attempt), idempotent_replay=False, storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT dispatch_attempt_id, execution_id, provider_job_id, provider, status,
                       idempotency_key, latency_ms, error, created_at, attempt_number, allowed_by_policy
                FROM provider_dispatch_attempts
                WHERE provider = %s AND idempotency_key = %s
                """,
                (provider_name, idem),
            )
            row = cur.fetchone()
            if row:
                attempt = {
                    "dispatch_attempt_id": row[0], "attempt_id": row[0], "execution_id": row[1], "provider_job_id": row[2], "worker_job_id": row[2],
                    "provider": row[3], "provider_key": row[3], "status": row[4], "result_status": row[4], "idempotency_key": row[5],
                    "latency_ms": row[6], "error": row[7], "reason": row[7], "created_at": _dt(row[8]),
                    "attempt_number": row[9], "allowed_by_policy": row[10], "live_external_call_executed": False,
                    "credential_values_exposed": False, "customer_safe": True,
                }
                return _safe_response(success=True, status=attempt["status"], attempt=attempt, idempotent_replay=True, storage_mode="postgres", durable=True)
            attempt_id = f"provider_dispatch_{uuid.uuid4().hex[:16]}"
            cur.execute(
                """
                INSERT INTO provider_dispatch_attempts
                (dispatch_attempt_id, execution_id, provider_job_id, provider, status,
                 idempotency_key, latency_ms, error, attempt_number, allowed_by_policy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING dispatch_attempt_id, execution_id, provider_job_id, provider, status,
                          idempotency_key, latency_ms, error, created_at, attempt_number, allowed_by_policy
                """,
                (attempt_id, execution_id, provider_job_id or None, provider_name, status, idem, int(latency_ms or 0), error or reason, attempt_number, allowed_by_policy),
            )
            row = cur.fetchone()
        conn.commit()
    attempt = {
        "dispatch_attempt_id": row[0], "attempt_id": row[0], "execution_id": row[1], "provider_job_id": row[2], "worker_job_id": row[2],
        "provider": row[3], "provider_key": row[3], "status": row[4], "result_status": row[4], "idempotency_key": row[5],
        "latency_ms": row[6], "error": row[7], "reason": row[7], "created_at": _dt(row[8]),
        "attempt_number": row[9], "allowed_by_policy": row[10], "live_external_call_executed": False,
        "credential_values_exposed": False, "customer_safe": True,
    }
    return _safe_response(success=True, status=status, attempt=attempt, idempotent_replay=False, storage_mode="postgres", durable=True)


def list_provider_dispatch_attempts(tenant_id: str = "", execution_id: str = "", provider: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    clean_provider = str(provider or "").strip().lower()
    if _using_dev(readiness):
        attempts = list(_DEV_DISPATCH_ATTEMPTS)
        if execution_id:
            attempts = [attempt for attempt in attempts if attempt.get("execution_id") == execution_id]
        if clean_provider:
            attempts = [attempt for attempt in attempts if attempt.get("provider") == clean_provider]
        if tenant_id:
            attempts = [
                attempt
                for attempt in attempts
                if _DEV_EXECUTIONS.get(str(attempt.get("execution_id")), {}).get("tenant_id") == tenant_id
            ]
        attempts = sorted(attempts, key=lambda attempt: str(attempt.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", records=deepcopy(attempts), count=len(attempts), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if execution_id:
        clauses.append("a.execution_id = %s")
        params.append(execution_id)
    if clean_provider:
        clauses.append("a.provider = %s")
        params.append(clean_provider)
    if tenant_id:
        clauses.append("r.tenant_id = %s")
        params.append(tenant_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT a.dispatch_attempt_id, a.execution_id, a.provider_job_id, a.provider,
                       a.status, a.idempotency_key, a.latency_ms, a.error, a.created_at,
                       a.attempt_number, a.allowed_by_policy
                FROM provider_dispatch_attempts a
                LEFT JOIN provider_execution_records r ON r.execution_id = a.execution_id
                {where}
                ORDER BY a.created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    attempts = [
        {
            "dispatch_attempt_id": row[0],
            "attempt_id": row[0],
            "execution_id": row[1],
            "provider_job_id": row[2],
            "worker_job_id": row[2],
            "provider": row[3],
            "provider_key": row[3],
            "status": row[4],
            "result_status": row[4],
            "idempotency_key": row[5],
            "latency_ms": row[6],
            "error": row[7],
            "reason": row[7],
            "created_at": _dt(row[8]),
            "attempt_number": row[9],
            "allowed_by_policy": row[10],
            "live_external_call_executed": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        for row in rows
    ]
    return _safe_response(success=True, status="listed", records=attempts, count=len(attempts), storage_mode="postgres", durable=True)


def record_provider_retry(
    *,
    provider_job_id: str = "",
    execution_id: str,
    retry_reason: str,
    attempt_number: int,
    scheduled_for: Optional[Any] = None,
    retry_allowed: Optional[bool] = None,
    next_action: str = "",
    **_: Any,
) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    scheduled = scheduled_for or (_now() + timedelta(seconds=60))
    if isinstance(scheduled, str):
        scheduled_value = scheduled
    else:
        scheduled_value = scheduled.isoformat()
    retry = {
        "retry_id": f"provider_retry_{uuid.uuid4().hex[:16]}",
        "provider_job_id": provider_job_id,
        "execution_id": execution_id,
        "retry_reason": retry_reason,
        "failure_code": retry_reason,
        "attempt_number": int(attempt_number or 0),
        "retry_allowed": retry_allowed,
        "next_action": next_action,
        "scheduled_for": scheduled_value,
        "created_at": _now_iso(),
        "created_at_ms": int(_now().timestamp() * 1000),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_RETRIES.append(retry)
        return _safe_response(success=True, status="recorded", retry=deepcopy(retry), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_retry_history
                (retry_id, provider_job_id, execution_id, retry_reason, attempt_number,
                 scheduled_for, retry_allowed, next_action)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (retry_id) DO NOTHING
                """,
                (retry["retry_id"], provider_job_id or None, execution_id, retry_reason, int(attempt_number or 0), scheduled, retry_allowed, next_action or None),
            )
        conn.commit()
    return _safe_response(success=True, status="recorded", retry=retry, storage_mode="postgres", durable=True)


def list_provider_retry_history(tenant_id: str = "", execution_id: str = "", provider_job_id: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        retries = list(_DEV_RETRIES)
        if execution_id:
            retries = [retry for retry in retries if retry.get("execution_id") == execution_id]
        if provider_job_id:
            retries = [retry for retry in retries if retry.get("provider_job_id") == provider_job_id]
        if tenant_id:
            retries = [
                retry
                for retry in retries
                if _DEV_EXECUTIONS.get(str(retry.get("execution_id")), {}).get("tenant_id") == tenant_id
            ]
        retries = sorted(retries, key=lambda retry: str(retry.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", records=deepcopy(retries), count=len(retries), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if execution_id:
        clauses.append("h.execution_id = %s")
        params.append(execution_id)
    if provider_job_id:
        clauses.append("h.provider_job_id = %s")
        params.append(provider_job_id)
    if tenant_id:
        clauses.append("r.tenant_id = %s")
        params.append(tenant_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT h.retry_id, h.provider_job_id, h.execution_id, h.retry_reason,
                       h.attempt_number, h.scheduled_for, h.retry_allowed, h.next_action, h.created_at
                FROM provider_retry_history h
                LEFT JOIN provider_execution_records r ON r.execution_id = h.execution_id
                {where}
                ORDER BY h.created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    retries = [
        {
            "retry_id": row[0],
            "provider_job_id": row[1],
            "worker_job_id": row[1],
            "execution_id": row[2],
            "retry_reason": row[3],
            "failure_code": row[3],
            "attempt_number": row[4],
            "scheduled_for": _dt(row[5]),
            "retry_allowed": row[6],
            "next_action": row[7],
            "created_at": _dt(row[8]),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        for row in rows
    ]
    return _safe_response(success=True, status="listed", records=retries, count=len(retries), storage_mode="postgres", durable=True)


def record_provider_polling_state(*, provider_job_id: str, execution_id: str, provider: str, polling_status: str, next_poll_at: Optional[Any] = None, last_poll_at: Optional[Any] = None, provider_status: str = "") -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    record = {
        "provider_job_id": provider_job_id,
        "execution_id": execution_id,
        "provider": provider,
        "polling_status": polling_status,
        "next_poll_at": next_poll_at.isoformat() if isinstance(next_poll_at, datetime) else next_poll_at,
        "last_poll_at": last_poll_at.isoformat() if isinstance(last_poll_at, datetime) else last_poll_at,
        "provider_status": provider_status,
        "updated_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_POLLING[provider_job_id] = record
        if provider_job_id in _DEV_JOBS:
            _DEV_JOBS[provider_job_id]["polling_status"] = polling_status
            _DEV_JOBS[provider_job_id]["next_poll_at"] = record["next_poll_at"]
        return _safe_response(success=True, status="recorded", polling_state=deepcopy(record), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_polling_state
                (provider_job_id, execution_id, provider, polling_status, next_poll_at, last_poll_at, provider_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider_job_id) DO UPDATE SET
                    polling_status = EXCLUDED.polling_status,
                    next_poll_at = EXCLUDED.next_poll_at,
                    last_poll_at = EXCLUDED.last_poll_at,
                    provider_status = EXCLUDED.provider_status,
                    updated_at = NOW()
                """,
                (provider_job_id, execution_id, provider, polling_status, next_poll_at, last_poll_at, provider_status),
            )
        conn.commit()
    return _safe_response(success=True, status="recorded", polling_state=record, storage_mode="postgres", durable=True)


def record_provider_result(*, provider_job_id: str = "", execution_id: str, provider: str, result_status: str, result_summary: str = "", asset_id: str = "", asset_url: str = "", metadata: Optional[Dict[str, Any]] = None, **_: Any) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    result = {
        "result_id": f"provider_result_{uuid.uuid4().hex[:16]}",
        "provider_job_id": provider_job_id,
        "execution_id": execution_id,
        "provider": provider,
        "result_status": result_status,
        "result_summary": str(result_summary or "")[:2000],
        "asset_id": asset_id,
        "asset_url": asset_url,
        "metadata": deepcopy(metadata or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_RESULTS.append(result)
        return _safe_response(success=True, status="recorded", result=deepcopy(result), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_result_records
                (result_id, provider_job_id, execution_id, provider, result_status,
                 result_summary, asset_id, asset_url, metadata_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (result["result_id"], provider_job_id or None, execution_id, provider, result_status, result["result_summary"], asset_id or None, asset_url or None, _json(metadata)),
            )
        conn.commit()
    return _safe_response(success=True, status="recorded", result=result, storage_mode="postgres", durable=True)


def record_provider_delivery_packet(*, provider_job_id: str = "", execution_id: str, asset_id: str = "", delivery_status: str = "ready", delivery_packet_id: str = "", **_: Any) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    packet_id = delivery_packet_id or f"delivery_packet_{uuid.uuid4().hex[:14]}"
    packet = {
        "delivery_packet_id": packet_id,
        "packet_id": packet_id,
        "provider_job_id": provider_job_id,
        "job_id": provider_job_id,
        "execution_id": execution_id,
        "asset_id": asset_id,
        "delivery_status": delivery_status,
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_DELIVERY_PACKETS[packet_id] = packet
        return _safe_response(success=True, status=delivery_status, delivery_packet=deepcopy(packet), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_delivery_packets
                (delivery_packet_id, provider_job_id, execution_id, asset_id, delivery_status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (delivery_packet_id) DO NOTHING
                """,
                (packet_id, provider_job_id or None, execution_id, asset_id or None, delivery_status),
            )
        conn.commit()
    return _safe_response(success=True, status=delivery_status, delivery_packet=packet, storage_mode="postgres", durable=True)


def record_provider_latency(
    *,
    provider: str = "",
    provider_key: str = "",
    capability: str = "",
    latency_ms: int,
    status: str = "",
    tenant_id: str = "",
    request_id: str = "",
    execution_id: str = "",
    **_: Any,
) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    metric = {
        "metric_id": f"provider_latency_{uuid.uuid4().hex[:16]}",
        "latency_id": None,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "provider": str(provider or provider_key or "unknown").lower(),
        "provider_key": str(provider or provider_key or "unknown").lower(),
        "capability": capability,
        "latency_ms": int(latency_ms or 0),
        "status": status,
        "operation": capability or status,
        "created_at": _now_iso(),
        "created_at_ms": int(_now().timestamp() * 1000),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    metric["latency_id"] = metric["metric_id"]
    if _using_dev(readiness):
        _DEV_LATENCY.append(metric)
        return _safe_response(success=True, status="recorded", metric=deepcopy(metric), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO provider_latency_metrics
                (metric_id, tenant_id, request_id, execution_id, provider, capability, latency_ms, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO NOTHING
                """,
                (
                    metric["metric_id"],
                    tenant_id or None,
                    request_id or None,
                    execution_id or None,
                    metric["provider"],
                    capability or None,
                    int(latency_ms or 0),
                    status or None,
                ),
            )
        conn.commit()
    return _safe_response(success=True, status="recorded", metric=metric, storage_mode="postgres", durable=True)


def list_provider_latency_metrics(tenant_id: str = "", provider: str = "", execution_id: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    clean_provider = str(provider or "").strip().lower()
    if _using_dev(readiness):
        metrics = list(_DEV_LATENCY)
        if tenant_id:
            metrics = [metric for metric in metrics if metric.get("tenant_id") == tenant_id]
        if clean_provider:
            metrics = [metric for metric in metrics if metric.get("provider") == clean_provider]
        if execution_id:
            metrics = [metric for metric in metrics if metric.get("execution_id") == execution_id]
        metrics = sorted(metrics, key=lambda metric: str(metric.get("created_at") or ""), reverse=True)[:safe_limit]
        latencies = [int(metric.get("latency_ms") or 0) for metric in metrics]
        return _safe_response(
            success=True,
            status="listed",
            records=deepcopy(metrics),
            count=len(metrics),
            average_latency_ms=(sum(latencies) / len(latencies) if latencies else None),
            max_latency_ms=(max(latencies) if latencies else None),
            min_latency_ms=(min(latencies) if latencies else None),
            storage_mode="dev_memory",
            dev_only=True,
        )
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if clean_provider:
        clauses.append("provider = %s")
        params.append(clean_provider)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT metric_id, tenant_id, request_id, execution_id, provider, capability,
                       latency_ms, status, created_at
                FROM provider_latency_metrics
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    metrics = [
        {
            "metric_id": row[0],
            "latency_id": row[0],
            "tenant_id": row[1],
            "request_id": row[2],
            "execution_id": row[3],
            "provider": row[4],
            "provider_key": row[4],
            "capability": row[5],
            "operation": row[5] or row[7],
            "latency_ms": row[6],
            "status": row[7],
            "created_at": _dt(row[8]),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        for row in rows
    ]
    latencies = [int(metric.get("latency_ms") or 0) for metric in metrics]
    return _safe_response(
        success=True,
        status="listed",
        records=metrics,
        count=len(metrics),
        average_latency_ms=(sum(latencies) / len(latencies) if latencies else None),
        max_latency_ms=(max(latencies) if latencies else None),
        min_latency_ms=(min(latencies) if latencies else None),
        storage_mode="postgres",
        durable=True,
    )


def get_provider_execution_status() -> Dict[str, Any]:
    return get_provider_admin_summary()


def get_provider_admin_summary(tenant_id: str = "", provider: str = "") -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    jobs_result = list_provider_jobs(tenant_id=tenant_id, provider=provider, limit=200)
    jobs = jobs_result.get("jobs", [])
    execution_records = list_provider_execution_records(tenant_id=tenant_id, provider=provider, limit=200).get("records", [])
    dispatch_attempts = list_provider_dispatch_attempts(tenant_id=tenant_id, provider=provider, limit=200).get("records", [])
    retry_history = list_provider_retry_history(tenant_id=tenant_id, limit=200).get("records", [])
    latency_metrics = list_provider_latency_metrics(tenant_id=tenant_id, provider=provider, limit=200)
    counts: Dict[str, int] = {}
    for job in jobs:
        status = str(job.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    delivery_packets = list_delivery_packets(tenant_id=tenant_id).get("delivery_packets", [])
    return _safe_response(
        success=True,
        ready=True,
        status="ready",
        provider_execution_admin_visibility_ready=True,
        provider_ledger_ready=True,
        storage_mode=readiness.get("storage_mode"),
        durable=readiness.get("durable", False),
        dev_only=readiness.get("dev_only", False),
        summary={
            "queued_job_count": counts.get("queued", 0),
            "running_job_count": counts.get("running", 0),
            "polling_job_count": counts.get("polling", 0),
            "completed_job_count": counts.get("completed", 0),
            "failed_job_count": counts.get("failed", 0),
            "timed_out_job_count": counts.get("timed_out", 0),
            "retry_scheduled_job_count": counts.get("retry_scheduled", 0),
            "delivery_packet_count": len(delivery_packets),
            "execution_record_count": len(execution_records),
            "dispatch_attempt_count": len(dispatch_attempts),
            "retry_history_count": len(retry_history),
            "latency_metric_count": latency_metrics.get("count", 0),
            "total_jobs": len(jobs),
            **counts,
        },
        execution_records=execution_records,
        recent_execution_records=execution_records[:20],
        jobs=jobs,
        recent_jobs=jobs[:20],
        dispatch_attempts=dispatch_attempts,
        recent_dispatch_attempts=dispatch_attempts[:20],
        retry_history=retry_history,
        recent_retry_history=retry_history[:20],
        latency_metrics=latency_metrics.get("records", []),
        recent_latency_metrics=latency_metrics.get("records", [])[:20],
        delivery_packets=delivery_packets,
        recent_delivery_packets=delivery_packets[:10],
        retry_timeout={
            "retry_scheduled": counts.get("retry_scheduled", 0),
            "manual_review_required": counts.get("manual_review_required", 0),
            "dead_letter": counts.get("dead_letter", 0),
        },
    )


def list_delivery_packets(tenant_id: str = "", execution_id: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    if not readiness.get("success"):
        return readiness
    if _using_dev(readiness):
        packets = list(_DEV_DELIVERY_PACKETS.values())
        if tenant_id:
            packets = [p for p in packets if _DEV_JOBS.get(str(p.get("provider_job_id")), {}).get("tenant_id") == tenant_id]
        if execution_id:
            packets = [p for p in packets if p.get("execution_id") == execution_id]
        return _safe_response(success=True, status="listed", packet_count=len(packets), delivery_packets=deepcopy(packets[:limit]), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if execution_id:
        clauses.append("p.execution_id = %s")
        params.append(execution_id)
    if tenant_id:
        clauses.append("j.tenant_id = %s")
        params.append(tenant_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(max(1, min(int(limit or 100), 500)))
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT p.delivery_packet_id, p.provider_job_id, p.execution_id, p.asset_id,
                       p.delivery_status, p.created_at
                FROM provider_delivery_packets p
                LEFT JOIN provider_jobs j ON j.provider_job_id = p.provider_job_id
                {where}
                ORDER BY p.created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    packets = [
        {
            "delivery_packet_id": r[0],
            "packet_id": r[0],
            "provider_job_id": r[1],
            "job_id": r[1],
            "execution_id": r[2],
            "asset_id": r[3],
            "delivery_status": r[4],
            "created_at": _dt(r[5]),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        for r in rows
    ]
    return _safe_response(success=True, status="listed", packet_count=len(packets), delivery_packets=packets, storage_mode="postgres", durable=True)


def reset_dev_provider_ledger_for_tests() -> Dict[str, Any]:
    _DEV_EXECUTIONS.clear()
    _DEV_JOBS.clear()
    _DEV_JOB_EVENTS.clear()
    _DEV_DISPATCH_ATTEMPTS.clear()
    _DEV_RETRIES.clear()
    _DEV_POLLING.clear()
    _DEV_RESULTS.clear()
    _DEV_DELIVERY_PACKETS.clear()
    _DEV_LATENCY.clear()
    return _safe_response(success=True, reset=True, status="dev_provider_ledger_reset", storage_mode="dev_memory", dev_only=True)
