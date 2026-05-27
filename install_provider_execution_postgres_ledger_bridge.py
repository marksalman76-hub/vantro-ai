from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

sql_dir = ROOT / "backend" / "sql"
sql_dir.mkdir(parents=True, exist_ok=True)

bridge_path = runtime_dir / "provider_execution_postgres_ledger_bridge.py"
sql_path = sql_dir / "provider_execution_ledger_schema.sql"
test_file = ROOT / "test_provider_execution_postgres_ledger_bridge_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_ledger_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [bridge_path, sql_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

sql_path.write_text(r'''
CREATE TABLE IF NOT EXISTS provider_execution_records (
    execution_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    task_type TEXT NOT NULL,
    execution_status TEXT NOT NULL,
    worker_job_id TEXT,
    provider_job_id TEXT,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL,
    updated_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_worker_event_ledger (
    ledger_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details_json TEXT,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_dispatch_attempt_records (
    attempt_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    allowed_by_policy BOOLEAN DEFAULT FALSE,
    result_status TEXT NOT NULL,
    reason TEXT,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_retry_history_records (
    retry_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    failure_code TEXT NOT NULL,
    retry_allowed BOOLEAN DEFAULT FALSE,
    next_action TEXT NOT NULL,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_latency_metric_records (
    latency_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    operation TEXT NOT NULL,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_provider_execution_records_tenant_id ON provider_execution_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_provider_execution_records_provider_key ON provider_execution_records(provider_key);
CREATE INDEX IF NOT EXISTS idx_provider_worker_event_ledger_tenant_id ON provider_worker_event_ledger(tenant_id);
CREATE INDEX IF NOT EXISTS idx_provider_worker_event_ledger_execution_id ON provider_worker_event_ledger(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_dispatch_attempt_records_execution_id ON provider_dispatch_attempt_records(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_retry_history_records_execution_id ON provider_retry_history_records(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_latency_metric_records_tenant_provider ON provider_latency_metric_records(tenant_id, provider_key);
'''.lstrip(), encoding="utf-8")

bridge_path.write_text(r'''
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


SQL_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql" / "provider_execution_ledger_schema.sql"


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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    apply_provider_ledger_schema_if_possible,
    get_provider_ledger_schema_sql,
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_retry_history_bridge,
    persist_worker_event_bridge,
    provider_postgres_bridge_summary,
    provider_postgres_ledger_bridge_status,
    reset_provider_postgres_bridge_fallback_for_tests,
)

os.environ.pop("DATABASE_URL", None)

reset = reset_provider_postgres_bridge_fallback_for_tests()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = provider_postgres_ledger_bridge_status()
assert status["bridge_ready"] is True
assert status["database_url_present"] is False
assert status["in_memory_fallback_enabled"] is True
assert status["credential_values_exposed"] is False

schema = get_provider_ledger_schema_sql()
assert schema["schema_sql_present"] is True
assert "CREATE TABLE IF NOT EXISTS provider_execution_records" in schema["sql"]
assert schema["credential_values_exposed"] is False

applied = apply_provider_ledger_schema_if_possible()
assert applied["status"] == "skipped"
assert applied["reason"] == "DATABASE_URL_missing"
assert applied["fallback_storage_active"] is True

record_bridge = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
record = record_bridge["record"]
assert record_bridge["persistence_mode"] == "in_memory_fallback"
assert record_bridge["postgres_write_attempted"] is False
assert record["execution_status"] == "created"

event_bridge = persist_worker_event_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True, "secret": "must-not-store"},
)
assert event_bridge["entry"]["event_type"] == "worker_prepared"
assert "secret" not in event_bridge["entry"]["details"]

attempt_bridge = persist_dispatch_attempt_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="dispatch_disabled",
)
assert attempt_bridge["attempt"]["allowed_by_policy"] is False

retry_bridge = persist_retry_history_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry_bridge["retry"]["retry_allowed"] is True

metric_bridge = persist_latency_metric_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    provider_key="openai",
    latency_ms=1234,
    operation="dispatch_prepare",
)
assert metric_bridge["metric"]["latency_ms"] == 1234

summary = provider_postgres_bridge_summary()
assert summary["execution_records"]["count"] == 1
assert summary["worker_events"]["count"] == 1
assert summary["dispatch_attempts"]["count"] == 1
assert summary["retry_history"]["count"] == 1
assert summary["latency_metrics"]["count"] == 1
assert summary["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"
status_with_db = provider_postgres_ledger_bridge_status()
assert status_with_db["database_url_present"] is True

prepared = apply_provider_ledger_schema_if_possible()
assert prepared["status"] == "prepared"
assert prepared["reason"] == "DATABASE_URL_present_driver_application_pending"
assert prepared["applied"] is False

print("PROVIDER_EXECUTION_POSTGRES_LEDGER_BRIDGE_DIRECT_TESTS_PASSED")
print("database_url_present_initial", status["database_url_present"])
print("schema_available", schema["schema_sql_present"])
print("apply_without_db", applied["status"], applied["reason"])
print("record_mode", record_bridge["persistence_mode"])
print("summary_counts", summary["execution_records"]["count"], summary["worker_events"]["count"], summary["dispatch_attempts"]["count"], summary["retry_history"]["count"], summary["latency_metrics"]["count"])
print("database_url_present_after", status_with_db["database_url_present"])
print("apply_with_db", prepared["status"], prepared["reason"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_POSTGRES_LEDGER_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {bridge_path}")
print(f"Created/updated: {sql_path}")
print(f"Created/updated: {test_file}")
print("Postgres schema + safe fallback bridge installed.")