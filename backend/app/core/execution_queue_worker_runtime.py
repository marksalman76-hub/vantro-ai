from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.core.execution_queue_runtime import (
    mark_execution_failed,
    list_execution_queue,
)


QUEUE_WORKER_PROFILE = "priority4_execution_queue_worker_v1"

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

_LOCKED_QUEUE_IDS = set()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _worker_enabled() -> bool:
    return os.getenv("EXECUTION_QUEUE_WORKER_ENABLED", "true").lower() in {"1", "true", "yes", "on"}


def _max_batch_size() -> int:
    try:
        return max(1, min(25, int(os.getenv("EXECUTION_QUEUE_WORKER_BATCH_SIZE", "5"))))
    except Exception:
        return 5


def _claimable_statuses() -> List[str]:
    return ["queued", "retry_scheduled"]


def queue_worker_health() -> Dict[str, Any]:
    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_enabled": _worker_enabled(),
        "safe_worker_mode": True,
        "concurrency_control_enabled": True,
        "claiming_enabled": True,
        "retry_execution_foundation_enabled": True,
        "heartbeat_enabled": True,
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
        "entitlement_bypass": False,
        "governance_bypass": False,
        "state": dict(_WORKER_STATE),
        "locked_queue_count": len(_LOCKED_QUEUE_IDS),
        "locked_queue_ids": sorted(list(_LOCKED_QUEUE_IDS))[:25],
    }


def worker_heartbeat() -> Dict[str, Any]:
    _WORKER_STATE["last_heartbeat_at"] = _now_iso()
    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_id": _WORKER_STATE["worker_id"],
        "heartbeat_at": _WORKER_STATE["last_heartbeat_at"],
    }


def clear_queue_worker_locks() -> Dict[str, Any]:
    cleared = len(_LOCKED_QUEUE_IDS)
    _LOCKED_QUEUE_IDS.clear()
    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "cleared_locks": cleared,
        "locked_queue_count": len(_LOCKED_QUEUE_IDS),
    }


def _normalise_items(queue_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(queue_result, dict):
        return []

    for key in ("items", "queue", "executions", "results"):
        value = queue_result.get(key)
        if isinstance(value, list):
            return value

    return []


def _candidate_batch(limit: int = 0) -> List[Dict[str, Any]]:
    batch_limit = int(limit or _max_batch_size())
    candidates: List[Dict[str, Any]] = []

    for status in _claimable_statuses():
        if len(candidates) >= batch_limit:
            break

        result = list_execution_queue(status=status, limit=batch_limit)
        items = _normalise_items(result)

        for item in items:
            if len(candidates) >= batch_limit:
                break

            queue_id = item.get("queue_id") or item.get("id")
            if queue_id is None:
                continue

            try:
                queue_id_int = int(queue_id)
            except Exception:
                continue

            if queue_id_int in _LOCKED_QUEUE_IDS:
                continue

            candidates.append(item)

    return candidates


def claim_execution_queue_batch(limit: int = 0) -> Dict[str, Any]:
    """
    Preview claimable queue items without permanently locking them.

    This route is for admin/operator inspection. Actual processing locks are
    applied only inside run_queue_worker_once, then released after the run.
    """
    if not _worker_enabled():
        return {
            "success": False,
            "worker_profile": QUEUE_WORKER_PROFILE,
            "error": "queue_worker_disabled",
            "claimed": [],
        }

    claimed = _candidate_batch(limit=limit)

    return {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "claim_mode": "preview_non_locking",
        "claimed_count": len(claimed),
        "claimed": claimed,
        "locked_queue_count": len(_LOCKED_QUEUE_IDS),
    }


def _lock_for_processing(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    locked_items: List[Dict[str, Any]] = []

    for item in items:
        queue_id = item.get("queue_id") or item.get("id")
        try:
            queue_id_int = int(queue_id)
        except Exception:
            continue

        if queue_id_int in _LOCKED_QUEUE_IDS:
            continue

        _LOCKED_QUEUE_IDS.add(queue_id_int)
        locked_items.append(item)

    _WORKER_STATE["total_claimed"] += len(locked_items)
    return locked_items


def _release_processing_locks(items: List[Dict[str, Any]]) -> None:
    for item in items:
        queue_id = item.get("queue_id") or item.get("id")
        try:
            _LOCKED_QUEUE_IDS.discard(int(queue_id))
        except Exception:
            pass


def _process_item_safely(item: Dict[str, Any]) -> Dict[str, Any]:
    queue_id = item.get("queue_id") or item.get("id")
    action_type = str(item.get("action_type") or item.get("action") or "unknown")
    tenant_id = str(item.get("tenant_id") or "unknown")
    agent_id = str(item.get("agent_id") or "unknown")

    result = {
        "queue_id": queue_id,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "action_type": action_type,
        "processed_at": _now_iso(),
        "execution_mode": "worker_safe_foundation",
        "provider_direct_execution": False,
        "governed_execution_required": True,
        "status": "worker_foundation_processed",
    }

    return result


def run_queue_worker_once(limit: int = 0) -> Dict[str, Any]:
    worker_heartbeat()
    _WORKER_STATE["last_run_at"] = _now_iso()
    _WORKER_STATE["total_batches"] += 1

    candidates = _candidate_batch(limit=limit)
    claimed = _lock_for_processing(candidates)

    results: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    try:
        for item in claimed:
            queue_id = item.get("queue_id") or item.get("id")
            try:
                processed = _process_item_safely(item)
                results.append(processed)
                _WORKER_STATE["total_processed"] += 1
            except Exception as exc:
                failed_result = {
                    "queue_id": queue_id,
                    "error": str(exc),
                    "failed_at": _now_iso(),
                }
                failed.append(failed_result)
                _WORKER_STATE["total_failed"] += 1
                try:
                    if queue_id is not None:
                        mark_execution_failed(int(queue_id), str(exc))
                except Exception:
                    pass
    finally:
        _release_processing_locks(claimed)

    batch_result = {
        "success": True,
        "worker_profile": QUEUE_WORKER_PROFILE,
        "worker_id": _WORKER_STATE["worker_id"],
        "claimed_count": len(claimed),
        "processed_count": len(results),
        "failed_count": len(failed),
        "results": results,
        "failed": failed,
        "locked_queue_count_after_run": len(_LOCKED_QUEUE_IDS),
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
    }

    _WORKER_STATE["last_results"] = results[-10:]

    return batch_result
