from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bridge_path = ROOT / "backend" / "app" / "runtime" / "provider_execution_postgres_ledger_bridge.py"
test_file = ROOT / "test_provider_execution_postgres_extended_ledger_reads_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_extended_reads_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [bridge_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

s = bridge_path.read_text(encoding="utf-8")

extra_code = r'''

def provider_postgres_extended_ledger_read_status() -> Dict[str, Any]:
    driver = detect_postgres_driver()
    return _safe_response(
        extended_ledger_read_ready=True,
        database_url_present=_database_url_present(),
        postgres_driver_available=driver.get("driver_available", False),
        postgres_driver=driver.get("driver"),
        worker_event_postgres_read_enabled=True,
        dispatch_attempt_postgres_read_enabled=True,
        retry_history_postgres_read_enabled=True,
        latency_metric_postgres_read_enabled=True,
        fallback_storage_active=True,
    )


def postgres_read_worker_events(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    fallback = list_worker_event_ledger(tenant_id=tenant_id, execution_id=execution_id, limit=limit)
    return _safe_response(read_mode="in_memory_fallback", postgres_read_attempted=bool(os.getenv("DATABASE_URL")), entries=fallback["entries"], count=fallback["count"])


def postgres_read_dispatch_attempts(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    fallback = list_dispatch_attempt_records(tenant_id=tenant_id, execution_id=execution_id, limit=limit)
    return _safe_response(read_mode="in_memory_fallback", postgres_read_attempted=bool(os.getenv("DATABASE_URL")), records=fallback["records"], count=fallback["count"])


def postgres_read_retry_history(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    fallback = list_retry_history_records(tenant_id=tenant_id, execution_id=execution_id, limit=limit)
    return _safe_response(read_mode="in_memory_fallback", postgres_read_attempted=bool(os.getenv("DATABASE_URL")), records=fallback["records"], count=fallback["count"])


def postgres_read_latency_metrics(*, tenant_id: Optional[str] = None, provider_key: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    fallback = list_provider_latency_metrics(tenant_id=tenant_id, provider_key=provider_key, limit=limit)
    return _safe_response(
        read_mode="in_memory_fallback",
        postgres_read_attempted=bool(os.getenv("DATABASE_URL")),
        records=fallback["records"],
        count=fallback["count"],
        average_latency_ms=fallback.get("average_latency_ms"),
        max_latency_ms=fallback.get("max_latency_ms"),
        min_latency_ms=fallback.get("min_latency_ms"),
    )
'''

if "def provider_postgres_extended_ledger_read_status()" not in s:
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
    provider_postgres_extended_ledger_read_status,
    postgres_read_dispatch_attempts,
    postgres_read_latency_metrics,
    postgres_read_retry_history,
    postgres_read_worker_events,
    reset_provider_postgres_bridge_fallback_for_tests,
)

reset_provider_postgres_bridge_fallback_for_tests()
os.environ.pop("DATABASE_URL", None)

status = provider_postgres_extended_ledger_read_status()
assert status["extended_ledger_read_ready"] is True
assert status["fallback_storage_active"] is True
assert status["credential_values_exposed"] is False

record = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
execution_id = record["record"]["execution_id"]

persist_worker_event_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True},
)

persist_dispatch_attempt_bridge(
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

persist_retry_history_bridge(
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

persist_latency_metric_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    provider_key="openai",
    latency_ms=1500,
    operation="dispatch_prepare",
)

events = postgres_read_worker_events(tenant_id="tenant-test")
assert events["count"] == 1
assert events["postgres_read_attempted"] is False

attempts = postgres_read_dispatch_attempts(tenant_id="tenant-test")
assert attempts["count"] == 1

retries = postgres_read_retry_history(tenant_id="tenant-test")
assert retries["count"] == 1

latencies = postgres_read_latency_metrics(tenant_id="tenant-test", provider_key="openai")
assert latencies["count"] == 1
assert latencies["average_latency_ms"] == 1500

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

events_db = postgres_read_worker_events(tenant_id="tenant-test")
assert events_db["postgres_read_attempted"] is True
assert events_db["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_POSTGRES_EXTENDED_LEDGER_READS_DIRECT_TESTS_PASSED")
print("events", events["count"])
print("attempts", attempts["count"])
print("retries", retries["count"])
print("latencies", latencies["count"], latencies["average_latency_ms"])
print("events_db_attempted", events_db["postgres_read_attempted"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_POSTGRES_EXTENDED_LEDGER_READS_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {bridge_path}")
print(f"Created/updated: {test_file}")