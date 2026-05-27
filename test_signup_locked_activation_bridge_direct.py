from backend.app.runtime.one_time_agent_selection_lock import reset_one_time_agent_selection_lock_for_tests
from backend.app.runtime.signup_locked_activation_bridge import (
    activate_signup_locked_selection,
    create_signup_locked_selection_draft,
    get_signup_locked_selection_status,
    request_signup_agent_change_after_activation,
    signup_locked_activation_bridge_status,
)

reset = reset_one_time_agent_selection_lock_for_tests()
assert reset["reset"] is True

status = signup_locked_activation_bridge_status()
assert status["signup_locked_activation_bridge_ready"] is True
assert status["one_time_activation_lock_enabled"] is True

draft = create_signup_locked_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert draft["status"] == "draft_created"
assert draft["draft"]["activation_allowed"] is True

activated = activate_signup_locked_selection(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    draft_id=draft["draft"]["draft_id"],
)
assert activated["status"] == "activated"
assert activated["client_can_change_selection"] is False

existing = get_signup_locked_selection_status(
    tenant_id="tenant-test",
    package_id="package-starter-1",
)
assert existing["status"] == "found"
assert existing["selection_locked"] is True

blocked_new_draft = create_signup_locked_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["crm_agent"],
)
assert blocked_new_draft["status"] == "blocked"
assert blocked_new_draft["reason"] == "package_agent_selection_already_activated"

change = request_signup_agent_change_after_activation(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    requested_agent_keys=["crm_agent"],
    reason="Client wants to change agents.",
)
assert change["status"] == "owner_admin_review_required"
assert change["client_can_change_selection"] is False

print("SIGNUP_LOCKED_ACTIVATION_BRIDGE_DIRECT_TESTS_PASSED")
print("draft_status", draft["status"])
print("activated_status", activated["status"])
print("existing_status", existing["status"])
print("blocked_new_draft", blocked_new_draft["status"])
print("change_status", change["status"])
