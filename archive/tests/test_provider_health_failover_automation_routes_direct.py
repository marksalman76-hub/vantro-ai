from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-health-failover/status").json()
assert status["provider_health_failover_automation_ready"] is True
assert status["credential_values_exposed"] is False

good = client.post(
    "/provider-health-failover/profile",
    json={
        "provider_key": "openai",
        "success_count": 10,
        "failure_count": 0,
        "timeout_count": 0,
        "average_latency_ms": 2000,
        "average_quality_score": 95,
        "retry_rate": 0.0,
        "learning_score": 90,
    },
).json()
assert good["health_score"] >= 90

bad = client.post(
    "/provider-health-failover/profile",
    json={
        "provider_key": "runway",
        "success_count": 1,
        "failure_count": 5,
        "timeout_count": 2,
        "average_latency_ms": 120000,
        "average_quality_score": 50,
        "retry_rate": 0.6,
        "learning_score": 40,
    },
).json()
assert bad["failover_recommended"] is True

ranked = client.post(
    "/provider-health-failover/rank",
    json={
        "requested_provider": "runway",
        "candidates": [bad, good],
    },
).json()
assert ranked["selected_provider"] == "openai"
assert ranked["failover_required"] is True

selection = client.post(
    "/provider-health-failover/select",
    json={
        "requested_provider": "runway",
        "available_providers": ["openai", "runway"],
        "provider_health_inputs": {
            "openai": {
                "success_count": 10,
                "failure_count": 0,
                "timeout_count": 0,
                "average_latency_ms": 2000,
                "average_quality_score": 95,
                "retry_rate": 0.0,
            },
            "runway": {
                "success_count": 1,
                "failure_count": 5,
                "timeout_count": 2,
                "average_latency_ms": 120000,
                "average_quality_score": 50,
                "retry_rate": 0.6,
            },
        },
    },
).json()
assert selection["selected_provider"] == "openai"
assert selection["failover_required"] is True
assert selection["live_external_call_executed"] is False

post_result = client.post(
    "/provider-health-failover/post-result-recommendation",
    json={
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a strong provider result suitable for customer preview."},
        "latency_ms": 1200,
        "retry_count": 0,
    },
).json()
assert post_result["recommendation"] == "keep_or_increase_provider_priority"

print("PROVIDER_HEALTH_FAILOVER_AUTOMATION_ROUTES_DIRECT_TESTS_PASSED")
print("good_health", good["health_score"])
print("bad_health", bad["health_score"])
print("ranked_selected", ranked["selected_provider"])
print("selection_selected", selection["selected_provider"])
print("post_result_recommendation", post_result["recommendation"])
