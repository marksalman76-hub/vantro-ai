from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"workforce_runtime_action_history_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_import = """from backend.app.runtime.autonomous_governed_action_router import (
    route_autonomous_governed_packet,
)
"""

new_import = """from backend.app.runtime.autonomous_governed_action_router import (
    route_autonomous_governed_packet,
)
from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
)
"""

if old_import not in content:
    raise SystemExit("AUTONOMOUS_ROUTER_IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_block = """        else:
            execution_results.append(packet_result)
"""

new_block = """        else:
            history_record = record_action_execution(
                tenant_id="owner_admin" if enterprise_access else "client",
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                execution_payload=packet_result,
            )
            packet_result["history_id"] = history_record.get("history_id")
            packet_result["history_persisted"] = True
            execution_results.append(packet_result)
"""

if old_block not in content:
    raise SystemExit("EXECUTION_APPEND_BLOCK_NOT_FOUND")

content = content.replace(old_block, new_block)

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_action_history_workforce_runtime.py"
test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan
from backend.app.runtime.persistent_action_execution_history import list_action_execution_history

plan = {
    "action_packets": [
        {
            "packet_id": "history_auto_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
)

assert result["success"] is True
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["performed_actual_action"] is True
assert completed["history_persisted"] is True
assert completed["history_id"]

history = list_action_execution_history(tenant_id="owner_admin", limit=10)
assert history["success"] is True
assert history["count"] >= 1
assert any(r.get("packet_id") == "history_auto_001" for r in history["records"])

print("ACTION_HISTORY_WORKFORCE_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("ACTION_HISTORY_WIRED_INTO_WORKFORCE_RUNTIME")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")