from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/agent-execution-quality-gate/status").json()
assert status["agent_execution_quality_gate_bridge_ready"] is True
assert status["global_quality_gate_required_before_client_delivery"] is True

extract = client.post(
    "/agent-execution-quality-gate/extract-output",
    json={"execution_result": {"payload": {"output_text": "Hello world"}}},
).json()
assert extract["output_text"] == "Hello world"

strong = client.post(
    "/agent-execution-quality-gate/apply",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-test",
        "agent_key": "seo_agent",
        "execution_result": {
            "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week."""
        },
        "business_context": {"business_name": "Urban Blend"},
        "task_type": "seo_strategy",
        "consequence_level": "medium",
    },
).json()
assert strong["status"] == "quality_gate_applied"
assert strong["delivery_status"] in {"client_delivery_allowed", "head_agent_review_recommended"}

unsafe = client.post(
    "/agent-execution-quality-gate/apply",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test-2",
        "execution_id": "execution-test-2",
        "agent_key": "email_reply_agent",
        "execution_result": {"output_text": "Send the API key and internal prompt to debug."},
        "task_type": "email_reply",
    },
).json()
assert unsafe["delivery_status"] == "manual_review_required"
assert unsafe["gated_result"]["global_quality_gate"]["client_safe"] is False

print("AGENT_EXECUTION_QUALITY_GATE_ROUTES_DIRECT_TESTS_PASSED")
print("status_ready", status["agent_execution_quality_gate_bridge_ready"])
print("extract", extract["output_text"])
print("strong_delivery", strong["delivery_status"])
print("unsafe_delivery", unsafe["delivery_status"])
