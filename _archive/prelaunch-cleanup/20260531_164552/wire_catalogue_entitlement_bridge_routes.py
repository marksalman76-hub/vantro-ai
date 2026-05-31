from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_catalogue_entitlement_bridge_routes_direct.py"

backup_dir = ROOT / "backups" / f"catalogue_entitlement_bridge_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Catalogue entitlement bridge routes
# Added by wire_catalogue_entitlement_bridge_routes.py
# Purpose:
# - use locked 27-agent catalogue as package/selection source of truth
# - validate plan-specific selected agents
# - build activation entitlement packets without exposing internals
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.catalogue_entitlement_bridge import (
        build_agent_activation_entitlement_packet,
        catalogue_entitlement_bridge_status,
        get_package_catalogue_rules,
        list_package_selectable_agents,
        validate_package_agent_selection,
    )
except Exception:  # pragma: no cover
    build_agent_activation_entitlement_packet = None
    catalogue_entitlement_bridge_status = None
    get_package_catalogue_rules = None
    list_package_selectable_agents = None
    validate_package_agent_selection = None


@app.get("/catalogue-entitlement-bridge/status")
def catalogue_entitlement_bridge_status_route():
    return catalogue_entitlement_bridge_status()


@app.get("/catalogue-entitlement-bridge/package-rules/{plan}")
def catalogue_entitlement_bridge_package_rules_route(plan: str):
    return get_package_catalogue_rules(plan)


@app.get("/catalogue-entitlement-bridge/selectable-agents/{plan}")
def catalogue_entitlement_bridge_selectable_agents_route(plan: str):
    return list_package_selectable_agents(plan)


@app.post("/catalogue-entitlement-bridge/validate-selection")
async def catalogue_entitlement_bridge_validate_selection_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return validate_package_agent_selection(
        plan=safe_payload.get("plan") or "business",
        selected_agent_keys=selected,
    )


@app.post("/catalogue-entitlement-bridge/activation-packet")
async def catalogue_entitlement_bridge_activation_packet_route(payload: dict):
    safe_payload = dict(payload or {})
    selected = safe_payload.get("selected_agent_keys") or []
    if not isinstance(selected, list):
        selected = []

    return build_agent_activation_entitlement_packet(
        plan=safe_payload.get("plan") or "business",
        selected_agent_keys=selected,
    )
'''

marker = "# Catalogue entitlement bridge routes"
if marker in main_text:
    print("CATALOGUE_ENTITLEMENT_BRIDGE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("CATALOGUE_ENTITLEMENT_BRIDGE_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/catalogue-entitlement-bridge/status").json()
assert status["catalogue_entitlement_bridge_ready"] is True
assert status["commercial_catalogue_count"] == 27

business_agents = client.get("/catalogue-entitlement-bridge/selectable-agents/business").json()
assert business_agents["available_count"] == 26
assert business_agents["head_agent_available"] is False

enterprise_agents = client.get("/catalogue-entitlement-bridge/selectable-agents/enterprise").json()
assert enterprise_agents["available_count"] == 27
assert enterprise_agents["head_agent_available"] is True

valid = client.post(
    "/catalogue-entitlement-bridge/validate-selection",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert valid["valid"] is True

blocked = client.post(
    "/catalogue-entitlement-bridge/validate-selection",
    json={
        "plan": "business",
        "selected_agent_keys": ["head_agent"],
    },
).json()
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = client.post(
    "/catalogue-entitlement-bridge/activation-packet",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert packet["activation_allowed"] is True
assert len(packet["active_agents"]) == 3
assert packet["client_access_limited_to_paid_selected_agents"] is True

print("CATALOGUE_ENTITLEMENT_BRIDGE_ROUTES_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("business_available", business_agents["available_count"])
print("enterprise_available", enterprise_agents["available_count"])
print("packet_active_agents", len(packet["active_agents"]))
print("hidden_unpurchased", packet["client_hidden_agents_count"])
'''.lstrip(), encoding="utf-8")

print("CATALOGUE_ENTITLEMENT_BRIDGE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")