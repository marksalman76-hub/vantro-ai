from pathlib import Path

from backend.app.runtime.activation_execution_audit_link import (
    get_activation_execution_audit_status,
    list_activation_execution_decisions,
    record_activation_execution_decision,
)
from backend.app.runtime.governed_activation_persistence import (
    get_activation_persistence_status,
    hydrate_activation_state,
    persist_activation_packet,
)
from backend.app.runtime.runtime_entitlement_hydration_bridge import (
    get_runtime_entitlement_hydration_bridge_status,
    hydrate_entitlements_for_execution,
)

tenant_id = "verify-activation-lifecycle-lock-chain-001"

activation_status = get_activation_persistence_status()
assert activation_status["governed_activation_persistence_ready"] is True
assert activation_status["credential_values_exposed"] is False

packet = {
    "tenant_id": tenant_id,
    "package_id": "business",
    "selected_agents": ["seo_agent", "email_reply_agent"],
}

persisted = persist_activation_packet(packet, actor_role="system")
assert persisted["success"] is True
assert persisted["status"] == "activated"
assert persisted["activation_record"]["activation_locked"] is True

hydrated = hydrate_activation_state(tenant_id)
assert hydrated["success"] is True
assert hydrated["activation_locked"] is True
assert hydrated["entitlement_hydrated"] is True
assert "seo_agent" in hydrated["activated_agents"]

second_packet = persist_activation_packet(
    {
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["head_agent"],
    },
    actor_role="client",
)
assert second_packet["success"] is False
assert second_packet["status"] == "blocked"
assert second_packet["next_stage"] == "owner_admin_review_required"

runtime_status = get_runtime_entitlement_hydration_bridge_status()
assert runtime_status["runtime_entitlement_hydration_bridge_ready"] is True
assert runtime_status["credential_values_exposed"] is False

approved_runtime = hydrate_entitlements_for_execution(
    {
        "actor_role": "client",
        "tenant_id": tenant_id,
        "agent_id": "seo_agent",
    }
)
assert approved_runtime["success"] is True
assert approved_runtime["execution_allowed"] is True

blocked_runtime = hydrate_entitlements_for_execution(
    {
        "actor_role": "client",
        "tenant_id": tenant_id,
        "agent_id": "head_agent",
    }
)
assert blocked_runtime["success"] is False
assert blocked_runtime["execution_allowed"] is False
assert blocked_runtime["next_stage"] == "owner_admin_review_required"

audit_status = get_activation_execution_audit_status()
assert audit_status["activation_execution_audit_link_ready"] is True
assert audit_status["credential_values_exposed"] is False

record_activation_execution_decision(
    tenant_id=tenant_id,
    requested_agent="seo_agent",
    actor_role="client",
    execution_allowed=True,
    entitlement_check=approved_runtime,
)

record_activation_execution_decision(
    tenant_id=tenant_id,
    requested_agent="head_agent",
    actor_role="client",
    execution_allowed=False,
    entitlement_check=blocked_runtime,
)

audit_events = list_activation_execution_decisions(tenant_id)
assert audit_events["success"] is True
assert audit_events["event_count"] >= 2
assert audit_events["credential_values_exposed"] is False

frontend_restore_route = Path("frontend/src/app/api/activation-state-restore/route.ts")
client_page = Path("frontend/src/app/client/page.tsx")

assert frontend_restore_route.exists()
assert client_page.exists()

restore_text = frontend_restore_route.read_text(encoding="utf-8")
client_text = client_page.read_text(encoding="utf-8")

assert "activation_state_restore_bridge_ready" in restore_text
assert "governed-activation-persistence/hydrate" in restore_text
assert "credential_values_exposed: false" in restore_text
assert "customer_safe: true" in restore_text

assert "/api/activation-state-restore" in client_text
assert "AGENTS LOCKED" in client_text
assert "RESTORED" in client_text
assert "CHANGES REQUIRE APPROVAL" in client_text
assert "credential_values_exposed: false" in client_text
assert "customer_safe: true" in client_text

print("ACTIVATION_LIFECYCLE_LOCK_CHAIN_VERIFICATION_PASSED")
print("activation_persistence_ready", activation_status["governed_activation_persistence_ready"])
print("persisted_status", persisted["status"])
print("hydrated_status", hydrated["status"])
print("second_packet_status", second_packet["status"])
print("runtime_bridge_ready", runtime_status["runtime_entitlement_hydration_bridge_ready"])
print("approved_runtime_status", approved_runtime["status"])
print("blocked_runtime_error", blocked_runtime["error"])
print("audit_link_ready", audit_status["activation_execution_audit_link_ready"])
print("audit_event_count", audit_events["event_count"])
print("frontend_restore_route", frontend_restore_route.exists())
print("client_restore_wiring", "/api/activation-state-restore" in client_text)
print("client_lock_visibility", "AGENTS LOCKED" in client_text)