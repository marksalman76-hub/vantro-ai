from pathlib import Path

p = Path("backend/app/main.py")
text = p.read_text(encoding="utf-8")

old = '''    if not tenant_account.get("success"):
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
'''

new = '''    if not tenant_account.get("success"):
        if not owner_admin_internal_execution and not owner_managed_client_credit_bypass:
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
                "owner_admin_internal_bypass": owner_admin_internal_execution,
                "owner_managed_client_bypass": owner_managed_client_credit_bypass,
            },
        }
'''

if old not in text:
    raise SystemExit("tenant account block anchor not found")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("OWNER_MANAGED_TENANT_ACCOUNT_BYPASS_PATCHED")