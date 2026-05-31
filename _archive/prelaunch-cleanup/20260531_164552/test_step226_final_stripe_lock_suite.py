import subprocess
import sys

tests = [
    "test_step222_stripe_checkout_endpoint_lock.py",
    "test_step223_checkout_completed_mapping_lock.py",
    "test_step224_stripe_webhook_signature_lock.py",
    "test_step225_cancel_reactivate_durable_sync_lock.py",
    "test_step226_customer_billing_portal_invoice_lock.py",
    "test_step217_stripe_webhook_lifecycle_lock.py",
]

print("STEP_226_FINAL_STRIPE_LOCK_SUITE")
failed = []

for test in tests:
    print(f"\nRUNNING {test}")
    result = subprocess.run([sys.executable, test], text=True)
    print(f"RESULT {test}: exit_code={result.returncode}")

    if result.returncode != 0:
        failed.append(test)

if failed:
    print("\nSTEP_226_FINAL_STRIPE_LOCK_FAILED")
    print("FAILED_TESTS", failed)
    raise SystemExit(1)

print("\nSTEP_226_FINAL_STRIPE_LOCK_SUITE_OK")
