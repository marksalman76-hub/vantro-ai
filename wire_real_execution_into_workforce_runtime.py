from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"workforce_runtime_real_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_import = """import time
import uuid
from typing import Dict, Any, List
"""

new_import = """import time
import uuid
from typing import Dict, Any, List

from backend.app.runtime.real_action_execution_bridge import (
    execute_real_action_packet,
)
"""

if old_import not in content:
    raise SystemExit("IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_execution_block = """
        packet_result.update({
            "execution_status": "completed",
            "delegate_execution": "executed",
            "completed_output": specialist["completed_output"],
            "external_action_performed": False,
            "live_external_call_executed": False,
        })

        execution_results.append(packet_result)
"""

new_execution_block = """
        real_execution_result = execute_real_action_packet(
            {
                "packet_id": packet.get("packet_id"),
                "assigned_agent": assigned_agent,
                "implementation_action": (
                    packet.get("implementation_action")
                    or packet.get("title")
                    or specialist["completed_output"]
                ),
                "risk_level": packet.get("risk_level", "medium"),
            },
            actor_role="owner_admin",
            owner_approved=owner_approved,
            tenant_id="owner_admin",
        )

        packet_result.update({
            "execution_status": real_execution_result.get("execution_status"),
            "delegate_execution": (
                "executed"
                if real_execution_result.get("performed_actual_action")
                else "blocked"
            ),
            "performed_actual_action": real_execution_result.get("performed_actual_action", False),
            "real_execution": True,
            "deliverable": real_execution_result.get("deliverable"),
            "completed_output": (
                real_execution_result.get("deliverable", {})
                .get("content", {})
                .get("body")
            ),
            "external_action_performed": real_execution_result.get("external_provider_called", False),
            "live_external_call_executed": real_execution_result.get("external_provider_called", False),
        })

        execution_results.append(packet_result)
"""

if old_execution_block not in content:
    raise SystemExit("EXECUTION_BLOCK_NOT_FOUND")

content = content.replace(old_execution_block, new_execution_block)

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_real_workforce_execution_runtime.py"

test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

plan = {
    "action_packets": [
        {
            "packet_id": "packet_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Create healthcare positioning strategy document",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "packet_002",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Launch paid campaign and increase budget",
            "risk_level": "high",
            "approval_required": True,
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
assert result["completed_count"] >= 1

completed = result["completed_results"][0]

assert completed["real_execution"] is True
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["asset_status"] == "created"

print("REAL_WORKFORCE_EXECUTION_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("REAL_WORKFORCE_EXECUTION_RUNTIME_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")