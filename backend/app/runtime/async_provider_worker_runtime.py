
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
