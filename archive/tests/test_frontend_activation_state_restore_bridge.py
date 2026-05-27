from pathlib import Path

route = Path("frontend/src/app/api/activation-state-restore/route.ts")
assert route.exists(), "Missing activation-state-restore API route"

text = route.read_text(encoding="utf-8")

assert "activation_state_restore_bridge_ready" in text
assert "governed-activation-persistence/hydrate" in text
assert "ADMIN_PLATFORM_TOKEN" in text
assert "credential_values_exposed: false" in text
assert "customer_safe: true" in text
assert "cache: \"no-store\"" in text
assert "missing_tenant_id" in text
assert "auth_required" in text

print("FRONTEND_ACTIVATION_STATE_RESTORE_BRIDGE_TESTS_PASSED")
print("route_exists", route.exists())
print("restore_marker", "activation_state_restore_bridge_ready" in text)
print("backend_hydrate_bridge", "governed-activation-persistence/hydrate" in text)
