from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

template = {
    "step": 123,
    "name": "Live Environment Values Capture Template",
    "generated_at_utc": now,
    "status": "live_environment_values_capture_template_created",
    "secret_values_included": False,
    "safe_to_store": True,
    "capturable_non_secret_values": {
        "backend_provider": "",
        "frontend_provider": "",
        "database_provider": "",
        "dns_provider": "",
        "email_provider": "",
        "payment_provider": "Stripe",
        "llm_primary_provider": "OpenAI",
        "production_backend_url": "",
        "production_frontend_url": "",
        "admin_route": "/admin",
        "client_route": "/client",
        "health_route": "/health",
        "stripe_mode": "test_or_live_pending_owner_decision",
        "email_sender_domain": "",
        "custom_domain": "",
    },
    "forbidden_values": [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "XAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "DATABASE_URL",
        "JWT_SECRET",
        "ADMIN_AUTH_SECRET",
        "SMTP_PASSWORD",
        "SHOPIFY_API_SECRET",
        "any live API key",
        "any password",
        "any private token"
    ],
    "release_decision": {
        "can_continue": True,
        "next_step": "external_live_setup_manual_checkpoint",
    },
}

json_path = DATA / "step123_live_environment_values_capture_template.json"
md_path = DOCS / "STEP_123_LIVE_ENVIRONMENT_VALUES_CAPTURE_TEMPLATE.md"

json_path.write_text(json.dumps(template, indent=2), encoding="utf-8")

allowed_rows = "\n".join(
    f"| {key} | `{value}` |"
    for key, value in template["capturable_non_secret_values"].items()
)

forbidden = "\n".join(f"- `{item}`" for item in template["forbidden_values"])

md = f"""# Step 123 — Live Environment Values Capture Template

Generated: {now}

## Status

**Result:** Live environment values capture template created.  
**Secret values included:** No  
**Safe to store:** Yes, only if secret fields remain blank and no private values are added.

## Capturable Non-Secret Values

| Field | Value |
|---|---|
{allowed_rows}

## Forbidden Values

Do not store or paste any of the following in this file, docs, GitHub, screenshots, chat, or frontend variables.

{forbidden}

## Purpose

This template captures only non-secret deployment facts needed for validation:

- selected providers
- production URLs
- public routes
- public/custom domains
- selected Stripe mode status
- non-secret email/domain details

## Release Decision

- Can continue: `True`
- Next step: External live setup manual checkpoint.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_123_LIVE_ENVIRONMENT_VALUES_CAPTURE_TEMPLATE_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", template["secret_values_included"])
print("safe_to_store", template["safe_to_store"])
print("can_continue", template["release_decision"]["can_continue"])
print("STEP_123_OK")