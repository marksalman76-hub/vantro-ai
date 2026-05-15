from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DOCS = ROOT / "docs"
DATA = ROOT / "backend" / "app" / "data"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

template = """# Ecommerce AI Agent Platform — Production Environment Template
# DO NOT COMMIT REAL SECRET VALUES.
# Use this as a deployment checklist for Render, Vercel, or the selected production host.

APP_ENV=production

# Backend / Frontend URLs
BACKEND_URL=
FRONTEND_URL=

# Security
JWT_SECRET=
ADMIN_AUTH_SECRET=
OWNER_ADMIN_EMAIL=

# LLM Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=

# Payments
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=

# Database / Persistence
DATABASE_URL=

# Email / Notifications
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=

# Optional Integrations
SHOPIFY_API_KEY=
SHOPIFY_API_SECRET=
META_ADS_ACCESS_TOKEN=
TIKTOK_ADS_ACCESS_TOKEN=
KLAVIYO_API_KEY=
"""

template_path = DOCS / "PRODUCTION_ENVIRONMENT_TEMPLATE_DO_NOT_COMMIT_SECRETS.env"
template_path.write_text(template, encoding="utf-8")

record = {
    "step": 103,
    "name": "Create Production Environment Template",
    "status": "production_env_template_created",
    "generated_at_utc": now,
    "template_path": str(template_path),
    "secret_values_included": False,
    "safe_to_commit": False,
    "next_step": "production_domain_and_deployment_endpoint_validation",
}

record_path = DATA / "step103_production_env_template_record.json"
record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

print("STEP_103_PRODUCTION_ENV_TEMPLATE_CREATED")
print("template_path", template_path)
print("record_path", record_path)
print("secret_values_included", False)
print("safe_to_commit", False)
print("STEP_103_OK")