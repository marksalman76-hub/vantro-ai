from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_gold_standard_agent_output_benchmark_routes_direct.py"

backup_dir = ROOT / "backups" / f"gold_standard_agent_output_benchmark_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Gold-standard agent output benchmark routes
# Added by wire_gold_standard_agent_output_benchmark_routes.py
# Purpose:
# - compare agent outputs against gold-standard benchmarks
# - require improvement when outputs are below premium benchmark quality
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.gold_standard_agent_output_benchmark_runtime import (
        evaluate_output_against_gold_standard,
        generate_benchmark_improvement_plan,
        get_gold_standard_benchmark,
        gold_standard_agent_output_benchmark_status,
        score_output_against_gold_standard,
    )
except Exception:  # pragma: no cover
    evaluate_output_against_gold_standard = None
    generate_benchmark_improvement_plan = None
    get_gold_standard_benchmark = None
    gold_standard_agent_output_benchmark_status = None
    score_output_against_gold_standard = None


@app.get("/gold-standard-agent-output-benchmark/status")
def gold_standard_agent_output_benchmark_status_route():
    return gold_standard_agent_output_benchmark_status()


@app.get("/gold-standard-agent-output-benchmark/{agent_key}")
def gold_standard_agent_output_benchmark_get_route(agent_key: str):
    return get_gold_standard_benchmark(agent_key)


@app.post("/gold-standard-agent-output-benchmark/score")
async def gold_standard_agent_output_benchmark_score_route(payload: dict):
    safe_payload = dict(payload or {})
    return score_output_against_gold_standard(
        agent_key=safe_payload.get("agent_key") or "default",
        output_text=safe_payload.get("output_text") or "",
        business_context=safe_payload.get("business_context") or {},
        task_type=safe_payload.get("task_type") or "general",
        consequence_level=safe_payload.get("consequence_level") or "medium",
    )


@app.post("/gold-standard-agent-output-benchmark/improvement-plan")
async def gold_standard_agent_output_benchmark_improvement_plan_route(payload: dict):
    safe_payload = dict(payload or {})
    benchmark_score = safe_payload.get("benchmark_score") or {}
    if not isinstance(benchmark_score, dict):
        benchmark_score = {}

    return generate_benchmark_improvement_plan(
        agent_key=safe_payload.get("agent_key") or "default",
        benchmark_score=benchmark_score,
    )


@app.post("/gold-standard-agent-output-benchmark/evaluate")
async def gold_standard_agent_output_benchmark_evaluate_route(payload: dict):
    safe_payload = dict(payload or {})
    return evaluate_output_against_gold_standard(
        agent_key=safe_payload.get("agent_key") or "default",
        output_text=safe_payload.get("output_text") or "",
        business_context=safe_payload.get("business_context") or {},
        task_type=safe_payload.get("task_type") or "general",
        consequence_level=safe_payload.get("consequence_level") or "medium",
    )
'''

marker = "# Gold-standard agent output benchmark routes"
if marker in main_text:
    print("GOLD_STANDARD_AGENT_OUTPUT_BENCHMARK_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("GOLD_STANDARD_AGENT_OUTPUT_BENCHMARK_ROUTES_WIRED")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("GOLD_STANDARD_AGENT_OUTPUT_BENCHMARK_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")