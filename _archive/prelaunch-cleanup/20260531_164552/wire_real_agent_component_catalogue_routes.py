from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_real_agent_component_catalogue_routes_direct.py"

backup_dir = ROOT / "backups" / f"real_agent_component_catalogue_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Real agent/component catalogue routes
# Added by wire_real_agent_component_catalogue_routes.py
# Purpose:
# - lock commercial agent count separately from internal operational components
# - clarify 27 commercial agents vs larger runtime intelligence count
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_agent_component_catalogue import (
        calculate_catalogue_counts,
        get_catalogue_component_by_key,
        list_client_selectable_agents,
        list_real_agent_component_catalogue,
        real_agent_component_catalogue_status,
    )
except Exception:  # pragma: no cover
    calculate_catalogue_counts = None
    get_catalogue_component_by_key = None
    list_client_selectable_agents = None
    list_real_agent_component_catalogue = None
    real_agent_component_catalogue_status = None


@app.get("/real-agent-component-catalogue/status")
def real_agent_component_catalogue_status_route():
    return real_agent_component_catalogue_status()


@app.get("/real-agent-component-catalogue/full")
def real_agent_component_catalogue_full_route():
    return list_real_agent_component_catalogue()


@app.get("/real-agent-component-catalogue/counts")
def real_agent_component_catalogue_counts_route():
    return {
        "counts": calculate_catalogue_counts(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/real-agent-component-catalogue/component/{component_key}")
def real_agent_component_catalogue_component_route(component_key: str):
    return get_catalogue_component_by_key(component_key)


@app.get("/real-agent-component-catalogue/client-selectable")
def real_agent_component_catalogue_client_selectable_route(plan: str = "business"):
    return list_client_selectable_agents(plan)
'''

marker = "# Real agent/component catalogue routes"
if marker in main_text:
    print("REAL_AGENT_COMPONENT_CATALOGUE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("REAL_AGENT_COMPONENT_CATALOGUE_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/real-agent-component-catalogue/status").json()
assert status["real_agent_component_catalogue_locked"] is True
assert status["commercial_catalogue_count"] == 27
assert status["visible_agent_count"] == 33
assert status["operational_component_count"] == 48

counts = client.get("/real-agent-component-catalogue/counts").json()["counts"]
assert counts["client_facing_agents"] == 27
assert counts["system_agents"] == 6

full = client.get("/real-agent-component-catalogue/full").json()
assert full["commercial_catalogue_count"] == 27
assert full["total_operational_component_count"] == 48

head = client.get("/real-agent-component-catalogue/component/head_agent").json()
assert head["found"] is True
assert head["component"]["enterprise_only"] is True

business = client.get("/real-agent-component-catalogue/client-selectable?plan=business").json()
assert business["count"] == 26
assert business["head_agent_available"] is False

enterprise = client.get("/real-agent-component-catalogue/client-selectable?plan=enterprise").json()
assert enterprise["count"] == 27
assert enterprise["head_agent_available"] is True

print("REAL_AGENT_COMPONENT_CATALOGUE_ROUTES_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("visible_agent_count", status["visible_agent_count"])
print("operational_component_count", status["operational_component_count"])
print("business_selectable", business["count"])
print("enterprise_selectable", enterprise["count"])
'''.lstrip(), encoding="utf-8")

print("REAL_AGENT_COMPONENT_CATALOGUE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")