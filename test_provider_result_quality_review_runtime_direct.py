from backend.app.runtime.provider_result_quality_review_runtime import (
    classify_provider_result_review_action,
    evaluate_provider_result_for_delivery,
    provider_result_quality_review_status,
    score_provider_result_quality,
)

status = provider_result_quality_review_status()
assert status["provider_result_quality_review_ready"] is True
assert status["credential_values_exposed"] is False

excellent = score_provider_result_quality(
    provider_key="openai",
    task_type="text_generation",
    result_payload={"output_text": "This is a strong, useful, specific generated result for the client campaign."},
    latency_ms=1200,
    retry_count=0,
)
assert excellent["quality_score"] >= 90
assert excellent["quality_band"] == "excellent"

poor = score_provider_result_quality(
    provider_key="openai",
    task_type="text_generation",
    result_payload={"output_text": "placeholder"},
    latency_ms=130000,
    retry_count=2,
)
assert poor["quality_score"] < 55
assert "low_quality_terms_detected" in poor["reasons"]

ready = classify_provider_result_review_action(
    quality_score=92,
    consequence_level="medium",
    retry_count=0,
)
assert ready["review_action"] == "ready_for_customer_preview"

retry = classify_provider_result_review_action(
    quality_score=65,
    consequence_level="medium",
    retry_count=0,
)
assert retry["review_action"] == "queue_retry"

manual = classify_provider_result_review_action(
    quality_score=40,
    consequence_level="high",
    retry_count=3,
)
assert manual["review_action"] == "manual_review_required"

owner = classify_provider_result_review_action(
    quality_score=95,
    consequence_level="high",
    retry_count=0,
    owner_review_required=True,
)
assert owner["review_action"] == "owner_review_required"

evaluated = evaluate_provider_result_for_delivery(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id="execution-test",
    provider_key="openai",
    task_type="text_generation",
    result_payload={"output_text": "This is a polished, customer-safe output ready for preview."},
    latency_ms=1234,
    retry_count=0,
    consequence_level="medium",
)
assert evaluated["status"] == "evaluated"
assert evaluated["ready_for_customer_preview"] is True
assert evaluated["credential_values_exposed"] is False
assert evaluated["event_bridge"]["entry"]["event_type"] == "provider_result_quality_reviewed"

print("PROVIDER_RESULT_QUALITY_REVIEW_RUNTIME_DIRECT_TESTS_PASSED")
print("excellent_score", excellent["quality_score"])
print("poor_score", poor["quality_score"])
print("ready_action", ready["review_action"])
print("retry_action", retry["review_action"])
print("manual_action", manual["review_action"])
print("owner_action", owner["review_action"])
print("evaluated_action", evaluated["classification"]["review_action"])
