import os
import subprocess
import requests
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BASE_URL = "http://127.0.0.1:8000"

checks = []
failures = []


def record(name, passed, detail=""):
    checks.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"{name}: {status} {detail}")
    if not passed:
        failures.append((name, detail))


def run_cmd(name, command, cwd=ROOT):
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        passed = result.returncode == 0
        detail = (result.stdout or result.stderr).strip().splitlines()[-1:] or [""]
        record(name, passed, detail[0])
    except Exception as exc:
        record(name, False, str(exc))


def get_json(name, path, headers=None):
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=headers or {"x-tenant-id": "owner", "x-actor-role": "owner"},
            timeout=30,
        )
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        record(name, response.status_code == 200, f"HTTP={response.status_code}")
        return data
    except Exception as exc:
        record(name, False, str(exc))
        return {}


print("PHASE_E_LAUNCH_REGRESSION_READINESS_START")

# Backend compile checks
run_cmd("compile_main", "python -m py_compile backend\\app\\main.py")
run_cmd("compile_agent_registry", "python -m py_compile backend\\app\\agents\\agent_registry.py")
run_cmd("compile_governance_registry", "python -m py_compile backend\\app\\core\\governance_execution_registry.py")
run_cmd("compile_approval_gateway", "python -m py_compile backend\\app\\approval\\owner_approval_gateway.py")
run_cmd("compile_workflow_engine", "python -m py_compile backend\\app\\workflows\\ecommerce_workflow_engine.py")
run_cmd("compile_quality_gate", "python -m py_compile backend\\app\\quality\\premium_quality_gate.py")
run_cmd("compile_admin_deployment_runtime", "python -m py_compile backend\\app\\core\\admin_deployment_control_runtime.py")

# Core API checks
health = get_json("api_health", "/health")
record("api_health_success", bool(health), str(health)[:120])

# Registry checks
run_cmd(
    "registry_counts",
    "python -c \"from backend.app.agents.agent_registry import list_purchasable_agents,list_internal_agents; print(len(list_purchasable_agents()), list_internal_agents())\""
)

run_cmd(
    "registry_internal_exclusion",
    "python -c \"from backend.app.core.admin_deployment_control_runtime import FULL_AGENT_CATALOGUE; assert 'orchestration_agent' not in FULL_AGENT_CATALOGUE; assert len(FULL_AGENT_CATALOGUE)==25; print('DEPLOYABLE_25_INTERNAL_EXCLUDED')\""
)

# 25-agent certification check
run_cmd("all_25_agent_execution_certification", "python test_phase_a_all_25_agents_execution.py")

# Billing / credit / onboarding route presence checks
get_json("database_readiness", "/admin/database-readiness")
get_json("billing_readiness", "/admin/billing/readiness")
get_json("security_events", "/admin/durable-client-account-security-events?limit=5")
get_json("admin_deployment_summary", "/admin/deployment-control/summary")

# Client-safe exposure check in known frontend files
frontend_files = [
    ROOT / "frontend" / "src" / "app" / "client" / "page.tsx",
    ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx",
]

blocked_visible_terms = [
    "client_0001",
    "client_demo_001",
    "tenant_id",
    "webhook",
    "api_key",
    "secret",
    "internal config",
    "raw json",
]

for file_path in frontend_files:
    if file_path.exists():
        text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
        exposed = [term for term in blocked_visible_terms if term in text]
        record(f"client_safe_ui_scan_{file_path.name}", not exposed, f"exposed={exposed}")
    else:
        record(f"client_safe_ui_scan_{file_path.name}", False, "file_missing")

# Frontend build if frontend exists
frontend_dir = ROOT / "frontend"
if frontend_dir.exists():
    run_cmd("frontend_build", "npm run build", cwd=frontend_dir)
else:
    record("frontend_build", False, "frontend folder missing")

print("\nPHASE_E_LAUNCH_REGRESSION_READINESS_RESULTS")
print("TOTAL_CHECKS", len(checks))
print("FAILED_COUNT", len(failures))

if failures:
    print("FAILED_DETAILS")
    for name, detail in failures:
        print({"check": name, "detail": detail})
else:
    print("PHASE_E_LAUNCH_REGRESSION_READY")