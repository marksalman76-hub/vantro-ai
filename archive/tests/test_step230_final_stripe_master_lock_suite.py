import subprocess
import sys

tests = [
    "test_step222_stripe_checkout_endpoint_lock.py",
    "test_step223_checkout_completed_mapping_lock.py",
    "test_step224_stripe_webhook_signature_lock.py",
    "test_step225_cancel_reactivate_durable_sync_lock.py",
    "test_step226_customer_billing_portal_invoice_lock.py",
    "test_step226_final_stripe_lock_suite.py",
    "test_step227_live_stripe_env_readiness.py",
    "test_step228_real_stripe_checkout_creation.py",
    "test_step229_advanced_stripe_billing_lock.py",
]

print("STEP_230_FINAL_STRIPE_MASTER_LOCK_SUITE")
failed = []

for test in tests:
    print(f"\nRUNNING {test}")
    result = subprocess.run([sys.executable, test], text=True)
    print(f"RESULT {test}: exit_code={result.returncode}")

    if result.returncode != 0:
        failed.append(test)

if failed:
    print("\nSTEP_230_FINAL_STRIPE_MASTER_LOCK_FAILED")
    print("FAILED_TESTS", failed)
    raise SystemExit(1)

print("\nSTEP_230_FINAL_STRIPE_MASTER_LOCK_SUITE_OK")