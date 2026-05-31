from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
adapter_file = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

backup_dir = ROOT / "backups" / f"action_adapter_external_readiness_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(adapter_file, backup_dir / adapter_file.name)

content = adapter_file.read_text(encoding="utf-8")

old_import = """from uuid import uuid4
"""
new_import = """from uuid import uuid4

from backend.app.runtime.external_action_readiness_classifier import (
    classify_external_action_readiness,
)
"""

if old_import not in content:
    raise SystemExit("IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_signature = """def execute_action_adapter(packet: Dict[str, Any], *, tenant_id: str = "unknown") -> Dict[str, Any]:
"""
new_signature = """def execute_action_adapter(
    packet: Dict[str, Any],
    *,
    tenant_id: str = "unknown",
    connected_integrations: List[str] | None = None,
    owner_approved: bool = False,
) -> Dict[str, Any]:
"""

if old_signature not in content:
    raise SystemExit("FUNCTION_SIGNATURE_NOT_FOUND")

content = content.replace(old_signature, new_signature)

old_after_adapter = """    adapter = classify_action_adapter(packet)
    action_text = (
"""
new_after_adapter = """    adapter = classify_action_adapter(packet)
    external_readiness = classify_external_action_readiness(
        adapter=adapter,
        connected_integrations=connected_integrations or [],
        owner_approved=owner_approved,
    )
    action_text = (
"""

if old_after_adapter not in content:
    raise SystemExit("ADAPTER_CLASSIFICATION_BLOCK_NOT_FOUND")

content = content.replace(old_after_adapter, new_after_adapter)

old_risky_return = '''            "customer_safe": True,
            "credential_values_exposed": False,
            "actions_performed": [],
            "output": "Action requires owner approval before live campaign, send, publish, or spend execution.",
            "created_at": _now(),
        }
'''

new_risky_return = '''            "customer_safe": True,
            "credential_values_exposed": False,
            "external_readiness": external_readiness,
            "external_action_ready": external_readiness.get("external_action_ready", False),
            "internal_fallback_used": False,
            "actions_performed": [],
            "output": "Action requires owner approval before live campaign, send, publish, or spend execution.",
            "created_at": _now(),
        }
'''

if old_risky_return not in content:
    raise SystemExit("RISKY_RETURN_BLOCK_NOT_FOUND")

content = content.replace(old_risky_return, new_risky_return)

old_success_return = '''        "external_provider_called": False,
        "live_external_call_executed": False,
        "actions_performed": actions,
        "output": output,
'''

new_success_return = '''        "external_provider_called": external_readiness.get("external_action_ready", False),
        "live_external_call_executed": False,
        "external_readiness": external_readiness,
        "external_action_ready": external_readiness.get("external_action_ready", False),
        "internal_fallback_used": not external_readiness.get("external_action_ready", False),
        "missing_connections": external_readiness.get("missing_connections", []),
        "actions_performed": actions,
        "output": output,
'''

if old_success_return not in content:
    raise SystemExit("SUCCESS_RETURN_BLOCK_NOT_FOUND")

content = content.replace(old_success_return, new_success_return)

adapter_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_action_adapters_external_readiness.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
}

fallback = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
)
assert fallback["performed_actual_action"] is True
assert fallback["external_action_ready"] is False
assert fallback["internal_fallback_used"] is True
assert "crm" in fallback["missing_connections"]
assert "calendar" in fallback["missing_connections"]

ready = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email", "crm", "calendar"],
)
assert ready["performed_actual_action"] is True
assert ready["external_action_ready"] is True
assert ready["internal_fallback_used"] is False
assert ready["external_readiness"]["route"] == "external_action_ready"

risky = execute_action_adapter(
    {"implementation_action": "Launch paid campaign and increase budget"},
    tenant_id="tenant_test",
    connected_integrations=["ads"],
    owner_approved=False,
)
assert risky["owner_approval_required"] is True
assert risky["external_action_ready"] is False
assert risky["external_readiness"]["route"] == "owner_approval_required"

print("ACTION_ADAPTERS_EXTERNAL_READINESS_TEST_PASSED")
''', encoding="utf-8")

print("EXTERNAL_READINESS_WIRED_INTO_ACTION_ADAPTERS")
print(f"Backup: {backup_dir}")
print(f"Updated: {adapter_file}")
print(f"Created: {test_file}")