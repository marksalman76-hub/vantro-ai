from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-result-quality/status").json()
assert status["provider_result_quality_review_ready"] is True
assert status["credential_values_exposed"] is False

score = client.post(
    "/provider-result-quality/score",
    json={
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a strong, specific, customer-safe result for a real client task."},
        "latency_ms": 1200,
        "retry_count": 0,
    },
).json()
assert score["quality_score"] >= 90

classified = client.post(
    "/provider-result-quality/classify",
    json={
        "quality_score": score["quality_score"],
        "consequence_level": "medium",
        "retry_count": 0,
    },
).json()
assert classified["review_action"] == "ready_for_customer_preview"

evaluated = client.post(
    "/provider-result-quality/evaluate",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-test",
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a polished, customer-safe output ready for preview."},
        "latency_ms": 1234,
        "retry_count": 0,
        "consequence_level": "medium",
    },
).json()
assert evaluated["status"] == "evaluated"
assert evaluated["ready_for_customer_preview"] is True
assert evaluated["credential_values_exposed"] is False

print("PROVIDER_RESULT_QUALITY_REVIEW_ROUTES_DIRECT_TESTS_PASSED")
print("score", score["quality_score"], score["quality_band"])
print("classified", classified["review_action"])
print("evaluated", evaluated["classification"]["review_action"])
