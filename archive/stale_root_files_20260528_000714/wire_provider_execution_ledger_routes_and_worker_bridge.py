from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
worker_path = ROOT / "backend" / "app" / "runtime" / "provider_dispatch_policy_worker_foundation.py"
test_file = ROOT / "test_provider_execution_ledger_routes_worker_bridge_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_ledger_routes_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [main_path, worker_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")
if not worker_path.exists():
    raise FileNotFoundError(f"Missing worker runtime: {worker_path}")

main_text = main_path.read_text(encoding="utf-8")
worker_text = worker_path.read_text(encoding="utf-8")

bridge_import = r'''from backend.app.runtime.provider_execution_persistence_ledger import (
    append_worker_event_ledger_entry,
    create_provider_execution_record,
    record_dispatch_attempt,
    record_provider_latency_metric,
    record_retry_history,
    update_provider_execution_record,
)
'''

if "provider_execution_persistence_ledger import" not in worker_text:
    worker_text = worker_text.replace(
        "from backend.app.runtime.real_provider_http_execution_layer import execute_real_provider_http_request\n",
        "from backend.app.runtime.real_provider_http_execution_layer import execute_real_provider_http_request\n" + bridge_import,
    )

old_create_return = r'''    return {
        "worker_job_id": worker_job_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "worker_state": worker_state,
        "next_action": next_action,
        "bridge_packet": bridge_packet,
        "dispatch_policy": policy,
        "timeline_event": timeline_event,
        "live_external_call_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at_ms": _now_ms(),
    }'''

new_create_return = r'''    execution_record = create_provider_execution_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        execution_status=worker_state,
        worker_job_id=worker_job_id,
    )

    ledger_entry = append_worker_event_ledger_entry(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_record["execution_id"],
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        event_type="provider_worker_job_prepared",
        status=worker_state,
        details={"next_action": next_action},
    )

    dispatch_attempt = record_dispatch_attempt(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_record["execution_id"],
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        attempt_number=1,
        allowed_by_policy=policy["dispatch_allowed"],
        result_status=worker_state,
        reason=policy["reason"],
    )

    latency_metric = record_provider_latency_metric(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_record["execution_id"],
        provider_key=provider_key,
        latency_ms=int(policy.get("http_packet", {}).get("latency_ms", 0) or 0),
        operation="worker_dispatch_policy_evaluation",
    )

    return {
        "worker_job_id": worker_job_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "worker_state": worker_state,
        "next_action": next_action,
        "bridge_packet": bridge_packet,
        "dispatch_policy": policy,
        "timeline_event": timeline_event,
        "execution_record": execution_record,
        "ledger_entry": ledger_entry,
        "dispatch_attempt": dispatch_attempt,
        "latency_metric": latency_metric,
        "live_external_call_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at_ms": _now_ms(),
    }'''

if old_create_return in worker_text and "execution_record = create_provider_execution_record(" not in worker_text:
    worker_text = worker_text.replace(old_create_return, new_create_return)

old_advance_return = r'''    return {
        "worker_job_id": worker_job_id,
        "previous_state": current_state,
        "next_state": next_state,
        "next_action": next_action,
        "timeline_event": timeline_event,
        "live_external_call_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "updated_at_ms": _now_ms(),
    }'''

new_advance_return = r'''    synthetic_execution = create_provider_execution_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type="provider_worker_advance",
        execution_status=next_state,
        worker_job_id=worker_job_id,
    )

    ledger_entry = append_worker_event_ledger_entry(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=synthetic_execution["execution_id"],
        worker_job_id=worker_job_id,
        provider_key=provider_key,
        event_type="provider_worker_job_advanced",
        status=next_state,
        details={
            "previous_state": current_state,
            "next_action": next_action,
        },
    )

    retry_record = None
    if failure_code:
        retry_record = record_retry_history(
            tenant_id=tenant_id,
            request_id=request_id,
            execution_id=synthetic_execution["execution_id"],
            worker_job_id=worker_job_id,
            provider_key=provider_key,
            attempt_number=attempt_count,
            failure_code=failure_code,
            retry_allowed=next_state == "retry_queued",
            next_action=next_action,
        )

    update_provider_execution_record(
        execution_id=synthetic_execution["execution_id"],
        execution_status=next_state,
        worker_job_id=worker_job_id,
    )

    return {
        "worker_job_id": worker_job_id,
        "previous_state": current_state,
        "next_state": next_state,
        "next_action": next_action,
        "timeline_event": timeline_event,
        "execution_record": synthetic_execution,
        "ledger_entry": ledger_entry,
        "retry_record": retry_record,
        "live_external_call_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "updated_at_ms": _now_ms(),
    }'''

if old_advance_return in worker_text and "synthetic_execution = create_provider_execution_record(" not in worker_text:
    worker_text = worker_text.replace(old_advance_return, new_advance_return)

worker_path.write_text(worker_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution persistence ledger routes
# Added by wire_provider_execution_ledger_routes_and_worker_bridge.py
# Purpose:
# - expose execution records, worker ledger, dispatch attempts, retry history,
#   and latency metrics
# - use safe in-memory fallback until Postgres binding is added
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_persistence_ledger import (
        append_worker_event_ledger_entry,
        create_provider_execution_record,
        get_provider_execution_record,
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
        update_provider_execution_record,
    )
except Exception:  # pragma: no cover
    append_worker_event_ledger_entry = None
    create_provider_execution_record = None
    get_provider_execution_record = None
    list_dispatch_attempt_records = None
    list_provider_execution_records = None
    list_provider_latency_metrics = None
    list_retry_history_records = None
    list_worker_event_ledger = None
    provider_execution_persistence_status = None
    record_dispatch_attempt = None
    record_provider_latency_metric = None
    record_retry_history = None
    reset_provider_execution_ledger_for_tests = None
    update_provider_execution_record = None


@app.get("/provider-execution-ledger/status")
def provider_execution_ledger_status_route():
    if provider_execution_persistence_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_execution_persistence_status()


@app.post("/provider-execution-ledger/create-record")
async def provider_execution_ledger_create_record_route(payload: dict):
    if create_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    safe_payload = dict(payload or {})
    return create_provider_execution_record(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.post("/provider-execution-ledger/update-record/{execution_id}")
async def provider_execution_ledger_update_record_route(execution_id: str, payload: dict):
    if update_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    safe_payload = dict(payload or {})
    return update_provider_execution_record(
        execution_id=execution_id,
        execution_status=safe_payload.get("execution_status"),
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
        extra=safe_payload.get("extra"),
    )


@app.get("/provider-execution-ledger/record/{execution_id}")
def provider_execution_ledger_get_record_route(execution_id: str):
    if get_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return get_provider_execution_record(execution_id)


@app.get("/provider-execution-ledger/records")
def provider_execution_ledger_list_records_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 50,
):
    if list_provider_execution_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_provider_execution_records(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/worker-events")
def provider_execution_ledger_worker_events_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_worker_event_ledger is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_worker_event_ledger(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/dispatch-attempts")
def provider_execution_ledger_dispatch_attempts_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_dispatch_attempt_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_dispatch_attempt_records(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/retry-history")
def provider_execution_ledger_retry_history_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_retry_history_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_retry_history_records(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/latency-metrics")
def provider_execution_ledger_latency_metrics_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if list_provider_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_provider_latency_metrics(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/provider-execution-ledger/reset-for-tests")
async def provider_execution_ledger_reset_for_tests_route():
    if reset_provider_execution_ledger_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return reset_provider_execution_ledger_for_tests()
'''

marker = "# Provider execution persistence ledger routes"
if marker in main_text:
    print("PROVIDER_EXECUTION_LEDGER_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_EXECUTION_LEDGER_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

reset = client.post("/provider-execution-ledger/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

initial = client.get("/provider-execution-ledger/status").json()
assert initial["persistence_runtime_ready"] is True
assert initial["storage_mode"] == "in_memory_safe_fallback"
assert initial["execution_record_count"] == 0

created = client.post(
    "/provider-execution-ledger/create-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
assert created["execution_status"] == "created"
assert created["credential_values_exposed"] is False

updated = client.post(
    f"/provider-execution-ledger/update-record/{created['execution_id']}",
    json={
        "execution_status": "dispatch_blocked",
        "provider_job_id": "provider-job-123",
        "extra": {
            "safe_note": "ok",
            "api_key": "must-not-store",
            "token": "must-not-store",
        },
    },
).json()
assert updated["execution_status"] == "dispatch_blocked"
assert "api_key" not in updated.get("extra", {})
assert "token" not in updated.get("extra", {})

fetched = client.get(f"/provider-execution-ledger/record/{created['execution_id']}").json()
assert fetched["execution_id"] == created["execution_id"]

records = client.get("/provider-execution-ledger/records?tenant_id=tenant-test").json()
assert records["count"] == 1

worker_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-worker-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert "execution_record" in worker_blocked
assert "ledger_entry" in worker_blocked
assert "dispatch_attempt" in worker_blocked
assert "latency_metric" in worker_blocked
assert worker_blocked["credential_values_exposed"] is False

worker_events = client.get("/provider-execution-ledger/worker-events?tenant_id=tenant-test").json()
assert worker_events["count"] >= 1

attempts = client.get("/provider-execution-ledger/dispatch-attempts?tenant_id=tenant-test").json()
assert attempts["count"] >= 1

latencies = client.get("/provider-execution-ledger/latency-metrics?tenant_id=tenant-test&provider_key=openai").json()
assert latencies["count"] >= 1

advanced_retry = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": worker_blocked["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-worker-test",
        "current_state": "dispatch_blocked",
        "attempt_count": 1,
        "failure_code": "provider_timeout",
    },
).json()
assert advanced_retry["next_state"] == "retry_queued"
assert "execution_record" in advanced_retry
assert "ledger_entry" in advanced_retry
assert "retry_record" in advanced_retry
assert advanced_retry["credential_values_exposed"] is False

retries = client.get("/provider-execution-ledger/retry-history?tenant_id=tenant-test").json()
assert retries["count"] >= 1

final = client.get("/provider-execution-ledger/status").json()
assert final["execution_record_count"] >= 3
assert final["worker_event_count"] >= 2
assert final["dispatch_attempt_count"] >= 1
assert final["retry_history_count"] >= 1
assert final["latency_metric_count"] >= 1
assert final["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_LEDGER_ROUTES_WORKER_BRIDGE_DIRECT_TESTS_PASSED")
print("created_execution", created["execution_id"])
print("updated_status", updated["execution_status"])
print("worker_state", worker_blocked["worker_state"])
print("worker_events", worker_events["count"])
print("attempts", attempts["count"])
print("latencies", latencies["count"])
print("retry_state", advanced_retry["next_state"])
print("retries", retries["count"])
print("final_counts", final["execution_record_count"], final["worker_event_count"], final["dispatch_attempt_count"], final["retry_history_count"], final["latency_metric_count"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_LEDGER_ROUTES_AND_WORKER_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Updated: {worker_path}")
print(f"Created/updated: {test_file}")
print("Ledger routes and automatic worker ledger bridge installed.")