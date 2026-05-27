from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "run_agent_panel_present": "run agent" in text,
    "run_admin_agent_function_present": "runadminagent" in text,
    "owner_actor_role_present": '"x-actor-role": "owner"' in text,
    "owner_approved_present": "owner_approved: true" in text,
    "client_credit_bypass_copy_present": "client credit limits do not apply here" in text,
    "no_json_block_component": "jsonblock" not in text,
}

print("STEP_248D_ADMIN_RUN_AGENT_PANEL_RESULTS")
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

print("STEP_248D_ADMIN_RUN_AGENT_PANEL_OK")
