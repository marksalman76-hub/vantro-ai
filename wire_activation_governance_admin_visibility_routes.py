from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"activation_governance_admin_visibility_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_activation_governance_admin_visibility_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.activation_governance_admin_visibility import (
    get_activation_governance_admin_visibility,
    get_activation_governance_admin_visibility_status,
)
"""

route_block = r'''

@app.get("/activation-governance-admin-visibility/status")
async def activation_governance_admin_visibility_status():
    return get_activation_governance_admin_visibility_status()


@app.get("/activation-governance-admin-visibility/summary")
async def activation_governance_admin_visibility_summary(tenant_id: str = ""):
    return get_activation_governance_admin_visibility(tenant_id)
'''

if "from backend.app.runtime.activation_governance_admin_visibility import" not in text:
    text = import_block + "\n" + text

if "/activation-governance-admin-visibility/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/activation-governance-admin-visibility/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["activation_governance_admin_visibility_ready"] is True
assert status_json["credential_values_exposed"] is False

summary = client.get("/activation-governance-admin-visibility/summary")
assert summary.status_code == 200
summary_json = summary.json()
assert summary_json["success"] is True
assert summary_json["activation_governance_admin_visibility_ready"] is True
assert "summary" in summary_json
assert summary_json["credential_values_exposed"] is False
assert summary_json["customer_safe"] is True

print("ACTIVATION_GOVERNANCE_ADMIN_VISIBILITY_ROUTES_TESTS_PASSED")
print("status_ready", status_json["activation_governance_admin_visibility_ready"])
print("summary_ready", summary_json["activation_governance_admin_visibility_ready"])
print("credential_values_exposed", summary_json["credential_values_exposed"])
''', encoding="utf-8")

print("ACTIVATION_GOVERNANCE_ADMIN_VISIBILITY_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")