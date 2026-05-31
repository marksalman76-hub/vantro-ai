from backend.app.runtime.signup_agent_selection_bridge import (
    build_signup_activation_packet,
    get_signup_agent_selection_options,
    signup_agent_selection_bridge_status,
    validate_signup_agent_selection,
)

status = signup_agent_selection_bridge_status()
assert status["signup_agent_selection_bridge_ready"] is True
assert status["uses_locked_27_agent_catalogue"] is True

starter = get_signup_agent_selection_options("starter")
assert starter["max_selectable_agents"] == 3
assert starter["available_count"] == 26
assert starter["head_agent_available"] is False

enterprise = get_signup_agent_selection_options("enterprise")
assert enterprise["max_selectable_agents"] == 27
assert enterprise["available_count"] == 27
assert enterprise["head_agent_available"] is True

valid = validate_signup_agent_selection(
    "starter",
    ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert valid["valid"] is True
assert valid["activation_allowed"] is True

blocked = validate_signup_agent_selection("business", ["head_agent"])
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = build_signup_activation_packet(
    "starter",
    ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert packet["status"] == "activation_packet_ready"
assert packet["selected_count"] == 3
assert len(packet["client_visible_agents"]) == 3

print("SIGNUP_AGENT_SELECTION_BRIDGE_DIRECT_TESTS_PASSED")
print("starter_available", starter["available_count"])
print("enterprise_available", enterprise["available_count"])
print("valid_selected", valid["selected_count"])
print("packet_selected", packet["selected_count"])
