from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_step211_owner_admin_internal_bypass_{timestamp}.py"

text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

old = '''    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success") or not tenant_account.get("account"):
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }

    active_agents = tenant_account["account"].get("active_agents", [])
    normalised_active_agents = {AGENT_ALIAS_MAP.get(agent, agent) for agent in active_agents}

    if request.actor_role not in {"owner", "admin", "system"}:
        if requested_agent not in normalised_active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
                "normalised_agent": requested_agent,
                "active_agents": active_agents,
            }
'''

new = '''    owner_admin_internal_execution = request.actor_role in {"owner", "admin", "system"}

    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success") or not tenant_account.get("account"):
        if not owner_admin_internal_execution:
            return {
                "success": False,
                "error": "tenant_not_found_or_not_active",
                "tenant_id": request.tenant_id,
            }

        tenant_account = {
            "success": True,
            "account": {
                "tenant_id": request.tenant_id,
                "active_agents": [requested_agent],
                "owner_admin_internal_bypass": True,
            },
        }

    active_agents = tenant_account["account"].get("active_agents", [])
    normalised_active_agents = {AGENT_ALIAS_MAP.get(agent, agent) for agent in active_agents}

    if not owner_admin_internal_execution:
        if requested_agent not in normalised_active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
                "normalised_agent": requested_agent,
                "active_agents": active_agents,
            }
'''

if old not in text:
    raise RuntimeError("Expected tenant/account entitlement block not found. Refusing unsafe edit.")

text = text.replace(old, new)

main_file.write_text(text, encoding="utf-8")
py_compile.compile(str(main_file), doraise=True)

print("STEP_211_OWNER_ADMIN_INTERNAL_BYPASS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print("STEP_211_OK")