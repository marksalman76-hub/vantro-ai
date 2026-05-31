from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "provider_dispatch_policy_worker_foundation.py"
test_file = ROOT / "test_provider_dispatch_policy_worker_foundation_direct.py"
backup_dir = ROOT / "backups" / f"provider_dispatch_policy_worker_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

from backend.app.runtime.real_provider_http_execution_layer import execute_real_provider_http_request
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

    return {
        "worker_job_id": worker_job_id,
        "previous_state": current_state,
        "next_state": next_state,
        "next_action": next_action,
        "timeline_event": timeline_event,
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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.provider_dispatch_policy_worker_foundation import (
    advance_provider_worker_job,
    create_provider_worker_job_packet,
    evaluate_provider_dispatch_policy,
    provider_dispatch_policy_status,
    provider_worker_foundation_status,
)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

policy_status = provider_dispatch_policy_status()
assert policy_status["real_dispatch_globally_enabled"] is False
assert policy_status["requires_owner_governed_execution_confirmed"] is True
assert policy_status["credential_values_exposed"] is False

blocked_policy = evaluate_provider_dispatch_policy(
    provider_key="openai",
    payload={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
)
assert blocked_policy["dispatch_allowed"] is False
assert blocked_policy["reason"] == "real_provider_http_dispatch_globally_disabled"
assert blocked_policy["live_external_call_executed"] is False
assert blocked_policy["credential_values_exposed"] is False

worker_blocked = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert worker_blocked["next_action"] == "hold_for_policy_or_credentials"
assert worker_blocked["live_external_call_executed"] is False
assert worker_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

still_blocked = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert still_blocked["worker_state"] == "dispatch_blocked"
assert still_blocked["dispatch_policy"]["http_packet_status"] == "ready_for_real_http_dispatch"
assert still_blocked["dispatch_policy"]["dispatch_allowed"] is False
assert still_blocked["dispatch_policy"]["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_worker = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert ready_worker["worker_state"] == "ready_for_worker_dispatch"
assert ready_worker["next_action"] == "queue_real_provider_dispatch"
assert ready_worker["live_external_call_executed"] is False

advanced = advance_provider_worker_job(
    worker_job_id=ready_worker["worker_job_id"],
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    current_state=ready_worker["worker_state"],
)
assert advanced["next_state"] == "dispatch_waiting_final_enablement"
assert advanced["next_action"] == "wait_for_final_policy_enablement"
assert advanced["credential_values_exposed"] is False

retry = advance_provider_worker_job(
    worker_job_id=ready_worker["worker_job_id"],
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    current_state="dispatch_blocked",
    attempt_count=1,
    failure_code="provider_timeout",
)
assert retry["next_state"] == "retry_queued"
assert retry["next_action"] == "queue_retry"

foundation = provider_worker_foundation_status()
assert foundation["worker_foundation_ready"] is True
assert foundation["real_background_dispatch_enabled"] is False
assert foundation["dispatch_policy_layer_enabled"] is True
assert foundation["credential_values_exposed"] is False

print("PROVIDER_DISPATCH_POLICY_WORKER_FOUNDATION_DIRECT_TESTS_PASSED")
print("policy_enabled", policy_status["real_dispatch_globally_enabled"])
print("blocked_policy", blocked_policy["dispatch_allowed"], blocked_policy["reason"])
print("worker_blocked", worker_blocked["worker_state"], worker_blocked["next_action"])
print("still_blocked", still_blocked["dispatch_policy"]["http_packet_status"], still_blocked["dispatch_policy"]["reason"])
print("ready_worker", ready_worker["worker_state"], ready_worker["next_action"])
print("advanced_worker", advanced["next_state"], advanced["next_action"])
print("retry_worker", retry["next_state"], retry["next_action"])
print("foundation_ready", foundation["worker_foundation_ready"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_DISPATCH_POLICY_WORKER_FOUNDATION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Worker foundation added. Real background dispatch remains disabled.")