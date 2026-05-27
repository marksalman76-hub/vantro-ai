from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "no_json_block_component": "jsonblock" not in text,
    "no_raw_pre_json_display": "json.stringify(value" not in text,
    "command_centre_present": "owner command centre" in text,
    "runtime_health_present": "runtime health" in text,
    "provider_governance_present": "provider governance" in text,
    "operational_recovery_present": "operational recovery" in text,
    "billing_deployment_present": "billing & deployment" in text,
}

print("STEP_248C_CLEAN_ADMIN_PORTAL_UI_RESULTS")
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

print("STEP_248C_CLEAN_ADMIN_PORTAL_UI_OK")
