from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
runtime_path = ROOT / "backend" / "app" / "runtime" / "async_provider_orchestration_runtime.py"
test_file = ROOT / "test_real_provider_http_routes_and_bridge_direct.py"

backup_dir = ROOT / "backups" / f"real_provider_http_routes_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [main_path, runtime_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")
if not runtime_path.exists():
    raise FileNotFoundError(f"Missing async orchestration runtime: {runtime_path}")

main_text = main_path.read_text(encoding="utf-8")
runtime_text = runtime_path.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1) Patch async_provider_orchestration_runtime.py with HTTP dispatch bridge
# ---------------------------------------------------------------------------

bridge_import = "from backend.app.runtime.real_provider_http_execution_layer import execute_real_provider_http_request, real_provider_http_runtime_status\n"

if "real_provider_http_execution_layer import execute_real_provider_http_request" not in runtime_text:
    runtime_text = runtime_text.replace(
        "from backend.app.runtime.live_provider_adapters import (\n",
        bridge_import + "from backend.app.runtime.live_provider_adapters import (\n",
    )

bridge_function = r'''

def create_provider_http_dispatch_preparation_packet(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    payload: Optional[Dict[str, Any]] = None,
    live_execution_requested: bool = False,
    owner_governed_execution_confirmed: bool = False,
) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    safe_payload.update({
        "tenant_id": tenant_id,
        "request_id": request_id,
        "task_type": task_type,
        "live_execution_requested": live_execution_requested,
        "owner_governed_execution_confirmed": owner_governed_execution_confirmed,
    })

    orchestration_packet = create_provider_orchestration_packet(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        payload=payload or {},
        live_execution_requested=live_execution_requested,
        owner_governed_execution_confirmed=owner_governed_execution_confirmed,
    )

    http_dispatch = execute_real_provider_http_request(provider_key, safe_payload)

    return {
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "orchestration_status": orchestration_packet.get("orchestration_status"),
        "http_dispatch_status": http_dispatch.get("status"),
        "orchestration_packet": orchestration_packet,
        "http_dispatch_packet": http_dispatch,
        "real_http_dispatch_enabled": False,
        "live_external_call_executed": False,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def provider_http_dispatch_bridge_status(provider_key: str) -> Dict[str, Any]:
    return {
        "provider_key": provider_key,
        "orchestration_runtime_ready": True,
        "http_runtime_status": real_provider_http_runtime_status(provider_key),
        "bridge_ready": True,
        "real_http_dispatch_enabled": False,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''

if "def create_provider_http_dispatch_preparation_packet(" not in runtime_text:
    runtime_text = runtime_text.rstrip() + bridge_function + "\n"

runtime_path.write_text(runtime_text, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) Patch main.py with safe real-provider HTTP routes + bridge route
# ---------------------------------------------------------------------------

route_block = r'''

# ---------------------------------------------------------------------------
# Real provider HTTP execution routes + orchestration bridge
# Added by wire_real_provider_http_execution_routes.py
# Purpose:
# - expose HTTP request builders/status safely
# - expose success/error normalisation safely
# - expose orchestration-to-HTTP dispatch preparation bridge
# - do NOT execute real external provider calls
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        build_provider_http_request_packet,
        execute_real_provider_http_request,
        map_provider_http_exception,
        normalise_provider_success_response,
        real_provider_http_runtime_status,
    )
    from backend.app.runtime.async_provider_orchestration_runtime import (
        create_provider_http_dispatch_preparation_packet,
        provider_http_dispatch_bridge_status,
    )
except Exception:  # pragma: no cover
    build_provider_http_request_packet = None
    execute_real_provider_http_request = None
    map_provider_http_exception = None
    normalise_provider_success_response = None
    real_provider_http_runtime_status = None
    create_provider_http_dispatch_preparation_packet = None
    provider_http_dispatch_bridge_status = None


@app.get("/real-provider-http/runtime-status/{provider_key}")
def real_provider_http_runtime_status_route(provider_key: str):
    if real_provider_http_runtime_status is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return real_provider_http_runtime_status(provider_key)


@app.post("/real-provider-http/request-packet/{provider_key}")
async def real_provider_http_request_packet_route(provider_key: str, payload: dict):
    if build_provider_http_request_packet is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return build_provider_http_request_packet(provider_key, dict(payload or {}))


@app.post("/real-provider-http/execute/{provider_key}")
async def real_provider_http_execute_route(provider_key: str, payload: dict):
    if execute_real_provider_http_request is None:
        return {
            "status": "blocked",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return execute_real_provider_http_request(provider_key, dict(payload or {}))


@app.post("/real-provider-http/success-normalisation/{provider_key}")
async def real_provider_http_success_normalisation_route(provider_key: str, payload: dict):
    if normalise_provider_success_response is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    raw_response = safe_payload.get("raw_response") or {}
    if not isinstance(raw_response, dict):
        raw_response = {}

    return normalise_provider_success_response(
        provider_key=provider_key,
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        raw_response=raw_response,
        asset_type=safe_payload.get("asset_type") or "generated_asset",
    )


@app.post("/real-provider-http/error-normalisation/{provider_key}")
async def real_provider_http_error_normalisation_route(provider_key: str, payload: dict):
    if map_provider_http_exception is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return map_provider_http_exception(
        provider_key,
        exception_type=safe_payload.get("exception_type") or "provider_unknown_error",
        status_code=safe_payload.get("status_code"),
    )


@app.post("/real-provider-http/dispatch-bridge/{provider_key}")
async def real_provider_http_dispatch_bridge_route(provider_key: str, payload: dict):
    if create_provider_http_dispatch_preparation_packet is None:
        return {
            "status": "unavailable",
            "reason": "provider_http_dispatch_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_http_dispatch_preparation_packet(
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


@app.get("/real-provider-http/dispatch-bridge-status/{provider_key}")
def real_provider_http_dispatch_bridge_status_route(provider_key: str):
    if provider_http_dispatch_bridge_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_http_dispatch_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_http_dispatch_bridge_status(provider_key)
'''

marker = "# Real provider HTTP execution routes + orchestration bridge"
if marker in main_text:
    print("REAL_PROVIDER_HTTP_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("REAL_PROVIDER_HTTP_ROUTES_AND_BRIDGE_WIRED")

# ---------------------------------------------------------------------------
# 3) Direct test file
# ---------------------------------------------------------------------------

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)

status = client.get("/real-provider-http/runtime-status/openai").json()
assert status["known_adapter"] is True
assert status["configured"] is False
assert status["ready"] is False
assert "OPENAI_API_KEY" in status["missing"]
assert status["real_http_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

packet = client.post(
    "/real-provider-http/request-packet/openai",
    json={"prompt": "test", "model": "gpt-test"},
).json()
assert packet["provider_key"] == "openai"
assert packet["provider_endpoint"] == "responses"
assert packet["input_present"] is True
assert packet["credential_values_exposed"] is False

blocked = client.post(
    "/real-provider-http/execute/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked["status"] == "blocked"
assert blocked["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["credential_values_exposed"] is False

bridge_blocked = client.post(
    "/real-provider-http/dispatch-bridge/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert bridge_blocked["orchestration_status"] == "blocked"
assert bridge_blocked["http_dispatch_status"] == "blocked"
assert bridge_blocked["live_external_call_executed"] is False
assert bridge_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = client.post(
    "/real-provider-http/execute/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready["status"] == "ready_for_real_http_dispatch"
assert ready["request_packet"]["provider_endpoint"] == "responses"
assert ready["live_external_call_executed"] is False
assert ready["dispatch_blocked_until_provider_credentials_and_final_policy_enablement"] is True
assert ready["credential_values_exposed"] is False

bridge_ready = client.post(
    "/real-provider-http/dispatch-bridge/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert bridge_ready["orchestration_status"] == "ready_for_live_provider_call"
assert bridge_ready["http_dispatch_status"] == "ready_for_real_http_dispatch"
assert bridge_ready["real_http_dispatch_enabled"] is False
assert bridge_ready["live_external_call_executed"] is False
assert bridge_ready["credential_values_exposed"] is False

success = client.post(
    "/real-provider-http/success-normalisation/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "asset_type": "text",
        "raw_response": {
            "id": "provider-job-123",
            "output_text": "Safe generated result.",
        },
    },
).json()
assert success["status"] == "completed"
assert success["provider_job_id"] == "provider-job-123"
assert success["asset_packet"]["customer_safe"] is True
assert success["credential_values_exposed"] is False

error = client.post(
    "/real-provider-http/error-normalisation/openai",
    json={
        "exception_type": "auth_error",
        "status_code": 401,
    },
).json()
assert error["failure_code"] == "provider_auth_error"
assert error["retryable"] is False
assert error["owner_review_required"] is True
assert error["credential_values_exposed"] is False

bridge_status = client.get("/real-provider-http/dispatch-bridge-status/openai").json()
assert bridge_status["bridge_ready"] is True
assert bridge_status["real_http_dispatch_enabled"] is False
assert bridge_status["credential_values_exposed"] is False

print("REAL_PROVIDER_HTTP_ROUTES_AND_BRIDGE_DIRECT_TESTS_PASSED")
print("status_configured", status["configured"])
print("request_endpoint", packet["provider_endpoint"])
print("blocked_status", blocked["status"], blocked["reason"])
print("bridge_blocked", bridge_blocked["orchestration_status"], bridge_blocked["http_dispatch_status"])
print("ready_status", ready["status"])
print("bridge_ready", bridge_ready["orchestration_status"], bridge_ready["http_dispatch_status"])
print("success_status", success["status"], success["provider_job_id"])
print("error_failure", error["failure_code"], error["retryable"])
print("bridge_status", bridge_status["bridge_ready"], bridge_status["real_http_dispatch_enabled"])
'''.lstrip(), encoding="utf-8")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Updated: {runtime_path}")
print(f"Created/updated: {test_file}")
print("Real-provider HTTP routes and orchestration bridge added safely.")