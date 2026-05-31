from backend.app.runtime.catalogue_entitlement_bridge import (
    build_agent_activation_entitlement_packet,
    catalogue_entitlement_bridge_status,
    get_package_catalogue_rules,
    list_package_selectable_agents,
    validate_package_agent_selection,
)

status = catalogue_entitlement_bridge_status()
assert status["catalogue_entitlement_bridge_ready"] is True
assert status["commercial_catalogue_count"] == 27

starter_rules = get_package_catalogue_rules("starter")
assert starter_rules["rules"]["max_selectable_agents"] == 3

business_agents = list_package_selectable_agents("business")
assert business_agents["available_count"] == 26
assert business_agents["head_agent_available"] is False

enterprise_agents = list_package_selectable_agents("enterprise")
assert enterprise_agents["available_count"] == 27
assert enterprise_agents["head_agent_available"] is True

valid = validate_package_agent_selection(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert valid["valid"] is True
assert valid["selected_count"] == 3

over_limit = validate_package_agent_selection(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent", "crm_agent"],
)
assert over_limit["valid"] is False
assert over_limit["over_limit"] is True

blocked = validate_package_agent_selection(
    plan="business",
    selected_agent_keys=["head_agent"],
)
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = build_agent_activation_entitlement_packet(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert packet["activation_allowed"] is True
assert len(packet["active_agents"]) == 3
assert packet["client_access_limited_to_paid_selected_agents"] is True
assert packet["full_catalogue_installed_for_owner_admin"] is True

print("CATALOGUE_ENTITLEMENT_BRIDGE_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("business_available", business_agents["available_count"])
print("enterprise_available", enterprise_agents["available_count"])
print("packet_active_agents", len(packet["active_agents"]))
print("hidden_unpurchased", packet["client_hidden_agents_count"])
