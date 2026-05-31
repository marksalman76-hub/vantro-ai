from backend.app.runtime.safe_provider_action_adapters import (
    classify_provider_action,
    evaluate_safe_provider_action,
)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


internal = evaluate_safe_provider_action({
    "action_type": "admin_owner_execution",
    "owner_approved": True,
})
assert_true(internal["success"] is True, "admin owner internal action should pass")
assert_true(internal["execution_status"] == "safe_internal_action_allowed", "wrong internal status")
assert_true(internal["external_action_performed"] is False, "must not perform external action")
assert_true(internal["credential_values_exposed"] is False, "must not expose credentials")

blocked = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(blocked["success"] is False, "unapproved live action should block")
assert_true(blocked["execution_status"] == "blocked_owner_approval_required", "wrong approval block status")
assert_true(blocked["external_action_performed"] is False, "must not perform external action")

disabled = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": False,
})
assert_true(disabled["success"] is False, "disabled live execution should block")
assert_true(disabled["execution_status"] == "blocked_live_execution_disabled", "wrong disabled status")

ready = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(ready["success"] is True, "approved live action should be adapter-ready")
assert_true(ready["execution_status"] == "live_action_ready_for_provider_adapter", "wrong ready status")
assert_true(ready["external_action_performed"] is False, "foundation layer must not call provider")

unknown = evaluate_safe_provider_action({"action_type": "unknown_action"})
assert_true(unknown["success"] is False, "unknown action should not pass")
assert_true(unknown["execution_status"] == "unsupported_provider_action", "wrong unknown status")

classified = classify_provider_action({"action_type": "live_provider_action", "provider": "runway"})
assert_true(classified["is_live_action"] is True, "live action classification failed")
assert_true(classified["requires_owner_approval"] is True, "live action must require approval")

print("SAFE_PROVIDER_ACTION_ADAPTERS_TEST_PASSED")
print("Internal:", internal)
print("Blocked:", blocked)
print("Disabled:", disabled)
print("Ready:", ready)
print("Unknown:", unknown)
