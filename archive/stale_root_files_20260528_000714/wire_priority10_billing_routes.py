from pathlib import Path

main_file = Path("backend/app/main.py")

content = main_file.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_file = backup_dir / "main_before_priority10_billing_routes.py"
backup_file.write_text(content, encoding="utf-8")

required_imports = """
from backend.app.core.subscription_billing_runtime import (
    billing_readiness,
)

from backend.app.core.stripe_advanced_billing_runtime import (
    advanced_billing_readiness,
)

from backend.app.core.stripe_customer_billing_portal import (
    billing_portal_readiness,
)

from backend.app.core.stripe_production_hardening_runtime import (
    stripe_production_env_readiness,
    admin_billing_dashboard,
    verify_stripe_webhook_signature,
    route_stripe_webhook_event,
)
"""

if "stripe_production_env_readiness" not in content:
    marker = "from fastapi.middleware.cors import CORSMiddleware"
    content = content.replace(
        marker,
        marker + "\n" + required_imports
    )

route_block = '''

@app.get("/admin/stripe-production-readiness")
async def admin_stripe_production_readiness():
    return stripe_production_env_readiness()


@app.get("/admin/billing-automation/readiness")
async def admin_billing_automation_readiness():
    return advanced_billing_readiness()


@app.get("/admin/subscription-policy/readiness")
async def admin_subscription_policy_readiness():
    return billing_readiness()


@app.get("/admin/customer-billing-portal/readiness")
async def admin_customer_billing_portal_readiness(
    tenant_id: str
):
    return billing_portal_readiness(tenant_id)


@app.post("/webhooks/stripe/hardened")
async def hardened_stripe_webhook(payload: dict):
    verification = verify_stripe_webhook_signature(payload)

    if not verification.get("success"):
        return verification

    return route_stripe_webhook_event(payload)


@app.post("/admin/billing-dashboard")
async def admin_billing_dashboard_route(payload: dict):
    return admin_billing_dashboard(payload)

'''

if "/admin/stripe-production-readiness" not in content:
    content += route_block

main_file.write_text(content, encoding="utf-8")

print("PRIORITY10_BILLING_ROUTES_WIRED")
print("Backup:", backup_file)