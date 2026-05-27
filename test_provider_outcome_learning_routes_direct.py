from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/provider-outcome-learning/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/provider-outcome-learning/status").json()
assert status["provider_outcome_learning_ready"] is True
assert status["learning_memory_count"] == 0

good = client.post(
    "/provider-outcome-learning/record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-1",
        "execution_id": "execution-1",
        "provider_key": "openai",
        "task_type": "text_generation",
        "quality_score": 95,
        "review_action": "ready_for_customer_preview",
        "final_outcome": "approved",
        "retry_count": 0,
        "latency_ms": 1200,
    },
).json()
assert good["success"] is True

bad = client.post(
    "/provider-outcome-learning/record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-2",
        "execution_id": "execution-2",
        "provider_key": "openai",
        "task_type": "text_generation",
        "quality_score": 55,
        "review_action": "queue_retry",
        "final_outcome": "rejected",
        "retry_count": 2,
        "latency_ms": 65000,
    },
).json()
assert bad["failure"] is True

listed = client.get("/provider-outcome-learning/list?tenant_id=tenant-test&provider_key=openai").json()
assert listed["count"] == 2

summary = client.get("/provider-outcome-learning/summary?tenant_id=tenant-test&provider_key=openai").json()
assert summary["record_count"] == 2
assert summary["credential_values_exposed"] is False

recommendation = client.get("/provider-outcome-learning/recommendation?tenant_id=tenant-test&provider_key=openai").json()
assert recommendation["owner_review_required_before_strategy_change"] is True
assert recommendation["recommendation"]

print("PROVIDER_OUTCOME_LEARNING_ROUTES_DIRECT_TESTS_PASSED")
print("listed_count", listed["count"])
print("summary_action", summary["recommended_action"])
print("recommendation", recommendation["recommendation"])
