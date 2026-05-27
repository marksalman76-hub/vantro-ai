from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_async_provider_orchestration_routes_direct.py"
backup_dir = ROOT / "backups" / f"async_provider_orchestration_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Async provider orchestration routes
# Added by wire_async_provider_orchestration_routes.py
# Purpose:
# - expose async provider orchestration packets
# - expose polling state transitions
# - expose retry/manual-review escalation
# - expose execution timeline + latency aggregation
# - expose provider selection/failover preparation
# - do NOT execute real external provider calls
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.async_provider_orchestration_runtime import (
        advance_provider_polling_state,
        aggregate_provider_latency_metrics,
        build_provider_execution_timeline_event,
        create_provider_orchestration_packet,
        create_retry_escalation_packet,
        prepare_provider_selection_packet,
    )
except Exception:  # pragma: no cover
    advance_provider_polling_state = None
    aggregate_provider_latency_metrics = None
    build_provider_execution_timeline_event = None
    create_provider_orchestration_packet = None
    create_retry_escalation_packet = None
    prepare_provider_selection_packet = None


@app.post("/async-provider-orchestration/packet")
async def async_provider_orchestration_packet_route(payload: dict):
    if create_provider_orchestration_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_orchestration_packet(
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


@app.post("/async-provider-orchestration/polling-state")
async def async_provider_orchestration_polling_state_route(payload: dict):
    if advance_provider_polling_state is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return advance_provider_polling_state(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        provider_job_id=safe_payload.get("provider_job_id") or "unknown-job",
        current_state=safe_payload.get("current_state") or "queued",
        provider_status=safe_payload.get("provider_status") or "queued",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
    )


@app.post("/async-provider-orchestration/retry-escalation")
async def async_provider_orchestration_retry_escalation_route(payload: dict):
    if create_retry_escalation_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_retry_escalation_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        failure_code=safe_payload.get("failure_code") or "provider_error",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
        max_attempts=int(safe_payload.get("max_attempts", 3) or 3),
    )


@app.post("/async-provider-orchestration/timeline-event")
async def async_provider_orchestration_timeline_event_route(payload: dict):
    if build_provider_execution_timeline_event is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return build_provider_execution_timeline_event(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        event_type=safe_payload.get("event_type") or "provider_orchestration_event",
        status=safe_payload.get("status") or "queued",
        latency_ms=safe_payload.get("latency_ms"),
    )


@app.post("/async-provider-orchestration/latency-metrics")
async def async_provider_orchestration_latency_metrics_route(payload: dict):
    if aggregate_provider_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    events = safe_payload.get("events") or []
    if not isinstance(events, list):
        events = []

    return aggregate_provider_latency_metrics(events)


@app.post("/async-provider-orchestration/provider-selection")
async def async_provider_orchestration_provider_selection_route(payload: dict):
    if prepare_provider_selection_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    available_providers = safe_payload.get("available_providers") or []
    provider_health = safe_payload.get("provider_health") or {}

    if not isinstance(available_providers, list):
        available_providers = []
    if not isinstance(provider_health, dict):
        provider_health = {}

    return prepare_provider_selection_packet(
        requested_provider=safe_payload.get("requested_provider") or "unknown-provider",
        available_providers=available_providers,
        provider_health=provider_health,
    )
'''

marker = "# Async provider orchestration routes"
if marker in main_text:
    print("ASYNC_PROVIDER_ORCHESTRATION_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("ASYNC_PROVIDER_ORCHESTRATION_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)

blocked = client.post(
    "/async-provider-orchestration/packet",
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

assert blocked["orchestration_status"] == "blocked"
assert blocked["adapter_result"]["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["customer_safe"] is True
assert blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = client.post(
    "/async-provider-orchestration/packet",
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

assert ready["orchestration_status"] == "ready_for_live_provider_call"
assert ready["adapter_result"]["adapter_name"] == "openai_live_execution_adapter_v1"
assert ready["live_external_call_executed"] is False
assert ready["audit_linkage"]["audit_event_type"] == "provider_execution_linkage"
assert ready["credential_values_exposed"] is False

polling = client.post(
    "/async-provider-orchestration/polling-state",
    json={
        "provider_key": "openai",
        "provider_job_id": "job-123",
        "current_state": "running",
        "provider_status": "succeeded",
        "attempt_count": 1,
    },
).json()

assert polling["mapped_state"] == "completed"
assert polling["next_action"] == "mark_completed"
assert polling["credential_values_exposed"] is False

retry = client.post(
    "/async-provider-orchestration/retry-escalation",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "failure_code": "provider_timeout",
        "attempt_count": 1,
    },
).json()

assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"
assert retry["credential_values_exposed"] is False

manual = client.post(
    "/async-provider-orchestration/retry-escalation",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "failure_code": "provider_timeout",
        "attempt_count": 3,
    },
).json()

assert manual["retry_allowed"] is False
assert manual["next_action"] == "owner_review_required"
assert manual["owner_review_required"] is True
assert manual["credential_values_exposed"] is False

event = client.post(
    "/async-provider-orchestration/timeline-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": ready["execution_id"],
        "provider_key": "openai",
        "event_type": "provider_execution_started",
        "status": "running",
        "latency_ms": 1200,
    },
).json()

assert event["event_scope"] == "provider_orchestration"
assert event["customer_safe"] is True
assert event["credential_values_exposed"] is False

metrics = client.post(
    "/async-provider-orchestration/latency-metrics",
    json={
        "events": [
            {"latency_ms": 1200},
            {"latency_ms": 2400},
        ]
    },
).json()

assert metrics["event_count"] == 2
assert metrics["average_latency_ms"] == 1800
assert metrics["credential_values_exposed"] is False

selection = client.post(
    "/async-provider-orchestration/provider-selection",
    json={
        "requested_provider": "runway",
        "available_providers": ["openai", "runway"],
        "provider_health": {
            "openai": {
                "success_count": 10,
                "failure_count": 0,
                "timeout_count": 0,
                "average_latency_ms": 2000,
            },
            "runway": {
                "success_count": 1,
                "failure_count": 4,
                "timeout_count": 1,
                "average_latency_ms": 90000,
            },
        },
    },
).json()

assert selection["selected_provider"] == "openai"
assert selection["customer_safe"] is True
assert selection["credential_values_exposed"] is False

print("ASYNC_PROVIDER_ORCHESTRATION_ROUTES_DIRECT_TESTS_PASSED")
print("blocked_status", blocked["orchestration_status"], blocked["adapter_result"]["reason"])
print("ready_status", ready["orchestration_status"], ready["adapter_result"]["adapter_name"])
print("polling_next_action", polling["next_action"])
print("retry_next_action", retry["next_action"])
print("manual_next_action", manual["next_action"])
print("average_latency_ms", metrics["average_latency_ms"])
print("selected_provider", selection["selected_provider"])
'''.lstrip(), encoding="utf-8")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")
print("Async orchestration routes added without enabling real external provider calls.")