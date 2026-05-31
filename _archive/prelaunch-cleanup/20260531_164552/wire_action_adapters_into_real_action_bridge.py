from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
bridge_file = ROOT / "backend" / "app" / "runtime" / "real_action_execution_bridge.py"

backup_dir = ROOT / "backups" / f"real_action_bridge_adapter_wire_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(bridge_file, backup_dir / bridge_file.name)

content = bridge_file.read_text(encoding="utf-8")

old_import = """from uuid import uuid4
"""

new_import = """from uuid import uuid4

from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter
"""

if old_import not in content:
    raise SystemExit("IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_deliverable_block = """    deliverable = {
        "deliverable_id": f"deliverable_{uuid4().hex[:12]}",
        "type": action_type,
        "title": f"Executed: {str(implementation_action)[:90]}",
        "summary": str(implementation_action),
        "created_by_agent": assigned_agent,
        "customer_safe": True,
        "asset_status": "created",
        "download_ready": False,
        "preview_ready": True,
        "content": {
            "headline": f"{assigned_agent} completed the approved task.",
            "body": str(implementation_action),
            "next_step": "Review the created output, then approve client delivery or request amendment.",
        },
    }

    return {
        "success": True,
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "source_packet_id": source_packet_id,
        "assigned_agent": assigned_agent,
        "action_type": action_type,
        "adapter": adapter,
        "execution_status": "executed_internal_action",
        "performed_actual_action": True,
        "owner_approval_required": False,
        "external_provider_called": False,
        "credential_values_exposed": False,
        "customer_safe_message": "Approved action executed and customer-safe deliverable created.",
        "deliverable": deliverable,
        "created_at": _now(),
    }
"""

new_deliverable_block = """    adapter_execution = execute_action_adapter(
        {
            **packet,
            "assigned_agent": assigned_agent,
            "implementation_action": implementation_action,
            "action_type": action_type,
        },
        tenant_id=tenant_id,
    )

    if adapter_execution.get("owner_approval_required") and not owner_approved:
        return {
            "success": True,
            "execution_id": execution_id,
            "tenant_id": tenant_id,
            "source_packet_id": source_packet_id,
            "assigned_agent": assigned_agent,
            "action_type": action_type,
            "adapter": adapter_execution.get("adapter", adapter),
            "execution_status": "blocked_owner_approval_required",
            "performed_actual_action": False,
            "owner_approval_required": True,
            "external_provider_called": False,
            "credential_values_exposed": False,
            "customer_safe_message": adapter_execution.get("output"),
            "actions_performed": adapter_execution.get("actions_performed", []),
            "created_at": _now(),
        }

    deliverable = {
        "deliverable_id": f"deliverable_{uuid4().hex[:12]}",
        "type": action_type,
        "title": f"Executed: {str(implementation_action)[:90]}",
        "summary": adapter_execution.get("output") or str(implementation_action),
        "created_by_agent": assigned_agent,
        "customer_safe": True,
        "asset_status": adapter_execution.get("asset", {}).get("status", "created"),
        "download_ready": adapter_execution.get("asset", {}).get("download_ready", False),
        "preview_ready": adapter_execution.get("asset", {}).get("preview_ready", True),
        "actions_performed": adapter_execution.get("actions_performed", []),
        "adapter": adapter_execution.get("adapter"),
        "asset": adapter_execution.get("asset"),
        "content": {
            "headline": f"{assigned_agent} executed an operational adapter.",
            "body": adapter_execution.get("output") or str(implementation_action),
            "next_step": "Review the created operational actions, then approve client delivery or request amendment.",
        },
    }

    return {
        "success": True,
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "source_packet_id": source_packet_id,
        "assigned_agent": assigned_agent,
        "action_type": action_type,
        "adapter": adapter_execution.get("adapter", adapter),
        "execution_status": adapter_execution.get("execution_status", "adapter_action_executed"),
        "performed_actual_action": adapter_execution.get("performed_actual_action", True),
        "owner_approval_required": adapter_execution.get("owner_approval_required", False),
        "external_provider_called": adapter_execution.get("external_provider_called", False),
        "credential_values_exposed": False,
        "customer_safe_message": adapter_execution.get("output"),
        "actions_performed": adapter_execution.get("actions_performed", []),
        "deliverable": deliverable,
        "created_at": _now(),
    }
"""

if old_deliverable_block not in content:
    raise SystemExit("DELIVERABLE_BLOCK_NOT_FOUND")

content = content.replace(old_deliverable_block, new_deliverable_block)

bridge_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_real_action_bridge_with_adapters.py"
test_file.write_text(r'''
from backend.app.runtime.real_action_execution_bridge import execute_real_action_packet

interview_packet = {
    "packet_id": "adapter_bridge_001",
    "assigned_agent": "marketing_specialist_agent",
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
    "risk_level": "medium",
}

result = execute_real_action_packet(interview_packet, tenant_id="tenant_test")

assert result["success"] is True
assert result["performed_actual_action"] is True
assert result["execution_status"] == "adapter_action_executed"
assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(result["actions_performed"]) >= 2
assert result["deliverable"]["actions_performed"][0]["type"] == "email_draft_created"

risky_packet = {
    "packet_id": "adapter_bridge_risky_001",
    "assigned_agent": "marketing_specialist_agent",
    "implementation_action": "Launch paid campaign and increase budget",
    "risk_level": "high",
}

risky_result = execute_real_action_packet(risky_packet, tenant_id="tenant_test", owner_approved=False)

assert risky_result["performed_actual_action"] is False
assert risky_result["owner_approval_required"] is True
assert risky_result["execution_status"] == "blocked_owner_approval_required"

print("REAL_ACTION_BRIDGE_WITH_ADAPTERS_TEST_PASSED")
''', encoding="utf-8")

print("ACTION_ADAPTERS_WIRED_INTO_REAL_ACTION_BRIDGE")
print(f"Backup: {backup_dir}")
print(f"Updated: {bridge_file}")
print(f"Created: {test_file}")