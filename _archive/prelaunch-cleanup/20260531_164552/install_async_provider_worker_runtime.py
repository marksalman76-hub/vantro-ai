from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"async_provider_worker_runtime_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "async_provider_worker_runtime.py"
test_path = ROOT / "test_async_provider_worker_runtime.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    list_provider_jobs,
    update_provider_job_status,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def enqueue_async_provider_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    created = create_provider_job(payload)

    if not created.get("success"):
        return created

    return {
        "success": True,
        "status": "queued",
        "worker_status": "accepted",
        "job": created["job"],
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def process_provider_job(job_id: str, *, simulate_success: bool = True) -> Dict[str, Any]:
    found = get_provider_job(job_id)

    if not found.get("success"):
        return {
            "success": False,
            "status": "not_found",
            "error": "provider_job_not_found",
            "job_id": job_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    job = found["job"]

    if job.get("status") == "completed":
        return {
            "success": True,
            "status": "already_completed",
            "job": job,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    running = update_provider_job_status(
        job_id,
        "running",
        provider_job_reference=job.get("provider_job_reference") or f"worker_ref_{job_id}",
    )

    if not running.get("success"):
        return running

    if not simulate_success:
        failed = update_provider_job_status(
            job_id,
            "failed",
            error="provider_worker_simulated_failure",
        )
        return {
            "success": False,
            "status": "failed",
            "worker_status": "failed",
            "job": failed.get("job"),
            "error": "provider_worker_simulated_failure",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    asset_records: List[Dict[str, Any]] = [
        {
            "asset_id": f"asset_{job_id}",
            "asset_type": job.get("requested_asset_type") or "generated_asset",
            "delivery_status": "ready",
            "linked_execution_id": job.get("execution_id"),
            "created_at": _now(),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    ]

    completed = update_provider_job_status(
        job_id,
        "completed",
        result_payload={
            "provider_status": "succeeded",
            "worker_completed_at": _now(),
        },
        asset_records=asset_records,
    )

    return {
        "success": True,
        "status": "completed",
        "worker_status": "completed",
        "job": completed.get("job"),
        "asset_records": deepcopy(asset_records),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def process_next_queued_provider_job(*, simulate_success: bool = True) -> Dict[str, Any]:
    queued = list_provider_jobs(status="queued").get("jobs", [])

    if not queued:
        return {
            "success": True,
            "status": "idle",
            "message": "No queued provider jobs.",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    job = queued[0]
    return process_provider_job(job["job_id"], simulate_success=simulate_success)


def process_provider_job_batch(limit: int = 5, *, simulate_success: bool = True) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit or 5), 25))
    results = []

    for _ in range(safe_limit):
        result = process_next_queued_provider_job(simulate_success=simulate_success)

        if result.get("status") == "idle":
            break

        results.append(result)

    return {
        "success": True,
        "status": "batch_processed",
        "processed_count": len(results),
        "results": results,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_async_provider_worker_status() -> Dict[str, Any]:
    queued_count = list_provider_jobs(status="queued").get("job_count", 0)
    running_count = list_provider_jobs(status="running").get("job_count", 0)
    completed_count = list_provider_jobs(status="completed").get("job_count", 0)
    failed_count = list_provider_jobs(status="failed").get("job_count", 0)

    return {
        "success": True,
        "async_provider_worker_ready": True,
        "queued_job_pickup_enabled": True,
        "running_status_enabled": True,
        "completion_status_enabled": True,
        "failure_status_enabled": True,
        "asset_record_output_enabled": True,
        "queue_counts": {
            "queued": queued_count,
            "running": running_count,
            "completed": completed_count,
            "failed": failed_count,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.async_provider_worker_runtime import (
    enqueue_async_provider_job,
    get_async_provider_worker_status,
    process_next_queued_provider_job,
    process_provider_job,
    process_provider_job_batch,
)
from backend.app.runtime.provider_job_persistence_runtime import get_provider_job

status = get_async_provider_worker_status()
assert status["async_provider_worker_ready"] is True
assert status["credential_values_exposed"] is False

queued = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
assert queued["success"] is True
assert queued["status"] == "queued"

job_id = queued["job"]["job_id"]

completed = process_provider_job(job_id)
assert completed["success"] is True
assert completed["status"] == "completed"
assert completed["worker_status"] == "completed"
assert len(completed["asset_records"]) == 1

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "completed"
assert len(found["job"]["asset_records"]) == 1

already = process_provider_job(job_id)
assert already["success"] is True
assert already["status"] == "already_completed"

queued_fail = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_002",
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
})
failed = process_provider_job(queued_fail["job"]["job_id"], simulate_success=False)
assert failed["success"] is False
assert failed["status"] == "failed"

idle_or_batch = process_provider_job_batch(limit=2)
assert idle_or_batch["success"] is True
assert idle_or_batch["credential_values_exposed"] is False

queued_next = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_003",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
next_result = process_next_queued_provider_job()
assert next_result["success"] is True
assert next_result["status"] == "completed"

final_status = get_async_provider_worker_status()
assert final_status["async_provider_worker_ready"] is True

print("ASYNC_PROVIDER_WORKER_RUNTIME_TESTS_PASSED")
print("status_ready", status["async_provider_worker_ready"])
print("queued_status", queued["status"])
print("completed_status", completed["status"])
print("already_status", already["status"])
print("failed_status", failed["status"])
print("batch_status", idle_or_batch["status"])
print("next_status", next_result["status"])
''', encoding="utf-8")

print("ASYNC_PROVIDER_WORKER_RUNTIME_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")