from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/global-agent-output-quality/status").json()
assert status["global_agent_output_quality_ready"] is True

rubric = client.get("/global-agent-output-quality/rubric/seo-agent").json()
assert rubric["agent_key"] == "seo_agent"

score = client.post(
    "/global-agent-output-quality/score",
    json={
        "agent_key": "seo_agent",
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
        "business_context": {"business_name": "Urban Blend"},
        "task_type": "seo_strategy",
    },
).json()
assert score["quality_score"] >= 82
assert score["client_safe"] is True

classified = client.post(
    "/global-agent-output-quality/classify",
    json={
        "quality_score": score["quality_score"],
        "quality_band": score["quality_band"],
        "consequence_level": "medium",
        "client_safe": score["client_safe"],
        "retry_count": 0,
    },
).json()
assert classified["action"] in {"deliver_to_client", "deliver_or_head_agent_review"}

evaluated = client.post(
    "/global-agent-output-quality/evaluate",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-test",
        "agent_key": "seo_agent",
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
        "business_context": {"business_name": "Urban Blend"},
        "task_type": "seo_strategy",
    },
).json()
assert evaluated["status"] == "evaluated"
assert evaluated["score"]["client_safe"] is True
assert evaluated["credential_values_exposed"] is False

print("GLOBAL_AGENT_OUTPUT_QUALITY_ROUTES_DIRECT_TESTS_PASSED")
print("score", score["quality_score"], score["quality_band"])
print("classified", classified["action"])
print("evaluated", evaluated["classification"]["action"])
