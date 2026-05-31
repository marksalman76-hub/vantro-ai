from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"workforce_runtime_autonomous_router_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_import = """from backend.app.runtime.real_action_execution_bridge import (
    execute_real_action_packet,
)
"""

new_import = """from backend.app.runtime.autonomous_governed_action_router import (
    route_autonomous_governed_packet,
)
"""

if old_import not in content:
    raise SystemExit("REAL_ACTION_IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_block = """        real_execution_result = execute_real_action_packet(
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

new_block = """        autonomous_route_result = route_autonomous_governed_packet(
            {
                "packet_id": packet.get("packet_id"),
                "assigned_agent": assigned_agent,
                "recommended_agent": assigned_agent,
                "implementation_action": (
                    packet.get("implementation_action")
                    or packet.get("title")
                    or specialist["completed_output"]
                ),
                "risk_level": packet.get("risk_level", "medium"),
            },
            package_tier=package_tier,
            client_owned_agents=client_owned_agents,
            actor_role="owner_admin" if enterprise_access else "client",
            tenant_id="owner_admin" if enterprise_access else "client",
            owner_approved=owner_approved,
        )

        packet_result.update({
            "execution_status": autonomous_route_result.get("routing_status"),
            "delegate_execution": (
                "executed"
                if autonomous_route_result.get("performed_actual_action")
                else "blocked"
            ),
            "performed_actual_action": autonomous_route_result.get("performed_actual_action", False),
            "autonomous_governance": True,
            "autonomous_route": autonomous_route_result.get("routing_status"),
            "governance": autonomous_route_result.get("governance"),
            "real_execution": True,
            "deliverable": autonomous_route_result.get("deliverable"),
            "completed_output": (
                autonomous_route_result.get("deliverable", {})
                .get("content", {})
                .get("body")
            ),
            "external_action_performed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
            "live_external_call_executed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
        })

        if autonomous_route_result.get("routing_status") in {
            "queued_for_owner_approval",
            "manual_review_required",
        }:
            queued_results.append(packet_result)
        elif autonomous_route_result.get("routing_status") == "recommendation_only":
            blocked_results.append(packet_result)
        else:
            execution_results.append(packet_result)
"""

if old_block not in content:
    raise SystemExit("REAL_EXECUTION_BLOCK_NOT_FOUND")

content = content.replace(old_block, new_block)

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_autonomous_workforce_runtime.py"

test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

plan = {
    "action_packets": [
        {
            "packet_id": "auto_safe_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Create healthcare positioning strategy document draft",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "auto_risky_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Launch paid campaign and increase budget",
            "risk_level": "high",
            "approval_required": False,
        },
        {
            "packet_id": "auto_not_owned_001",
            "recommended_agent": "seo_agent",
            "implementation_action": "Create SEO topic cluster draft",
            "risk_level": "medium",
            "approval_required": False,
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="business",
)

assert result["success"] is True
assert result["completed_count"] == 1
assert result["queued_count"] == 1
assert result["blocked_count"] == 1

completed = result["completed_results"][0]
assert completed["autonomous_governance"] is True
assert completed["autonomous_route"] == "autonomously_executed"
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["asset_status"] == "created"

queued = result["queued_results"][0]
assert queued["autonomous_route"] == "queued_for_owner_approval"
assert queued["performed_actual_action"] is False

blocked = result["blocked_results"][0]
assert blocked["autonomous_route"] == "recommendation_only"
assert blocked["performed_actual_action"] is False

enterprise_result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=[],
    package_tier="enterprise",
)

assert enterprise_result["success"] is True
assert enterprise_result["completed_count"] == 2
assert enterprise_result["queued_count"] == 1
assert enterprise_result["blocked_count"] == 0

print("AUTONOMOUS_WORKFORCE_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("AUTONOMOUS_ROUTER_WIRED_INTO_WORKFORCE_RUNTIME")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")