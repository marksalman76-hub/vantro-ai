
from backend.app.runtime.autonomous_governed_action_router import (
    classify_autonomous_governance,
    route_autonomous_governed_packet,
    route_autonomous_governed_packets,
)

safe_packet = {
    "packet_id": "safe_001",
    "recommended_agent": "marketing_specialist_agent",
    "implementation_action": "Create a healthcare positioning strategy document draft",
    "risk_level": "medium",
}

risky_packet = {
    "packet_id": "risk_001",
    "recommended_agent": "marketing_specialist_agent",
    "implementation_action": "Launch paid campaign and increase budget",
    "risk_level": "high",
}

not_owned_packet = {
    "packet_id": "not_owned_001",
    "recommended_agent": "seo_agent",
    "implementation_action": "Create SEO topic cluster draft",
    "risk_level": "medium",
}

safe_classification = classify_autonomous_governance(
    safe_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
)
assert safe_classification["route"] == "autonomous_safe_execution"
assert safe_classification["autonomous_allowed"] is True

safe_result = route_autonomous_governed_packet(
    safe_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert safe_result["routing_status"] == "autonomously_executed"
assert safe_result["performed_actual_action"] is True
assert safe_result["deliverable"]["asset_status"] == "created"

risky_result = route_autonomous_governed_packet(
    risky_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert risky_result["routing_status"] == "queued_for_owner_approval"
assert risky_result["performed_actual_action"] is False

not_owned_result = route_autonomous_governed_packet(
    not_owned_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert not_owned_result["routing_status"] == "recommendation_only"
assert not_owned_result["performed_actual_action"] is False

batch = route_autonomous_governed_packets(
    [safe_packet, risky_packet, not_owned_packet],
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert batch["total_packets"] == 3
assert batch["autonomously_executed_count"] == 1
assert batch["owner_approval_queue_count"] == 1
assert batch["recommendation_only_count"] == 1
assert batch["performed_actual_action_count"] == 1

print("AUTONOMOUS_GOVERNED_ACTION_ROUTER_TEST_PASSED")
