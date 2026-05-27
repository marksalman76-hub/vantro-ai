from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

target = ROOT / "backend" / "app" / "runtime" / "real_provider_http_execution_layer.py"
test_file = ROOT / "test_controlled_openai_live_execution_direct.py"

backup_dir = ROOT / "backups" / f"controlled_openai_live_execution_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

s = target.read_text(encoding="utf-8")

extra = r'''

def controlled_openai_live_execution_status() -> Dict[str, Any]:
    return {
        "provider_key": "openai",
        "controlled_live_execution_ready": True,
        "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        "real_dispatch_globally_enabled": os.getenv("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", "").lower() == "true",
        "requires_live_execution_requested": True,
        "requires_owner_governed_execution_confirmed": True,
        "actual_network_call_enabled": os.getenv("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", "").lower() == "true",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def execute_controlled_openai_live_request(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    started_at = _now_ms()

    base = execute_real_provider_http_request("openai", payload)

    if base.get("status") != "ready_for_real_http_dispatch":
        return {
            "provider_key": "openai",
            "status": "blocked",
            "reason": base.get("reason") or base.get("status"),
            "base_result": base,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if os.getenv("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", "").lower() != "true":
        return {
            "provider_key": "openai",
            "status": "blocked",
            "reason": "real_provider_http_dispatch_globally_disabled",
            "base_result": base,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if os.getenv("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", "").lower() != "true":
        return {
            "provider_key": "openai",
            "status": "ready_but_network_call_disabled",
            "reason": "OPENAI_ACTUAL_NETWORK_CALL_ENABLED_not_true",
            "base_result": base,
            "request_packet": base.get("request_packet"),
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        request_packet = base.get("request_packet", {})
        body = request_packet.get("request_body") or {}

        response = client.responses.create(**body)
        response_id = getattr(response, "id", None) or f"openai_response_{uuid.uuid4().hex[:12]}"
        output_text = getattr(response, "output_text", None)

        normalised = normalise_provider_success_response(
            provider_key="openai",
            tenant_id=payload.get("tenant_id") or "unknown-tenant",
            request_id=payload.get("request_id") or "unknown-request",
            raw_response={
                "id": response_id,
                "output_text": output_text,
            },
            asset_type=payload.get("asset_type") or "text",
        )

        return {
            "provider_key": "openai",
            "status": "completed",
            "provider_job_id": response_id,
            "normalised_response": normalised,
            "live_external_call_executed": True,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    except Exception as exc:
        failure = map_provider_http_exception(
            "openai",
            exception_type="provider_unknown_error",
            status_code=None,
        )
        failure["safe_error"] = str(exc)[:300]
        return {
            "provider_key": "openai",
            "status": "failed",
            "failure": failure,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
'''

if "def execute_controlled_openai_live_request(" not in s:
    s = s.rstrip() + extra + "\n"

target.write_text(s, encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.real_provider_http_execution_layer import (
    controlled_openai_live_execution_status,
    execute_controlled_openai_live_request,
)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)
os.environ.pop("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", None)

status = controlled_openai_live_execution_status()
assert status["controlled_live_execution_ready"] is True
assert status["openai_api_key_present"] is False
assert status["actual_network_call_enabled"] is False
assert status["credential_values_exposed"] is False

blocked_no_key = execute_controlled_openai_live_request({
    "tenant_id": "tenant-test",
    "request_id": "request-test",
    "prompt": "test",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
})
assert blocked_no_key["status"] == "blocked"
assert blocked_no_key["live_external_call_executed"] is False
assert blocked_no_key["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

blocked_policy = execute_controlled_openai_live_request({
    "tenant_id": "tenant-test",
    "request_id": "request-test",
    "prompt": "test",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
})
assert blocked_policy["status"] == "blocked"
assert blocked_policy["reason"] == "real_provider_http_dispatch_globally_disabled"
assert blocked_policy["live_external_call_executed"] is False

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_no_network = execute_controlled_openai_live_request({
    "tenant_id": "tenant-test",
    "request_id": "request-test",
    "prompt": "test",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
})
assert ready_no_network["status"] == "ready_but_network_call_disabled"
assert ready_no_network["reason"] == "OPENAI_ACTUAL_NETWORK_CALL_ENABLED_not_true"
assert ready_no_network["live_external_call_executed"] is False
assert ready_no_network["credential_values_exposed"] is False

print("CONTROLLED_OPENAI_LIVE_EXECUTION_DIRECT_TESTS_PASSED")
print("status_ready", status["controlled_live_execution_ready"])
print("blocked_no_key", blocked_no_key["status"])
print("blocked_policy", blocked_policy["status"], blocked_policy["reason"])
print("ready_no_network", ready_no_network["status"], ready_no_network["reason"])
'''.lstrip(), encoding="utf-8")

print("CONTROLLED_OPENAI_LIVE_EXECUTION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")
print(f"Created/updated: {test_file}")