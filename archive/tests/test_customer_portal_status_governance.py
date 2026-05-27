from pathlib import Path
import re

ROOT = Path.cwd()
client = (ROOT / "frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

checks = {
    "status_badge_component": "function CustomerAgentStatusBadge" in client,
    "green_active_dot": "bg-emerald-500" in client,
    "red_inactive_dot": "bg-rose-500" in client,
    "active_uppercase": "ACTIVE" in client,
    "inactive_uppercase": "INACTIVE" in client,
    "selection_locked_notice": "Agent selections are locked after activation" in client,
    "admin_approval_required": "owner/admin approval" in client,
    "business_profile_present": "Business Profile" in client or "Business profile" in client,
    "integrations_present": "Integrations" in client,
    "billing_present": "Billing" in client,
    "support_present": "Support" in client,
    "customer_safe_helper": "customerPortalSafeText" in client,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Customer portal governance checks failed: {failed}"

for forbidden in [
    "provider internals",
    "queue internals",
    "raw JSON",
    "debug route",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "ADMIN_PLATFORM_TOKEN",
    "sk-",
]:
    assert forbidden not in client, f"Forbidden customer portal marker found: {forbidden}"

print("CUSTOMER_PORTAL_STATUS_GOVERNANCE_TESTS_PASSED")
print("active_inactive_status_dots_ready", True)
print("agent_selection_lock_notice_ready", True)
print("customer_safe_wording_ready", True)
print("credential_values_exposed", False)
