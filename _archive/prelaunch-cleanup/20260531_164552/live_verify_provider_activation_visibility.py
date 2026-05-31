import json
import os
import urllib.request
from pathlib import Path

BASE_URL = "https://api.trance-formation.com.au"
ORIGIN = "https://trance-formation.com.au"


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

    raise RuntimeError("No admin token found. Set ADMIN_PLATFORM_TOKEN in CMD.")


ADMIN_TOKEN = load_admin_token()


def request_json(method, path, payload=None, suffix="default"):
    url = BASE_URL.rstrip("/") + path
    data = None
    headers = {
        "Content-Type": "application/json",
        "x-admin-token": ADMIN_TOKEN,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
        "x-csrf-token": "live-provider-activation-visibility",
        "Origin": ORIGIN,
        "x-request-id": f"live-provider-activation-visibility-{suffix}",
        "x-idempotency-key": f"live-provider-activation-visibility-{suffix}",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    with urllib.request.urlopen(req, timeout=45) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status, visibility = request_json("GET", "/admin/provider-activation-visibility", suffix="status")
assert_true(status == 200, f"visibility route failed: {status}")
assert_true(visibility["success"] is True, "visibility success failed")
assert_true(visibility["visibility_only"] is True, "visibility must be visibility-only")
assert_true(visibility["external_action_performed"] is False, "must not perform external action")
assert_true(visibility["live_external_call_executed"] is False, "must not execute live external call")
assert_true(visibility["credential_values_exposed"] is False, "must not expose credentials")
assert_true(visibility["governance_enforced"] is True, "governance must be enforced")
assert_true(visibility["owner_admin_client_limits_applied"] is False, "owner/admin client limits must not apply")
assert_true("registry_status" in visibility, "registry status missing")
assert_true("dispatch_policy_status" in visibility, "dispatch policy status missing")
assert_true("controlled_openai_status" in visibility, "controlled OpenAI status missing")
assert_true("provider_runtime_status" in visibility, "provider runtime status missing")
assert_true("provider_dispatch_evaluation" in visibility, "provider dispatch evaluation missing")

assert_true(visibility["dispatch_policy_status"]["requires_final_policy_enablement"] is True, "final policy enablement should be required")
assert_true(visibility["worker_foundation_status"]["worker_foundation_ready"] is True, "worker foundation should be ready")

for provider, runtime in visibility["provider_runtime_status"].items():
    assert_true(runtime["credential_values_exposed"] is False, f"{provider} exposed credentials")
    assert_true(runtime["customer_safe"] is True, f"{provider} not customer safe")

for provider, evaluation in visibility["provider_dispatch_evaluation"].items():
    assert_true(evaluation["live_external_call_executed"] is False, f"{provider} executed external call")
    assert_true(evaluation["credential_values_exposed"] is False, f"{provider} exposed credentials")

status, blocked = request_json("POST", "/admin/provider-activation-visibility/evaluate", {
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "live_provider_activation_visibility_blocked",
    "prompt": "Production visibility test only.",
    "live_execution_requested": False,
    "owner_governed_execution_confirmed": False,
}, suffix="blocked")

assert_true(status == 200, f"blocked evaluate failed: {status}")
assert_true(blocked["success"] is True, "blocked evaluate success failed")
assert_true(blocked["visibility_only"] is True, "blocked evaluate must be visibility-only")
assert_true(blocked["external_action_performed"] is False, "blocked evaluate must not perform external action")
assert_true(blocked["live_external_call_executed"] is False, "blocked evaluate must not execute live external call")
assert_true(blocked["credential_values_exposed"] is False, "blocked evaluate must not expose credentials")
assert_true(blocked["dispatch_policy"]["live_external_call_executed"] is False, "dispatch policy must not execute externally")

status, ready_probe = request_json("POST", "/admin/provider-activation-visibility/evaluate", {
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "live_provider_activation_visibility_ready_probe",
    "prompt": "Production visibility test only.",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
}, suffix="ready-probe")

assert_true(status == 200, f"ready probe failed: {status}")
assert_true(ready_probe["success"] is True, "ready probe success failed")
assert_true(ready_probe["visibility_only"] is True, "ready probe must be visibility-only")
assert_true(ready_probe["external_action_performed"] is False, "ready probe must not perform external action")
assert_true(ready_probe["live_external_call_executed"] is False, "ready probe must not execute live external call")
assert_true(ready_probe["credential_values_exposed"] is False, "ready probe must not expose credentials")
assert_true(ready_probe["dispatch_policy"]["live_external_call_executed"] is False, "ready probe dispatch policy must not execute externally")

openai_probe = ready_probe.get("controlled_openai_probe") or {}
assert_true(openai_probe.get("live_external_call_executed") is False, "controlled OpenAI probe must not execute externally")
assert_true(openai_probe.get("credential_values_exposed") is False, "controlled OpenAI probe must not expose credentials")

print("LIVE_PROVIDER_ACTIVATION_VISIBILITY_VERIFIED")
print(json.dumps({
    "base_url": BASE_URL,
    "visibility_only": visibility["visibility_only"],
    "live_external_call_executed": visibility["live_external_call_executed"],
    "external_action_performed": visibility["external_action_performed"],
    "credential_values_exposed": visibility["credential_values_exposed"],
    "governance_enforced": visibility["governance_enforced"],
    "owner_admin_client_limits_applied": visibility["owner_admin_client_limits_applied"],
    "configured_provider_count": visibility["registry_status"].get("configured_provider_count"),
    "unconfigured_provider_count": visibility["registry_status"].get("unconfigured_provider_count"),
    "real_dispatch_globally_enabled": visibility["dispatch_policy_status"].get("real_dispatch_globally_enabled"),
    "worker_foundation_ready": visibility["worker_foundation_status"].get("worker_foundation_ready"),
    "openai_api_key_present": visibility["controlled_openai_status"].get("openai_api_key_present"),
    "openai_actual_network_call_enabled": visibility["controlled_openai_status"].get("actual_network_call_enabled"),
    "blocked_evaluate_reason": blocked["dispatch_policy"].get("reason"),
    "ready_probe_reason": ready_probe["dispatch_policy"].get("reason"),
}, indent=2))