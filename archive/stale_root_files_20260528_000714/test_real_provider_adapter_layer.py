from backend.app.runtime.real_provider_adapter_layer import (
    get_provider_adapter_status,
    normalise_provider_request,
    route_provider_request,
    execute_provider_request_scaffold,
)

request = normalise_provider_request({
    "tenant_id": "admin-test",
    "actor_role": "owner",
    "provider_key": "openai",
    "capability": "image_generation",
    "input": {"prompt": "test"},
})

assert request["tenant_id"] == "admin-test"
assert request["credential_values_exposed"] is False
assert request["customer_safe"] is True

status = get_provider_adapter_status("openai")
assert status["provider_key"] == "openai"
assert status["known_adapter"] is True
assert status["credential_values_exposed"] is False

route = route_provider_request({
    "tenant_id": "admin-test",
    "actor_role": "owner",
    "provider_key": "openai",
    "capability": "image_generation",
    "input": {"prompt": "test"},
})

assert route["credential_values_exposed"] is False
assert route["customer_safe"] is True
assert route["routed"] in [True, False]

result = execute_provider_request_scaffold({
    "tenant_id": "admin-test",
    "actor_role": "owner",
    "provider_key": "openai",
    "capability": "image_generation",
    "input": {"prompt": "test"},
    "live_execution_requested": True,
})

assert result["credential_values_exposed"] is False
assert result["customer_safe"] is True
assert result["submitted"] is False

print("REAL_PROVIDER_ADAPTER_LAYER_TEST_PASSED")
print("openai_known_adapter =", status["known_adapter"])
print("openai_configured =", status["configured"])
print("route_routed =", route["routed"])
print("result_status =", result["status"])
