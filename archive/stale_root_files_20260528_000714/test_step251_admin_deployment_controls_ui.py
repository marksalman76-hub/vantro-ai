from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "deployment_panel_present": "deploy / suspend / cancel client system" in text,
    "manual_deploy_route_present": "/admin/deployment-control/manual-deploy" in text,
    "suspend_route_present": "/admin/deployment-control/suspend" in text,
    "cancel_route_present": "/admin/deployment-control/cancel" in text,
    "reactivate_route_present": "/admin/deployment-control/reactivate" in text,
    "unlimited_credits_present": "unlimited_credits: true" in text,
    "activation_link_present": "activation_link" in text,
}

print("STEP_251_ADMIN_DEPLOYMENT_CONTROLS_UI_RESULTS")
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

print("STEP_251_ADMIN_DEPLOYMENT_CONTROLS_UI_OK")
