from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_execution_postgres_extended_ledger_write_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_extended_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution Postgres extended ledger write routes
# Added by wire_provider_execution_postgres_extended_ledger_write_routes.py
# Purpose:
# - expose DB-capable worker event, dispatch attempt, retry history,
#   and latency metric writes
# - preserve safe fallback when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        persist_dispatch_attempt_bridge,
        persist_latency_metric_bridge,
        persist_retry_history_bridge,
        persist_worker_event_bridge,
        provider_postgres_extended_ledger_write_status,
    )
except Exception:  # pragma: no cover
    persist_dispatch_attempt_bridge = None
    persist_latency_metric_bridge = None
    persist_retry_history_bridge = None
    persist_worker_event_bridge = None
    provider_postgres_extended_ledger_write_status = None


@app.get("/provider-postgres-extended-ledger-writes/status")
def provider_postgres_extended_ledger_write_status_route():
    if provider_postgres_extended_ledger_write_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_extended_ledger_write_status()


@app.post("/provider-postgres-extended-ledger-writes/worker-event")
async def provider_postgres_extended_worker_event_route(payload: dict):
    if persist_worker_event_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    details = safe_payload.get("details") or {}
    if not isinstance(details, dict):
        details = {}

    return persist_worker_event_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        event_type=safe_payload.get("event_type") or "provider_worker_event",
        status=safe_payload.get("status") or "created",
        details=details,
    )


@app.post("/provider-postgres-extended-ledger-writes/dispatch-attempt")
async def provider_postgres_extended_dispatch_attempt_route(payload: dict):
    if persist_dispatch_attempt_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_dispatch_attempt_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        allowed_by_policy=bool(safe_payload.get("allowed_by_policy", False)),
        result_status=safe_payload.get("result_status") or "blocked",
        reason=safe_payload.get("reason"),
    )


@app.post("/provider-postgres-extended-ledger-writes/retry-history")
async def provider_postgres_extended_retry_history_route(payload: dict):
    if persist_retry_history_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_retry_history_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        failure_code=safe_payload.get("failure_code") or "provider_error",
        retry_allowed=bool(safe_payload.get("retry_allowed", False)),
        next_action=safe_payload.get("next_action") or "owner_review_required",
    )


@app.post("/provider-postgres-extended-ledger-writes/latency-metric")
async def provider_postgres_extended_latency_metric_route(payload: dict):
    if persist_latency_metric_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_latency_metric_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        operation=safe_payload.get("operation") or "provider_operation",
    )
'''

marker = "# Provider execution Postgres extended ledger write routes"
if marker in main_text:
    print("PROVIDER_POSTGRES_EXTENDED_LEDGER_WRITE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_POSTGRES_EXTENDED_LEDGER_WRITE_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

status_no_db = client.get("/provider-postgres-extended-ledger-writes/status").json()
assert status_no_db["extended_ledger_write_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

event_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True, "secret": "must-not-store"},
    },
).json()
assert event_no_db["persistence_mode"] == "in_memory_fallback"
assert event_no_db["postgres_write_attempted"] is False
assert "secret" not in event_no_db["entry"]["details"]

attempt_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_no_db["persistence_mode"] == "in_memory_fallback"
assert attempt_no_db["postgres_write_attempted"] is False

retry_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_no_db["persistence_mode"] == "in_memory_fallback"

latency_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "provider_key": "openai",
        "latency_ms": 1234,
        "operation": "dispatch_prepare",
    },
).json()
assert latency_no_db["persistence_mode"] == "in_memory_fallback"

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-extended-ledger-writes/status").json()
assert status_with_db["database_url_present"] is True
assert status_with_db["credential_values_exposed"] is False

event_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True},
    },
).json()
assert event_bad_db["postgres_write_attempted"] is True
assert event_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}
assert event_bad_db["credential_values_exposed"] is False

attempt_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_bad_db["postgres_write_attempted"] is True

retry_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_bad_db["postgres_write_attempted"] is True

latency_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "provider_key": "openai",
        "latency_ms": 2222,
        "operation": "dispatch_prepare",
    },
).json()
assert latency_bad_db["postgres_write_attempted"] is True

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_WRITE_ROUTES_DIRECT_TESTS_PASSED")
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

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_WRITE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")