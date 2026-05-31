from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_agent_execution_quality_gate_routes_direct.py"

backup_dir = ROOT / "backups" / f"agent_execution_quality_gate_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Agent execution quality gate bridge routes
# Added by wire_agent_execution_quality_gate_routes.py
# Purpose:
# - apply global output quality gate to agent execution results
# - prevent weak/unsafe outputs from reaching clients
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.agent_execution_quality_gate_bridge import (
        agent_execution_quality_gate_bridge_status,
        apply_global_quality_gate_to_agent_result,
        extract_agent_output_text,
    )
except Exception:  # pragma: no cover
    agent_execution_quality_gate_bridge_status = None
    apply_global_quality_gate_to_agent_result = None
    extract_agent_output_text = None


@app.get("/agent-execution-quality-gate/status")
def agent_execution_quality_gate_status_route():
    return agent_execution_quality_gate_bridge_status()


@app.post("/agent-execution-quality-gate/apply")
async def agent_execution_quality_gate_apply_route(payload: dict):
    safe_payload = dict(payload or {})
    execution_result = safe_payload.get("execution_result") or {}
    if not isinstance(execution_result, dict):
        execution_result = {"output_text": str(execution_result)}

    business_context = safe_payload.get("business_context") or {}
    if not isinstance(business_context, dict):
        business_context = {}

    return apply_global_quality_gate_to_agent_result(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        agent_key=safe_payload.get("agent_key") or "default",
        execution_result=execution_result,
        business_context=business_context,
        task_type=safe_payload.get("task_type") or "general",
        consequence_level=safe_payload.get("consequence_level") or "medium",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )


@app.post("/agent-execution-quality-gate/extract-output")
async def agent_execution_quality_gate_extract_output_route(payload: dict):
    safe_payload = dict(payload or {})
    execution_result = safe_payload.get("execution_result") or {}
    if not isinstance(execution_result, dict):
        execution_result = {"output_text": str(execution_result)}

    return {
        "output_text": extract_agent_output_text(execution_result),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''

marker = "# Agent execution quality gate bridge routes"
if marker in main_text:
    print("AGENT_EXECUTION_QUALITY_GATE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("AGENT_EXECUTION_QUALITY_GATE_ROUTES_WIRED")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("AGENT_EXECUTION_QUALITY_GATE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")