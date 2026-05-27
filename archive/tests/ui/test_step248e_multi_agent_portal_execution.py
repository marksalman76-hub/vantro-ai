from pathlib import Path
import subprocess

ROOT = Path.cwd()
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

client = client_page.read_text(encoding="utf-8", errors="ignore").lower()
admin = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "client_multi_agent_state_present": "selectedagents" in client,
    "client_toggle_function_present": "toggleclientagent" in client,
    "client_paid_agent_copy_present": "only active paid agents are shown" in client,
    "client_multi_run_status_present": "multi_agent_execution" in client,
    "admin_multi_agent_state_present": "selectedadminagents" in admin,
    "admin_toggle_function_present": "toggleadminagent" in admin,
    "admin_multi_run_status_present": "admin_multi_agent_execution" in admin,
    "admin_owner_copy_present": "owner/admin can run one agent or multiple agents" in admin,
    "admin_owner_headers_present": '"x-actor-role": "owner"' in admin,
}

print("STEP_248E_MULTI_AGENT_PORTAL_EXECUTION_RESULTS")
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

print("STEP_248E_MULTI_AGENT_PORTAL_EXECUTION_OK")
