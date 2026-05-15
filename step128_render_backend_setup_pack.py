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
    "step": 128,
    "name": "Render Backend Setup Pack",
    "generated_at_utc": now,
    "status": "render_backend_setup_pack_created",
    "completed_steps": "51-127",
    "secret_values_included": False,
    "provider": "Render",
    "service_type": "Web Service",
    "runtime": "Python",
    "required_render_env_vars": [
        "APP_ENV",
        "BACKEND_URL",
        "FRONTEND_URL",
        "DATABASE_URL",
        "JWT_SECRET",
        "ADMIN_AUTH_SECRET",
        "OWNER_ADMIN_EMAIL",
        "OPENAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET"
    ],
    "optional_render_env_vars": [
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "XAI_API_KEY",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "FROM_EMAIL",
        "SHOPIFY_API_KEY",
        "SHOPIFY_API_SECRET",
        "META_ADS_ACCESS_TOKEN",
        "TIKTOK_ADS_ACCESS_TOKEN",
        "KLAVIYO_API_KEY"
    ],
    "render_setup_steps": [
        "Create a new Render Web Service",
        "Connect the GitHub repository",
        "Select the ecommerce AI agent platform repository",
        "Set runtime to Python",
        "Set environment to production",
        "Configure build command based on project requirements",
        "Configure start command based on backend entry point",
        "Add required environment variables in Render dashboard only",
        "Deploy the service",
        "Copy the live Render backend URL",
        "Validate /health endpoint",
        "Update non-secret live value record with backend URL"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "supabase_database_setup_pack",
    },
}

json_path = DATA / "step128_render_backend_setup_pack.json"
md_path = DOCS / "STEP_128_RENDER_BACKEND_SETUP_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

required = "\n".join(f"- `{item}`" for item in pack["required_render_env_vars"])
optional = "\n".join(f"- `{item}`" for item in pack["optional_render_env_vars"])
steps = "\n".join(f"{i}. {item}" for i, item in enumerate(pack["render_setup_steps"], start=1))

md = f"""# Step 128 — Render Backend Setup Pack

Generated: {now}

## Status

**Result:** Render backend setup pack created.  
**Completed steps:** `{pack["completed_steps"]}`  
**Secret values included:** No

## Render Service Settings

| Item | Value |
|---|---|
| Provider | Render |
| Service type | Web Service |
| Runtime | Python |
| Environment | Production |

## Required Render Environment Variables

Add these only inside the Render dashboard.

{required}

## Optional Render Environment Variables

Add only if the related provider/integration is enabled.

{optional}

## Render Setup Steps

{steps}

## Important Start/Build Command Note

Use the backend start/build command that matches the current project structure.  
If unsure, inspect the existing backend entry point before setting the Render command.

Do not guess the command if the project entry point is unclear.

## Safety Rules

- Do not paste Render env var values into source files.
- Do not commit `.env` files.
- Do not expose backend secrets to Vercel/frontend.
- Keep CORS locked to the Vercel production domain once the Vercel URL exists.
- Keep owner/admin and entitlement controls enabled.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Supabase database setup pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_128_RENDER_BACKEND_SETUP_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("provider", pack["provider"])
print("secret_values_included", pack["secret_values_included"])
print("can_continue_documentation", pack["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", pack["release_decision"]["can_continue_live_validation"])
print("STEP_128_OK")