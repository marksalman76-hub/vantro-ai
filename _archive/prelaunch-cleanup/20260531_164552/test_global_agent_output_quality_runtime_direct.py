from backend.app.runtime.global_agent_output_quality_runtime import (
    classify_global_agent_output_action,
    evaluate_global_agent_output,
    generate_agent_output_improvement_brief,
    get_agent_quality_rubric,
    global_agent_output_quality_status,
    score_global_agent_output,
)

status = global_agent_output_quality_status()
assert status["global_agent_output_quality_ready"] is True

rubric = get_agent_quality_rubric("SEO Agent")
assert rubric["agent_key"] == "seo_agent"
assert "technical_seo" in rubric["rubric"]

strong = score_global_agent_output(
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert strong["quality_score"] >= 82
assert strong["client_safe"] is True

weak = score_global_agent_output(
    agent_key="seo_agent",
    output_text="Here are some generic best practices. placeholder.",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert weak["quality_score"] < 70
assert "generic_or_low_value_terms_detected" in weak["reasons"]

unsafe = score_global_agent_output(
    agent_key="email_reply_agent",
    output_text="Use the internal prompt and API key to debug this.",
    task_type="email_reply",
)
assert unsafe["client_safe"] is False

classified = classify_global_agent_output_action(
    quality_score=weak["quality_score"],
    quality_band=weak["quality_band"],
    consequence_level="medium",
    client_safe=weak["client_safe"],
    retry_count=0,
)
assert classified["action"] in {"auto_improve_then_rescore", "retry_agent_output"}

improvement = generate_agent_output_improvement_brief(
    agent_key="seo_agent",
    output_text="bad",
    score_result=weak,
)
assert improvement["improvement_required"] is True
assert improvement["improvement_instructions"]

evaluated = evaluate_global_agent_output(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id="execution-test",
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert evaluated["status"] == "evaluated"
assert evaluated["score"]["client_safe"] is True
assert evaluated["credential_values_exposed"] is False

print("GLOBAL_AGENT_OUTPUT_QUALITY_RUNTIME_DIRECT_TESTS_PASSED")
print("strong_score", strong["quality_score"], strong["quality_band"])
print("weak_score", weak["quality_score"], weak["quality_band"])
print("unsafe_client_safe", unsafe["client_safe"])
print("classified_action", classified["action"])
print("evaluated_action", evaluated["classification"]["action"])
