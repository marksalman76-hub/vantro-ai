from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "client_registry_panel_present": "client registry" in text,
    "client_registry_state_present": "clientregistry" in text,
    "client_registry_summary_present": "clientregistrysummary" in text,
    "deployment_list_route_present": "/admin/deployment-control/list" in text,
    "deployment_summary_route_present": "/admin/deployment-control/summary" in text,
    "run_agent_list_max_height_present": "maxheight: 260" in text,
    "client_status_tracking_present": "suspended" in text and "cancelled" in text and "active" in text,
}

print("STEP_252_ADMIN_UI_TIDY_CLIENT_REGISTRY_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_252_ADMIN_UI_TIDY_CLIENT_REGISTRY_OK")
