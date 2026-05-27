from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_background_worker_loop_routes_direct.py"

backup_dir = ROOT / "backups" / f"background_worker_loop_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Background worker loop foundation routes
# Added by wire_background_worker_loop_routes.py
# Purpose:
# - expose safe worker queue, cycle, dispatch check, polling, retry,
#   and completion reconciliation routes
# - do NOT enable real external provider dispatch
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.background_worker_loop_foundation import (
        background_worker_loop_foundation_status,
        enqueue_background_provider_job,
        list_background_worker_queue,
        reconcile_background_worker_completion,
        reset_background_worker_loop_for_tests,
        run_background_worker_cycle_once,
        run_background_worker_dispatch_check,
        run_background_worker_polling_cycle,
        run_background_worker_retry_scheduler,
    )
except Exception:  # pragma: no cover
    background_worker_loop_foundation_status = None
    enqueue_background_provider_job = None
    list_background_worker_queue = None
    reconcile_background_worker_completion = None
    reset_background_worker_loop_for_tests = None
    run_background_worker_cycle_once = None
    run_background_worker_dispatch_check = None
    run_background_worker_polling_cycle = None
    run_background_worker_retry_scheduler = None


@app.get("/background-worker-loop/status")
def background_worker_loop_status_route():
    if background_worker_loop_foundation_status is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return background_worker_loop_foundation_status()


@app.post("/background-worker-loop/enqueue")
async def background_worker_loop_enqueue_route(payload: dict):
    if enqueue_background_provider_job is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return enqueue_background_provider_job(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.get("/background-worker-loop/queue")
def background_worker_loop_queue_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if list_background_worker_queue is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return list_background_worker_queue(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/background-worker-loop/cycle-once")
async def background_worker_loop_cycle_once_route():
    if run_background_worker_cycle_once is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return run_background_worker_cycle_once()


@app.post("/background-worker-loop/dispatch-check")
async def background_worker_loop_dispatch_check_route(payload: dict):
    if run_background_worker_dispatch_check is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_dispatch_check(queue_item)


@app.post("/background-worker-loop/polling-cycle")
async def background_worker_loop_polling_cycle_route(payload: dict):
    if run_background_worker_polling_cycle is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_polling_cycle(
        queue_item=queue_item,
        provider_job_id=safe_payload.get("provider_job_id"),
        provider_status=safe_payload.get("provider_status") or "queued",
    )


@app.post("/background-worker-loop/retry-scheduler")
async def background_worker_loop_retry_scheduler_route(payload: dict):
    if run_background_worker_retry_scheduler is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_retry_scheduler(
        queue_item=queue_item,
        failure_code=safe_payload.get("failure_code") or "provider_error",
    )


@app.post("/background-worker-loop/reconcile-completion")
async def background_worker_loop_reconcile_completion_route(payload: dict):
    if reconcile_background_worker_completion is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return reconcile_background_worker_completion(
        queue_item=queue_item,
        final_status=safe_payload.get("final_status") or "owner_review_required",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )


@app.post("/background-worker-loop/reset-for-tests")
async def background_worker_loop_reset_for_tests_route():
    if reset_background_worker_loop_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return reset_background_worker_loop_for_tests()
'''

marker = "# Background worker loop foundation routes"
if marker in main_text:
    print("BACKGROUND_WORKER_LOOP_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("BACKGROUND_WORKER_LOOP_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

reset = client.post("/background-worker-loop/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = client.get("/background-worker-loop/status").json()
assert status["background_worker_loop_ready"] is True
assert status["real_external_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

enqueued = client.post(
    "/background-worker-loop/enqueue",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert enqueued["enqueued"] is True
assert enqueued["queue_size"] == 1
assert enqueued["live_external_call_executed"] is False
assert enqueued["credential_values_exposed"] is False

queue_item = enqueued["queue_item"]

queue = client.get("/background-worker-loop/queue?tenant_id=tenant-test").json()
assert queue["count"] == 1
assert queue["credential_values_exposed"] is False

dispatch = client.post(
    "/background-worker-loop/dispatch-check",
    json={"queue_item": queue_item},
).json()
assert dispatch["next_state"] == "dispatch_blocked"
assert dispatch["dispatch_allowed"] is False
assert dispatch["live_external_call_executed"] is False

polling = client.post(
    "/background-worker-loop/polling-cycle",
    json={
        "queue_item": queue_item,
        "provider_job_id": "provider-job-123",
        "provider_status": "succeeded",
    },
).json()
assert polling["mapped_state"] == "completed"
assert polling["terminal"] is True
assert polling["credential_values_exposed"] is False

retry = client.post(
    "/background-worker-loop/retry-scheduler",
    json={
        "queue_item": queue_item,
        "failure_code": "provider_timeout",
    },
).json()
assert retry["attempt_count"] == 1
assert retry["retry_allowed"] is True
assert retry["next_state"] == "retry_queued"

complete = client.post(
    "/background-worker-loop/reconcile-completion",
    json={
        "queue_item": queue_item,
        "final_status": "completed",
        "latency_ms": 2500,
    },
).json()
assert complete["reconciled_status"] == "completed"
assert complete["terminal"] is True

cycle = client.post("/background-worker-loop/cycle-once").json()
assert cycle["queue_size"] == 1
assert cycle["live_external_call_executed"] is False
assert cycle["credential_values_exposed"] is False

print("BACKGROUND_WORKER_LOOP_ROUTES_DIRECT_TESTS_PASSED")
print("queue_count", queue["count"])
print("dispatch", dispatch["next_state"], dispatch["dispatch_allowed"])
print("polling", polling["mapped_state"], polling["terminal"])
print("retry", retry["next_state"], retry["next_action"])
print("complete", complete["reconciled_status"])
print("cycle_processed", cycle["processed_count"])
'''.lstrip(), encoding="utf-8")

print("BACKGROUND_WORKER_LOOP_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")