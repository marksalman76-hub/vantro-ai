from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()

RUNNER = ROOT / "test_step215_launch_critical_regression_runner.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"test_step215_before_step238b_{timestamp}.py"
backup.write_text(RUNNER.read_text(encoding="utf-8"), encoding="utf-8")

RUNNER.write_text(r'''
import subprocess
import sys

TESTS = [
    "test_step213_owner_successful_execution_lock.py",
    "test_step214_customer_billing_block_lock.py",
    "test_step216_provider_billing_readiness_lock.py",
    "test_step217_stripe_webhook_lifecycle_lock.py",
    "test_step218_workflow_action_registry_lock.py",
    "test_step219_agent_catalogue_lock.py",
    "test_step220_premium_output_quality_lock.py",
    "test_step221_frontend_build_deployment_readiness_lock.py",
]

failed = []

print("STEP_215_LAUNCH_CRITICAL_REGRESSION_RUNNER")

for test in TESTS:
    print(f"\nRUNNING {test}")

    result = subprocess.run(
        [sys.executable, test],
        text=True,
    )

    print(f"RESULT {test}: exit_code={result.returncode}")

    if result.returncode != 0:
        failed.append(test)

if failed:
    print("\nSTEP_215_FAILED")
    print("FAILED_TESTS", failed)
    raise SystemExit(1)

print("\nSTEP_215_LAUNCH_CRITICAL_REGRESSION_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(RUNNER), doraise=True)

print("STEP_238B_REGRESSION_FALSE_FAILURE_FIX_OK")
print(f"Backup: {backup}")
print(f"Updated: {RUNNER}")