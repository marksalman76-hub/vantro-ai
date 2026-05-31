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
        "x-csrf-token": "live-run-agent-provider-bridge",
        "Origin": ORIGIN,
        "x-request-id": f"live-run-agent-provider-bridge-{suffix}",
        "x-idempotency-key": f"live-run-agent-provider-bridge-{suffix}",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    with urllib.request.urlopen(req, timeout=90) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


payload = {
    "tenant_id": "owner_admin",
    "requested_agent": "marketing_specialist_agent",
    "workflow_stage": "admin_live_provider_bridge_verification",
    "task": "Return exactly this text and nothing else: RUN_AGENT_LIVE_PROVIDER_BRIDGE_SUCCESS",
    "action_type": "governed_live_provider_generation",
    "region": "Global",
    "language": "English",
    "currency": "USD",
    "owner_approved": True,
    "execute_real_world_action": True,
    "project_id": "live_provider_bridge_verification",
    "actor_role": "owner_admin",
    "requested_credits": 1,
}

status, result = request_json("POST", "/run-agent", payload, suffix="run-agent")

assert_true(status == 200, f"/run-agent failed: {status}")
assert_true(result["success"] is True, "run-agent success failed")
assert_true(result["status"] == "agent_execution_completed", "agent execution did not complete")

execution = result.get("execution") or {}
assert_true(execution.get("adapter") == "governed_openai_live_provider_bridge", "wrong execution adapter")
assert_true(execution.get("action_type") == "governed_live_provider_generation", "wrong action type")
assert_true(execution.get("execution_status") == "governed_live_provider_execution_completed", "live provider bridge did not complete")

adapter_result = execution.get("adapter_result") or {}
assert_true(adapter_result.get("success") is True, "adapter result success failed")
assert_true(adapter_result.get("provider_key") == "openai", "provider should be OpenAI")
assert_true(adapter_result.get("status") == "completed", "OpenAI provider status not completed")
assert_true(adapter_result.get("live_external_call_executed") is True, "live external call not executed")
assert_true(adapter_result.get("credential_values_exposed") is False, "credentials exposed")
assert_true(adapter_result.get("customer_safe") is True, "result not customer safe")

normalised = adapter_result.get("normalised_response") or {}
safe_output = normalised.get("safe_output") or {}
assert_true("RUN_AGENT_LIVE_PROVIDER_BRIDGE_SUCCESS" in str(safe_output.get("text")), "expected OpenAI bridge output not found")

audit_asset = adapter_result.get("audit_asset") or {}
execution_bridge = audit_asset.get("execution_bridge") or {}
event_bridge = audit_asset.get("event_bridge") or {}
latency_bridge = audit_asset.get("latency_bridge") or {}

assert_true(execution_bridge.get("persistence_mode") == "postgres", "execution bridge not durable")
assert_true((execution_bridge.get("postgres_write_result") or {}).get("written") is True, "execution bridge write failed")
assert_true(event_bridge.get("persistence_mode") == "postgres", "event bridge not durable")
assert_true((event_bridge.get("postgres_write_result") or {}).get("written") is True, "event bridge write failed")
assert_true(latency_bridge.get("persistence_mode") == "postgres", "latency bridge not durable")
assert_true((latency_bridge.get("postgres_write_result") or {}).get("written") is True, "latency bridge write failed")

assert_true((result.get("memory") or {}).get("memory_saved") is True, "memory not saved")
assert_true((result.get("sqlite") or {}).get("sqlite_saved") is True, "sqlite not saved")

print("LIVE_RUN_AGENT_PROVIDER_BRIDGE_VERIFIED")
print(json.dumps({
    "base_url": BASE_URL,
    "run_agent_status": result.get("status"),
    "execution_status": execution.get("execution_status"),
    "adapter": execution.get("adapter"),
    "provider_key": adapter_result.get("provider_key"),
    "provider_status": adapter_result.get("status"),
    "live_external_call_executed": adapter_result.get("live_external_call_executed"),
    "credential_values_exposed": adapter_result.get("credential_values_exposed"),
    "customer_safe": adapter_result.get("customer_safe"),
    "execution_persistence": execution_bridge.get("persistence_mode"),
    "event_persistence": event_bridge.get("persistence_mode"),
    "latency_persistence": latency_bridge.get("persistence_mode"),
    "memory_saved": (result.get("memory") or {}).get("memory_saved"),
    "sqlite_saved": (result.get("sqlite") or {}).get("sqlite_saved"),
}, indent=2))