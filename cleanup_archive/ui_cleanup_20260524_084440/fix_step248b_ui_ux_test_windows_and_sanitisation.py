from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step248_final_ui_ux_polish_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"test_step248_before_step248b_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

TEST.write_text(r'''
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
record_path = ROOT / "backend" / "app" / "data" / "step248_final_ui_ux_polish_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))

client_file = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
admin_file = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
run_proxy_file = ROOT / "frontend" / "src" / "app" / "api" / "run-agent" / "route.ts"
admin_runtime_file = ROOT / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts"

client_page = client_file.read_text(encoding="utf-8", errors="ignore").lower()
admin_page = admin_file.read_text(encoding="utf-8", errors="ignore").lower()

combined = "\n".join(
    file.read_text(encoding="utf-8", errors="ignore").lower()
    for file in [client_file, admin_file, run_proxy_file, admin_runtime_file]
    if file.exists()
)

# These marker strings are allowed when used as sanitisation/blocking patterns.
actual_secret_indicators = [
    "sk_live_51",
    "sk_test_51",
    "whsec_4",
    "postgresql://postgres:",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "final_ui_ux_polish_requirements_locked",
    "client_requirements_true": all(record.get("client_portal_requirements", {}).values()),
    "admin_requirements_true": all(record.get("admin_portal_requirements", {}).values()),
    "client_workspace_present": "client workspace" in client_page,
    "run_agent_ui_present": "run ai agent" in client_page or "run agent" in client_page,
    "output_viewer_present": "output viewer" in client_page,
    "admin_command_centre_present": "command centre" in admin_page,
    "provider_governance_present": "provider governance" in admin_page,
    "operations_visibility_present": "operational recovery" in admin_page,
    "actual_secret_values_not_in_frontend": all(term not in combined for term in actual_secret_indicators),
}

print("STEP_248_FINAL_UI_UX_POLISH_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(
    ["npm.cmd", "run", "build"],
    cwd=str(ROOT / "frontend"),
    text=True,
)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_248_FINAL_UI_UX_POLISH_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_248B_UI_UX_TEST_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")