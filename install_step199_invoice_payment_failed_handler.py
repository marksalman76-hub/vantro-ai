from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BILLING = ROOT / "backend" / "app" / "core" / "subscription_billing_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"

billing_text = BILLING.read_text(encoding="utf-8")

handler = r'''

def handle_invoice_payment_failed(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    provider_event_id = payload.get("provider_event_id")

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    subscription = get_subscription(tenant_id)

    if not subscription.get("success"):
        return {"success": False, "error": "subscription_not_found"}

    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE client_subscriptions
            SET billing_status = %s,
                updated_at = %s
            WHERE tenant_id = %s
            RETURNING tenant_id, email, company_name, package_name, billing_cycle, billing_status, monthly_credits, next_billing_date, cancel_at_period_end
            """, (
                "past_due",
                now,
                tenant_id,
            ))

            row = cur.fetchone()

        conn.commit()

    event_result = record_billing_event({
        "tenant_id": tenant_id,
        "email": subscription["subscription"].get("email"),
        "event_type": "invoice.payment_failed",
        "provider": "stripe",
        "provider_event_id": provider_event_id,
        "billing_status": "past_due",
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
        "client_visible_status": "payment_attention_required",
    })

    return {
        "success": True,
        "billing_event": "invoice.payment_failed",
        "tenant_id": tenant_id,
        "subscription": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "billing_cycle": row[4],
            "billing_status": row[5],
            "monthly_credits": row[6],
            "next_billing_date": row[7].isoformat() if row[7] else None,
            "cancel_at_period_end": row[8],
        },
        "event_record": event_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
        "client_visible_status": "payment_attention_required",
        "execution_policy": "credit_consuming_actions_may_be_blocked_if_payment_remains_unresolved",
    }
'''

if "def handle_invoice_payment_failed" not in billing_text:
    billing_text = billing_text.rstrip() + "\n" + handler + "\n"

BILLING.write_text(billing_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

if "handle_invoice_payment_failed" not in main_text:
    main_text = main_text.replace(
        "    handle_invoice_payment_succeeded,\n)",
        "    handle_invoice_payment_succeeded,\n"
        "    handle_invoice_payment_failed,\n)",
    )

route = r'''

@app.post("/admin/billing/invoice-payment-failed")
async def admin_billing_invoice_payment_failed(payload: dict):
    return handle_invoice_payment_failed(payload)
'''

if "/admin/billing/invoice-payment-failed" not in main_text:
    main_text = main_text.rstrip() + "\n" + route + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("STEP_199_INVOICE_PAYMENT_FAILED_HANDLER_INSTALLED")
print("STEP_199_OK")