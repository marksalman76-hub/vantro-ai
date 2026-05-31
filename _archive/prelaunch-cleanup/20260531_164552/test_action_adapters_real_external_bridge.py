
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Conduct stakeholder interviews and create outreach follow-up tasks",
}

ready = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email", "crm", "calendar"],
)

assert ready["performed_actual_action"] is True
assert ready["external_action_ready"] is True
assert ready["external_provider_called"] is True
assert ready["live_external_call_executed"] is True
assert ready["internal_fallback_used"] is False
assert ready["real_external_execution"]["external_action_executed"] is True
assert len(ready["actions_performed"]) >= 2

fallback = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
)

assert fallback["performed_actual_action"] is True
assert fallback["external_action_ready"] is False
assert fallback["external_provider_called"] is False
assert fallback["internal_fallback_used"] is True

print("ACTION_ADAPTERS_REAL_EXTERNAL_BRIDGE_TEST_PASSED")
