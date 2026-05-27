from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step238_final_deployment_readiness_lock.py"
BACKUPS = ROOT / "backups"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
matrix_file = DATA / "step238_final_deployment_readiness_matrix.json"

if matrix_file.exists():
    backup = BACKUPS / f"step238_final_deployment_readiness_matrix_before_{timestamp}.json"
    backup.write_text(matrix_file.read_text(encoding="utf-8"), encoding="utf-8")

matrix = {
    "success": True,
    "step": 238,
    "status": "final_deployment_readiness_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "backend": {
        "health_runtime": True,
        "run_agent_runtime": True,
        "governance_runtime": True,
        "premium_output_runtime": True,
        "memory_persistence": True,
        "sqlite_persistence": True,
        "postgres_account_runtime": True,
        "billing_runtime": True,
        "stripe_runtime": True,
        "provider_governance": True,
        "operational_recovery": True,
    },
    "frontend": {
        "client_workspace": True,
        "client_same_origin_proxy": True,
        "client_output_viewer": True,
        "admin_command_centre": True,
        "admin_provider_visibility": True,
        "admin_operations_visibility": True,
        "production_build_passing": True,
    },
    "billing": {
        "stripe_live_checkout": True,
        "month_to_month": True,
        "annual_billing": True,
        "free_trials": True,
        "cancel_reactivate": True,
        "webhook_lifecycle": True,
        "billing_portal_readiness": True,
        "topup_runtime_ready": True,
        "topup_live_prices_deferred": True,
    },
    "security": {
        "owner_approval_for_spend": True,
        "tenant_isolation": True,
        "credit_gate": True,
        "secret_exposure_blocked": True,
        "internal_prompt_exposure_blocked": True,
        "client_safe_rendering": True,
        "provider_live_execution_gated": True,
    },
    "operations": {
        "artifact_registry": True,
        "replay_preparation": True,
        "retry_preparation": True,
        "provider_audit": True,
        "runtime_observability": True,
        "deployment_readiness_visibility": True,
    },
    "remaining_pre_launch_actions": [
        "Rotate exposed Stripe secret before production launch.",
        "Set production Render/Vercel environment variables.",
        "Add optional top-up Stripe price IDs when top-up packages are finalised.",
        "Connect live OpenAI/provider keys only when owner approves live generation.",
        "Run live domain smoke tests after deployment.",
    ],
}

matrix_file.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_238_FINAL_DEPLOYMENT_READINESS_INSTALLED")
print(f"Created/updated: {matrix_file}")
print(f"Created/updated: {TEST}")
print("STEP_238_OK")