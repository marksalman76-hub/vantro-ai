from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_outcome_learning_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_outcome_learning_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider outcome learning routes
# Added by wire_provider_outcome_learning_routes.py
# Purpose:
# - record provider outcome signals
# - summarise provider/task success patterns
# - generate owner-reviewed improvement recommendations
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_outcome_learning_runtime import (
        generate_provider_improvement_recommendation,
        list_provider_outcome_learning,
        provider_outcome_learning_status,
        record_provider_outcome_learning,
        reset_provider_outcome_learning_for_tests,
        summarise_provider_outcome_learning,
    )
except Exception:  # pragma: no cover
    generate_provider_improvement_recommendation = None
    list_provider_outcome_learning = None
    provider_outcome_learning_status = None
    record_provider_outcome_learning = None
    reset_provider_outcome_learning_for_tests = None
    summarise_provider_outcome_learning = None


@app.get("/provider-outcome-learning/status")
def provider_outcome_learning_status_route():
    return provider_outcome_learning_status()


@app.post("/provider-outcome-learning/record")
async def provider_outcome_learning_record_route(payload: dict):
    safe_payload = dict(payload or {})
    return record_provider_outcome_learning(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        quality_score=int(safe_payload.get("quality_score", 0) or 0),
        review_action=safe_payload.get("review_action") or "manual_review_required",
        final_outcome=safe_payload.get("final_outcome") or "unknown",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        notes=safe_payload.get("notes"),
    )


@app.get("/provider-outcome-learning/list")
def provider_outcome_learning_list_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
    limit: int = 100,
):
    return list_provider_outcome_learning(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
        limit=limit,
    )


@app.get("/provider-outcome-learning/summary")
def provider_outcome_learning_summary_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
):
    return summarise_provider_outcome_learning(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
    )


@app.get("/provider-outcome-learning/recommendation")
def provider_outcome_learning_recommendation_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
):
    return generate_provider_improvement_recommendation(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
    )


@app.post("/provider-outcome-learning/reset-for-tests")
async def provider_outcome_learning_reset_route():
    return reset_provider_outcome_learning_for_tests()
'''

marker = "# Provider outcome learning routes"
if marker in main_text:
    print("PROVIDER_OUTCOME_LEARNING_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_OUTCOME_LEARNING_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/provider-outcome-learning/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/provider-outcome-learning/status").json()
assert status["provider_outcome_learning_ready"] is True
assert status["learning_memory_count"] == 0

good = client.post(
    "/provider-outcome-learning/record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-1",
        "execution_id": "execution-1",
        "provider_key": "openai",
        "task_type": "text_generation",
        "quality_score": 95,
        "review_action": "ready_for_customer_preview",
        "final_outcome": "approved",
        "retry_count": 0,
        "latency_ms": 1200,
    },
).json()
assert good["success"] is True

bad = client.post(
    "/provider-outcome-learning/record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-2",
        "execution_id": "execution-2",
        "provider_key": "openai",
        "task_type": "text_generation",
        "quality_score": 55,
        "review_action": "queue_retry",
        "final_outcome": "rejected",
        "retry_count": 2,
        "latency_ms": 65000,
    },
).json()
assert bad["failure"] is True

listed = client.get("/provider-outcome-learning/list?tenant_id=tenant-test&provider_key=openai").json()
assert listed["count"] == 2

summary = client.get("/provider-outcome-learning/summary?tenant_id=tenant-test&provider_key=openai").json()
assert summary["record_count"] == 2
assert summary["credential_values_exposed"] is False

recommendation = client.get("/provider-outcome-learning/recommendation?tenant_id=tenant-test&provider_key=openai").json()
assert recommendation["owner_review_required_before_strategy_change"] is True
assert recommendation["recommendation"]

print("PROVIDER_OUTCOME_LEARNING_ROUTES_DIRECT_TESTS_PASSED")
print("listed_count", listed["count"])
print("summary_action", summary["recommended_action"])
print("recommendation", recommendation["recommendation"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_OUTCOME_LEARNING_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")