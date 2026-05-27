from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"run_agent_runtime_entitlement_integration_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_run_agent_runtime_entitlement_integration.py"

backup_main = BACKUP_DIR / "backend" / "app" / "main.py"
backup_main.parent.mkdir(parents=True, exist_ok=True)
backup_main.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.runtime_entitlement_hydration_bridge import hydrate_entitlements_for_execution
"""

if "from backend.app.runtime.runtime_entitlement_hydration_bridge import hydrate_entitlements_for_execution" not in text:
    text = import_block + "\n" + text

old_block = '''    active_agents = tenant_account.get("account", {}).get("active_agents", [])

    if not owner_admin_internal_execution:
        normalised_active_agents = [
            normalize_agent_id(agent) for agent in active_agents
        ]

        if requested_agent not in normalised_active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
                "normalised_agent": requested_agent,
            }
'''

new_block = '''    runtime_entitlement_check = hydrate_entitlements_for_execution({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "client_id": request.tenant_id,
        "agent_id": requested_agent,
        "agent_key": requested_agent,
        "requested_agent": requested_agent,
    })

    if not runtime_entitlement_check.get("execution_allowed"):
        return {
            "success": False,
            "status": "runtime_entitlement_blocked",
            "error": runtime_entitlement_check.get("error", "runtime_entitlement_denied"),
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
            "next_stage": runtime_entitlement_check.get("next_stage", "owner_admin_review_required"),
            "runtime_entitlement_check": runtime_entitlement_check,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
'''

if old_block not in text:
    raise RuntimeError("Expected legacy active_agents entitlement block not found. No changes made.")

text = text.replace(old_block, new_block, 1)

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from pathlib import Path

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

assert "hydrate_entitlements_for_execution" in text
assert "runtime_entitlement_check = hydrate_entitlements_for_execution" in text
assert "runtime_entitlement_blocked" in text
assert "credential_values_exposed" in text
assert "active_agents = tenant_account.get" not in text
assert "agent_not_active_for_tenant" not in text

print("RUN_AGENT_RUNTIME_ENTITLEMENT_INTEGRATION_TESTS_PASSED")
print("integration_marker", "runtime_entitlement_check = hydrate_entitlements_for_execution" in text)
print("legacy_active_agents_removed", "active_agents = tenant_account.get" not in text)
print("legacy_error_removed", "agent_not_active_for_tenant" not in text)
''', encoding="utf-8")

print("RUN_AGENT_RUNTIME_ENTITLEMENT_INTEGRATION_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")