from pathlib import Path

status_route = Path("frontend/src/app/api/admin-activation-governance/status/route.ts")
summary_route = Path("frontend/src/app/api/admin-activation-governance/summary/route.ts")

assert status_route.exists(), "Missing admin activation governance status route"
assert summary_route.exists(), "Missing admin activation governance summary route"

status_text = status_route.read_text(encoding="utf-8")
summary_text = summary_route.read_text(encoding="utf-8")

assert "activation-governance-admin-visibility/status" in status_text
assert "activation-governance-admin-visibility/summary" in summary_text
assert "ADMIN_PLATFORM_TOKEN" in status_text
assert "ADMIN_PLATFORM_TOKEN" in summary_text
assert "credential_values_exposed: false" in status_text
assert "credential_values_exposed: false" in summary_text
assert "customer_safe: true" in status_text
assert "customer_safe: true" in summary_text
assert "cache: \"no-store\"" in status_text
assert "cache: \"no-store\"" in summary_text

print("FRONTEND_ACTIVATION_GOVERNANCE_ADMIN_BRIDGE_TESTS_PASSED")
print("status_route_exists", status_route.exists())
print("summary_route_exists", summary_route.exists())
print("admin_token_fallback", "ADMIN_PLATFORM_TOKEN" in status_text and "ADMIN_PLATFORM_TOKEN" in summary_text)
