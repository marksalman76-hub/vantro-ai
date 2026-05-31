from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_result_quality_review_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_result_quality_review_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider result quality review routes
# Added by wire_provider_result_quality_review_routes.py
# Purpose:
# - score provider outputs
# - classify output as ready, retry, manual review, or owner review
# - preserve customer-safe delivery and no credential exposure
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_result_quality_review_runtime import (
        classify_provider_result_review_action,
        evaluate_provider_result_for_delivery,
        provider_result_quality_review_status,
        score_provider_result_quality,
    )
except Exception:  # pragma: no cover
    classify_provider_result_review_action = None
    evaluate_provider_result_for_delivery = None
    provider_result_quality_review_status = None
    score_provider_result_quality = None


@app.get("/provider-result-quality/status")
def provider_result_quality_status_route():
    if provider_result_quality_review_status is None:
        return {"status": "unavailable", "credential_values_exposed": False}
    return provider_result_quality_review_status()


@app.post("/provider-result-quality/score")
async def provider_result_quality_score_route(payload: dict):
    safe_payload = dict(payload or {})
    return score_provider_result_quality(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        result_payload=safe_payload.get("result_payload") or {},
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
    )


@app.post("/provider-result-quality/classify")
async def provider_result_quality_classify_route(payload: dict):
    safe_payload = dict(payload or {})
    return classify_provider_result_review_action(
        quality_score=int(safe_payload.get("quality_score", 0) or 0),
        consequence_level=safe_payload.get("consequence_level") or "medium",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        owner_review_required=bool(safe_payload.get("owner_review_required", False)),
    )


@app.post("/provider-result-quality/evaluate")
async def provider_result_quality_evaluate_route(payload: dict):
    safe_payload = dict(payload or {})
    return evaluate_provider_result_for_delivery(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        result_payload=safe_payload.get("result_payload") or {},
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        consequence_level=safe_payload.get("consequence_level") or "medium",
        owner_review_required=bool(safe_payload.get("owner_review_required", False)),
    )
'''

marker = "# Provider result quality review routes"
if marker in main_text:
    print("PROVIDER_RESULT_QUALITY_REVIEW_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_RESULT_QUALITY_REVIEW_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-result-quality/status").json()
assert status["provider_result_quality_review_ready"] is True
assert status["credential_values_exposed"] is False

score = client.post(
    "/provider-result-quality/score",
    json={
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a strong, specific, customer-safe result for a real client task."},
        "latency_ms": 1200,
        "retry_count": 0,
    },
).json()
assert score["quality_score"] >= 90

classified = client.post(
    "/provider-result-quality/classify",
    json={
        "quality_score": score["quality_score"],
        "consequence_level": "medium",
        "retry_count": 0,
    },
).json()
assert classified["review_action"] == "ready_for_customer_preview"

evaluated = client.post(
    "/provider-result-quality/evaluate",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-test",
        "provider_key": "openai",
        "task_type": "text_generation",
        "result_payload": {"output_text": "This is a polished, customer-safe output ready for preview."},
        "latency_ms": 1234,
        "retry_count": 0,
        "consequence_level": "medium",
    },
).json()
assert evaluated["status"] == "evaluated"
assert evaluated["ready_for_customer_preview"] is True
assert evaluated["credential_values_exposed"] is False

print("PROVIDER_RESULT_QUALITY_REVIEW_ROUTES_DIRECT_TESTS_PASSED")
print("score", score["quality_score"], score["quality_band"])
print("classified", classified["review_action"])
print("evaluated", evaluated["classification"]["review_action"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_RESULT_QUALITY_REVIEW_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")