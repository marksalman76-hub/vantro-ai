from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

pack = {
    "step": 117,
    "name": "Stripe Production Configuration Pack",
    "generated_at_utc": now,
    "status": "stripe_production_config_pack_created",
    "secret_values_included": False,
    "stripe_requirements": {
        "provider": "Stripe",
        "mode_decision_required": True,
        "required_backend_env_vars": [
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET"
        ],
        "required_frontend_public_env_vars": [
            "STRIPE_PUBLISHABLE_KEY"
        ],
        "required_dashboard_configuration": [
            "products/packages created",
            "prices created",
            "checkout success URL configured",
            "checkout cancel URL configured",
            "webhook endpoint configured",
            "webhook events selected",
            "test mode verified before live mode",
            "live mode enabled only after owner approval"
        ],
        "required_webhook_events": [
            "checkout.session.completed",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted"
        ],
        "required_validation": [
            "checkout session can be created",
            "successful payment activates correct package/entitlements",
            "failed payment blocks or suspends access correctly",
            "cancelled subscription downgrades or suspends access correctly",
            "webhook signature verification works",
            "client cannot activate unpaid features",
            "owner/admin can see billing status safely"
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "email_notification_production_config_pack",
    },
}

json_path = DATA / "step117_stripe_production_config_pack.json"
md_path = DOCS / "STEP_117_STRIPE_PRODUCTION_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

backend_vars = "\n".join(f"- `{item}`" for item in pack["stripe_requirements"]["required_backend_env_vars"])
frontend_vars = "\n".join(f"- `{item}`" for item in pack["stripe_requirements"]["required_frontend_public_env_vars"])
dashboard = "\n".join(f"- {item}" for item in pack["stripe_requirements"]["required_dashboard_configuration"])
events = "\n".join(f"- `{item}`" for item in pack["stripe_requirements"]["required_webhook_events"])
validation = "\n".join(f"- {item}" for item in pack["stripe_requirements"]["required_validation"])

md = f"""# Step 117 — Stripe Production Configuration Pack

Generated: {now}

## Status

**Result:** Stripe production configuration pack created.  
**Secret values included:** No

## Provider

Stripe

## Required Backend Environment Variables

Configure only inside backend deployment/provider dashboard.

{backend_vars}

## Required Frontend Public Environment Variables

Configure only in frontend host if checkout/client display requires it.

{frontend_vars}

## Required Stripe Dashboard Configuration

{dashboard}

## Required Webhook Events

{events}

## Required Production Validation

{validation}

## Stripe Safety Rules

- Do not commit Stripe secret keys.
- Do not add `STRIPE_SECRET_KEY` or `STRIPE_WEBHOOK_SECRET` to frontend variables.
- Use test mode before live mode.
- Enable live mode only after owner approval.
- Entitlements must activate only after verified successful payment.
- Failed/cancelled payments must block, downgrade, or suspend access according to package rules.
- Clients must not be able to activate unpaid agents, credits, packages, or features.

## Release Decision

- Can continue: `True`
- Next step: Email notification production configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_117_STRIPE_PRODUCTION_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_117_OK")