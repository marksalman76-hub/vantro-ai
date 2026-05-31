from backend.app.runtime.real_agent_component_catalogue import (
    calculate_catalogue_counts,
    get_catalogue_component_by_key,
    list_client_selectable_agents,
    list_real_agent_component_catalogue,
    real_agent_component_catalogue_status,
)

status = real_agent_component_catalogue_status()
assert status["real_agent_component_catalogue_locked"] is True
assert status["commercial_catalogue_count"] == 27
assert status["visible_agent_count"] == 33
assert status["operational_component_count"] == 48
assert status["client_catalogue_is_not_same_as_runtime_component_count"] is True

counts = calculate_catalogue_counts()
assert counts["client_facing_agents"] == 27
assert counts["system_agents"] == 6
assert counts["runtime_intelligence_components"] == 10
assert counts["hidden_internal_layers"] == 5

catalogue = list_real_agent_component_catalogue()
assert catalogue["commercial_catalogue_count"] == 27
assert catalogue["total_operational_component_count"] == 48

head = get_catalogue_component_by_key("head_agent")
assert head["found"] is True
assert head["component"]["enterprise_only"] is True

quality = get_catalogue_component_by_key("global_output_quality_runtime")
assert quality["found"] is True
assert quality["component_type"] == "runtime_intelligence_component"

business_agents = list_client_selectable_agents("business")
assert business_agents["head_agent_available"] is False
assert business_agents["count"] == 26

enterprise_agents = list_client_selectable_agents("enterprise")
assert enterprise_agents["head_agent_available"] is True
assert enterprise_agents["count"] == 27

print("REAL_AGENT_COMPONENT_CATALOGUE_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("visible_agent_count", status["visible_agent_count"])
print("operational_component_count", status["operational_component_count"])
print("business_selectable", business_agents["count"])
print("enterprise_selectable", enterprise_agents["count"])
