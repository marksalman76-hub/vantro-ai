from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

from backend.app.runtime.real_provider_http_execution_layer import execute_real_provider_http_request
from backend.app.runtime.provider_execution_persistence_ledger import (
    append_worker_event_ledger_entry,
    create_provider_execution_record,
    record_dispatch_attempt,
    record_provider_latency_metric,
    record_retry_history,
    update_provider_execution_record,
)
from backend.app.runtime.async_provider_orchestration_runtime import (
    create_provider_http_dispatch_preparation_packet,
    create_retry_escalation_packet,
    build_provider_execution_timeline_event,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def provider_dispatch_policy_status() -> Dict[str, Any]:
    return {
        "policy_name": "provider_dispatch_policy_v1",
        "real_dispatch_globally_enabled": os.getenv("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", "").lower() == "true",
        "requires_credentials": True,
        "requires_live_execution_requested": True,
        "requires_owner_governed_execution_confirmed": True,
        "requires_final_policy_enablement": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def evaluate_provider_dispatch_policy(
    *,
    provider_key: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    status = provider_dispatch_policy_status()

    http_packet = execute_real_provider_http_request(provider_key, safe_payload)

    final_policy_enabled = status["real_dispatch_globally_enabled"]
    provider_ready = http_packet.get("status") == "ready_for_real_http_dispatch"

    dispatch_allowed = bool(final_policy_enabled and provider_ready)

    if not final_policy_enabled:
        reason = "real_provider_http_dispatch_globally_disabled"
    elif not provider_ready:
        reason = http_packet.get("reason") or "provider_not_dispatch_ready"
    else:
        reason = "dispatch_allowed"

    return {
        "provider_key": provider_key,
        "dispatch_allowed": dispatch_allowed,
        "reason": reason,
        "policy_status": status,
        "http_packet_status": http_packet.get("status"),
        "http_packet": http_packet,
        "live_external_call_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "evaluated_at_ms": _now_ms(),
    }


def create_provider_worker_job_packet(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    payload: Optional[Dict[str, Any]] = None,
    live_execution_requested: bool = False,
    owner_governed_execution_confirmed: bool = False,
) -> Dict[str, Any]:
    worker_job_id = f"provider_worker_{uuid.uuid4().hex[:16]}"
    safe_payload = dict(payload or {})
    safe_payload.update({
        "tenant_id": tenant_id,
        "request_id": request_id,
        "task_type": task_type,
        "live_execution_requested": live_execution_requested,
        "owner_governed_execution_confirmed": owner_governed_execution_confirmed,
    })

    bridge_packet = create_provider_http_dispatch_preparation_packet(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        payload=payload or {},
        live_execution_requested=live_execution_requested,
        owner_governed_execution_confirmed=owner_governed_execution_confirmed,
    )

    policy = evaluate_provider_dispatch_policy(
        provider_key=provider_key,
        payload=safe_payload,
    )

    worker_state = "dispatch_blocked"
    next_action = "hold_for_policy_or_credentials"
    if policy["dispatch_allowed"]:
        worker_state = "ready_for_worker_dispatch"
        next_action = "queue_real_provider_dispatch"

    timeline_event = build_provider_execution_timeline_event(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=worker_job_id,
        provider_key=provider_key,
        event_type="provider_worker_job_prepared",
        status=worker_state,
    )

    execution_record = create_provider_execution_record(
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
    }


def advance_provider_worker_job(
    *,
    worker_job_id: str,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    current_state: str,
    attempt_count: int = 0,
    failure_code: Optional[str] = None,
) -> Dict[str, Any]:
    if current_state == "ready_for_worker_dispatch":
        next_state = "dispatch_waiting_final_enablement"
        next_action = "wait_for_final_policy_enablement"
    elif current_state == "dispatch_blocked" and failure_code:
        retry_packet = create_retry_escalation_packet(
            tenant_id=tenant_id,
            request_id=request_id,
            provider_key=provider_key,
            failure_code=failure_code,
            attempt_count=attempt_count,
        )
        next_state = "retry_queued" if retry_packet["retry_allowed"] else "owner_review_required"
        next_action = retry_packet["next_action"]
    elif current_state in {"completed", "owner_review_required"}:
        next_state = current_state
        next_action = "terminal"
    else:
        next_state = "polling_or_waiting"
        next_action = "continue_worker_cycle"

    timeline_event = build_provider_execution_timeline_event(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=worker_job_id,
        provider_key=provider_key,
        event_type="provider_worker_job_advanced",
        status=next_state,
    )

    synthetic_execution = create_provider_execution_record(
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
    }


def provider_worker_foundation_status() -> Dict[str, Any]:
    return {
        "worker_foundation_ready": True,
        "real_background_dispatch_enabled": False,
        "safe_queue_preparation_enabled": True,
        "dispatch_policy_layer_enabled": True,
        "retry_escalation_linked": True,
        "timeline_events_linked": True,
        "owner_governed_execution_required": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }
