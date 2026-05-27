from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_one_time_agent_selection_lock_routes_direct.py"

backup_dir = ROOT / "backups" / f"one_time_agent_selection_lock_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# One-time agent selection lock routes
# Added by wire_one_time_agent_selection_lock_routes.py
# Purpose:
# - clients select agents once per package during signup/onboarding
# - lock selected agents after activation
# - require owner/admin approval for post-activation changes
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.one_time_agent_selection_lock import (
        activate_agent_selection_once,
        create_agent_selection_draft,
        get_activated_agent_selection,
        one_time_agent_selection_lock_status,
        request_post_activation_agent_change,
        reset_one_time_agent_selection_lock_for_tests,
    )
except Exception:  # pragma: no cover
    activate_agent_selection_once = None
    create_agent_selection_draft = None
    get_activated_agent_selection = None
    one_time_agent_selection_lock_status = None
    request_post_activation_agent_change = None
    reset_one_time_agent_selection_lock_for_tests = None


@app.get("/one-time-agent-selection-lock/status")
def one_time_agent_selection_lock_status_route():
    return one_time_agent_selection_lock_status()


@app.post("/one-time-agent-selection-lock/draft")
async def one_time_agent_selection_lock_draft_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return create_agent_selection_draft(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        plan=safe_payload.get("plan") or "business",
        selected_agent_keys=selected,
    )


@app.post("/one-time-agent-selection-lock/activate")
async def one_time_agent_selection_lock_activate_route(payload: dict):
    safe_payload = dict(payload or {})

    return activate_agent_selection_once(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        draft_id=safe_payload.get("draft_id") or "",
    )


@app.get("/one-time-agent-selection-lock/activated")
def one_time_agent_selection_lock_activated_route(
    tenant_id: str,
    package_id: str,
):
    return get_activated_agent_selection(
        tenant_id=tenant_id,
        package_id=package_id,
    )


@app.post("/one-time-agent-selection-lock/request-change")
async def one_time_agent_selection_lock_request_change_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("requested_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return request_post_activation_agent_change(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        requested_agent_keys=selected,
        reason=safe_payload.get("reason"),
    )


@app.post("/one-time-agent-selection-lock/reset-for-tests")
async def one_time_agent_selection_lock_reset_route():
    return reset_one_time_agent_selection_lock_for_tests()
'''

marker = "# One-time agent selection lock routes"
if marker in main_text:
    print("ONE_TIME_AGENT_SELECTION_LOCK_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("ONE_TIME_AGENT_SELECTION_LOCK_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/one-time-agent-selection-lock/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/one-time-agent-selection-lock/status").json()
assert status["client_selects_once_per_package"] is True
assert status["selection_locked_after_activation"] is True

draft = client.post(
    "/one-time-agent-selection-lock/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert draft["status"] == "draft_created"
assert draft["draft"]["activation_allowed"] is True

activated = client.post(
    "/one-time-agent-selection-lock/activate",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "draft_id": draft["draft"]["draft_id"],
    },
).json()
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False

blocked = client.post(
    "/one-time-agent-selection-lock/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["crm_agent"],
    },
).json()
assert blocked["status"] == "blocked"
assert blocked["reason"] == "package_agent_selection_already_activated"

existing = client.get(
    "/one-time-agent-selection-lock/activated?tenant_id=tenant-test&package_id=package-starter-1"
).json()
assert existing["status"] == "found"
assert existing["client_can_change_selection"] is False

change = client.post(
    "/one-time-agent-selection-lock/request-change",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "requested_agent_keys": ["crm_agent"],
        "reason": "Client wants to swap.",
    },
).json()
assert change["status"] == "owner_admin_review_required"
assert change["client_can_change_selection"] is False

print("ONE_TIME_AGENT_SELECTION_LOCK_ROUTES_DIRECT_TESTS_PASSED")
print("activated_status", activated["status"])
print("active_agents", len(activated["activated_selection"]["active_agents"]))
print("blocked", blocked["status"], blocked["reason"])
print("change_status", change["status"])
'''.lstrip(), encoding="utf-8")

print("ONE_TIME_AGENT_SELECTION_LOCK_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")