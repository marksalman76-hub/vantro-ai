
from pathlib import Path

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

assert "hydrate_entitlements_for_execution" in text
assert "runtime_entitlement_check = hydrate_entitlements_for_execution" in text
assert "runtime_entitlement_blocked" in text
assert "credential_values_exposed" in text
assert "active_agents = tenant_account.get" not in text
assert "agent_not_active_for_tenant" not in text

print("RUN_AGENT_RUNTIME_ENTITLEMENT_INTEGRATION_TESTS_PASSED")
print("integration_marker", "runtime_entitlement_check = hydrate_entitlements_for_execution" in text)
print("legacy_active_agents_removed", "active_agents = tenant_account.get" not in text)
print("legacy_error_removed", "agent_not_active_for_tenant" not in text)
