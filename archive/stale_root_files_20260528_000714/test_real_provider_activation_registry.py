from backend.app.runtime.real_provider_activation_registry import (
    get_all_provider_activation_statuses,
    get_provider_activation_status,
    select_ready_provider_for_capability,
)

status = get_all_provider_activation_statuses()

assert status["activation_registry"] == "real_provider_activation_registry_v1"
assert status["credential_values_exposed"] is False
assert status["owner_governed_execution_required"] is True
assert status["async_execution_ready_for_next_layer"] is True
assert status["total_provider_count"] >= 6

openai = get_provider_activation_status("openai")
assert openai["provider_key"] == "openai"
assert openai["credential_values_exposed"] is False
assert "OPENAI_API_KEY" in [item["name"] for item in openai["required_env"]]

selection = select_ready_provider_for_capability("video_generation")
assert selection["credential_values_exposed"] is False
assert selection["owner_governed_execution_required"] is True

print("REAL_PROVIDER_ACTIVATION_REGISTRY_TEST_PASSED")
print("configured_provider_count =", status["configured_provider_count"])
print("providers =", ",".join([p["provider_key"] for p in status["providers"]]))
