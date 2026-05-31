from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BILLING = ROOT / "backend" / "app" / "core" / "subscription_billing_runtime.py"

text = BILLING.read_text(encoding="utf-8")

policy = r'''

def fixed_cycle_retry_policy():
    return {
        "success": True,
        "billing_policy": "automatic_recurring_stripe_subscription",
        "manual_monthly_payment_required": False,
        "card_storage": "stripe_tokenised_storage_only",
        "local_card_storage": False,
        "invoice_email_provider": "stripe",
        "payment_retry_interval_hours": 48,
        "billing_cycle_anchor_locked": True,
        "late_payment_moves_cycle_date": False,
        "rule": "If a payment fails and succeeds later, the original monthly billing cycle date remains unchanged.",
        "example": {
            "subscription_started": "2026-05-04",
            "payment_failed": "2026-06-04",
            "retry_succeeded": "2026-06-11",
            "next_billing_date_remains": "2026-07-04",
        },
    }
'''

if "def fixed_cycle_retry_policy" not in text:
    text = text.rstrip() + "\n" + policy + "\n"

BILLING.write_text(text, encoding="utf-8")

print("STEP_200_FIXED_CYCLE_RETRY_POLICY_INSTALLED")
print("STEP_200_OK")