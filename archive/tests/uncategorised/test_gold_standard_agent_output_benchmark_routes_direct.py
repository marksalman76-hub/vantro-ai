from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/gold-standard-agent-output-benchmark/status").json()
assert status["gold_standard_benchmark_ready"] is True

bench = client.get("/gold-standard-agent-output-benchmark/seo-agent").json()
assert bench["agent_key"] == "seo_agent"

score = client.post(
    "/gold-standard-agent-output-benchmark/score",
    json={
        "agent_key": "seo_agent",
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent keywords for service pages.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
        "business_context": {"business_name": "Urban Blend"},
        "task_type": "seo_strategy",
    },
).json()
assert score["benchmark_score"] >= 84
assert not score["must_include_missing"]

evaluated = client.post(
    "/gold-standard-agent-output-benchmark/evaluate",
    json={
        "agent_key": "seo_agent",
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent keywords for service pages.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
        "business_context": {"business_name": "Urban Blend"},
        "task_type": "seo_strategy",
    },
).json()
assert evaluated["status"] == "benchmark_evaluated"
assert evaluated["delivery_allowed_by_benchmark"] is True

print("GOLD_STANDARD_AGENT_OUTPUT_BENCHMARK_ROUTES_DIRECT_TESTS_PASSED")
print("score", score["benchmark_score"], score["benchmark_band"])
print("delivery_allowed", evaluated["delivery_allowed_by_benchmark"])
