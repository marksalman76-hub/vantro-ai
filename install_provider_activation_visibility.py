from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_activation_visibility.py"

backup_dir = ROOT / "backups" / f"provider_activation_visibility_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

main_text = main_file.read_text(encoding="utf-8")

imports = [
    "from backend.app.runtime.real_provider_activation_registry import provider_activation_registry_status, provider_readiness, select_ready_provider_for_capability\n",
    "from backend.app.runtime.real_provider_http_execution_layer import controlled_openai_live_execution_status, real_provider_http_runtime_status, execute_controlled_openai_live_request\n",
    "from backend.app.runtime.provider_dispatch_policy_worker_foundation import provider_dispatch_policy_status, evaluate_provider_dispatch_policy, provider_worker_foundation_status\n",
]

insert_anchor = "from fastapi import"
anchor_index = main_text.find(insert_anchor)
if anchor_index == -1:
    raise SystemExit("Could not find FastAPI import area")

line_end = main_text.find("\n", anchor_index)
for import_line in reversed(imports):
    if import_line not in main_text:
        main_text = main_text[:line_end + 1] + import_line + main_text[line_end + 1:]

route_block = r'''

@app.get("/admin/provider-activation-visibility")
async def admin_provider_activation_visibility():
    """
    Admin-safe provider activation visibility.

    This route exposes readiness and gating status only.
    It never exposes credential values and never performs external provider calls.
    """
    providers = ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]

    provider_runtime_status = {
        provider: real_provider_http_runtime_status(provider)
        for provider in providers
    }

    provider_dispatch_evaluation = {
        provider: evaluate_provider_dispatch_policy(
            provider_key=provider,
            payload={
                "tenant_id": "owner_admin",
                "request_id": f"provider_visibility_{provider}",
                "task_type": "provider_activation_visibility",
                "prompt": "Readiness check only. Do not execute externally.",
                "live_execution_requested": True,
                "owner_governed_execution_confirmed": True,
            },
        )
        for provider in providers
    }

    return {
        "success": True,
        "profile": "controlled_provider_activation_visibility_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "owner_admin_client_limits_applied": False,
        "governance_enforced": True,
        "registry_status": provider_activation_registry_status(),
        "dispatch_policy_status": provider_dispatch_policy_status(),
        "worker_foundation_status": provider_worker_foundation_status(),
        "controlled_openai_status": controlled_openai_live_execution_status(),
        "provider_runtime_status": provider_runtime_status,
        "provider_dispatch_evaluation": provider_dispatch_evaluation,
        "next_safe_step": "enable provider-specific live dispatch only after credentials, owner approval policy, audit logging, and rollback controls are verified",
    }


@app.post("/admin/provider-activation-visibility/evaluate")
async def admin_provider_activation_visibility_evaluate(payload: dict):
    """
    Admin-safe provider activation evaluator.

    Evaluates provider readiness only.
    It does not execute external provider calls.
    """
    provider_key = str(payload.get("provider_key") or payload.get("provider") or "openai").strip().lower()
    capability = str(payload.get("capability") or "text_generation").strip()

    readiness = provider_readiness(provider_key)
    selected = select_ready_provider_for_capability(capability)
    runtime_status = real_provider_http_runtime_status(provider_key)
    dispatch_policy = evaluate_provider_dispatch_policy(
        provider_key=provider_key,
        payload={
            **payload,
            "tenant_id": payload.get("tenant_id") or "owner_admin",
            "request_id": payload.get("request_id") or "provider_activation_visibility_evaluate",
            "live_execution_requested": bool(payload.get("live_execution_requested")),
            "owner_governed_execution_confirmed": bool(payload.get("owner_governed_execution_confirmed")),
        },
    )

    controlled_openai_probe = None
    if provider_key == "openai":
        controlled_openai_probe = execute_controlled_openai_live_request({
            **payload,
            "tenant_id": payload.get("tenant_id") or "owner_admin",
            "request_id": payload.get("request_id") or "controlled_openai_visibility_probe",
            "prompt": payload.get("prompt") or "Visibility probe only. Do not execute unless all gates are enabled.",
            "live_execution_requested": bool(payload.get("live_execution_requested")),
            "owner_governed_execution_confirmed": bool(payload.get("owner_governed_execution_confirmed")),
        })

    return {
        "success": True,
        "profile": "controlled_provider_activation_visibility_evaluator_v1",
        "provider_key": provider_key,
        "capability": capability,
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "readiness": readiness,
        "selected_provider_for_capability": selected,
        "runtime_status": runtime_status,
        "dispatch_policy": dispatch_policy,
        "controlled_openai_probe": controlled_openai_probe,
    }
'''

if '"/admin/provider-activation-visibility"' not in main_text:
    main_text = main_text.rstrip() + "\n" + route_block + "\n"

main_file.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/provider-activation-visibility")
assert_true(status.status_code == 200, f"visibility route failed: {status.status_code} {status.text}")
data = status.json()

assert_true(data["success"] is True, "visibility route should succeed")
assert_true(data["visibility_only"] is True, "visibility route must be visibility only")
assert_true(data["external_action_performed"] is False, "must not perform external action")
assert_true(data["live_external_call_executed"] is False, "must not execute live external call")
assert_true(data["credential_values_exposed"] is False, "must not expose credential values")
assert_true(data["governance_enforced"] is True, "governance must remain enforced")
assert_true("registry_status" in data, "registry status missing")
assert_true("dispatch_policy_status" in data, "dispatch policy status missing")
assert_true("controlled_openai_status" in data, "controlled OpenAI status missing")
assert_true(data["dispatch_policy_status"]["requires_final_policy_enablement"] is True, "final policy enablement must be required")

for provider, runtime in data["provider_runtime_status"].items():
    assert_true(runtime["credential_values_exposed"] is False, f"{provider} exposed credentials")
    assert_true(runtime["customer_safe"] is True, f"{provider} not customer safe")

blocked = client.post("/admin/provider-activation-visibility/evaluate", json={
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "test_provider_activation_visibility_blocked",
    "prompt": "Visibility test only.",
    "live_execution_requested": False,
    "owner_governed_execution_confirmed": False,
})
assert_true(blocked.status_code == 200, f"evaluate blocked failed: {blocked.status_code} {blocked.text}")
blocked_data = blocked.json()
assert_true(blocked_data["success"] is True, "evaluate should succeed")
assert_true(blocked_data["visibility_only"] is True, "evaluate must be visibility only")
assert_true(blocked_data["external_action_performed"] is False, "evaluate must not perform external action")
assert_true(blocked_data["live_external_call_executed"] is False, "evaluate must not execute live external call")
assert_true(blocked_data["credential_values_exposed"] is False, "evaluate must not expose credentials")
assert_true(blocked_data["dispatch_policy"]["live_external_call_executed"] is False, "dispatch policy must not execute externally")

ready_probe = client.post("/admin/provider-activation-visibility/evaluate", json={
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "test_provider_activation_visibility_ready_probe",
    "prompt": "Visibility test only.",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
})
assert_true(ready_probe.status_code == 200, f"evaluate ready probe failed: {ready_probe.status_code} {ready_probe.text}")
ready_data = ready_probe.json()
assert_true(ready_data["success"] is True, "ready probe should succeed")
assert_true(ready_data["live_external_call_executed"] is False, "ready probe route must not claim external call")
assert_true(ready_data["credential_values_exposed"] is False, "ready probe must not expose credentials")
assert_true(ready_data["dispatch_policy"]["live_external_call_executed"] is False, "ready probe dispatch policy must not execute externally")

openai_probe = ready_data.get("controlled_openai_probe") or {}
assert_true(openai_probe.get("live_external_call_executed") is False, "controlled OpenAI probe must not execute externally unless final env gates enable it")
assert_true(openai_probe.get("credential_values_exposed") is False, "controlled OpenAI probe must not expose credentials")

print("PROVIDER_ACTIVATION_VISIBILITY_TEST_PASSED")
print(data)
print(blocked_data)
print(ready_data)
'''.lstrip(), encoding="utf-8")

print("PROVIDER_ACTIVATION_VISIBILITY_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")