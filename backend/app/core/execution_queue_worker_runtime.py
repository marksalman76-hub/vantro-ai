from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.durable_execution_queue_runtime import (
    claim_next_execution_job,
    complete_execution_job,
    get_execution_queue_status,
    heartbeat_execution_job,
    release_expired_execution_leases,
)


QUEUE_WORKER_PROFILE = "priority4_execution_queue_worker_v2_durable"

_WORKER_STATE: Dict[str, Any] = {
    "worker_id": f"worker_{uuid.uuid4().hex[:12]}",
    "started_at": datetime.now(timezone.utc).isoformat(),
    "last_heartbeat_at": None,
    "last_run_at": None,
    "total_batches": 0,
    "total_claimed": 0,
    "total_processed": 0,
    "total_failed": 0,
    "last_results": [],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _worker_enabled() -> bool:
    return os.getenv("EXECUTION_QUEUE_WORKER_ENABLED", "true").lower() in {"1", "true", "yes", "on"}


def _max_batch_size() -> int:
    try:
        return max(1, min(25, int(os.getenv("EXECUTION_QUEUE_WORKER_BATCH_SIZE", "5"))))
    except Exception:
        return 5


def _lease_seconds() -> int:
    try:
        return max(30, min(3600, int(os.getenv("EXECUTION_QUEUE_LEASE_SECONDS", "300"))))
    except Exception:
        return 300


def queue_worker_health() -> Dict[str, Any]:
    queue_status = get_execution_queue_status(queue_name="execution_queue")
    return {
        "success": bool(queue_status.get("success", True)),
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_enabled": _worker_enabled(),
        "safe_worker_mode": True,
        "concurrency_control_enabled": True,
        "claiming_enabled": True,
        "claiming_mode": "durable_postgres_or_dev_only_fallback",
        "process_local_locks_enabled": False,
        "retry_execution_foundation_enabled": True,
        "heartbeat_enabled": True,
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
        "entitlement_bypass": False,
        "governance_bypass": False,
        "state": dict(_WORKER_STATE),
        "durable_queue": queue_status,
    }


def worker_heartbeat() -> Dict[str, Any]:
    _WORKER_STATE["last_heartbeat_at"] = _now_iso()
    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_id": _WORKER_STATE["worker_id"],
        "heartbeat_at": _WORKER_STATE["last_heartbeat_at"],
        "durable_queue": get_execution_queue_status(queue_name="execution_queue"),
    }


def clear_queue_worker_locks() -> Dict[str, Any]:
    released = release_expired_execution_leases(queue_name="execution_queue")
    return {
        "success": bool(released.get("success")),
        "worker_profile": QUEUE_WORKER_PROFILE,
        "clear_mode": "release_expired_durable_leases",
        "process_local_locks_enabled": False,
        "released_expired_leases": released,
    }


def claim_execution_queue_batch(limit: int = 0) -> Dict[str, Any]:
    if not _worker_enabled():
        return {
            "success": False,
            "worker_profile": QUEUE_WORKER_PROFILE,
            "error": "queue_worker_disabled",
            "claimed": [],
            "credential_values_exposed": False,
        }

    batch_limit = max(1, min(int(limit or _max_batch_size()), 25))
    claimed: List[Dict[str, Any]] = []

    for _ in range(batch_limit):
        result = claim_next_execution_job(
            queue_name="execution_queue",
            worker_id=_WORKER_STATE["worker_id"],
            lease_seconds=_lease_seconds(),
        )
        if not result.get("success"):
            return {
                "success": False,
                "worker_profile": QUEUE_WORKER_PROFILE,
                "claim_mode": "durable_atomic_claim",
                "claimed_count": len(claimed),
                "claimed": claimed,
                "error": result,
                "credential_values_exposed": False,
            }
        if result.get("status") == "empty" or not result.get("job"):
            break
        claimed.append(result["job"])

    _WORKER_STATE["total_claimed"] += len(claimed)
    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "claim_mode": "durable_atomic_claim",
        "claimed_count": len(claimed),
        "claimed": claimed,
        "process_local_locks_enabled": False,
        "credential_values_exposed": False,
    }


def _process_item_safely(item: Dict[str, Any]) -> Dict[str, Any]:
    job_id = item.get("job_id") or item.get("queue_id")
    action_type = str(item.get("action_type") or item.get("action") or "unknown")
    tenant_id = str(item.get("tenant_id") or "unknown")
    agent_id = str(item.get("agent_id") or "unknown")

    heartbeat_execution_job(
        str(job_id),
        worker_id=_WORKER_STATE["worker_id"],
        lease_seconds=_lease_seconds(),
    )

    return {
        "queue_id": job_id,
        "job_id": job_id,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "action_type": action_type,
        "processed_at": _now_iso(),
        "execution_mode": "durable_worker_safe_foundation",
        "provider_direct_execution": False,
        "governed_execution_required": True,
        "status": "worker_foundation_processed",
        "credential_values_exposed": False,
    }


def run_queue_worker_once(limit: int = 0) -> Dict[str, Any]:
    worker_heartbeat()
    _WORKER_STATE["last_run_at"] = _now_iso()
    _WORKER_STATE["total_batches"] += 1

    claim_result = claim_execution_queue_batch(limit=limit)
    if not claim_result.get("success"):
        return claim_result

    claimed = claim_result.get("claimed", [])
    results: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    for item in claimed:
        job_id = item.get("job_id") or item.get("queue_id")
        try:
            processed = _process_item_safely(item)
            complete_result = complete_execution_job(
                str(job_id),
                worker_id=_WORKER_STATE["worker_id"],
                result=processed,
            )
            processed["completion"] = {
                "success": complete_result.get("success"),
                "status": complete_result.get("status"),
            }
            results.append(processed)
            _WORKER_STATE["total_processed"] += 1
        except Exception as exc:
            failed_result = {
                "queue_id": job_id,
                "job_id": job_id,
                "error": str(exc),
                "failed_at": _now_iso(),
                "credential_values_exposed": False,
            }
            failed.append(failed_result)
            _WORKER_STATE["total_failed"] += 1

    batch_result = {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_id": _WORKER_STATE["worker_id"],
        "claimed_count": len(claimed),
        "processed_count": len(results),
        "failed_count": len(failed),
        "results": results,
        "failed": failed,
        "process_local_locks_enabled": False,
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
        "credential_values_exposed": False,
    }

    _WORKER_STATE["last_results"] = results[-10:]
    return batch_result
