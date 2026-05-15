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
    "step": 113,
    "name": "Backend Production Host Configuration Pack",
    "generated_at_utc": now,
    "status": "backend_production_host_config_pack_created",
    "secret_values_included": False,
    "backend_service_requirements": {
        "runtime": "Python",
        "recommended_host": "Render/Railway/Fly.io/AWS/GCP/Azure",
        "health_endpoint": "/health",
        "environment": "production",
        "required_env_vars": [
            "APP_ENV",
            "BACKEND_URL",
            "FRONTEND_URL",
            "DATABASE_URL",
            "JWT_SECRET",
            "ADMIN_AUTH_SECRET",
            "OWNER_ADMIN_EMAIL",
            "OPENAI_API_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
        ],
        "optional_env_vars": [
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
            "KLAVIYO_API_KEY",
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "frontend_production_host_configuration_pack",
    },
}

json_path = DATA / "step113_backend_production_host_config_pack.json"
md_path = DOCS / "STEP_113_BACKEND_PRODUCTION_HOST_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

required_rows = "\n".join(f"- `{item}`" for item in pack["backend_service_requirements"]["required_env_vars"])
optional_rows = "\n".join(f"- `{item}`" for item in pack["backend_service_requirements"]["optional_env_vars"])

md = f"""# Step 113 — Backend Production Host Configuration Pack

Generated: {now}

## Status

**Result:** Backend production host configuration pack created.  
**Secret values included:** No

## Backend Service Requirements

| Item | Value |
|---|---|
| Runtime | Python |
| Recommended host | Render / Railway / Fly.io / AWS / GCP / Azure |
| Environment | Production |
| Health endpoint | `/health` |

## Required Backend Environment Variables

Add these only inside the backend deployment provider dashboard.

{required_rows}

## Optional Backend Environment Variables

Add only if the related provider/integration is enabled.

{optional_rows}

## Recommended Backend Deployment Settings

| Setting | Value |
|---|---|
| Root directory | Project root or backend directory depending on provider |
| Python version | Use current project-compatible Python version |
| Build command | Install backend dependencies |
| Start command | Start backend API server |
| Health check path | `/health` |
| Auto deploy | Optional for release candidate; recommended after stable production setup |

## Backend Deployment Safety Rules

- Do not commit `.env` files with real values.
- Do not paste backend secrets into frontend variables.
- Do not expose provider credentials to client/browser runtime.
- Keep owner/admin routes protected.
- Keep production CORS restricted to the production frontend URL.
- Keep all approval/governance controls enabled.

## Release Decision

- Can continue: `True`
- Next step: Frontend production host configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_113_BACKEND_PRODUCTION_HOST_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_113_OK")