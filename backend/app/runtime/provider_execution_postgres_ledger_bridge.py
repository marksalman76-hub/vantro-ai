from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.runtime.durable_provider_execution_ledger import (
    create_provider_execution_record,
    ensure_provider_ledger_tables,
    get_provider_admin_summary,
    list_provider_dispatch_attempts,
    list_provider_execution_records,
    list_provider_job_events,
    list_provider_latency_metrics,
    list_provider_retry_history,
    record_provider_dispatch_attempt,
    record_provider_job_event,
    record_provider_latency,
    record_provider_retry,
    reset_dev_provider_ledger_for_tests,
)


SQL_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "provider_execution_ledger_schema.sql"


def _safe_response(**kwargs: Any) -> Dict[str, Any]:
    payload = dict(kwargs)
    payload["credential_values_exposed"] = False
    payload["customer_safe"] = True
    return payload


def _database_url_present() -> bool:
    return bool(os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"))


def _bridge_mode(mode: str) -> str:
    return "in_memory_fallback" if mode == "dev_memory" else mode


def _compat_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(event.get("payload") or {})
    return {
        "ledger_id": event.get("event_id"),
        "event_id": event.get("event_id"),
        "tenant_id": payload.get("tenant_id"),
        "request_id": payload.get("request_id"),
        "execution_id": event.get("execution_id"),
        "worker_job_id": event.get("provider_job_id") or event.get("job_id"),
        "provider_key": payload.get("provider_key"),
        "event_type": event.get("event_type"),
        "status": payload.get("status"),
        "details": dict(payload.get("details") or {}),
        "payload": payload,
        "created_at": event.get("created_at"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _compat_attempt(attempt: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(attempt or {})
    safe["attempt_id"] = safe.get("attempt_id") or safe.get("dispatch_attempt_id")
    safe["worker_job_id"] = safe.get("worker_job_id") or safe.get("provider_job_id")
    safe["provider_key"] = safe.get("provider_key") or safe.get("provider")
    safe["result_status"] = safe.get("result_status") or safe.get("status")
    safe.setdefault("live_external_call_executed", False)
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def _compat_retry(retry: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(retry or {})
    safe["worker_job_id"] = safe.get("worker_job_id") or safe.get("provider_job_id")
    safe["failure_code"] = safe.get("failure_code") or safe.get("retry_reason")
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def _compat_latency(metric: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(metric or {})
    safe["latency_id"] = safe.get("latency_id") or safe.get("metric_id")
    safe["provider_key"] = safe.get("provider_key") or safe.get("provider")
    safe["operation"] = safe.get("operation") or safe.get("capability") or safe.get("status")
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def provider_postgres_ledger_bridge_status() -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    return _safe_response(
        bridge_ready=bool(readiness.get("success")),
        database_url_present=_database_url_present(),
        postgres_schema_path=str(SQL_SCHEMA_PATH),
        postgres_binding_mode="canonical_durable_provider_ledger",
        in_memory_fallback_enabled=bool(readiness.get("dev_only")),
        current_fallback_status=readiness,
    )


def get_provider_ledger_schema_sql() -> Dict[str, Any]:
    if not SQL_SCHEMA_PATH.exists():
        return _safe_response(status="missing", schema_sql_present=False, sql="")
    return _safe_response(status="available", schema_sql_present=True, sql=SQL_SCHEMA_PATH.read_text(encoding="utf-8"))


def apply_provider_ledger_schema_if_possible() -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    return _safe_response(
        status="applied" if readiness.get("durable") else readiness.get("status"),
        reason=readiness.get("reason"),
        applied=bool(readiness.get("durable")),
        fallback_storage_active=bool(readiness.get("dev_only")),
    )


def apply_provider_ledger_schema_with_driver() -> Dict[str, Any]:
    return apply_provider_ledger_schema_if_possible()


def provider_postgres_migration_apply_status() -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    return _safe_response(
        migration_apply_ready=bool(readiness.get("success")),
        database_url_present=_database_url_present(),
        schema_sql_present=True,
        postgres_driver_available=not bool(readiness.get("postgres_configured_but_driver_unavailable")),
        postgres_driver="psycopg",
        fallback_storage_active=bool(readiness.get("dev_only")),
    )


def detect_postgres_driver() -> Dict[str, Any]:
    try:
        import psycopg  # type: ignore
        return _safe_response(driver_available=True, driver="psycopg")
    except Exception:
        pass
    try:
        import psycopg2  # type: ignore
        return _safe_response(driver_available=True, driver="psycopg2")
    except Exception:
        pass
    return _safe_response(driver_available=False, driver=None)


def persist_provider_execution_record_bridge(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    execution_status: str = "created",
    worker_job_id: Optional[str] = None,
    provider_job_id: Optional[str] = None,
) -> Dict[str, Any]:
    result = create_provider_execution_record(
        tenant_id=tenant_id,
        provider=provider_key,
        capability=task_type,
        action_type=task_type,
        status=execution_status,
        request_payload={"request_id": request_id, "worker_job_id": worker_job_id, "provider_job_id": provider_job_id},
        idempotency_key=f"{tenant_id}:{provider_key}:{request_id}:{task_type}",
        worker_job_id=worker_job_id or "",
        provider_job_id=provider_job_id or "",
    )
    record = dict(result.get("record") or {})
    record["provider_key"] = record.get("provider")
    record["task_type"] = task_type
    record["execution_status"] = record.get("status")
    record["worker_job_id"] = worker_job_id
    record["provider_job_id"] = provider_job_id
    record["request_id"] = request_id
    return _safe_response(
        persistence_mode=_bridge_mode(str(result.get("storage_mode") or "")),
        postgres_write_attempted=_database_url_present(),
        postgres_write_result={"written": bool(result.get("durable")), "reason": result.get("status")},
        record=record,
    )


def persist_worker_event_bridge(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    event_type: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    result = record_provider_job_event(
        provider_job_id=worker_job_id,
        execution_id=execution_id,
        event_type=event_type,
        payload={"tenant_id": tenant_id, "request_id": request_id, "provider_key": provider_key, "status": status, "details": details or {}},
    )
    return _safe_response(
        persistence_mode=_bridge_mode(str(result.get("storage_mode") or "")),
        postgres_write_attempted=_database_url_present(),
        postgres_write_result={"written": bool(result.get("durable")), "reason": result.get("status")},
        entry=_compat_event(result.get("event") or {}),
    )


def persist_dispatch_attempt_bridge(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    attempt_number: int,
    allowed_by_policy: bool,
    result_status: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    result = record_provider_dispatch_attempt(
        execution_id=execution_id,
        provider_job_id=worker_job_id,
        provider=provider_key,
        status=result_status,
        idempotency_key=f"{tenant_id}:{provider_key}:{request_id}:{attempt_number}",
        error=reason,
        reason=reason,
        attempt_number=attempt_number,
        allowed_by_policy=allowed_by_policy,
    )
    return _safe_response(
        persistence_mode=_bridge_mode(str(result.get("storage_mode") or "")),
        postgres_write_attempted=_database_url_present(),
        postgres_write_result={"written": bool(result.get("durable")), "reason": result.get("status")},
        attempt=_compat_attempt(result.get("attempt") or {}),
    )


def persist_retry_history_bridge(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    attempt_number: int,
    failure_code: str,
    retry_allowed: bool,
    next_action: str,
) -> Dict[str, Any]:
    result = record_provider_retry(
        provider_job_id=worker_job_id,
        execution_id=execution_id,
        retry_reason=failure_code,
        attempt_number=attempt_number,
        retry_allowed=retry_allowed,
        next_action=next_action,
    )
    return _safe_response(
        persistence_mode=_bridge_mode(str(result.get("storage_mode") or "")),
        postgres_write_attempted=_database_url_present(),
        postgres_write_result={"written": bool(result.get("durable")), "reason": result.get("status")},
        retry=_compat_retry(result.get("retry") or {}),
    )


def persist_latency_metric_bridge(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    latency_ms: int,
    operation: str,
) -> Dict[str, Any]:
    result = record_provider_latency(
        provider=provider_key,
        capability=operation,
        latency_ms=latency_ms,
        status=operation,
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
    )
    return _safe_response(
        persistence_mode=_bridge_mode(str(result.get("storage_mode") or "")),
        postgres_write_attempted=_database_url_present(),
        postgres_write_result={"written": bool(result.get("durable")), "reason": result.get("status")},
        metric=_compat_latency(result.get("metric") or {}),
    )


def provider_postgres_bridge_summary() -> Dict[str, Any]:
    return _safe_response(status=provider_postgres_ledger_bridge_status(), summary=get_provider_admin_summary())


def reset_provider_postgres_bridge_fallback_for_tests() -> Dict[str, Any]:
    return reset_dev_provider_ledger_for_tests()


def postgres_read_provider_execution_records(*, tenant_id: Optional[str] = None, provider_key: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    listed = list_provider_execution_records(tenant_id=tenant_id or "", provider=provider_key or "", limit=limit)
    return _safe_response(
        read_mode=_bridge_mode(str(listed.get("storage_mode") or "")),
        postgres_read_attempted=_database_url_present(),
        records=listed.get("records", []),
        count=listed.get("count", 0),
    )


def postgres_read_worker_events(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    listed = list_provider_job_events(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    entries = [_compat_event(event) for event in listed.get("events", [])]
    return _safe_response(read_mode=_bridge_mode(str(listed.get("storage_mode") or "")), postgres_read_attempted=_database_url_present(), entries=entries, count=len(entries))


def postgres_read_dispatch_attempts(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    listed = list_provider_dispatch_attempts(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    records = [_compat_attempt(attempt) for attempt in listed.get("records", [])]
    return _safe_response(read_mode=_bridge_mode(str(listed.get("storage_mode") or "")), postgres_read_attempted=_database_url_present(), records=records, count=len(records))


def postgres_read_retry_history(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    listed = list_provider_retry_history(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    records = [_compat_retry(retry) for retry in listed.get("records", [])]
    return _safe_response(read_mode=_bridge_mode(str(listed.get("storage_mode") or "")), postgres_read_attempted=_database_url_present(), records=records, count=len(records))


def postgres_read_latency_metrics(*, tenant_id: Optional[str] = None, provider_key: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    listed = list_provider_latency_metrics(tenant_id=tenant_id or "", provider=provider_key or "", limit=limit)
    records = [_compat_latency(metric) for metric in listed.get("records", [])]
    return _safe_response(
        read_mode=_bridge_mode(str(listed.get("storage_mode") or "")),
        postgres_read_attempted=_database_url_present(),
        records=records,
        count=len(records),
        average_latency_ms=listed.get("average_latency_ms"),
        max_latency_ms=listed.get("max_latency_ms"),
        min_latency_ms=listed.get("min_latency_ms"),
    )


def provider_postgres_read_write_status() -> Dict[str, Any]:
    readiness = ensure_provider_ledger_tables()
    driver = detect_postgres_driver()
    return _safe_response(read_write_bridge_ready=bool(readiness.get("success")), database_url_present=_database_url_present(), postgres_driver_available=driver.get("driver_available", False), postgres_driver=driver.get("driver"), provider_execution_record_postgres_write_enabled=True, provider_execution_record_postgres_read_enabled=True, fallback_storage_active=bool(readiness.get("dev_only")))


def provider_postgres_extended_ledger_write_status() -> Dict[str, Any]:
    base = provider_postgres_read_write_status()
    base.update(
        extended_ledger_write_ready=bool(base.get("read_write_bridge_ready")),
        worker_event_postgres_write_enabled=True,
        dispatch_attempt_postgres_write_enabled=True,
        retry_history_postgres_write_enabled=True,
        latency_metric_postgres_write_enabled=True,
    )
    return base


def provider_postgres_extended_ledger_read_status() -> Dict[str, Any]:
    base = provider_postgres_read_write_status()
    base.update(
        extended_ledger_read_ready=bool(base.get("read_write_bridge_ready")),
        worker_event_postgres_read_enabled=True,
        dispatch_attempt_postgres_read_enabled=True,
        retry_history_postgres_read_enabled=True,
        latency_metric_postgres_read_enabled=True,
    )
    return base


def postgres_write_provider_execution_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_response(written=False, reason="use_persist_provider_execution_record_bridge", fallback_required=False)


def postgres_write_worker_event(entry: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_response(written=False, reason="use_persist_worker_event_bridge", fallback_required=False)


def postgres_write_dispatch_attempt(attempt: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_response(written=False, reason="use_persist_dispatch_attempt_bridge", fallback_required=False)


def postgres_write_retry_history(retry: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_response(written=False, reason="use_persist_retry_history_bridge", fallback_required=False)


def postgres_write_latency_metric(metric: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_response(written=False, reason="use_persist_latency_metric_bridge", fallback_required=False)
