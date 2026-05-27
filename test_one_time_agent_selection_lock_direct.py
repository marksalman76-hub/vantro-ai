from backend.app.runtime.one_time_agent_selection_lock import (
    activate_agent_selection_once,
    create_agent_selection_draft,
    get_activated_agent_selection,
    one_time_agent_selection_lock_status,
    request_post_activation_agent_change,
    reset_one_time_agent_selection_lock_for_tests,
)

reset = reset_one_time_agent_selection_lock_for_tests()
assert reset["reset"] is True

status = one_time_agent_selection_lock_status()
assert status["client_selects_once_per_package"] is True
assert status["selection_locked_after_activation"] is True

draft = create_agent_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert draft["status"] == "draft_created"
assert draft["draft"]["activation_allowed"] is True

activated = activate_agent_selection_once(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    draft_id=draft["draft"]["draft_id"],
)
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False
assert len(activated["activated_selection"]["active_agents"]) == 3

second_draft = create_agent_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["crm_agent"],
)
assert second_draft["status"] == "blocked"
assert second_draft["reason"] == "package_agent_selection_already_activated"

second_activate = activate_agent_selection_once(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    draft_id=draft["draft"]["draft_id"],
)
assert second_activate["status"] == "blocked"
assert second_activate["reason"] == "package_agent_selection_already_activated"

existing = get_activated_agent_selection(
    tenant_id="tenant-test",
    package_id="package-starter-1",
)
assert existing["status"] == "found"
assert existing["client_can_change_selection"] is False

change = request_post_activation_agent_change(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    requested_agent_keys=["crm_agent"],
    reason="Client wants to swap.",
)
assert change["status"] == "owner_admin_review_required"
assert change["client_can_change_selection"] is False

print("ONE_TIME_AGENT_SELECTION_LOCK_DIRECT_TESTS_PASSED")
print("activated_status", activated["status"])
print("active_agents", len(activated["activated_selection"]["active_agents"]))
print("second_draft", second_draft["status"], second_draft["reason"])
print("change_status", change["status"])
