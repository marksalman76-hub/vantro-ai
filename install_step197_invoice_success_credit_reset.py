from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BILLING = ROOT / "backend" / "app" / "core" / "subscription_billing_runtime.py"

text = BILLING.read_text(encoding="utf-8")

code = r'''

def handle_invoice_payment_succeeded(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    provider_event_id = payload.get("provider_event_id")

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    subscription = get_subscription(tenant_id)

    if not subscription.get("success"):
        return {"success": False, "error": "subscription_not_found"}

    monthly_credits = int(subscription["subscription"].get("monthly_credits") or 0)

    from backend.app.core.postgres_account_runtime import assign_client_credits

    credit_result = assign_client_credits({
        "tenant_id": tenant_id,
        "monthly_credits": monthly_credits,
        "top_up_credits": 0,
    })

    event_result = record_billing_event({
        "tenant_id": tenant_id,
        "email": subscription["subscription"].get("email"),
        "event_type": "invoice.payment_succeeded",
        "provider": "stripe",
        "provider_event_id": provider_event_id,
        "credit_reset": credit_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
    })

    return {
        "success": True,
        "billing_event": "invoice.payment_succeeded",
        "tenant_id": tenant_id,
        "monthly_credits_reset_to": monthly_credits,
        "credit_reset": credit_result,
        "event_record": event_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
    }
'''

if "def handle_invoice_payment_succeeded" not in text:
    text = text.rstrip() + "\n" + code + "\n"

BILLING.write_text(text, encoding="utf-8")

print("STEP_197_INVOICE_SUCCESS_CREDIT_RESET_INSTALLED")
print("STEP_197_OK")