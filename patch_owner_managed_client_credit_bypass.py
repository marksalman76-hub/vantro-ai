from pathlib import Path

p = Path("backend/app/main.py")
text = p.read_text(encoding="utf-8")

old = '''    actor_role = (request.actor_role or "").strip().lower()
    owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}

    if not credit_gate.get("credit_gate_passed") and not owner_admin_credit_bypass:
'''

new = '''    actor_role = (request.actor_role or "").strip().lower()
    tenant_id_clean = str(request.tenant_id or "").strip().lower()
    package_tier_clean = str(getattr(request, "package_tier", "") or "").strip().lower()

    owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}

    owner_managed_client_credit_bypass = (
        tenant_id_clean in {"client_demo_001", "owner_managed_demo", "manual_deployment_client"}
        or package_tier_clean in {"owner_managed", "manual_deployment", "demo", "internal"}
    )

    if not credit_gate.get("credit_gate_passed") and owner_managed_client_credit_bypass:
        credit_gate = {
            **credit_gate,
            "credit_gate_passed": True,
            "owner_managed_client_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_managed_or_demo_client_not_credit_limited",
        }

    if not credit_gate.get("credit_gate_passed") and not owner_admin_credit_bypass:
'''

if old not in text:
    raise SystemExit("credit gate block anchor not found")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("OWNER_MANAGED_CLIENT_CREDIT_BYPASS_PATCHED")