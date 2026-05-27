
from backend.app.runtime.runtime_entitlement_hydration_bridge import (
    get_runtime_entitlement_hydration_bridge_status,
    hydrate_entitlements_for_execution,
    seed_execution_entitlements_from_activation_packet,
)

tenant_id = "test-runtime-entitlement-hydration-001"

status = get_runtime_entitlement_hydration_bridge_status()
assert status["runtime_entitlement_hydration_bridge_ready"] is True
assert status["credential_values_exposed"] is False

missing_tenant = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "agent_id": "seo_agent",
})
assert missing_tenant["success"] is False
assert missing_tenant["error"] == "missing_tenant_id"

owner = hydrate_entitlements_for_execution({
    "actor_role": "owner_admin",
    "agent_id": "head_agent",
})
assert owner["success"] is True
assert owner["execution_allowed"] is True
assert owner["runtime_entitlements"]["owner_admin_unrestricted"] is True

missing_activation = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "seo_agent",
})
assert missing_activation["success"] is False
assert missing_activation["error"] == "activation_state_not_found"

seeded = seed_execution_entitlements_from_activation_packet({
    "tenant_id": tenant_id,
    "package_id": "business",
    "selected_agents": ["seo_agent", "email_reply_agent"],
    "actor_role": "system",
})
assert seeded["success"] is True
assert seeded["status"] == "activated"

approved = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "seo_agent",
})
assert approved["success"] is True
assert approved["execution_allowed"] is True
assert approved["status"] == "approved"

blocked = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "head_agent",
})
assert blocked["success"] is False
assert blocked["execution_allowed"] is False
assert blocked["error"] == "requested_agent_not_activated"
assert blocked["next_stage"] == "owner_admin_review_required"

print("RUNTIME_ENTITLEMENT_HYDRATION_BRIDGE_TESTS_PASSED")
print("status_ready", status["runtime_entitlement_hydration_bridge_ready"])
print("missing_tenant_status", missing_tenant["status"])
print("owner_status", owner["status"])
print("missing_activation_error", missing_activation["error"])
print("seeded_status", seeded["status"])
print("approved_status", approved["status"])
print("blocked_error", blocked["error"])
