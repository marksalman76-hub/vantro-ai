from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_health_failover_automation_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_health_failover_automation_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider health + failover automation routes
# Added by wire_provider_health_failover_automation_routes.py
# Purpose:
# - rank providers by health, quality, latency, retry/failure patterns
# - recommend failover while preserving owner-review governance
# - do not execute live external calls
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_health_failover_automation_runtime import (
        automate_provider_selection,
        build_provider_health_profile,
        provider_health_failover_automation_status,
        rank_provider_failover_candidates,
        recommend_provider_after_result,
    )
except Exception:  # pragma: no cover
    automate_provider_selection = None
    build_provider_health_profile = None
    provider_health_failover_automation_status = None
    rank_provider_failover_candidates = None
    recommend_provider_after_result = None


@app.get("/provider-health-failover/status")
def provider_health_failover_status_route():
    return provider_health_failover_automation_status()


@app.post("/provider-health-failover/profile")
async def provider_health_failover_profile_route(payload: dict):
    safe_payload = dict(payload or {})
    return build_provider_health_profile(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        success_count=int(safe_payload.get("success_count", 0) or 0),
        failure_count=int(safe_payload.get("failure_count", 0) or 0),
        timeout_count=int(safe_payload.get("timeout_count", 0) or 0),
        average_latency_ms=safe_payload.get("average_latency_ms"),
        average_quality_score=safe_payload.get("average_quality_score"),
        retry_rate=float(safe_payload.get("retry_rate", 0.0) or 0.0),
        learning_score=safe_payload.get("learning_score"),
    )


@app.post("/provider-health-failover/rank")
async def provider_health_failover_rank_route(payload: dict):
    safe_payload = dict(payload or {})
    candidates = safe_payload.get("candidates") or []
    if not isinstance(candidates, list):
        candidates = []

    return rank_provider_failover_candidates(
        requested_provider=safe_payload.get("requested_provider") or "unknown-provider",
        candidates=candidates,
    )


@app.post("/provider-health-failover/select")
async def provider_health_failover_select_route(payload: dict):
    safe_payload = dict(payload or {})
    available = safe_payload.get("available_providers") or []
    health_inputs = safe_payload.get("provider_health_inputs") or {}

    if not isinstance(available, list):
        available = []
    if not isinstance(health_inputs, dict):
        health_inputs = {}

    return automate_provider_selection(
        requested_provider=safe_payload.get("requested_provider") or "unknown-provider",
        available_providers=available,
        provider_health_inputs=health_inputs,
    )


@app.post("/provider-health-failover/post-result-recommendation")
async def provider_health_failover_post_result_recommendation_route(payload: dict):
    safe_payload = dict(payload or {})
    return recommend_provider_after_result(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        result_payload=safe_payload.get("result_payload") or {},
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
    )
'''

marker = "# Provider health + failover automation routes"
if marker in main_text:
    print("PROVIDER_HEALTH_FAILOVER_AUTOMATION_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_HEALTH_FAILOVER_AUTOMATION_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-health-failover/status").json()
assert status["provider_health_failover_automation_ready"] is True
assert status["credential_values_exposed"] is False

good = client.post(
    "/provider-health-failover/profile",
    json={
        "provider_key": "openai",
        "success_count": 10,
        "failure_count": 0,
        "timeout_count": 0,
        "average_latency_ms": 2000,
        "average_quality_score": 95,
        "retry_rate": 0.0,
        "learning_score": 90,
    },
).json()
assert good["health_score"] >= 90

bad = client.post(
    "/provider-health-failover/profile",
    json={
        "provider_key": "runway",
        "success_count": 1,
        "failure_count": 5,
        "timeout_count": 2,
        "average_latency_ms": 120000,
        "average_quality_score": 50,
        "retry_rate": 0.6,
        "learning_score": 40,
    },
).json()
assert bad["failover_recommended"] is True

ranked = client.post(
    "/provider-health-failover/rank",
    json={
        "requested_provider": "runway",
        "candidates": [bad, good],
    },
).json()
assert ranked["selected_provider"] == "openai"
assert ranked["failover_required"] is True

selection = client.post(
    "/provider-health-failover/select",
    json={
        "requested_provider": "runway",
        "available_providers": ["openai", "runway"],
        "provider_health_inputs": {
            "openai": {
                "success_count": 10,
                "failure_count": 0,
                "timeout_count": 0,
                "average_latency_ms": 2000,
                "average_quality_score": 95,
                "retry_rate": 0.0,
            },
            "runway": {
                "success_count": 1,
                "failure_count": 5,
                "timeout_count": 2,
                "average_latency_ms": 120000,
                "average_quality_score": 50,
                "retry_rate": 0.6,
            },
        },
    },
).json()
assert selection["selected_provider"] == "openai"
assert selection["failover_required"] is True
assert selection["live_external_call_executed"] is False

post_result = client.post(
    "/provider-health-failover/post-result-recommendation",
    json={
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a strong provider result suitable for customer preview."},
        "latency_ms": 1200,
        "retry_count": 0,
    },
).json()
assert post_result["recommendation"] == "keep_or_increase_provider_priority"

print("PROVIDER_HEALTH_FAILOVER_AUTOMATION_ROUTES_DIRECT_TESTS_PASSED")
print("good_health", good["health_score"])
print("bad_health", bad["health_score"])
print("ranked_selected", ranked["selected_provider"])
print("selection_selected", selection["selected_provider"])
print("post_result_recommendation", post_result["recommendation"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_HEALTH_FAILOVER_AUTOMATION_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")