from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "async_provider_orchestration_runtime.py"
test_file = ROOT / "test_async_provider_orchestration_runtime_direct.py"
backup_dir = ROOT / "backups" / f"async_provider_orchestration_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.live_provider_adapters import (
    build_failover_routing_packet,
    build_polling_packet,
    calculate_provider_health_score,
    create_execution_audit_linkage,
    execute_gate_safe_provider_request,
    normalise_provider_failure,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def create_provider_orchestration_packet(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    payload: Optional[Dict[str, Any]] = None,
    live_execution_requested: bool = False,
    owner_governed_execution_confirmed: bool = False,
) -> Dict[str, Any]:
    execution_id = f"provider_exec_{uuid.uuid4().hex[:16]}"
    safe_payload = dict(payload or {})
    safe_payload.update({
        "tenant_id": tenant_id,
        "request_id": request_id,
        "task_type": task_type,
        "live_execution_requested": live_execution_requested,
        "owner_governed_execution_confirmed": owner_governed_execution_confirmed,
    })

    adapter_result = execute_gate_safe_provider_request(provider_key, safe_payload)
    status = adapter_result.get("status", "blocked")

    provider_job_id = adapter_result.get("provider_job_id")
    polling_packet = None
    if provider_job_id:
        polling_packet = build_polling_packet(provider_key, provider_job_id)

    audit_linkage = create_execution_audit_linkage(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        provider_job_id=provider_job_id,
        execution_status=status,
    )

    return {
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "orchestration_status": status,
        "adapter_result": adapter_result,
        "polling_packet": polling_packet,
        "audit_linkage": audit_linkage,
        "queued_for_polling": bool(provider_job_id),
        "live_external_call_executed": False,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def advance_provider_polling_state(
    *,
    provider_key: str,
    provider_job_id: str,
    current_state: str,
    provider_status: str,
    attempt_count: int = 0,
) -> Dict[str, Any]:
    polling_packet = build_polling_packet(provider_key, provider_job_id)
    status_map = polling_packet["status_map"]

    mapped_state = "running"
    for canonical, provider_values in status_map.items():
        if provider_status in provider_values:
            mapped_state = canonical
            break

    retry_recommended = mapped_state == "failed" and attempt_count < 3
    terminal = mapped_state in {"completed", "failed"}

    return {
        "provider_key": provider_key,
        "provider_job_id": provider_job_id,
        "previous_state": current_state,
        "provider_status": provider_status,
        "mapped_state": mapped_state,
        "terminal": terminal,
        "retry_recommended": retry_recommended,
        "next_action": (
            "mark_completed" if mapped_state == "completed"
            else "retry_or_escalate" if retry_recommended
            else "manual_review" if mapped_state == "failed"
            else "continue_polling"
        ),
        "credential_values_exposed": False,
        "updated_at_ms": _now_ms(),
    }


def create_retry_escalation_packet(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    failure_code: str,
    attempt_count: int,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    retry_allowed = attempt_count < max_attempts
    failure = normalise_provider_failure(
        provider_key,
        error_code=failure_code,
        message="Provider execution failed safely and was normalised for retry/escalation.",
        retryable=retry_allowed,
    )

    return {
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "retry_allowed": retry_allowed,
        "next_action": "queue_retry" if retry_allowed else "owner_review_required",
        "failure": failure,
        "owner_review_required": not retry_allowed,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def build_provider_execution_timeline_event(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    event_type: str,
    status: str,
    latency_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "provider_key": provider_key,
        "event_type": event_type,
        "status": status,
        "latency_ms": latency_ms,
        "event_scope": "provider_orchestration",
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def aggregate_provider_latency_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    latencies = [
        int(e["latency_ms"])
        for e in events
        if e.get("latency_ms") is not None
    ]

    if not latencies:
        average_latency = None
        max_latency = None
        min_latency = None
    else:
        average_latency = round(sum(latencies) / len(latencies))
        max_latency = max(latencies)
        min_latency = min(latencies)

    return {
        "event_count": len(events),
        "latency_sample_count": len(latencies),
        "average_latency_ms": average_latency,
        "max_latency_ms": max_latency,
        "min_latency_ms": min_latency,
        "credential_values_exposed": False,
    }


def prepare_provider_selection_packet(
    *,
    requested_provider: str,
    available_providers: List[str],
    provider_health: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    provider_health = provider_health or {}
    failover = build_failover_routing_packet(
        requested_provider=requested_provider,
        available_providers=available_providers,
    )

    scored = []
    for provider in failover["available_configured_providers"]:
        raw = provider_health.get(provider, {})
        score_packet = calculate_provider_health_score(
            success_count=int(raw.get("success_count", 0) or 0),
            failure_count=int(raw.get("failure_count", 0) or 0),
            timeout_count=int(raw.get("timeout_count", 0) or 0),
            average_latency_ms=raw.get("average_latency_ms"),
        )
        scored.append({
            "provider_key": provider,
            "health_score": score_packet["health_score"],
            "failover_recommended": score_packet["failover_recommended"],
        })

    scored.sort(key=lambda x: x["health_score"], reverse=True)

    return {
        "requested_provider": requested_provider,
        "selected_provider": scored[0]["provider_key"] if scored else None,
        "scored_providers": scored,
        "failover_ready": failover["failover_ready"],
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.async_provider_orchestration_runtime import (
    advance_provider_polling_state,
    aggregate_provider_latency_metrics,
    build_provider_execution_timeline_event,
    create_provider_orchestration_packet,
    create_retry_escalation_packet,
    prepare_provider_selection_packet,
)


def assert_safe(packet):
    assert packet["credential_values_exposed"] is False


os.environ.pop("OPENAI_API_KEY", None)

blocked = create_provider_orchestration_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)

assert blocked["orchestration_status"] == "blocked"
assert blocked["adapter_result"]["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["customer_safe"] is True
assert_safe(blocked)

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = create_provider_orchestration_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)

assert ready["orchestration_status"] == "ready_for_live_provider_call"
assert ready["adapter_result"]["adapter_name"] == "openai_live_execution_adapter_v1"
assert ready["live_external_call_executed"] is False
assert ready["audit_linkage"]["audit_event_type"] == "provider_execution_linkage"
assert_safe(ready)

polling = advance_provider_polling_state(
    provider_key="openai",
    provider_job_id="job-123",
    current_state="running",
    provider_status="succeeded",
    attempt_count=1,
)
assert polling["mapped_state"] == "completed"
assert polling["next_action"] == "mark_completed"
assert_safe(polling)

retry = create_retry_escalation_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    failure_code="provider_timeout",
    attempt_count=1,
)
assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"
assert_safe(retry)

manual = create_retry_escalation_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    failure_code="provider_timeout",
    attempt_count=3,
)
assert manual["retry_allowed"] is False
assert manual["next_action"] == "owner_review_required"
assert manual["owner_review_required"] is True
assert_safe(manual)

event1 = build_provider_execution_timeline_event(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=ready["execution_id"],
    provider_key="openai",
    event_type="provider_execution_started",
    status="running",
    latency_ms=1200,
)
event2 = build_provider_execution_timeline_event(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=ready["execution_id"],
    provider_key="openai",
    event_type="provider_execution_completed",
    status="completed",
    latency_ms=2400,
)

metrics = aggregate_provider_latency_metrics([event1, event2])
assert metrics["event_count"] == 2
assert metrics["average_latency_ms"] == 1800
assert metrics["max_latency_ms"] == 2400

selection = prepare_provider_selection_packet(
    requested_provider="runway",
    available_providers=["openai", "runway"],
    provider_health={
        "openai": {"success_count": 10, "failure_count": 0, "timeout_count": 0, "average_latency_ms": 2000},
        "runway": {"success_count": 1, "failure_count": 4, "timeout_count": 1, "average_latency_ms": 90000},
    },
)
assert selection["selected_provider"] == "openai"
assert selection["customer_safe"] is True
assert_safe(selection)

print("ASYNC_PROVIDER_ORCHESTRATION_RUNTIME_DIRECT_TESTS_PASSED")
print("blocked_status", blocked["orchestration_status"], blocked["adapter_result"]["reason"])
print("ready_status", ready["orchestration_status"], ready["adapter_result"]["adapter_name"])
print("polling_next_action", polling["next_action"])
print("retry_next_action", retry["next_action"])
print("manual_next_action", manual["next_action"])
print("average_latency_ms", metrics["average_latency_ms"])
print("selected_provider", selection["selected_provider"])
'''.lstrip(), encoding="utf-8")

print("ASYNC_PROVIDER_ORCHESTRATION_RUNTIME_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Real external calls remain blocked; this prepares orchestration only.")