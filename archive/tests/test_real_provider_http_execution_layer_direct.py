import os

from backend.app.runtime.real_provider_http_execution_layer import (
    build_provider_http_request_packet,
    execute_real_provider_http_request,
    map_provider_http_exception,
    normalise_provider_success_response,
    real_provider_http_runtime_status,
)


os.environ.pop("OPENAI_API_KEY", None)

status = real_provider_http_runtime_status("openai")
assert status["known_adapter"] is True
assert status["configured"] is False
assert status["ready"] is False
assert "OPENAI_API_KEY" in status["missing"]
assert status["real_http_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

blocked = execute_real_provider_http_request(
    "openai",
    {
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
)
assert blocked["status"] == "blocked"
assert blocked["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = execute_real_provider_http_request(
    "openai",
    {
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
)
assert ready["status"] == "ready_for_real_http_dispatch"
assert ready["request_packet"]["provider_endpoint"] == "responses"
assert ready["request_packet"]["input_present"] is True
assert ready["live_external_call_executed"] is False
assert ready["dispatch_blocked_until_provider_credentials_and_final_policy_enablement"] is True
assert ready["credential_values_exposed"] is False

replicate_packet = build_provider_http_request_packet(
    "replicate",
    {"prompt": "generate image", "version": "test-version"},
)
assert replicate_packet["provider_key"] == "replicate"
assert replicate_packet["provider_endpoint"] == "predictions"
assert replicate_packet["credential_values_exposed"] is False

runway_packet = build_provider_http_request_packet(
    "runway",
    {"prompt": "generate video", "duration_seconds": 5},
)
assert runway_packet["provider_key"] == "runway"
assert runway_packet["provider_endpoint"] == "generation"
assert runway_packet["credential_values_exposed"] is False

success = normalise_provider_success_response(
    provider_key="openai",
    tenant_id="tenant-test",
    request_id="request-test",
    raw_response={"id": "provider-job-123", "output_text": "Safe generated result."},
    asset_type="text",
)
assert success["status"] == "completed"
assert success["provider_job_id"] == "provider-job-123"
assert success["asset_packet"]["customer_safe"] is True
assert success["credential_values_exposed"] is False

timeout = map_provider_http_exception(
    "openai",
    exception_type="timeout",
    status_code=504,
)
assert timeout["failure_code"] == "provider_timeout"
assert timeout["retryable"] is True
assert timeout["credential_values_exposed"] is False

auth = map_provider_http_exception(
    "openai",
    exception_type="auth_error",
    status_code=401,
)
assert auth["failure_code"] == "provider_auth_error"
assert auth["retryable"] is False
assert auth["owner_review_required"] is True

print("REAL_PROVIDER_HTTP_EXECUTION_LAYER_DIRECT_TESTS_PASSED")
print("blocked_status", blocked["status"], blocked["reason"])
print("ready_status", ready["status"])
print("openai_endpoint", ready["request_packet"]["provider_endpoint"])
print("replicate_endpoint", replicate_packet["provider_endpoint"])
print("runway_endpoint", runway_packet["provider_endpoint"])
print("success_status", success["status"], success["provider_job_id"])
print("timeout_failure", timeout["failure_code"], timeout["retryable"])
print("auth_failure", auth["failure_code"], auth["retryable"])
