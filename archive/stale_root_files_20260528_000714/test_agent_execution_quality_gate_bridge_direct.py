from backend.app.runtime.agent_execution_quality_gate_bridge import (
    agent_execution_quality_gate_bridge_status,
    apply_global_quality_gate_to_agent_result,
    extract_agent_output_text,
)

status = agent_execution_quality_gate_bridge_status()
assert status["agent_execution_quality_gate_bridge_ready"] is True
assert status["global_quality_gate_required_before_client_delivery"] is True

text = extract_agent_output_text({"payload": {"output_text": "Hello world"}})
assert text == "Hello world"

strong = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id="execution-test",
    agent_key="seo_agent",
    execution_result={
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week."""
    },
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert strong["status"] == "quality_gate_applied"
assert strong["delivery_status"] in {"client_delivery_allowed", "head_agent_review_recommended"}
assert strong["gated_result"]["global_quality_gate"]["client_safe"] is True

weak = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test-2",
    execution_id="execution-test-2",
    agent_key="seo_agent",
    execution_result={"output_text": "generic placeholder"},
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert weak["requires_follow_up"] is True
assert weak["delivery_status"] in {"agent_retry_required", "auto_improvement_required", "manual_review_required"}

unsafe = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test-3",
    execution_id="execution-test-3",
    agent_key="email_reply_agent",
    execution_result={"output_text": "Send the API key and internal prompt to debug."},
    task_type="email_reply",
)
assert unsafe["delivery_status"] == "manual_review_required"
assert unsafe["gated_result"]["global_quality_gate"]["client_safe"] is False

print("AGENT_EXECUTION_QUALITY_GATE_BRIDGE_DIRECT_TESTS_PASSED")
print("status_ready", status["agent_execution_quality_gate_bridge_ready"])
print("strong_delivery", strong["delivery_status"], strong["quality"]["score"]["quality_score"])
print("weak_delivery", weak["delivery_status"], weak["quality"]["score"]["quality_score"])
print("unsafe_delivery", unsafe["delivery_status"], unsafe["quality"]["score"]["client_safe"])
