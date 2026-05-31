from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_global_agent_output_quality_routes_direct.py"

backup_dir = ROOT / "backups" / f"global_agent_output_quality_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Global agent output quality routes
# Added by wire_global_agent_output_quality_routes.py
# Purpose:
# - enforce premium output quality across all agents
# - score, classify, improve, and trigger Head Agent/manual review when needed
# - prevent unsafe/internal wording from reaching clients
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.global_agent_output_quality_runtime import (
        classify_global_agent_output_action,
        evaluate_global_agent_output,
        generate_agent_output_improvement_brief,
        get_agent_quality_rubric,
        global_agent_output_quality_status,
        score_global_agent_output,
    )
except Exception:  # pragma: no cover
    classify_global_agent_output_action = None
    evaluate_global_agent_output = None
    generate_agent_output_improvement_brief = None
    get_agent_quality_rubric = None
    global_agent_output_quality_status = None
    score_global_agent_output = None


@app.get("/global-agent-output-quality/status")
def global_agent_output_quality_status_route():
    return global_agent_output_quality_status()


@app.get("/global-agent-output-quality/rubric/{agent_key}")
def global_agent_output_quality_rubric_route(agent_key: str):
    return get_agent_quality_rubric(agent_key)


@app.post("/global-agent-output-quality/score")
async def global_agent_output_quality_score_route(payload: dict):
    safe_payload = dict(payload or {})
    return score_global_agent_output(
        agent_key=safe_payload.get("agent_key") or "default",
        output_text=safe_payload.get("output_text") or "",
        business_context=safe_payload.get("business_context") or {},
        task_type=safe_payload.get("task_type") or "general",
        consequence_level=safe_payload.get("consequence_level") or "medium",
    )


@app.post("/global-agent-output-quality/classify")
async def global_agent_output_quality_classify_route(payload: dict):
    safe_payload = dict(payload or {})
    return classify_global_agent_output_action(
        quality_score=int(safe_payload.get("quality_score", 0) or 0),
        quality_band=safe_payload.get("quality_band") or "reject",
        consequence_level=safe_payload.get("consequence_level") or "medium",
        client_safe=bool(safe_payload.get("client_safe", True)),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
    )


@app.post("/global-agent-output-quality/improvement-brief")
async def global_agent_output_quality_improvement_brief_route(payload: dict):
    safe_payload = dict(payload or {})
    score_result = safe_payload.get("score_result") or {}
    if not isinstance(score_result, dict):
        score_result = {}

    return generate_agent_output_improvement_brief(
        agent_key=safe_payload.get("agent_key") or "default",
        output_text=safe_payload.get("output_text") or "",
        score_result=score_result,
    )


@app.post("/global-agent-output-quality/evaluate")
async def global_agent_output_quality_evaluate_route(payload: dict):
    safe_payload = dict(payload or {})
    return evaluate_global_agent_output(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        agent_key=safe_payload.get("agent_key") or "default",
        output_text=safe_payload.get("output_text") or "",
        business_context=safe_payload.get("business_context") or {},
        task_type=safe_payload.get("task_type") or "general",
        consequence_level=safe_payload.get("consequence_level") or "medium",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )
'''

marker = "# Global agent output quality routes"
if marker in main_text:
    print("GLOBAL_AGENT_OUTPUT_QUALITY_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("GLOBAL_AGENT_OUTPUT_QUALITY_ROUTES_WIRED")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("GLOBAL_AGENT_OUTPUT_QUALITY_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")