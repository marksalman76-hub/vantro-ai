from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

if "handle_invoice_payment_succeeded" not in text:
    text = text.replace(
        "    upsert_subscription,\n)",
        "    upsert_subscription,\n"
        "    handle_invoice_payment_succeeded,\n)",
    )

route = r'''

@app.post("/admin/billing/invoice-payment-succeeded")
async def admin_billing_invoice_payment_succeeded(payload: dict):
    return handle_invoice_payment_succeeded(payload)
'''

if "/admin/billing/invoice-payment-succeeded" not in text:
    text = text.rstrip() + "\n" + route + "\n"

MAIN.write_text(text, encoding="utf-8")

print("STEP_198_INVOICE_SUCCESS_ROUTE_INSTALLED")
print("STEP_198_OK")