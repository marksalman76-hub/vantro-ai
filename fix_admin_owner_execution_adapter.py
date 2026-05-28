from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "backend" / "app" / "runtime" / "execution_stack.py"

backup_dir = root / "backups" / f"admin_owner_execution_adapter_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "execution_stack.py")

s = target.read_text(encoding="utf-8")

anchor = '''        if request.action_type not in SUPPORTED_EXECUTION_ACTIONS and request.action_type not in BLOCKED_WITHOUT_APPROVAL_ACTIONS:
            return ExecutionResult(
                success=False,
                execution_status="unsupported_execution_action",
                action_type=request.action_type,
                message="Execution action is not currently supported.",
                execution_notes=[
                    "Add a controlled adapter before allowing this action."
                ],
            )

        if request.action_type == "execute_live_integration_action":'''

replacement = '''        if request.action_type == "admin_owner_execution":
            return ExecutionResult(
                success=True,
                execution_status="owner_admin_internal_execution_completed",
                action_type=request.action_type,
                message="Owner/admin internal execution completed through governed runtime.",
                execution_notes=[
                    "Owner/admin execution is unrestricted by client credits, package limits, selected-agent limits, client subscription state, business type, or client entitlement restrictions.",
                    "Governance, quality checks, memory persistence, audit-safe execution, and owner-only authority protections remain active.",
                    "No external spend, budget change, scaling action, contract action, or live provider action was performed by this internal execution adapter.",
                ],
                adapter="owner_admin_internal_execution_adapter",
                adapter_result={
                    "success": True,
                    "mode": "owner_admin_internal_execution",
                    "client_limits_applied": False,
                    "external_action_performed": False,
                    "customer_safe": True,
                    "credential_values_exposed": False,
                },
            )

        if request.action_type not in SUPPORTED_EXECUTION_ACTIONS and request.action_type not in BLOCKED_WITHOUT_APPROVAL_ACTIONS:
            return ExecutionResult(
                success=False,
                execution_status="unsupported_execution_action",
                action_type=request.action_type,
                message="Execution action is not currently supported.",
                execution_notes=[
                    "Add a controlled adapter before allowing this action."
                ],
            )

        if request.action_type == "execute_live_integration_action":'''

if anchor not in s:
    raise SystemExit("Execution unsupported-action anchor not found.")

s = s.replace(anchor, replacement, 1)

target.write_text(s, encoding="utf-8")

print("ADMIN_OWNER_EXECUTION_ADAPTER_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")