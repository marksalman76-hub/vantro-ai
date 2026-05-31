from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_controlled_openai_live_execution_routes_direct.py"

backup_dir = ROOT / "backups" / f"controlled_openai_live_execution_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Controlled OpenAI live execution routes
# Added by wire_controlled_openai_live_execution_routes.py
# Purpose:
# - expose controlled OpenAI live execution readiness
# - keep actual network calls disabled unless explicit env + owner gates allow
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        controlled_openai_live_execution_status,
        execute_controlled_openai_live_request,
    )
except Exception:  # pragma: no cover
    controlled_openai_live_execution_status = None
    execute_controlled_openai_live_request = None


@app.get("/controlled-openai-live-execution/status")
def controlled_openai_live_execution_status_route():
    if controlled_openai_live_execution_status is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_live_execution_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return controlled_openai_live_execution_status()


@app.post("/controlled-openai-live-execution/execute")
async def controlled_openai_live_execution_execute_route(payload: dict):
    if execute_controlled_openai_live_request is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_live_execution_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return execute_controlled_openai_live_request(dict(payload or {}))
'''

marker = "# Controlled OpenAI live execution routes"
if marker in main_text:
    print("CONTROLLED_OPENAI_LIVE_EXECUTION_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("CONTROLLED_OPENAI_LIVE_EXECUTION_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)
os.environ.pop("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", None)

status = client.get("/controlled-openai-live-execution/status").json()
assert status["controlled_live_execution_ready"] is True
assert status["openai_api_key_present"] is False
assert status["credential_values_exposed"] is False

blocked_no_key = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked_no_key["status"] == "blocked"
assert blocked_no_key["live_external_call_executed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

blocked_policy = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked_policy["status"] == "blocked"
assert blocked_policy["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_no_network = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready_no_network["status"] == "ready_but_network_call_disabled"
assert ready_no_network["live_external_call_executed"] is False
assert ready_no_network["credential_values_exposed"] is False

print("CONTROLLED_OPENAI_LIVE_EXECUTION_ROUTES_DIRECT_TESTS_PASSED")
print("status_ready", status["controlled_live_execution_ready"])
print("blocked_no_key", blocked_no_key["status"])
print("blocked_policy", blocked_policy["status"], blocked_policy["reason"])
print("ready_no_network", ready_no_network["status"], ready_no_network["reason"])
'''.lstrip(), encoding="utf-8")

print("CONTROLLED_OPENAI_LIVE_EXECUTION_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")