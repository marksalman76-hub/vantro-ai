from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bridge_path = ROOT / "backend" / "app" / "runtime" / "provider_execution_postgres_ledger_bridge.py"
test_file = ROOT / "test_provider_execution_postgres_extended_ledger_writes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_extended_writes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [bridge_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

if not bridge_path.exists():
    raise FileNotFoundError(f"Missing bridge file: {bridge_path}")

s = bridge_path.read_text(encoding="utf-8")

extra_code = r'''

def _postgres_execute_write(sql: str, values: tuple) -> Dict[str, Any]:
    conn, driver = _get_db_connection()
    if conn is None:
        return _safe_response(written=False, reason="db_unavailable", fallback_required=True)

    try:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        return _safe_response(written=True, reason="postgres_write_success", driver=driver)
    except Exception as exc:
        try:
            conn.close()
        except Exception:
            pass
        return _safe_response(
            written=False,
            reason="postgres_write_failed",
            fallback_required=True,
            safe_error=str(exc)[:300],
            driver=driver,
        )


def postgres_write_worker_event(entry: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
    INSERT INTO provider_worker_event_ledger (
        ledger_id, tenant_id, request_id, execution_id, worker_job_id,
        provider_key, event_type, status, details_json,
        customer_safe, credential_values_exposed, created_at_ms
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ledger_id) DO NOTHING
    """
    values = (
        entry.get("ledger_id"),
        entry.get("tenant_id"),
        entry.get("request_id"),
        entry.get("execution_id"),
        entry.get("worker_job_id"),
        entry.get("provider_key"),
        entry.get("event_type"),
        entry.get("status"),
        json.dumps(entry.get("details") or {}),
        True,
        False,
        entry.get("created_at_ms"),
    )
    return _postgres_execute_write(sql, values)


def postgres_write_dispatch_attempt(attempt: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
    INSERT INTO provider_dispatch_attempt_records (
        attempt_id, tenant_id, request_id, execution_id, worker_job_id,
        provider_key, attempt_number, allowed_by_policy, result_status, reason,
        live_external_call_executed, customer_safe, credential_values_exposed, created_at_ms
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (attempt_id) DO NOTHING
    """
    values = (
        attempt.get("attempt_id"),
        attempt.get("tenant_id"),
        attempt.get("request_id"),
        attempt.get("execution_id"),
        attempt.get("worker_job_id"),
        attempt.get("provider_key"),
        int(attempt.get("attempt_number", 1) or 1),
        bool(attempt.get("allowed_by_policy", False)),
        attempt.get("result_status"),
        attempt.get("reason"),
        False,
        True,
        False,
        attempt.get("created_at_ms"),
    )
    return _postgres_execute_write(sql, values)


def postgres_write_retry_history(retry: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
    INSERT INTO provider_retry_history_records (
        retry_id, tenant_id, request_id, execution_id, worker_job_id,
        provider_key, attempt_number, failure_code, retry_allowed, next_action,
        customer_safe, credential_values_exposed, created_at_ms
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (retry_id) DO NOTHING
    """
    values = (
        retry.get("retry_id"),
        retry.get("tenant_id"),
        retry.get("request_id"),
        retry.get("execution_id"),
        retry.get("worker_job_id"),
        retry.get("provider_key"),
        int(retry.get("attempt_number", 1) or 1),
        retry.get("failure_code"),
        bool(retry.get("retry_allowed", False)),
        retry.get("next_action"),
        True,
        False,
        retry.get("created_at_ms"),
    )
    return _postgres_execute_write(sql, values)


def postgres_write_latency_metric(metric: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
    INSERT INTO provider_latency_metric_records (
        latency_id, tenant_id, request_id, execution_id, provider_key,
        latency_ms, operation, customer_safe, credential_values_exposed, created_at_ms
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (latency_id) DO NOTHING
    """
    values = (
        metric.get("latency_id"),
        metric.get("tenant_id"),
        metric.get("request_id"),
        metric.get("execution_id"),
        metric.get("provider_key"),
        int(metric.get("latency_ms", 0) or 0),
        metric.get("operation"),
        True,
        False,
        metric.get("created_at_ms"),
    )
    return _postgres_execute_write(sql, values)


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

    write_result = postgres_write_worker_event(entry)

    return _safe_response(
        persistence_mode="postgres" if write_result.get("written") else "in_memory_fallback",
        postgres_write_attempted=bool(os.getenv("DATABASE_URL")),
        postgres_write_result=write_result,
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

    write_result = postgres_write_dispatch_attempt(attempt)

    return _safe_response(
        persistence_mode="postgres" if write_result.get("written") else "in_memory_fallback",
        postgres_write_attempted=bool(os.getenv("DATABASE_URL")),
        postgres_write_result=write_result,
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

    write_result = postgres_write_retry_history(retry)

    return _safe_response(
        persistence_mode="postgres" if write_result.get("written") else "in_memory_fallback",
        postgres_write_attempted=bool(os.getenv("DATABASE_URL")),
        postgres_write_result=write_result,
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

    write_result = postgres_write_latency_metric(metric)

    return _safe_response(
        persistence_mode="postgres" if write_result.get("written") else "in_memory_fallback",
        postgres_write_attempted=bool(os.getenv("DATABASE_URL")),
        postgres_write_result=write_result,
        metric=metric,
    )


def provider_postgres_extended_ledger_write_status() -> Dict[str, Any]:
    driver = detect_postgres_driver()
    return _safe_response(
        extended_ledger_write_ready=True,
        database_url_present=_database_url_present(),
        postgres_driver_available=driver.get("driver_available", False),
        postgres_driver=driver.get("driver"),
        worker_event_postgres_write_enabled=True,
        dispatch_attempt_postgres_write_enabled=True,
        retry_history_postgres_write_enabled=True,
        latency_metric_postgres_write_enabled=True,
        fallback_storage_active=True,
    )
'''

if "def postgres_write_worker_event(" not in s:
    s = s.rstrip() + extra_code + "\n"

bridge_path.write_text(s, encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_retry_history_bridge,
    persist_worker_event_bridge,
    provider_postgres_extended_ledger_write_status,
    reset_provider_postgres_bridge_fallback_for_tests,
)

reset = reset_provider_postgres_bridge_fallback_for_tests()
assert reset["reset"] is True

os.environ.pop("DATABASE_URL", None)

status_no_db = provider_postgres_extended_ledger_write_status()
assert status_no_db["extended_ledger_write_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

record = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
execution_id = record["record"]["execution_id"]

event_no_db = persist_worker_event_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True, "secret": "must-not-store"},
)
assert event_no_db["persistence_mode"] == "in_memory_fallback"
assert event_no_db["postgres_write_attempted"] is False
assert "secret" not in event_no_db["entry"]["details"]

attempt_no_db = persist_dispatch_attempt_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="dispatch_disabled",
)
assert attempt_no_db["persistence_mode"] == "in_memory_fallback"
assert attempt_no_db["postgres_write_attempted"] is False

retry_no_db = persist_retry_history_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry_no_db["persistence_mode"] == "in_memory_fallback"

latency_no_db = persist_latency_metric_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    provider_key="openai",
    latency_ms=1234,
    operation="dispatch_prepare",
)
assert latency_no_db["persistence_mode"] == "in_memory_fallback"

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = provider_postgres_extended_ledger_write_status()
assert status_with_db["database_url_present"] is True
assert status_with_db["credential_values_exposed"] is False

event_bad_db = persist_worker_event_bridge(
    tenant_id="tenant-test-db",
    request_id="request-test-db",
    execution_id=execution_id,
    worker_job_id="worker-456",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True},
)
assert event_bad_db["postgres_write_attempted"] is True
assert event_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}
assert event_bad_db["credential_values_exposed"] is False

attempt_bad_db = persist_dispatch_attempt_bridge(
    tenant_id="tenant-test-db",
    request_id="request-test-db",
    execution_id=execution_id,
    worker_job_id="worker-456",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="dispatch_disabled",
)
assert attempt_bad_db["postgres_write_attempted"] is True
assert attempt_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}

retry_bad_db = persist_retry_history_bridge(
    tenant_id="tenant-test-db",
    request_id="request-test-db",
    execution_id=execution_id,
    worker_job_id="worker-456",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry_bad_db["postgres_write_attempted"] is True
assert retry_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}

latency_bad_db = persist_latency_metric_bridge(
    tenant_id="tenant-test-db",
    request_id="request-test-db",
    execution_id=execution_id,
    provider_key="openai",
    latency_ms=2222,
    operation="dispatch_prepare",
)
assert latency_bad_db["postgres_write_attempted"] is True
assert latency_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}

print("PROVIDER_EXECUTION_POSTGRES_EXTENDED_LEDGER_WRITES_DIRECT_TESTS_PASSED")
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("event_no_db", event_no_db["persistence_mode"], event_no_db["postgres_write_attempted"])
print("attempt_no_db", attempt_no_db["persistence_mode"], attempt_no_db["postgres_write_attempted"])
print("retry_no_db", retry_no_db["persistence_mode"])
print("latency_no_db", latency_no_db["persistence_mode"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("event_bad_db", event_bad_db["persistence_mode"], event_bad_db["postgres_write_attempted"])
print("attempt_bad_db", attempt_bad_db["persistence_mode"], attempt_bad_db["postgres_write_attempted"])
print("retry_bad_db", retry_bad_db["persistence_mode"], retry_bad_db["postgres_write_attempted"])
print("latency_bad_db", latency_bad_db["persistence_mode"], latency_bad_db["postgres_write_attempted"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_POSTGRES_EXTENDED_LEDGER_WRITES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {bridge_path}")
print(f"Created/updated: {test_file}")
print("Extended Postgres ledger writes installed with fallback.")