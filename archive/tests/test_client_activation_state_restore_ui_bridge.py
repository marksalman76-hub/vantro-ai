from pathlib import Path

text = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

assert "/api/activation-state-restore" in text
assert "activation_state_restore_bridge_ready" in text
assert "post_activation_client_changes_blocked" in text
assert "owner_admin_required_for_post_activation_changes" in text
assert "credential_values_exposed: false" in text
assert "customer_safe: true" in text
assert "setSelectedAgents(restoredAgents)" in text

print("CLIENT_ACTIVATION_STATE_RESTORE_UI_BRIDGE_TESTS_PASSED")
print("route_wired", "/api/activation-state-restore" in text)
print("restore_marker", "activation_state_restore_bridge_ready" in text)
