import json
import os
import urllib.request
from pathlib import Path

BASE_URL = "https://api.trance-formation.com.au"


def load_admin_token():
    env_file = Path(".env.local")
    keys = ["ADMIN_PLATFORM_TOKEN", "ADMIN_AUTH_SECRET", "OWNER_ADMIN_TOKEN"]

    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            if key.strip() in keys and value.strip():
                return value.strip().strip('"').strip("'")

    for key in keys:
        value = os.environ.get(key)
        if value:
            return value.strip()

    raise RuntimeError("No admin token found. Add ADMIN_PLATFORM_TOKEN to .env.local or set it in CMD.")


ADMIN_TOKEN = load_admin_token()


def request_json(method, path, payload=None, request_suffix="default"):
    url = BASE_URL.rstrip("/") + path
    data = None
    headers = {
        "Content-Type": "application/json",
        "x-admin-token": ADMIN_TOKEN,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
        "x-csrf-token": "live-row14-verification",
        "Origin": "https://trance-formation.com.au",
        "x-request-id": f"live-row14-provider-action-routes-{request_suffix}",
        "x-idempotency-key": f"live-row14-provider-action-routes-{request_suffix}",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status, readiness = request_json("GET", "/admin/provider-action-readiness", request_suffix="readiness")

assert_true(status == 200, f"Readiness route failed: {status}")
assert_true(readiness["success"] is True, "Readiness success failed")
assert_true(readiness["visibility_only"] is True, "Must be visibility only")
assert_true(readiness["live_external_calls_enabled"] is False, "Live external calls must be disabled")
assert_true(readiness["external_action_performed"] is False, "Must not perform external action")
assert_true(readiness["credential_values_exposed"] is False, "Must not expose credentials")
assert_true(readiness["owner_admin_client_limits_applied"] is False, "Owner/admin must not apply client limits")
assert_true(readiness["governance_enforced"] is True, "Governance must remain enforced")

checks = readiness["checks"]
assert_true(checks["admin_owner_execution"]["execution_status"] == "safe_internal_action_allowed", "Admin owner status failed")
assert_true(checks["live_provider_generation_missing_approval"]["execution_status"] == "blocked_owner_approval_required", "Missing approval block failed")
assert_true(checks["live_provider_generation_disabled"]["execution_status"] == "blocked_live_execution_disabled", "Disabled live execution block failed")
assert_true(checks["live_provider_generation_ready"]["execution_status"] == "live_action_ready_for_provider_adapter", "Ready state failed")
assert_true(checks["live_provider_generation_ready"]["external_action_performed"] is False, "Ready state must not call provider")

status, blocked = request_json("POST", "/admin/provider-action-readiness/evaluate", {
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
}, request_suffix="blocked")

assert_true(status == 200, f"Blocked evaluate route failed: {status}")
assert_true(blocked["decision"]["execution_status"] == "blocked_owner_approval_required", "Blocked status failed")
assert_true(blocked["external_action_performed"] is False, "Blocked evaluate must not perform external action")
assert_true(blocked["credential_values_exposed"] is False, "Blocked evaluate must not expose credentials")

status, ready = request_json("POST", "/admin/provider-action-readiness/evaluate", {
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
}, request_suffix="ready")

assert_true(status == 200, f"Ready evaluate route failed: {status}")
assert_true(ready["decision"]["execution_status"] == "live_action_ready_for_provider_adapter", "Ready status failed")
assert_true(ready["external_action_performed"] is False, "Ready evaluate must not perform external action")
assert_true(ready["credential_values_exposed"] is False, "Ready evaluate must not expose credentials")

print("LIVE_ROW14_PROVIDER_ACTION_ROUTES_VERIFIED")
print(json.dumps({
    "base_url": BASE_URL,
    "visibility_only": readiness["visibility_only"],
    "live_external_calls_enabled": readiness["live_external_calls_enabled"],
    "external_action_performed": readiness["external_action_performed"],
    "credential_values_exposed": readiness["credential_values_exposed"],
    "owner_admin_client_limits_applied": readiness["owner_admin_client_limits_applied"],
    "governance_enforced": readiness["governance_enforced"],
    "admin_owner_execution": checks["admin_owner_execution"]["execution_status"],
    "missing_approval": checks["live_provider_generation_missing_approval"]["execution_status"],
    "live_disabled": checks["live_provider_generation_disabled"]["execution_status"],
    "ready_state": checks["live_provider_generation_ready"]["execution_status"],
    "blocked_evaluate": blocked["decision"]["execution_status"],
    "ready_evaluate": ready["decision"]["execution_status"],
}, indent=2))