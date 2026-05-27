from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_dispatch_policy_worker_routes_direct.py"
backup_dir = ROOT / "backups" / f"provider_dispatch_policy_worker_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider dispatch policy + worker foundation routes
# Added by wire_provider_dispatch_policy_worker_routes.py
# Purpose:
# - expose dispatch policy status/evaluation
# - expose worker job preparation
# - expose safe worker state advancement
# - keep real background dispatch disabled
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_dispatch_policy_worker_foundation import (
        advance_provider_worker_job,
        create_provider_worker_job_packet,
        evaluate_provider_dispatch_policy,
        provider_dispatch_policy_status,
        provider_worker_foundation_status,
    )
except Exception:  # pragma: no cover
    advance_provider_worker_job = None
    create_provider_worker_job_packet = None
    evaluate_provider_dispatch_policy = None
    provider_dispatch_policy_status = None
    provider_worker_foundation_status = None


@app.get("/provider-dispatch-policy/status")
def provider_dispatch_policy_status_route():
    if provider_dispatch_policy_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_dispatch_policy_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_dispatch_policy_status()


@app.post("/provider-dispatch-policy/evaluate/{provider_key}")
async def provider_dispatch_policy_evaluate_route(provider_key: str, payload: dict):
    if evaluate_provider_dispatch_policy is None:
        return {
            "status": "unavailable",
            "reason": "provider_dispatch_policy_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return evaluate_provider_dispatch_policy(
        provider_key=provider_key,
        payload=dict(payload or {}),
    )


@app.get("/provider-worker-foundation/status")
def provider_worker_foundation_status_route():
    if provider_worker_foundation_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_worker_foundation_status()


@app.post("/provider-worker-foundation/create-job/{provider_key}")
async def provider_worker_foundation_create_job_route(provider_key: str, payload: dict):
    if create_provider_worker_job_packet is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_worker_job_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=provider_key,
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.post("/provider-worker-foundation/advance-job/{provider_key}")
async def provider_worker_foundation_advance_job_route(provider_key: str, payload: dict):
    if advance_provider_worker_job is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return advance_provider_worker_job(
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker-job",
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=provider_key,
        current_state=safe_payload.get("current_state") or "dispatch_blocked",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
        failure_code=safe_payload.get("failure_code"),
    )
'''

marker = "# Provider dispatch policy + worker foundation routes"
if marker in main_text:
    print("PROVIDER_DISPATCH_POLICY_WORKER_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_DISPATCH_POLICY_WORKER_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

status = client.get("/provider-dispatch-policy/status").json()
assert status["real_dispatch_globally_enabled"] is False
assert status["requires_owner_governed_execution_confirmed"] is True
assert status["credential_values_exposed"] is False

policy = client.post(
    "/provider-dispatch-policy/evaluate/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert policy["dispatch_allowed"] is False
assert policy["reason"] == "real_provider_http_dispatch_globally_disabled"
assert policy["live_external_call_executed"] is False
assert policy["credential_values_exposed"] is False

foundation = client.get("/provider-worker-foundation/status").json()
assert foundation["worker_foundation_ready"] is True
assert foundation["real_background_dispatch_enabled"] is False
assert foundation["credential_values_exposed"] is False

worker_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert worker_blocked["next_action"] == "hold_for_policy_or_credentials"
assert worker_blocked["live_external_call_executed"] is False
assert worker_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

still_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert still_blocked["worker_state"] == "dispatch_blocked"
assert still_blocked["dispatch_policy"]["http_packet_status"] == "ready_for_real_http_dispatch"
assert still_blocked["dispatch_policy"]["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_worker = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready_worker["worker_state"] == "ready_for_worker_dispatch"
assert ready_worker["next_action"] == "queue_real_provider_dispatch"
assert ready_worker["live_external_call_executed"] is False

advanced = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": ready_worker["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "current_state": ready_worker["worker_state"],
    },
).json()
assert advanced["next_state"] == "dispatch_waiting_final_enablement"
assert advanced["next_action"] == "wait_for_final_policy_enablement"
assert advanced["credential_values_exposed"] is False

retry = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": ready_worker["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "current_state": "dispatch_blocked",
        "attempt_count": 1,
        "failure_code": "provider_timeout",
    },
).json()
assert retry["next_state"] == "retry_queued"
assert retry["next_action"] == "queue_retry"
assert retry["credential_values_exposed"] is False

print("PROVIDER_DISPATCH_POLICY_WORKER_ROUTES_DIRECT_TESTS_PASSED")
print("policy_enabled", status["real_dispatch_globally_enabled"])
print("policy_result", policy["dispatch_allowed"], policy["reason"])
print("foundation_ready", foundation["worker_foundation_ready"])
print("worker_blocked", worker_blocked["worker_state"], worker_blocked["next_action"])
print("still_blocked", still_blocked["dispatch_policy"]["http_packet_status"], still_blocked["dispatch_policy"]["reason"])
print("ready_worker", ready_worker["worker_state"], ready_worker["next_action"])
print("advanced_worker", advanced["next_state"], advanced["next_action"])
print("retry_worker", retry["next_state"], retry["next_action"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_DISPATCH_POLICY_WORKER_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")
print("Routes added. Real background dispatch remains disabled.")