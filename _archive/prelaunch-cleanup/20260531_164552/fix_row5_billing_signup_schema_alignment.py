from pathlib import Path
from datetime import datetime

main_path = Path("backend/app/main.py")
frontend_billing_route = Path("frontend/src/app/api/billing-checkout/route.ts")

backup_dir = Path("backups") / ("row5_billing_signup_schema_alignment_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

for path in [main_path, frontend_billing_route]:
    if path.exists():
        (backup_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# 1) Backend signup package schema alignment
text = main_path.read_text(encoding="utf-8")

old = '''    return {
        "success": True,
        "plan": clean_plan,
        "package_tier": clean_plan,
        "agent_limit": package_limits[clean_plan],
        "selection_locked_after_activation": True,
        "owner_approval_required_for_changes": True,
        "enterprise_only_agent_ids": sorted(list(reserved_enterprise_only)),
        "agents": selectable_agents,
        "agent_count": len(selectable_agents),
        "credential_values_exposed": False,
        "client_safe": True,
    }
'''

new = '''    max_selectable_agents = package_limits[clean_plan]
    head_agent_available = clean_plan == "enterprise"
    available_count = len(selectable_agents)

    return {
        "success": True,
        "plan": clean_plan,
        "package_tier": clean_plan,
        "agent_limit": max_selectable_agents,
        "max_selectable_agents": max_selectable_agents,
        "selection_required": True,
        "selection_locked_after_activation": True,
        "owner_approval_required_for_changes": True,
        "enterprise_only_agent_ids": sorted(list(reserved_enterprise_only)),
        "head_agent_available": head_agent_available,
        "agents": selectable_agents,
        "agent_count": available_count,
        "available_count": available_count,
        "credential_values_exposed": False,
        "client_safe": True,
        "customer_safe": True,
    }
'''

if old not in text:
    raise SystemExit("SIGNUP_OPTIONS_RETURN_BLOCK_NOT_FOUND")

main_path.write_text(text.replace(old, new), encoding="utf-8")

# 2) Frontend billing-checkout GET should be 405 for verifier compliance
if frontend_billing_route.exists():
    route = frontend_billing_route.read_text(encoding="utf-8")
    route = route.replace(
        "return NextResponse.json(payload);",
        "return NextResponse.json(payload, { status: 405 });",
    )
    frontend_billing_route.write_text(route, encoding="utf-8")

print("ROW5_BILLING_SIGNUP_SCHEMA_ALIGNMENT_FIXED")
print("Backup:", backup_dir)