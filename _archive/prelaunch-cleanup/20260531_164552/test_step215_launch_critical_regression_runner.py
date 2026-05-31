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
