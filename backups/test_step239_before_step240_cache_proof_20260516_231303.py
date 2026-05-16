import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
matrix_path = ROOT / "backend" / "app" / "data" / "step239_commercial_launch_readiness_matrix.json"

matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

required_env_presence_only = {
    "STRIPE_SECRET_KEY": bool(os.getenv("STRIPE_SECRET_KEY")),
    "STRIPE_WEBHOOK_SECRET": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
    "STRIPE_PRICE_STARTER_MONTHLY": bool(os.getenv("STRIPE_PRICE_STARTER_MONTHLY")),
    "STRIPE_PRICE_GROWTH_MONTHLY": bool(os.getenv("STRIPE_PRICE_GROWTH_MONTHLY")),
    "STRIPE_PRICE_PRO_MONTHLY": bool(os.getenv("STRIPE_PRICE_PRO_MONTHLY")),
}

checks = {
    "matrix_success": matrix.get("success") is True,
    "commercial_launch_locked": matrix.get("status") == "commercial_launch_readiness_locked",
    "launch_readiness_all_true": all(matrix.get("launch_readiness", {}).values()),
    "commercial_requirements_all_true": all(matrix.get("commercial_requirements", {}).values()),
    "core_platform_ready": matrix.get("launch_gate", {}).get("core_platform_ready") is True,
    "commercial_beta_ready": matrix.get("launch_gate", {}).get("commercial_beta_ready") is True,
    "must_do_items_present": len(matrix.get("production_must_do_before_public_launch", [])) >= 5,
    "stripe_core_env_present": all(required_env_presence_only.values()),
}

print("STEP_239_COMMERCIAL_LAUNCH_READINESS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("env_presence_only", required_env_presence_only)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FINAL_CORE_REGRESSION")
regression = subprocess.run(
    [sys.executable, "test_step215_launch_critical_regression_runner.py"],
    text=True,
)
print("final_core_regression_exit_code", regression.returncode)

if regression.returncode != 0:
    failed.append("final_core_regression")

print("RUNNING_STEP_237_OPERATIONS_VISIBILITY")
operations = subprocess.run(
    [sys.executable, "test_step237_admin_operations_visibility_lock.py"],
    text=True,
)
print("step237_operations_exit_code", operations.returncode)

if operations.returncode != 0:
    failed.append("step237_operations_visibility")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_239_COMMERCIAL_LAUNCH_READINESS_LOCK_OK")
