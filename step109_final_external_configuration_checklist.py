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
    "step": 109,
    "name": "Final External Configuration Checklist",
    "generated_at_utc": now,
    "status": "external_configuration_checklist_created",
    "secret_values_included": False,
    "external_configuration_items": {
        "backend_host": {
            "required": True,
            "configure_in": "Render/Railway/Fly/AWS/GCP/Azure dashboard",
            "items": ["production backend service", "start command", "environment variables", "health endpoint"],
            "status": "pending",
        },
        "frontend_host": {
            "required": True,
            "configure_in": "Vercel/Netlify/Cloudflare Pages dashboard",
            "items": ["production frontend deployment", "backend API URL", "admin route", "client route"],
            "status": "pending",
        },
        "database": {
            "required": True,
            "configure_in": "Database provider dashboard",
            "items": ["production database", "DATABASE_URL", "backup policy", "restore test plan"],
            "status": "pending",
        },
        "llm_provider": {
            "required": True,
            "configure_in": "Deployment provider environment variables",
            "items": ["OPENAI_API_KEY", "fallback provider keys if used", "live execution readiness"],
            "status": "pending",
        },
        "stripe": {
            "required": True,
            "configure_in": "Stripe dashboard and deployment provider environment variables",
            "items": ["publishable key", "secret key", "webhook secret", "success/cancel URLs", "test/live mode decision"],
            "status": "pending",
        },
        "email_notifications": {
            "required": True,
            "configure_in": "Email provider dashboard and deployment provider environment variables",
            "items": ["SMTP/API credentials", "from email", "owner notification email", "delivery test"],
            "status": "pending",
        },
        "domain_dns": {
            "required": True,
            "configure_in": "DNS provider dashboard",
            "items": ["custom domain", "DNS records", "TLS/HTTPS", "frontend/backend domain mapping"],
            "status": "pending",
        },
        "security": {
            "required": True,
            "configure_in": "Application and provider dashboards",
            "items": ["JWT secret", "admin auth secret", "CORS allowed origins", "secret rotation plan", "no secrets in repo"],
            "status": "pending",
        },
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "create_live_endpoint_validation_script_template",
    },
}

json_path = DATA / "step109_final_external_configuration_checklist.json"
md_path = DOCS / "STEP_109_FINAL_EXTERNAL_CONFIGURATION_CHECKLIST.md"

json_path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")

rows = "\n".join(
    f"| {name.replace('_', ' ').title()} | {'Yes' if details['required'] else 'No'} | {details['status']} | {details['configure_in']} |"
    for name, details in checklist["external_configuration_items"].items()
)

md = f"""# Step 109 — Final External Configuration Checklist

Generated: {now}

## Status

**Result:** Final external configuration checklist created.  
**Secret values included:** No

## Configuration Matrix

| Area | Required | Status | Configure In |
|---|---:|---|---|
{rows}

## Critical Rule

Do not paste production secrets into files, docs, GitHub, chat, screenshots, or source code.  
Production secrets must only be added directly into the selected deployment/provider dashboards.

## Remaining External Configuration Items

- Backend host configured
- Frontend host configured
- Production database configured
- LLM provider credentials configured
- Stripe payment/webhook configuration completed
- Email notification provider configured
- Domain/DNS and HTTPS configured
- JWT/admin secrets configured
- CORS allowed origins locked to production frontend domain
- No secrets stored in repository

## Release Decision

- Can continue: `True`
- Next step: Create live endpoint validation script template.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_109_FINAL_EXTERNAL_CONFIGURATION_CHECKLIST_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", checklist["secret_values_included"])
print("can_continue", checklist["release_decision"]["can_continue"])
print("STEP_109_OK")