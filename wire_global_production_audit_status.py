from pathlib import Path
from datetime import datetime

main_path = Path("backend/app/main.py")
verifier_path = Path("live_verify_global_production_audit_status.py")

text = main_path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("global_production_audit_status_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

import_line = "from backend.app.runtime.global_production_audit_orchestrator import global_production_audit_status\n"
if import_line not in text:
    marker = "from backend.app.runtime.execution_stack import ("
    text = text.replace(marker, import_line + marker, 1)

route_block = '''
# Global Production Audit Admin Status Route
@app.get("/admin/global-production-audit/status")
def admin_global_production_audit_status():
    return global_production_audit_status()
'''

if "/admin/global-production-audit/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

verifier_path.write_text('''import json
import os
import urllib.request
import urllib.error

BASE_URL = os.getenv("API_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")
TOKEN = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

req = urllib.request.Request(
    f"{BASE_URL}/admin/global-production-audit/status",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "x-admin-token": TOKEN,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
    },
    method="GET",
)

try:
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        print(json.dumps(data, indent=2))

        required = [
            data.get("success") is True,
            data.get("global_production_audit_enabled") is True,
            data.get("global_first_architecture") is True,
            data.get("enterprise_ready") is True,
            data.get("customer_safe") is True,
            data.get("credential_values_exposed") is False,
            isinstance(data.get("audit_sections"), dict),
            "live_execution_runtime" in data.get("audit_sections", {}),
            "launch_readiness" in data.get("audit_sections", {}),
        ]

        if all(required):
            print("GLOBAL_PRODUCTION_AUDIT_STATUS_VERIFIED")
        else:
            raise RuntimeError("GLOBAL_PRODUCTION_AUDIT_STATUS_INCOMPLETE")
except urllib.error.HTTPError as exc:
    print("HTTP_ERROR", exc.code)
    print(exc.read().decode("utf-8", errors="replace"))
    raise
''', encoding="utf-8")

print("GLOBAL_PRODUCTION_AUDIT_STATUS_WIRED")
print("Backup:", backup)
print("Created:", verifier_path)