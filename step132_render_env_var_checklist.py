from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

checklist = {
    "step": 132,
    "name": "Render Environment Variable Checklist",
    "generated_at_utc": now,
    "status": "render_env_var_checklist_created",
    "completed_steps": "51-131",
    "secret_values_included": False,
    "render_required_env_vars": {
        "APP_ENV": "production",
        "BACKEND_URL": "Render backend URL after deploy",
        "FRONTEND_URL": "Vercel frontend URL after deploy",
        "DATABASE_URL": "Supabase Postgres connection string - enter in Render only",
        "JWT_SECRET": "Generate/store in Render only",
        "ADMIN_AUTH_SECRET": "Generate/store in Render only",
        "OWNER_ADMIN_EMAIL": "Owner/admin notification email",
        "OPENAI_API_KEY": "OpenAI key - enter in Render only",
        "STRIPE_SECRET_KEY": "Stripe secret key - enter in Render only",
        "STRIPE_WEBHOOK_SECRET": "Stripe webhook secret - enter in Render only"
    },
    "render_optional_env_vars": {
        "ANTHROPIC_API_KEY": "Optional fallback LLM key",
        "GOOGLE_API_KEY": "Optional fallback LLM key",
        "XAI_API_KEY": "Optional fallback LLM key",
        "SMTP_HOST": "Optional email provider host",
        "SMTP_PORT": "Optional email provider port",
        "SMTP_USER": "Optional email provider username",
        "SMTP_PASSWORD": "Optional email provider password - enter in Render only",
        "FROM_EMAIL": "Optional sender email",
        "SHOPIFY_API_KEY": "Optional ecommerce integration",
        "SHOPIFY_API_SECRET": "Optional ecommerce integration secret - enter in Render only",
        "META_ADS_ACCESS_TOKEN": "Optional ad integration token - enter in Render only",
        "TIKTOK_ADS_ACCESS_TOKEN": "Optional ad integration token - enter in Render only",
        "KLAVIYO_API_KEY": "Optional email/SMS integration key - enter in Render only"
    },
    "forbidden_locations": [
        "GitHub repository",
        "local committed .env files",
        "Vercel frontend env vars for backend secrets",
        "docs",
        "screenshots",
        "chat",
        "client/browser runtime"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "create_vercel_env_var_checklist_for_selected_stack",
    },
}

json_path = DATA / "step132_render_env_var_checklist.json"
md_path = DOCS / "STEP_132_RENDER_ENV_VAR_CHECKLIST.md"

json_path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")

required_rows = "\n".join(
    f"| `{key}` | {value} |"
    for key, value in checklist["render_required_env_vars"].items()
)
optional_rows = "\n".join(
    f"| `{key}` | {value} |"
    for key, value in checklist["render_optional_env_vars"].items()
)
forbidden = "\n".join(f"- {item}" for item in checklist["forbidden_locations"])

md = f"""# Step 132 — Render Environment Variable Checklist

Generated: {now}

## Status

**Result:** Render environment variable checklist created.  
**Completed steps:** `{checklist["completed_steps"]}`  
**Secret values included:** No

## Required Render Environment Variables

| Variable | Purpose |
|---|---|
{required_rows}

## Optional Render Environment Variables

| Variable | Purpose |
|---|---|
{optional_rows}

## Forbidden Locations For Secrets

{forbidden}

## Render Env Var Rules

- Backend secrets go in Render only.
- Supabase `DATABASE_URL` goes in Render only.
- OpenAI and Stripe secret keys go in Render only.
- Do not put backend secrets in Vercel.
- Do not commit real `.env` files.
- Do not paste secret values into chat or screenshots.
- `FRONTEND_URL` should be updated after the Vercel production URL exists.
- CORS must be locked to the final Vercel production URL.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Vercel env var checklist for selected stack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_132_RENDER_ENV_VAR_CHECKLIST_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", checklist["secret_values_included"])
print("can_continue_documentation", checklist["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", checklist["release_decision"]["can_continue_live_validation"])
print("STEP_132_OK")