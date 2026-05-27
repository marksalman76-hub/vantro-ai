from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

old_block = '''    if request.tenant_id not in DEMO_TENANTS:
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }

    if not agent_exists(request.requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
        }

    if request.requested_agent not in DEMO_TENANTS[request.tenant_id]:
        return {
            "success": False,
            "error": "agent_not_active_for_tenant",
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
        }
'''

new_block = '''    if not agent_exists(request.requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
        }

    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success"):
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }

    active_agents = tenant_account.get("account", {}).get("active_agents", [])

    if request.actor_role not in {"owner", "admin", "system"}:
        if request.requested_agent not in active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
            }
'''

if old_block not in text:
    raise SystemExit("Expected DEMO_TENANTS check block not found. Stop and inspect run_agent.")

text = text.replace(old_block, new_block)

MAIN.write_text(text, encoding="utf-8")

print("STEP_191_RUN_AGENT_DURABLE_TENANT_CHECK_INSTALLED")
print("STEP_191_OK")