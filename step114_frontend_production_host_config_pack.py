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
    "step": 114,
    "name": "Frontend Production Host Configuration Pack",
    "generated_at_utc": now,
    "status": "frontend_production_host_config_pack_created",
    "secret_values_included": False,
    "frontend_service_requirements": {
        "recommended_host": "Vercel/Netlify/Cloudflare Pages",
        "environment": "production",
        "required_public_env_vars": [
            "FRONTEND_URL",
            "BACKEND_URL",
            "STRIPE_PUBLISHABLE_KEY"
        ],
        "forbidden_frontend_env_vars": [
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
            "SHOPIFY_API_SECRET"
        ],
        "required_routes": [
            "/",
            "/admin",
            "/client"
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "database_production_configuration_pack",
    },
}

json_path = DATA / "step114_frontend_production_host_config_pack.json"
md_path = DOCS / "STEP_114_FRONTEND_PRODUCTION_HOST_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

public_vars = "\n".join(f"- `{item}`" for item in pack["frontend_service_requirements"]["required_public_env_vars"])
forbidden_vars = "\n".join(f"- `{item}`" for item in pack["frontend_service_requirements"]["forbidden_frontend_env_vars"])
routes = "\n".join(f"- `{item}`" for item in pack["frontend_service_requirements"]["required_routes"])

md = f"""# Step 114 — Frontend Production Host Configuration Pack

Generated: {now}

## Status

**Result:** Frontend production host configuration pack created.  
**Secret values included:** No

## Frontend Service Requirements

| Item | Value |
|---|---|
| Recommended host | Vercel / Netlify / Cloudflare Pages |
| Environment | Production |
| Required routes | `/`, `/admin`, `/client` |

## Required Public Frontend Environment Variables

Only public/client-safe values may be configured in the frontend host.

{public_vars}

## Forbidden Frontend Environment Variables

Do not add backend secrets, provider secrets, database URLs, admin secrets, or LLM keys to the frontend host.

{forbidden_vars}

## Required Frontend Routes

{routes}

## Frontend Deployment Safety Rules

- Frontend must not expose internal prompts, agent logic, learning architecture, governance internals, backend routes, or secret configuration.
- Client portal must remain customer-safe and must not show raw internal IDs, secret names, backend config, or execution internals.
- Admin dashboard can show operational status, but not raw provider secrets.
- Frontend API calls must target the production backend URL only.
- Production frontend URL must be added to backend CORS allowlist.
- HTTPS must be enabled.

## Release Decision

- Can continue: `True`
- Next step: Database production configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_114_FRONTEND_PRODUCTION_HOST_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_114_OK")