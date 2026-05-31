from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
adapter_file = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

backup_dir = ROOT / "backups" / f"action_adapter_real_external_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(adapter_file, backup_dir / adapter_file.name)

content = adapter_file.read_text(encoding="utf-8")

old_import = """from backend.app.runtime.external_action_readiness_classifier import (
    classify_external_action_readiness,
)
"""

new_import = """from backend.app.runtime.external_action_readiness_classifier import (
    classify_external_action_readiness,
)
from backend.app.runtime.real_external_integration_execution_bridge import (
    execute_real_external_action,
)
"""

if old_import not in content:
    raise SystemExit("EXTERNAL_READINESS_IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_after_action_text = """    execution_id = f"adapter_exec_{uuid4().hex[:12]}"
    asset_id = f"asset_{uuid4().hex[:12]}"
    task_id = f"task_{uuid4().hex[:12]}"
"""

new_after_action_text = """    execution_id = f"adapter_exec_{uuid4().hex[:12]}"
    asset_id = f"asset_{uuid4().hex[:12]}"
    task_id = f"task_{uuid4().hex[:12]}"

    real_external_result = None
    if external_readiness.get("external_action_ready") is True:
        real_external_result = execute_real_external_action(
            adapter=adapter,
            action_text=str(action_text),
            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
            owner_approved=owner_approved,
        )
"""

if old_after_action_text not in content:
    raise SystemExit("ACTION_TEXT_BLOCK_NOT_FOUND")

content = content.replace(old_after_action_text, new_after_action_text)

old_success = '''        "external_provider_called": external_readiness.get("external_action_ready", False),
        "live_external_call_executed": False,
        "external_readiness": external_readiness,
        "external_action_ready": external_readiness.get("external_action_ready", False),
        "internal_fallback_used": not external_readiness.get("external_action_ready", False),
        "missing_connections": external_readiness.get("missing_connections", []),
        "actions_performed": actions,
        "output": output,
'''

new_success = '''        "external_provider_called": bool(real_external_result and real_external_result.get("external_action_executed")),
        "live_external_call_executed": bool(real_external_result and real_external_result.get("live_external_call_executed")),
        "external_readiness": external_readiness,
        "external_action_ready": external_readiness.get("external_action_ready", False),
        "real_external_execution": real_external_result,
        "internal_fallback_used": not bool(real_external_result and real_external_result.get("external_action_executed")),
        "missing_connections": external_readiness.get("missing_connections", []),
        "actions_performed": (
            real_external_result.get("actions_performed", [])
            if real_external_result and real_external_result.get("external_action_executed")
            else actions
        ),
        "output": (
            "Real external integration actions executed."
            if real_external_result and real_external_result.get("external_action_executed")
            else output
        ),
'''

if old_success not in content:
    raise SystemExit("SUCCESS_EXTERNAL_FLAGS_BLOCK_NOT_FOUND")

content = content.replace(old_success, new_success)

adapter_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_action_adapters_real_external_bridge.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Conduct stakeholder interviews and create outreach follow-up tasks",
}

ready = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email", "crm", "calendar"],
)

assert ready["performed_actual_action"] is True
assert ready["external_action_ready"] is True
assert ready["external_provider_called"] is True
assert ready["live_external_call_executed"] is True
assert ready["internal_fallback_used"] is False
assert ready["real_external_execution"]["external_action_executed"] is True
assert len(ready["actions_performed"]) >= 2

fallback = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
)

assert fallback["performed_actual_action"] is True
assert fallback["external_action_ready"] is False
assert fallback["external_provider_called"] is False
assert fallback["internal_fallback_used"] is True

print("ACTION_ADAPTERS_REAL_EXTERNAL_BRIDGE_TEST_PASSED")
''', encoding="utf-8")

print("REAL_EXTERNAL_BRIDGE_WIRED_INTO_ACTION_ADAPTERS")
print(f"Backup: {backup_dir}")
print(f"Updated: {adapter_file}")
print(f"Created: {test_file}")