from pathlib import Path

ROOT = Path.cwd()
admin = (ROOT / "frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

checks = {
    "admin_command_centre": "Admin Command Centre" in admin,
    "provider_execution_link": "/admin/provider-execution" in admin,
    "runtime_health": "Runtime Health" in admin,
    "approvals": "Approvals" in admin,
    "clients_tenants": "Clients & Tenants" in admin,
    "entitlements": "Entitlements" in admin,
    "billing": "Billing" in admin,
    "agent_execution": "Agent Execution" in admin,
    "integrations": "Integrations" in admin,
    "readiness_panel": "Readiness Panel" in admin,
    "owner_governance_rules": "Owner Governance Rules" in admin,
    "credential_exposure_false": "Credential exposure" in admin and "FALSE" in admin,
    "owner_spend_rule": "No agent may increase spend without owner approval." in admin,
    "customer_safe_wording": "customer-safe" in admin.lower(),
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Admin owner control plane checks failed: {failed}"

for forbidden in [
    "sk-",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "raw JSON",
    "debug route",
]:
    assert forbidden not in admin, f"Forbidden marker found in admin page: {forbidden}"

print("ADMIN_OWNER_CONTROL_PLANE_TESTS_PASSED")
print("admin_command_centre_ready", True)
print("provider_execution_link_ready", True)
print("readiness_panel_ready", True)
print("credential_values_exposed", False)
