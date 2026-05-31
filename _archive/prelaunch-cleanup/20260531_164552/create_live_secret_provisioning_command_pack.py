from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()

required = {
    "Render backend": [
        "ADMIN_PLATFORM_TOKEN",
        "JWT_SECRET",
        "SESSION_SECRET",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SMTP_PASSWORD",
        "BREVO_API_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ],
    "Vercel frontend": [
        "ADMIN_PLATFORM_TOKEN",
        "SESSION_SECRET",
    ],
    "Supabase": [
        "DATABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ],
}

docs = ROOT / "docs" / "runbooks"
docs.mkdir(parents=True, exist_ok=True)

body = """# Live Secret Provisioning Command Pack

Do not paste real secrets into chat.
Do not commit secrets to Git.

## Required provider dashboards

- Render: backend environment variables
- Vercel: frontend environment variables
- Supabase: database/service credentials
- OpenAI: production API key
- Stripe: live secret key + webhook secret
- Brevo/SMTP: production email credentials

## Required values

"""

for section, names in required.items():
    body += f"\n### {section}\n"
    for name in names:
        body += f"- [ ] {name}\n"

body += """

## After provisioning

Run:

```cmd
cd /d "C:\\Users\\User\\Desktop\\ecommerce-ai-agent-platform"

node scripts\\activation\\live-production-provisioning-check.js