from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_signup_locked_activation_routes_direct.py"

backup_dir = ROOT / "backups" / f"signup_locked_activation_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Signup locked activation routes
# Added by wire_signup_locked_activation_routes.py
# Purpose:
# - create signup agent-selection drafts
# - lock selected agents once package is activated
# - block post-activation client changes
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.signup_locked_activation_bridge import (
        activate_signup_locked_selection,
        create_signup_locked_selection_draft,
        get_signup_locked_selection_status,
        request_signup_agent_change_after_activation,
        signup_locked_activation_bridge_status,
    )
except Exception:  # pragma: no cover
    activate_signup_locked_selection = None
    create_signup_locked_selection_draft = None
    get_signup_locked_selection_status = None
    request_signup_agent_change_after_activation = None
    signup_locked_activation_bridge_status = None


@app.get("/signup-locked-activation/status")
def signup_locked_activation_status_route():
    return signup_locked_activation_bridge_status()


@app.post("/signup-locked-activation/draft")
async def signup_locked_activation_draft_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return create_signup_locked_selection_draft(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        plan=safe_payload.get("plan") or "business",
        selected_agent_keys=selected,
    )


@app.post("/signup-locked-activation/activate")
async def signup_locked_activation_activate_route(payload: dict):
    safe_payload = dict(payload or {})

    return activate_signup_locked_selection(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        draft_id=safe_payload.get("draft_id") or "",
    )


@app.get("/signup-locked-activation/selection-status")
def signup_locked_activation_selection_status_route(
    tenant_id: str,
    package_id: str,
):
    return get_signup_locked_selection_status(
        tenant_id=tenant_id,
        package_id=package_id,
    )


@app.post("/signup-locked-activation/request-change")
async def signup_locked_activation_request_change_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("requested_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return request_signup_agent_change_after_activation(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        package_id=safe_payload.get("package_id") or "unknown-package",
        requested_agent_keys=selected,
        reason=safe_payload.get("reason") or "",
    )
'''

marker = "# Signup locked activation routes"
if marker in main_text:
    print("SIGNUP_LOCKED_ACTIVATION_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("SIGNUP_LOCKED_ACTIVATION_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/one-time-agent-selection-lock/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/signup-locked-activation/status").json()
assert status["signup_locked_activation_bridge_ready"] is True

draft = client.post(
    "/signup-locked-activation/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert draft["status"] == "draft_created"

activated = client.post(
    "/signup-locked-activation/activate",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "draft_id": draft["draft"]["draft_id"],
    },
).json()
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False

existing = client.get(
    "/signup-locked-activation/selection-status?tenant_id=tenant-test&package_id=package-starter-1"
).json()
assert existing["status"] == "found"
assert existing["selection_locked"] is True

blocked = client.post(
    "/signup-locked-activation/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["crm_agent"],
    },
).json()
assert blocked["status"] == "blocked"

change = client.post(
    "/signup-locked-activation/request-change",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "requested_agent_keys": ["crm_agent"],
        "reason": "Client wants to change agents.",
    },
).json()
assert change["status"] == "owner_admin_review_required"

print("SIGNUP_LOCKED_ACTIVATION_ROUTES_DIRECT_TESTS_PASSED")
print("draft_status", draft["status"])
print("activated_status", activated["status"])
print("existing_status", existing["status"])
print("blocked_status", blocked["status"])
print("change_status", change["status"])
'''.lstrip(), encoding="utf-8")

print("SIGNUP_LOCKED_ACTIVATION_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")