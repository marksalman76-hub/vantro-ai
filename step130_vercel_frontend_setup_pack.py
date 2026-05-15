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
    "step": 130,
    "name": "Vercel Frontend Setup Pack",
    "generated_at_utc": now,
    "status": "vercel_frontend_setup_pack_created",
    "completed_steps": "51-129",
    "secret_values_included": False,
    "provider": "Vercel",
    "frontend_required_public_env_vars": [
        "FRONTEND_URL",
        "BACKEND_URL",
        "STRIPE_PUBLISHABLE_KEY"
    ],
    "forbidden_vercel_env_vars": [
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
        "Supabase service role key",
        "database password",
        "any private token"
    ],
    "required_vercel_actions": [
        "Create/import Vercel project",
        "Connect GitHub repository",
        "Select frontend root directory",
        "Configure public frontend environment variables only",
        "Set BACKEND_URL to Render backend URL after Render deploy",
        "Deploy Vercel frontend",
        "Copy Vercel production frontend URL",
        "Add Vercel production frontend URL to Render backend CORS allowlist",
        "Validate homepage route",
        "Validate admin route",
        "Validate client route",
        "Validate frontend-to-backend API communication"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "render_vercel_supabase_external_setup_sequence",
    },
}

json_path = DATA / "step130_vercel_frontend_setup_pack.json"
md_path = DOCS / "STEP_130_VERCEL_FRONTEND_SETUP_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

public_vars = "\n".join(f"- `{item}`" for item in pack["frontend_required_public_env_vars"])
forbidden = "\n".join(f"- `{item}`" for item in pack["forbidden_vercel_env_vars"])
actions = "\n".join(f"{i}. {item}" for i, item in enumerate(pack["required_vercel_actions"], start=1))

md = f"""# Step 130 — Vercel Frontend Setup Pack

Generated: {now}

## Status

**Result:** Vercel frontend setup pack created.  
**Completed steps:** `{pack["completed_steps"]}`  
**Secret values included:** No

## Vercel Settings

| Item | Value |
|---|---|
| Provider | Vercel |
| Environment | Production |
| Required live dependency | Render backend URL |

## Required Public Frontend Environment Variables

Only client-safe public/config values may be added in Vercel.

{public_vars}

## Forbidden Vercel Environment Variables

Never add these to Vercel/frontend runtime.

{forbidden}

## Required Vercel Actions

{actions}

## Vercel Safety Rules

- Do not add backend secrets to Vercel.
- Do not add database credentials to Vercel.
- Do not expose LLM, Stripe secret, SMTP, JWT, admin, or Supabase service role keys.
- Customer portal must not expose internal prompts, agent logic, learning logic, governance rules, or backend configuration.
- Admin dashboard may show operational state, but must not expose secrets.
- Vercel production URL must be added to Render backend CORS allowlist.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Render/Vercel/Supabase external setup sequence.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_130_VERCEL_FRONTEND_SETUP_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("provider", pack["provider"])
print("secret_values_included", pack["secret_values_included"])
print("can_continue_documentation", pack["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", pack["release_decision"]["can_continue_live_validation"])
print("STEP_130_OK")