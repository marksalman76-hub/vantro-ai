from pathlib import Path

p = Path("backend/app/main.py")
text = p.read_text(encoding="utf-8")

old = '''    requested_agent = normalise_agent_identity(normalize_agent_id(request.requested_agent))

    credit_gate = pg_client_credit_gate({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "requested_credits": request.requested_credits,
    })

    actor_role = (request.actor_role or "").strip().lower()
'''

new = '''    requested_agent = normalise_agent_identity(normalize_agent_id(request.requested_agent))

    actor_role = (request.actor_role or "").strip().lower()
    tenant_id_clean = str(request.tenant_id or "").strip().lower()

    owner_managed_client_credit_bypass = (
        tenant_id_clean in {
            "client_demo_001",
            "owner_managed_demo",
            "owner_managed_demo_client",
            "manual_deployment_client",
            "internal_demo_client",
        }
        or tenant_id_clean.startswith("owner_managed_")
        or tenant_id_clean.startswith("manual_deployment_")
        or tenant_id_clean.startswith("demo_")
    )

    if owner_managed_client_credit_bypass:
        credit_gate = {
            "success": True,
            "credit_gate_passed": True,
            "owner_managed_client_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_managed_or_demo_client_not_credit_limited",
        }
    else:
        credit_gate = pg_client_credit_gate({
            "actor_role": request.actor_role,
            "tenant_id": request.tenant_id,
            "requested_credits": request.requested_credits,
        })

'''

if old not in text:
    raise SystemExit("pre-credit-gate anchor not found")

text = text.replace(old, new, 1)

# Remove duplicate variables from the previous after-gate patch if present.
text = text.replace('''    tenant_id_clean = str(request.tenant_id or "").strip().lower()
    package_tier_clean = str(getattr(request, "package_tier", "") or "").strip().lower()

''', "")

p.write_text(text, encoding="utf-8")
print("OWNER_MANAGED_BYPASS_MOVED_BEFORE_CREDIT_GATE")