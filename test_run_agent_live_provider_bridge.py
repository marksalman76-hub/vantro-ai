from backend.app.runtime.execution_stack import ExecutionRequest, ExecutionStack


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


stack = ExecutionStack()

blocked_quality = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="governed_live_provider_generation",
    payload={"prompt": "Return bridge test."},
    owner_approved=True,
    quality_passed=False,
))
assert_true(blocked_quality.success is False, "quality gate must still block")
assert_true(blocked_quality.execution_status == "blocked_quality_gate_required", "quality gate status mismatch")

blocked_approval = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="launch_paid_campaign",
    payload={"prompt": "Do not launch."},
    owner_approved=False,
    quality_passed=True,
))
assert_true(blocked_approval.success is False, "spend action must still block without owner approval")
assert_true(blocked_approval.execution_status == "blocked_pending_owner_approval", "approval block status mismatch")

bridge = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="governed_live_provider_generation",
    payload={
        "request_id": "local_bridge_test_no_external_expectation",
        "prompt": "Local bridge test. External execution depends on environment gates.",
    },
    owner_approved=True,
    quality_passed=True,
))

assert_true(bridge.action_type == "governed_live_provider_generation", "bridge action mismatch")
assert_true(bridge.adapter == "governed_openai_live_provider_bridge", "bridge adapter mismatch")
assert_true(bridge.adapter_result is not None, "bridge adapter result missing")
assert_true(bridge.adapter_result.get("credential_values_exposed") is False, "credentials exposed")
assert_true(bridge.adapter_result.get("customer_safe") is True, "bridge result not customer safe")
assert_true(bridge.execution_status in {
    "governed_live_provider_execution_completed",
    "governed_live_provider_execution_not_completed",
}, "unexpected bridge status")

print("RUN_AGENT_LIVE_PROVIDER_BRIDGE_TEST_PASSED")
print({
    "quality_block": blocked_quality.execution_status,
    "approval_block": blocked_approval.execution_status,
    "bridge_status": bridge.execution_status,
    "bridge_adapter": bridge.adapter,
    "live_external_call_executed": bridge.adapter_result.get("live_external_call_executed"),
})
