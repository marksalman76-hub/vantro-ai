from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.runtime.provider_execution_persistence_ledger import (
    append_worker_event_ledger_entry,
    create_provider_execution_record,
    list_dispatch_attempt_records,
    list_provider_execution_records,
    list_provider_latency_metrics,
    list_retry_history_records,
    list_worker_event_ledger,
    provider_execution_persistence_status,
    record_dispatch_attempt,
    record_provider_latency_metric,
    record_retry_history,
    reset_provider_execution_ledger_for_tests,
)


SQL_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "provider_execution_ledger_schema.sql"


def _database_url_present() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def _safe_response(**kwargs: Any) -> Dict[str, Any]:
    payload = dict(kwargs)
    payload["credential_values_exposed"] = False
    payload["customer_safe"] = True
    return payload


def provider_postgres_ledger_bridge_status() -> Dict[str, Any]:
    return _safe_response(
        bridge_ready=True,
        database_url_present=_database_url_present(),
        postgres_schema_path=str(SQL_SCHEMA_PATH),
        postgres_binding_mode="safe_fallback_until_db_driver_enabled",
        in_memory_fallback_enabled=True,
        current_fallback_status=provider_execution_persistence_status(),
    )


def get_provider_ledger_schema_sql() -> Dict[str, Any]:
    if not SQL_SCHEMA_PATH.exists():
        return _safe_response(
            status="missing",
            schema_sql_present=False,
            sql="",
        )

    return _safe_response(
        status="available",
        schema_sql_present=True,
        sql=SQL_SCHEMA_PATH.read_text(encoding="utf-8"),
    )


def apply_provider_ledger_schema_if_possible() -> Dict[str, Any]:
    if not _database_url_present():
        return _safe_response(
            status="skipped",
            reason="DATABASE_URL_missing",
            applied=False,
            fallback_storage_active=True,
        )

    # Intentionally not opening DB connection here yet.
    # This bridge is DB-ready but driver-safe. Actual application should be wired
    # only after confirming the installed DB driver and production migration policy.
    return _safe_response(
        status="prepared",
        reason="DATABASE_URL_present_driver_application_pending",
        applied=False,
        fallback_storage_active=True,
    )


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
    record = create_provider_execution_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        execution_status=execution_status,
        worker_job_id=worker_job_id,
        provider_job_id=provider_job_id,
    )

    return _safe_response(
        persistence_mode="in_memory_fallback",
        postgres_write_attempted=False,
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
    entry = append_worker_event_ledger_entry(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        event_type=event_type,
        status=status,
        details=details,
    )

    return _safe_response(
        persistence_mode="in_memory_fallback",
        postgres_write_attempted=False,
        entry=entry,
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
    attempt = record_dispatch_attempt(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        attempt_number=attempt_number,
        allowed_by_policy=allowed_by_policy,
        result_status=result_status,
        reason=reason,
    )

    return _safe_response(
        persistence_mode="in_memory_fallback",
        postgres_write_attempted=False,
        attempt=attempt,
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
    retry = record_retry_history(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        attempt_number=attempt_number,
        failure_code=failure_code,
        retry_allowed=retry_allowed,
        next_action=next_action,
    )

    return _safe_response(
        persistence_mode="in_memory_fallback",
        postgres_write_attempted=False,
        retry=retry,
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
    metric = record_provider_latency_metric(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key=provider_key,
        latency_ms=latency_ms,
        operation=operation,
    )

    return _safe_response(
        persistence_mode="in_memory_fallback",
        postgres_write_attempted=False,
        metric=metric,
    )


def provider_postgres_bridge_summary() -> Dict[str, Any]:
    return _safe_response(
        status=provider_postgres_ledger_bridge_status(),
        execution_records=list_provider_execution_records(limit=10),
        worker_events=list_worker_event_ledger(limit=10),
        dispatch_attempts=list_dispatch_attempt_records(limit=10),
        retry_history=list_retry_history_records(limit=10),
        latency_metrics=list_provider_latency_metrics(limit=10),
    )


def reset_provider_postgres_bridge_fallback_for_tests() -> Dict[str, Any]:
    return reset_provider_execution_ledger_for_tests()

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


def apply_provider_ledger_schema_with_driver() -> Dict[str, Any]:
    if not _database_url_present():
        return _safe_response(
            status="skipped",
            reason="DATABASE_URL_missing",
            applied=False,
            fallback_storage_active=True,
        )

    schema = get_provider_ledger_schema_sql()
    if not schema.get("schema_sql_present"):
        return _safe_response(
            status="failed",
            reason="schema_sql_missing",
            applied=False,
            fallback_storage_active=True,
        )

    driver = detect_postgres_driver()
    if not driver.get("driver_available"):
        return _safe_response(
            status="skipped",
            reason="postgres_driver_missing",
            applied=False,
            fallback_storage_active=True,
            database_url_present=True,
        )

    database_url = os.getenv("DATABASE_URL")
    sql = schema["sql"]

    try:
        if driver["driver"] == "psycopg":
            import psycopg  # type: ignore
            with psycopg.connect(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()

        elif driver["driver"] == "psycopg2":
            import psycopg2  # type: ignore
            conn = psycopg2.connect(database_url)
            try:
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                cur.close()
            finally:
                conn.close()
        else:
            return _safe_response(
                status="skipped",
                reason="unsupported_driver",
                applied=False,
                fallback_storage_active=True,
            )

        return _safe_response(
            status="applied",
            reason="schema_applied_successfully",
            applied=True,
            fallback_storage_active=True,
            driver=driver["driver"],
        )

    except Exception as exc:
        return _safe_response(
            status="failed",
            reason="schema_apply_failed",
            applied=False,
            fallback_storage_active=True,
            driver=driver.get("driver"),
            safe_error=str(exc)[:300],
        )


def provider_postgres_migration_apply_status() -> Dict[str, Any]:
    driver = detect_postgres_driver()
    return _safe_response(
        migration_apply_ready=True,
        database_url_present=_database_url_present(),
        schema_sql_present=get_provider_ledger_schema_sql().get("schema_sql_present", False),
        postgres_driver_available=driver.get("driver_available", False),
        postgres_driver=driver.get("driver"),
        fallback_storage_active=True,
        credential_values_exposed=False,
    )

