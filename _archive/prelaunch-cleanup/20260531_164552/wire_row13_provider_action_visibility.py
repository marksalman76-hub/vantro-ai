from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_row13_provider_action_visibility.py"

backup_dir = ROOT / "backups" / f"row13_provider_action_visibility_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

main_text = main_file.read_text(encoding="utf-8")

import_block = "from backend.app.runtime.safe_provider_action_adapters import evaluate_safe_provider_action, classify_provider_action\n"
if import_block not in main_text:
    insert_after = "from fastapi import"
    idx = main_text.find(insert_after)
    if idx == -1:
        raise SystemExit("Could not find FastAPI import area in backend/app/main.py")
    line_end = main_text.find("\n", idx)
    main_text = main_text[:line_end + 1] + import_block + main_text[line_end + 1:]

route_block = r'''

@app.get("/admin/provider-action-readiness")
async def admin_provider_action_readiness():
    """
    Admin/operator visibility endpoint for Row 13 provider/action safety.

    This endpoint is intentionally read-only and non-live:
    - no external provider calls
    - no credential values returned
    - no client limits applied to owner/admin visibility
    - governance and owner approval rules remain visible
    """
    scenarios = {
        "admin_owner_execution": {
            "action_type": "admin_owner_execution",
            "owner_approved": True,
        },
        "live_provider_generation_missing_approval": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": False,
            "live_execution_enabled": True,
        },
        "live_provider_generation_disabled": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": True,
            "live_execution_enabled": False,
        },
        "live_provider_generation_ready": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": True,
            "live_execution_enabled": True,
        },
        "unknown_action": {
            "action_type": "unknown_action",
        },
    }

    checks = {
        name: evaluate_safe_provider_action(payload)
        for name, payload in scenarios.items()
    }

    return {
        "success": True,
        "row": 13,
        "profile": "safe_provider_action_adapter_foundation",
        "visibility_only": True,
        "live_external_calls_enabled": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "owner_admin_client_limits_applied": False,
        "governance_enforced": True,
        "owner_approval_required_for_live_actions": True,
        "supported_live_action_types": [
            "live_provider_generation",
            "live_provider_action",
            "external_provider_execution",
            "shopify_live_action",
            "stripe_live_action",
            "email_live_send",
            "crm_live_write",
            "ad_platform_live_action",
        ],
        "supported_safe_internal_action_types": [
            "admin_owner_execution",
            "internal_execution",
            "preview_generation",
            "draft_generation",
            "safe_draft_action",
        ],
        "checks": checks,
    }


@app.post("/admin/provider-action-readiness/evaluate")
async def admin_provider_action_readiness_evaluate(payload: dict):
    """
    Admin/operator evaluator for a proposed provider/action payload.

    This endpoint classifies and evaluates readiness only.
    It does not execute provider actions.
    """
    classified = classify_provider_action(payload)
    decision = evaluate_safe_provider_action(payload)

    return {
        "success": True,
        "row": 13,
        "visibility_only": True,
        "live_external_calls_enabled": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "classification": classified,
        "decision": decision,
    }
'''

if '"/admin/provider-action-readiness"' not in main_text:
    main_text = main_text.rstrip() + "\n" + route_block + "\n"

main_file.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/provider-action-readiness")
assert_true(status.status_code == 200, f"status route failed: {status.status_code} {status.text}")
data = status.json()

assert_true(data["success"] is True, "readiness response should succeed")
assert_true(data["visibility_only"] is True, "route must be visibility-only")
assert_true(data["live_external_calls_enabled"] is False, "must not enable live external calls")
assert_true(data["external_action_performed"] is False, "must not perform external action")
assert_true(data["credential_values_exposed"] is False, "must not expose credentials")
assert_true(data["owner_admin_client_limits_applied"] is False, "owner/admin visibility must not apply client limits")
assert_true(data["governance_enforced"] is True, "governance must remain enforced")

checks = data["checks"]
assert_true(checks["admin_owner_execution"]["execution_status"] == "safe_internal_action_allowed", "admin internal check failed")
assert_true(checks["live_provider_generation_missing_approval"]["execution_status"] == "blocked_owner_approval_required", "approval block failed")
assert_true(checks["live_provider_generation_disabled"]["execution_status"] == "blocked_live_execution_disabled", "disabled live execution block failed")
assert_true(checks["live_provider_generation_ready"]["execution_status"] == "live_action_ready_for_provider_adapter", "ready state failed")
assert_true(checks["live_provider_generation_ready"]["external_action_performed"] is False, "ready state must not call provider")

eval_blocked = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(eval_blocked.status_code == 200, f"evaluate route failed: {eval_blocked.status_code} {eval_blocked.text}")
blocked_data = eval_blocked.json()
assert_true(blocked_data["success"] is True, "evaluate response should succeed")
assert_true(blocked_data["decision"]["execution_status"] == "blocked_owner_approval_required", "evaluate approval block failed")
assert_true(blocked_data["external_action_performed"] is False, "evaluate route must not perform external action")
assert_true(blocked_data["credential_values_exposed"] is False, "evaluate route must not expose credentials")

eval_ready = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(eval_ready.status_code == 200, f"evaluate ready failed: {eval_ready.status_code} {eval_ready.text}")
ready_data = eval_ready.json()
assert_true(ready_data["decision"]["execution_status"] == "live_action_ready_for_provider_adapter", "evaluate ready state failed")
assert_true(ready_data["decision"]["external_action_performed"] is False, "foundation must not call provider")

print("ROW13_PROVIDER_ACTION_VISIBILITY_TEST_PASSED")
print(data)
print(blocked_data)
print(ready_data)
'''.lstrip(), encoding="utf-8")

print("ROW13_PROVIDER_ACTION_VISIBILITY_WIRED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")