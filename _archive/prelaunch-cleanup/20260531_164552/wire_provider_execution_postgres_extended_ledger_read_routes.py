from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_execution_postgres_extended_ledger_read_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_extended_read_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution Postgres extended ledger read routes
# Added by wire_provider_execution_postgres_extended_ledger_read_routes.py
# Purpose:
# - expose read views for worker events, dispatch attempts, retry history,
#   and latency metrics
# - preserve safe fallback when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        provider_postgres_extended_ledger_read_status,
        postgres_read_dispatch_attempts,
        postgres_read_latency_metrics,
        postgres_read_retry_history,
        postgres_read_worker_events,
    )
except Exception:  # pragma: no cover
    provider_postgres_extended_ledger_read_status = None
    postgres_read_dispatch_attempts = None
    postgres_read_latency_metrics = None
    postgres_read_retry_history = None
    postgres_read_worker_events = None


@app.get("/provider-postgres-extended-ledger-reads/status")
def provider_postgres_extended_ledger_read_status_route():
    if provider_postgres_extended_ledger_read_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_extended_ledger_read_status()


@app.get("/provider-postgres-extended-ledger-reads/worker-events")
def provider_postgres_extended_worker_events_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_worker_events is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_worker_events(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/dispatch-attempts")
def provider_postgres_extended_dispatch_attempts_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_dispatch_attempts is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_dispatch_attempts(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/retry-history")
def provider_postgres_extended_retry_history_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_retry_history is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_retry_history(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/latency-metrics")
def provider_postgres_extended_latency_metrics_read_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if postgres_read_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_latency_metrics(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )
'''

marker = "# Provider execution Postgres extended ledger read routes"
if marker in main_text:
    print("PROVIDER_POSTGRES_EXTENDED_LEDGER_READ_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_POSTGRES_EXTENDED_LEDGER_READ_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

status = client.get("/provider-postgres-extended-ledger-reads/status").json()
assert status["extended_ledger_read_ready"] is True
assert status["fallback_storage_active"] is True
assert status["credential_values_exposed"] is False

record = client.post(
    "/provider-postgres-read-write/execution-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
execution_id = record["record"]["execution_id"]

client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True},
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "provider_key": "openai",
        "latency_ms": 1500,
        "operation": "dispatch_prepare",
    },
)

events = client.get("/provider-postgres-extended-ledger-reads/worker-events?tenant_id=tenant-test").json()
assert events["count"] >= 1
assert events["postgres_read_attempted"] is False
assert events["credential_values_exposed"] is False

attempts = client.get("/provider-postgres-extended-ledger-reads/dispatch-attempts?tenant_id=tenant-test").json()
assert attempts["count"] >= 1
assert attempts["credential_values_exposed"] is False

retries = client.get("/provider-postgres-extended-ledger-reads/retry-history?tenant_id=tenant-test").json()
assert retries["count"] >= 1
assert retries["credential_values_exposed"] is False

latencies = client.get("/provider-postgres-extended-ledger-reads/latency-metrics?tenant_id=tenant-test&provider_key=openai").json()
assert latencies["count"] >= 1
assert latencies["average_latency_ms"] is not None
assert latencies["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

events_db = client.get("/provider-postgres-extended-ledger-reads/worker-events?tenant_id=tenant-test").json()
assert events_db["postgres_read_attempted"] is True
assert events_db["credential_values_exposed"] is False

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_READ_ROUTES_DIRECT_TESTS_PASSED")
print("events", events["count"])
print("attempts", attempts["count"])
print("retries", retries["count"])
print("latencies", latencies["count"], latencies["average_latency_ms"])
print("events_db_attempted", events_db["postgres_read_attempted"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_READ_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")