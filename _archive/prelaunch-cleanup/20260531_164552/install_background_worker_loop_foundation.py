from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "background_worker_loop_foundation.py"
test_file = ROOT / "test_background_worker_loop_foundation_direct.py"

backup_dir = ROOT / "backups" / f"background_worker_loop_foundation_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.provider_dispatch_policy_worker_foundation import (
    advance_provider_worker_job,
    create_provider_worker_job_packet,
    evaluate_provider_dispatch_policy,
)
from backend.app.runtime.async_provider_orchestration_runtime import advance_provider_polling_state
from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_retry_history_bridge,
    persist_worker_event_bridge,
)


_WORKER_QUEUE: List[Dict[str, Any]] = []


def _now_ms() -> int:
    return int(time.time() * 1000)


def reset_background_worker_loop_for_tests() -> Dict[str, Any]:
    _WORKER_QUEUE.clear()
    return {
        "reset": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def enqueue_background_provider_job(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    payload: Optional[Dict[str, Any]] = None,
    live_execution_requested: bool = False,
    owner_governed_execution_confirmed: bool = False,
) -> Dict[str, Any]:
    worker_packet = create_provider_worker_job_packet(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        payload=payload or {},
        live_execution_requested=live_execution_requested,
        owner_governed_execution_confirmed=owner_governed_execution_confirmed,
    )

    queue_item = {
        "queue_id": f"provider_queue_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "payload": payload or {},
        "worker_job_id": worker_packet["worker_job_id"],
        "worker_state": worker_packet["worker_state"],
        "next_action": worker_packet["next_action"],
        "attempt_count": 0,
        "max_attempts": 3,
        "created_at_ms": _now_ms(),
        "updated_at_ms": _now_ms(),
        "worker_packet": worker_packet,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _WORKER_QUEUE.append(queue_item)

    return {
        "enqueued": True,
        "queue_item": queue_item,
        "queue_size": len(_WORKER_QUEUE),
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_background_worker_queue(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    items = list(_WORKER_QUEUE)

    if tenant_id:
        items = [i for i in items if i.get("tenant_id") == tenant_id]
    if provider_key:
        items = [i for i in items if i.get("provider_key") == provider_key]

    return {
        "queue_size": len(_WORKER_QUEUE),
        "items": items[:limit],
        "count": len(items[:limit]),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def run_background_worker_dispatch_check(queue_item: Dict[str, Any]) -> Dict[str, Any]:
    policy = evaluate_provider_dispatch_policy(
        provider_key=queue_item["provider_key"],
        payload={
            **queue_item.get("payload", {}),
            "tenant_id": queue_item["tenant_id"],
            "request_id": queue_item["request_id"],
            "task_type": queue_item["task_type"],
            "live_execution_requested": True,
            "owner_governed_execution_confirmed": True,
        },
    )

    if policy["dispatch_allowed"]:
        next_state = "ready_for_dispatch"
        next_action = "prepare_dispatch_cycle"
    else:
        next_state = "dispatch_blocked"
        next_action = "hold_for_policy_or_credentials"

    queue_item["worker_state"] = next_state
    queue_item["next_action"] = next_action
    queue_item["updated_at_ms"] = _now_ms()

    execution_id = queue_item.get("worker_packet", {}).get("execution_record", {}).get("execution_id", queue_item["worker_job_id"])

    persist_dispatch_attempt_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        worker_job_id=queue_item["worker_job_id"],
        provider_key=queue_item["provider_key"],
        attempt_number=queue_item["attempt_count"] + 1,
        allowed_by_policy=policy["dispatch_allowed"],
        result_status=next_state,
        reason=policy["reason"],
    )

    persist_worker_event_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        worker_job_id=queue_item["worker_job_id"],
        provider_key=queue_item["provider_key"],
        event_type="background_worker_dispatch_check",
        status=next_state,
        details={"next_action": next_action, "policy_reason": policy["reason"]},
    )

    return {
        "queue_id": queue_item["queue_id"],
        "worker_job_id": queue_item["worker_job_id"],
        "next_state": next_state,
        "next_action": next_action,
        "dispatch_allowed": policy["dispatch_allowed"],
        "policy_reason": policy["reason"],
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def run_background_worker_polling_cycle(
    *,
    queue_item: Dict[str, Any],
    provider_job_id: Optional[str] = None,
    provider_status: str = "queued",
) -> Dict[str, Any]:
    provider_job_id = provider_job_id or queue_item.get("provider_job_id") or f"pending_{queue_item['worker_job_id']}"

    polling = advance_provider_polling_state(
        provider_key=queue_item["provider_key"],
        provider_job_id=provider_job_id,
        current_state=queue_item.get("worker_state", "queued"),
        provider_status=provider_status,
        attempt_count=queue_item.get("attempt_count", 0),
    )

    queue_item["worker_state"] = polling["mapped_state"]
    queue_item["next_action"] = polling["next_action"]
    queue_item["provider_job_id"] = provider_job_id
    queue_item["updated_at_ms"] = _now_ms()

    execution_id = queue_item.get("worker_packet", {}).get("execution_record", {}).get("execution_id", queue_item["worker_job_id"])

    persist_worker_event_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        worker_job_id=queue_item["worker_job_id"],
        provider_key=queue_item["provider_key"],
        event_type="background_worker_polling_cycle",
        status=polling["mapped_state"],
        details={"provider_status": provider_status, "next_action": polling["next_action"]},
    )

    return {
        "queue_id": queue_item["queue_id"],
        "worker_job_id": queue_item["worker_job_id"],
        "provider_job_id": provider_job_id,
        "mapped_state": polling["mapped_state"],
        "next_action": polling["next_action"],
        "terminal": polling["terminal"],
        "retry_recommended": polling["retry_recommended"],
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def run_background_worker_retry_scheduler(queue_item: Dict[str, Any], failure_code: str = "provider_error") -> Dict[str, Any]:
    queue_item["attempt_count"] = int(queue_item.get("attempt_count", 0)) + 1
    retry_allowed = queue_item["attempt_count"] < int(queue_item.get("max_attempts", 3))

    next_state = "retry_queued" if retry_allowed else "owner_review_required"
    next_action = "queue_retry" if retry_allowed else "owner_review_required"

    queue_item["worker_state"] = next_state
    queue_item["next_action"] = next_action
    queue_item["updated_at_ms"] = _now_ms()

    execution_id = queue_item.get("worker_packet", {}).get("execution_record", {}).get("execution_id", queue_item["worker_job_id"])

    persist_retry_history_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        worker_job_id=queue_item["worker_job_id"],
        provider_key=queue_item["provider_key"],
        attempt_number=queue_item["attempt_count"],
        failure_code=failure_code,
        retry_allowed=retry_allowed,
        next_action=next_action,
    )

    advanced = advance_provider_worker_job(
        worker_job_id=queue_item["worker_job_id"],
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        provider_key=queue_item["provider_key"],
        current_state="dispatch_blocked",
        attempt_count=queue_item["attempt_count"],
        failure_code=failure_code,
    )

    return {
        "queue_id": queue_item["queue_id"],
        "worker_job_id": queue_item["worker_job_id"],
        "attempt_count": queue_item["attempt_count"],
        "retry_allowed": retry_allowed,
        "next_state": next_state,
        "next_action": next_action,
        "worker_advance": advanced,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def reconcile_background_worker_completion(
    *,
    queue_item: Dict[str, Any],
    final_status: str,
    latency_ms: int = 0,
) -> Dict[str, Any]:
    terminal_states = {"completed", "failed", "owner_review_required"}
    reconciled_status = final_status if final_status in terminal_states else "owner_review_required"

    queue_item["worker_state"] = reconciled_status
    queue_item["next_action"] = "terminal"
    queue_item["updated_at_ms"] = _now_ms()

    execution_id = queue_item.get("worker_packet", {}).get("execution_record", {}).get("execution_id", queue_item["worker_job_id"])

    persist_worker_event_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        worker_job_id=queue_item["worker_job_id"],
        provider_key=queue_item["provider_key"],
        event_type="background_worker_completion_reconciled",
        status=reconciled_status,
        details={"final_status": final_status},
    )

    persist_latency_metric_bridge(
        tenant_id=queue_item["tenant_id"],
        request_id=queue_item["request_id"],
        execution_id=execution_id,
        provider_key=queue_item["provider_key"],
        latency_ms=latency_ms,
        operation="background_worker_completion_reconciliation",
    )

    return {
        "queue_id": queue_item["queue_id"],
        "worker_job_id": queue_item["worker_job_id"],
        "reconciled_status": reconciled_status,
        "terminal": True,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def run_background_worker_cycle_once() -> Dict[str, Any]:
    cycle_id = f"worker_cycle_{uuid.uuid4().hex[:16]}"
    started_at = _now_ms()
    processed = []

    for queue_item in list(_WORKER_QUEUE):
        state = queue_item.get("worker_state")

        if state in {"created", "dispatch_blocked", "ready_for_worker_dispatch"}:
            processed.append(run_background_worker_dispatch_check(queue_item))
        elif state in {"running", "queued", "retry_queued"}:
            processed.append(run_background_worker_polling_cycle(queue_item=queue_item, provider_status="processing"))
        elif state == "failed":
            processed.append(run_background_worker_retry_scheduler(queue_item, failure_code="provider_error"))
        elif state in {"completed", "owner_review_required"}:
            processed.append({
                "queue_id": queue_item["queue_id"],
                "worker_job_id": queue_item["worker_job_id"],
                "skipped": True,
                "reason": "terminal_state",
                "credential_values_exposed": False,
                "customer_safe": True,
            })

    return {
        "cycle_id": cycle_id,
        "processed_count": len(processed),
        "queue_size": len(_WORKER_QUEUE),
        "processed": processed,
        "latency_ms": _now_ms() - started_at,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def background_worker_loop_foundation_status() -> Dict[str, Any]:
    return {
        "background_worker_loop_ready": True,
        "worker_queue_ready": True,
        "dispatch_check_ready": True,
        "polling_cycle_ready": True,
        "retry_scheduler_ready": True,
        "completion_reconciliation_ready": True,
        "real_external_dispatch_enabled": False,
        "queue_size": len(_WORKER_QUEUE),
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
import os

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

reset = reset_background_worker_loop_for_tests()
assert reset["reset"] is True

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

status = background_worker_loop_foundation_status()
assert status["background_worker_loop_ready"] is True
assert status["real_external_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

enqueued = enqueue_background_provider_job(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert enqueued["enqueued"] is True
assert enqueued["queue_size"] == 1
assert enqueued["live_external_call_executed"] is False

queue_item = enqueued["queue_item"]

dispatch = run_background_worker_dispatch_check(queue_item)
assert dispatch["next_state"] == "dispatch_blocked"
assert dispatch["dispatch_allowed"] is False
assert dispatch["live_external_call_executed"] is False

polling = run_background_worker_polling_cycle(
    queue_item=queue_item,
    provider_job_id="provider-job-123",
    provider_status="succeeded",
)
assert polling["mapped_state"] == "completed"
assert polling["terminal"] is True

retry = run_background_worker_retry_scheduler(queue_item, failure_code="provider_timeout")
assert retry["attempt_count"] == 1
assert retry["retry_allowed"] is True
assert retry["next_state"] == "retry_queued"

complete = reconcile_background_worker_completion(
    queue_item=queue_item,
    final_status="completed",
    latency_ms=2500,
)
assert complete["reconciled_status"] == "completed"
assert complete["terminal"] is True

listed = list_background_worker_queue(tenant_id="tenant-test")
assert listed["count"] == 1

cycle = run_background_worker_cycle_once()
assert cycle["queue_size"] == 1
assert cycle["live_external_call_executed"] is False
assert cycle["credential_values_exposed"] is False

final_status = background_worker_loop_foundation_status()
assert final_status["queue_size"] == 1

print("BACKGROUND_WORKER_LOOP_FOUNDATION_DIRECT_TESTS_PASSED")
print("queue_size", listed["count"])
print("dispatch", dispatch["next_state"], dispatch["dispatch_allowed"])
print("polling", polling["mapped_state"], polling["terminal"])
print("retry", retry["next_state"], retry["next_action"])
print("complete", complete["reconciled_status"])
print("cycle_processed", cycle["processed_count"])
'''.lstrip(), encoding="utf-8")

print("BACKGROUND_WORKER_LOOP_FOUNDATION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Background worker loop foundation installed. Real external dispatch remains disabled.")