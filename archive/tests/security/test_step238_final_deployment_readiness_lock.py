import json
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
matrix_path = ROOT / "backend" / "app" / "data" / "step238_final_deployment_readiness_matrix.json"

matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

checks = {
    "matrix_success": matrix.get("success") is True,
    "status_locked": matrix.get("status") == "final_deployment_readiness_locked",
    "backend_ready": all(matrix.get("backend", {}).values()),
    "frontend_ready": all(matrix.get("frontend", {}).values()),
    "billing_ready": all(matrix.get("billing", {}).values()),
    "security_ready": all(matrix.get("security", {}).values()),
    "operations_ready": all(matrix.get("operations", {}).values()),
    "remaining_actions_present": len(matrix.get("remaining_pre_launch_actions", [])) >= 3,
}

print("STEP_238_FINAL_DEPLOYMENT_READINESS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_LAUNCH_CRITICAL_REGRESSION")
regression = subprocess.run(
    [sys.executable, "test_step215_launch_critical_regression_runner.py"],
    text=True,
)
print("launch_regression_exit_code", regression.returncode)

if regression.returncode != 0:
    failed.append("launch_critical_regression")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_238_FINAL_DEPLOYMENT_READINESS_LOCK_OK")
