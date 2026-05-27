from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "backend" / "app" / "main.py"

backup_dir = root / "backups" / f"owner_admin_entitlement_bypass_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "main.py")

text = target.read_text(encoding="utf-8")

old = '''    system_entitlement_check = hydrate_entitlements_for_execution({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "client_id": request.tenant_id,
        "agent_id": requested_agent,
        "agent_key": requested_agent,
        "requested_agent": requested_agent,
    })

    if not system_entitlement_check.get("execution_allowed"):
        return {
            "success": False,
            "status": "system_entitlement_blocked",
            "error": system_entitlement_check.get("error", "system_entitlement_denied"),
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
            "next_stage": system_entitlement_check.get("next_stage", "owner_admin_review_required"),
            "system_entitlement_check": system_entitlement_check,
            "credential_values_exposed": False,
            "customer_safe": True,
        }'''

new = '''    if owner_admin_internal_execution:
        system_entitlement_check = {
            "execution_allowed": True,
            "entitlement_status": "owner_admin_internal_bypass",
            "owner_admin_entitlement_bypass": True,
            "client_entitlement_gate_applied": False,
            "bypass_reason": "owner_admin_internal_execution",
            "tenant_id": request.tenant_id,
            "requested_agent": requested_agent,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    else:
        system_entitlement_check = hydrate_entitlements_for_execution({
            "actor_role": request.actor_role,
            "tenant_id": request.tenant_id,
            "client_id": request.tenant_id,
            "agent_id": requested_agent,
            "agent_key": requested_agent,
            "requested_agent": requested_agent,
        })

    if not system_entitlement_check.get("execution_allowed"):
        return {
            "success": False,
            "status": "system_entitlement_blocked",
            "error": system_entitlement_check.get("error", "system_entitlement_denied"),
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
            "next_stage": system_entitlement_check.get("next_stage", "owner_admin_review_required"),
            "system_entitlement_check": system_entitlement_check,
            "credential_values_exposed": False,
            "customer_safe": True,
        }'''

if old not in text:
    raise SystemExit("Entitlement check block not found.")

text = text.replace(old, new, 1)
target.write_text(text, encoding="utf-8")

print("OWNER_ADMIN_ENTITLEMENT_BYPASS_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")