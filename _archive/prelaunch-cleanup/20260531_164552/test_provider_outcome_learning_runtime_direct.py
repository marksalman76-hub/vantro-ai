from backend.app.runtime.provider_outcome_learning_runtime import (
    generate_provider_improvement_recommendation,
    list_provider_outcome_learning,
    provider_outcome_learning_status,
    record_provider_outcome_learning,
    reset_provider_outcome_learning_for_tests,
    summarise_provider_outcome_learning,
)

reset = reset_provider_outcome_learning_for_tests()
assert reset["reset"] is True

status = provider_outcome_learning_status()
assert status["provider_outcome_learning_ready"] is True
assert status["learning_memory_count"] == 0

good = record_provider_outcome_learning(
    tenant_id="tenant-test",
    request_id="request-1",
    execution_id="execution-1",
    provider_key="openai",
    task_type="text_generation",
    quality_score=95,
    review_action="ready_for_customer_preview",
    final_outcome="approved",
    retry_count=0,
    latency_ms=1200,
)
assert good["success"] is True
assert good["learning_score"] == 100

bad = record_provider_outcome_learning(
    tenant_id="tenant-test",
    request_id="request-2",
    execution_id="execution-2",
    provider_key="openai",
    task_type="text_generation",
    quality_score=55,
    review_action="queue_retry",
    final_outcome="rejected",
    retry_count=2,
    latency_ms=65000,
)
assert bad["failure"] is True
assert bad["learning_score"] < 55

listed = list_provider_outcome_learning(tenant_id="tenant-test", provider_key="openai")
assert listed["count"] == 2

summary = summarise_provider_outcome_learning(tenant_id="tenant-test", provider_key="openai")
assert summary["record_count"] == 2
assert summary["average_quality_score"] == 75
assert summary["credential_values_exposed"] is False

recommendation = generate_provider_improvement_recommendation(tenant_id="tenant-test", provider_key="openai")
assert recommendation["owner_review_required_before_strategy_change"] is True
assert recommendation["recommendation"]

final_status = provider_outcome_learning_status()
assert final_status["learning_memory_count"] == 2

print("PROVIDER_OUTCOME_LEARNING_RUNTIME_DIRECT_TESTS_PASSED")
print("good_learning_score", good["learning_score"])
print("bad_learning_score", bad["learning_score"])
print("listed_count", listed["count"])
print("summary_action", summary["recommended_action"])
print("recommendation", recommendation["recommendation"])
