from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

provider_template = {
    "step": 107,
    "name": "Safe Provider Values Template",
    "generated_at_utc": now,
    "status": "safe_provider_values_template_created",
    "secret_values_included": False,
    "providers": {
        "backend_host": {
            "selected_provider": "",
            "production_backend_url": "",
            "health_endpoint": "/health",
            "secret_fields_required": [],
            "status": "pending",
        },
        "frontend_host": {
            "selected_provider": "",
            "production_frontend_url": "",
            "admin_dashboard_path": "/admin",
            "client_portal_path": "/client",
            "secret_fields_required": [],
            "status": "pending",
        },
        "database_provider": {
            "selected_provider": "",
            "database_url_configured_in_provider_dashboard": False,
            "secret_fields_required": ["DATABASE_URL"],
            "status": "pending",
        },
        "llm_provider_stack": {
            "primary": "OpenAI",
            "fallbacks": ["Anthropic", "Google Gemini", "xAI"],
            "secret_fields_required": [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
                "XAI_API_KEY"
            ],
            "live_credentials_configured_in_provider_dashboard": False,
            "status": "pending",
        },
        "payment_provider": {
            "selected_provider": "Stripe",
            "mode": "",
            "secret_fields_required": [
                "STRIPE_SECRET_KEY",
                "STRIPE_WEBHOOK_SECRET"
            ],
            "public_fields_required": [
                "STRIPE_PUBLISHABLE_KEY"
            ],
            "status": "pending",
        },
        "email_notification_provider": {
            "selected_provider": "",
            "secret_fields_required": [
                "SMTP_PASSWORD"
            ],
            "config_fields_required": [
                "SMTP_HOST",
                "SMTP_PORT",
                "SMTP_USER",
                "FROM_EMAIL"
            ],
            "status": "pending",
        },
        "domain_dns_provider": {
            "selected_provider": "",
            "custom_domain": "",
            "dns_configured": False,
            "https_enabled": False,
            "status": "pending",
        },
    },
    "release_decision": {
        "can_continue": True,
        "note": "Template contains no secret values. Real values must only be entered in deployment provider dashboards.",
        "next_step": "production_readiness_matrix_update",
    },
}

json_path = DATA / "step107_safe_provider_values_template.json"
md_path = DOCS / "STEP_107_SAFE_PROVIDER_VALUES_TEMPLATE.md"

json_path.write_text(json.dumps(provider_template, indent=2), encoding="utf-8")

md = f"""# Step 107 — Safe Provider Values Template

Generated: {now}

## Status

**Result:** Safe provider values template created.  
**Secret values included:** No  
**Safe to use as checklist:** Yes  
**Safe to store real secrets here:** No

## Provider Checklist

| Provider Layer | Status |
|---|---|
| Backend host | Pending |
| Frontend host | Pending |
| Database provider | Pending |
| LLM provider stack | Pending |
| Payment provider | Pending |
| Email notification provider | Pending |
| Domain/DNS provider | Pending |

## Required Secret Fields

Do not paste real values into this repository.

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `XAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SMTP_PASSWORD`

## Required Public / Config Fields

- `BACKEND_URL`
- `FRONTEND_URL`
- `STRIPE_PUBLISHABLE_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `FROM_EMAIL`
- `APP_ENV=production`

## Release Decision

- Can continue: `True`
- Real provider values must be configured only inside Render/Vercel/provider dashboards, not committed to source code.

## Next Step

Production readiness matrix update.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_107_SAFE_PROVIDER_VALUES_TEMPLATE_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", provider_template["secret_values_included"])
print("can_continue", provider_template["release_decision"]["can_continue"])
print("STEP_107_OK")