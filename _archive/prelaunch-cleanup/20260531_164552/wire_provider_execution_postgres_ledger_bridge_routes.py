from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_execution_postgres_ledger_bridge_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_ledger_bridge_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution Postgres ledger bridge routes
# Added by wire_provider_execution_postgres_ledger_bridge_routes.py
# Purpose:
# - expose Postgres schema/readiness bridge
# - keep safe in-memory fallback active until DB driver/migration is enabled
# - never expose credentials
# ---------------------------------------------------------------------------

try:
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
except Exception:  # pragma: no cover
    apply_provider_ledger_schema_if_possible = None
    get_provider_ledger_schema_sql = None
    persist_dispatch_attempt_bridge = None
    persist_latency_metric_bridge = None
    persist_provider_execution_record_bridge = None
    persist_retry_history_bridge = None
    persist_worker_event_bridge = None
    provider_postgres_bridge_summary = None
    provider_postgres_ledger_bridge_status = None
    reset_provider_postgres_bridge_fallback_for_tests = None


@app.get("/provider-postgres-ledger-bridge/status")
def provider_postgres_ledger_bridge_status_route():
    if provider_postgres_ledger_bridge_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_ledger_bridge_status()


@app.get("/provider-postgres-ledger-bridge/schema")
def provider_postgres_ledger_bridge_schema_route():
    if get_provider_ledger_schema_sql is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return get_provider_ledger_schema_sql()


@app.post("/provider-postgres-ledger-bridge/apply-schema")
async def provider_postgres_ledger_bridge_apply_schema_route():
    if apply_provider_ledger_schema_if_possible is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return apply_provider_ledger_schema_if_possible()


@app.post("/provider-postgres-ledger-bridge/persist-execution-record")
async def provider_postgres_ledger_bridge_persist_execution_record_route(payload: dict):
    if persist_provider_execution_record_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_provider_execution_record_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.post("/provider-postgres-ledger-bridge/persist-worker-event")
async def provider_postgres_ledger_bridge_persist_worker_event_route(payload: dict):
    if persist_worker_event_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
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


@app.post("/provider-postgres-ledger-bridge/persist-dispatch-attempt")
async def provider_postgres_ledger_bridge_persist_dispatch_attempt_route(payload: dict):
    if persist_dispatch_attempt_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
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


@app.post("/provider-postgres-ledger-bridge/persist-retry-history")
async def provider_postgres_ledger_bridge_persist_retry_history_route(payload: dict):
    if persist_retry_history_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
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


@app.post("/provider-postgres-ledger-bridge/persist-latency-metric")
async def provider_postgres_ledger_bridge_persist_latency_metric_route(payload: dict):
    if persist_latency_metric_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
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


@app.get("/provider-postgres-ledger-bridge/summary")
def provider_postgres_ledger_bridge_summary_route():
    if provider_postgres_bridge_summary is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_bridge_summary()


@app.post("/provider-postgres-ledger-bridge/reset-for-tests")
async def provider_postgres_ledger_bridge_reset_for_tests_route():
    if reset_provider_postgres_bridge_fallback_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return reset_provider_postgres_bridge_fallback_for_tests()
'''

marker = "# Provider execution Postgres ledger bridge routes"
if marker in main_text:
    print("PROVIDER_POSTGRES_LEDGER_BRIDGE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_POSTGRES_LEDGER_BRIDGE_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

reset = client.post("/provider-postgres-ledger-bridge/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = client.get("/provider-postgres-ledger-bridge/status").json()
assert status["bridge_ready"] is True
assert status["database_url_present"] is False
assert status["in_memory_fallback_enabled"] is True
assert status["credential_values_exposed"] is False

schema = client.get("/provider-postgres-ledger-bridge/schema").json()
assert schema["schema_sql_present"] is True
assert "CREATE TABLE IF NOT EXISTS provider_execution_records" in schema["sql"]
assert schema["credential_values_exposed"] is False

apply_no_db = client.post("/provider-postgres-ledger-bridge/apply-schema").json()
assert apply_no_db["status"] == "skipped"
assert apply_no_db["reason"] == "DATABASE_URL_missing"
assert apply_no_db["fallback_storage_active"] is True

record_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-execution-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
record = record_bridge["record"]
assert record_bridge["persistence_mode"] == "in_memory_fallback"
assert record_bridge["postgres_write_attempted"] is False
assert record["execution_status"] == "created"

event_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True, "secret": "must-not-store"},
    },
).json()
assert event_bridge["entry"]["event_type"] == "worker_prepared"
assert "secret" not in event_bridge["entry"]["details"]

attempt_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_bridge["attempt"]["allowed_by_policy"] is False

retry_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_bridge["retry"]["retry_allowed"] is True

metric_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "provider_key": "openai",
        "latency_ms": 1234,
        "operation": "dispatch_prepare",
    },
).json()
assert metric_bridge["metric"]["latency_ms"] == 1234

summary = client.get("/provider-postgres-ledger-bridge/summary").json()
assert summary["execution_records"]["count"] == 1
assert summary["worker_events"]["count"] == 1
assert summary["dispatch_attempts"]["count"] == 1
assert summary["retry_history"]["count"] == 1
assert summary["latency_metrics"]["count"] == 1
assert summary["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-ledger-bridge/status").json()
assert status_with_db["database_url_present"] is True

apply_with_db = client.post("/provider-postgres-ledger-bridge/apply-schema").json()
assert apply_with_db["status"] == "prepared"
assert apply_with_db["reason"] == "DATABASE_URL_present_driver_application_pending"
assert apply_with_db["applied"] is False

print("PROVIDER_POSTGRES_LEDGER_BRIDGE_ROUTES_DIRECT_TESTS_PASSED")
print("database_url_present_initial", status["database_url_present"])
print("schema_available", schema["schema_sql_present"])
print("apply_without_db", apply_no_db["status"], apply_no_db["reason"])
print("record_mode", record_bridge["persistence_mode"])
print("summary_counts", summary["execution_records"]["count"], summary["worker_events"]["count"], summary["dispatch_attempts"]["count"], summary["retry_history"]["count"], summary["latency_metrics"]["count"])
print("database_url_present_after", status_with_db["database_url_present"])
print("apply_with_db", apply_with_db["status"], apply_with_db["reason"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_POSTGRES_LEDGER_BRIDGE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")
print("Postgres ledger bridge routes installed.")