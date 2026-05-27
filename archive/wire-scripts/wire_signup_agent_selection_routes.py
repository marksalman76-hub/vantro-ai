from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_signup_agent_selection_routes_direct.py"

backup_dir = ROOT / "backups" / f"signup_agent_selection_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Signup agent selection routes
# Added by wire_signup_agent_selection_routes.py
# Purpose:
# - expose locked 27-agent catalogue selection during signup/onboarding
# - validate selected agents by plan before activation
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.signup_agent_selection_bridge import (
        build_signup_activation_packet,
        get_signup_agent_selection_options,
        signup_agent_selection_bridge_status,
        validate_signup_agent_selection,
    )
except Exception:  # pragma: no cover
    build_signup_activation_packet = None
    get_signup_agent_selection_options = None
    signup_agent_selection_bridge_status = None
    validate_signup_agent_selection = None


@app.get("/signup-agent-selection/status")
def signup_agent_selection_status_route():
    return signup_agent_selection_bridge_status()


@app.get("/signup-agent-selection/options/{plan}")
def signup_agent_selection_options_route(plan: str):
    return get_signup_agent_selection_options(plan)


@app.post("/signup-agent-selection/validate")
async def signup_agent_selection_validate_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return validate_signup_agent_selection(
        safe_payload.get("plan") or "business",
        selected,
    )


@app.post("/signup-agent-selection/activation-packet")
async def signup_agent_selection_activation_packet_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return build_signup_activation_packet(
        safe_payload.get("plan") or "business",
        selected,
    )
'''

marker = "# Signup agent selection routes"
if marker in main_text:
    print("SIGNUP_AGENT_SELECTION_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("SIGNUP_AGENT_SELECTION_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/signup-agent-selection/status").json()
assert status["signup_agent_selection_bridge_ready"] is True
assert status["uses_locked_27_agent_catalogue"] is True

starter = client.get("/signup-agent-selection/options/starter").json()
assert starter["max_selectable_agents"] == 3
assert starter["available_count"] == 26

enterprise = client.get("/signup-agent-selection/options/enterprise").json()
assert enterprise["max_selectable_agents"] == 27
assert enterprise["available_count"] == 27
assert enterprise["head_agent_available"] is True

valid = client.post(
    "/signup-agent-selection/validate",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert valid["valid"] is True
assert valid["activation_allowed"] is True

blocked = client.post(
    "/signup-agent-selection/validate",
    json={
        "plan": "business",
        "selected_agent_keys": ["head_agent"],
    },
).json()
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = client.post(
    "/signup-agent-selection/activation-packet",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert packet["status"] == "activation_packet_ready"
assert packet["selected_count"] == 3

print("SIGNUP_AGENT_SELECTION_ROUTES_DIRECT_TESTS_PASSED")
print("starter_available", starter["available_count"])
print("enterprise_available", enterprise["available_count"])
print("valid_selected", valid["selected_count"])
print("packet_selected", packet["selected_count"])
'''.lstrip(), encoding="utf-8")

print("SIGNUP_AGENT_SELECTION_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")