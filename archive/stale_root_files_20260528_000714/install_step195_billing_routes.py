from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

billing_import = '''
from backend.app.core.subscription_billing_runtime import (
    billing_readiness,
    get_subscription,
    record_billing_event,
    upsert_subscription,
)
'''

if "subscription_billing_runtime" not in text:
    text = billing_import + "\n" + text

routes = r'''

@app.get("/admin/billing/readiness")
async def admin_billing_readiness():
    return billing_readiness()


@app.post("/admin/billing/subscription/upsert")
async def admin_billing_subscription_upsert(payload: dict):
    return upsert_subscription(payload)


@app.get("/admin/billing/subscription")
async def admin_billing_subscription(identifier: str):
    return get_subscription(identifier)


@app.post("/admin/billing/event")
async def admin_billing_event(payload: dict):
    return record_billing_event(payload)
'''

if "/admin/billing/readiness" not in text:
    text = text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(text, encoding="utf-8")

print("STEP_195_BILLING_ROUTES_INSTALLED")
print("STEP_195_OK")