from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

guide = {
    "step": 112,
    "name": "Production Provider Setup Guide",
    "generated_at_utc": now,
    "status": "production_provider_setup_guide_created",
    "completed_steps": "51-111",
    "secret_values_included": False,
    "setup_order": [
        "Backend host",
        "Database provider",
        "Frontend host",
        "LLM provider credentials",
        "Stripe configuration",
        "Email notification provider",
        "Domain/DNS",
        "CORS/security hardening",
        "Live endpoint validation",
        "Final release approval"
    ],
    "release_decision": {
        "can_continue": True,
        "next_step": "backend_production_host_configuration_pack",
    }
}

json_path = DATA / "step112_production_provider_setup_guide.json"
md_path = DOCS / "STEP_112_PRODUCTION_PROVIDER_SETUP_GUIDE.md"

json_path.write_text(json.dumps(guide, indent=2), encoding="utf-8")

md = f"""# Step 112 — Production Provider Setup Guide

Generated: {now}

## Status

**Result:** Production provider setup guide created.  
**Completed steps:** `51-111`  
**Secret values included:** No

## Correct Setup Order

1. Backend host
2. Database provider
3. Frontend host
4. LLM provider credentials
5. Stripe configuration
6. Email notification provider
7. Domain/DNS
8. CORS/security hardening
9. Live endpoint validation
10. Final release approval

## Backend Host

Use Render, Railway, Fly.io, AWS, GCP, or Azure.

Required items:

- Production service created
- Project/repository connected
- Build command configured
- Start command configured
- Environment variables added in provider dashboard only
- Health endpoint `/health` verified
- Logs reviewed after first deploy

## Database Provider

Use a managed Postgres provider such as Render Postgres, Supabase, Neon, Railway Postgres, AWS RDS, or equivalent.

Required items:

- Production database created
- `DATABASE_URL` configured in backend host dashboard
- Backup policy enabled
- Restore process documented
- Database access not exposed publicly without security controls

## Frontend Host

Use Vercel, Netlify, Cloudflare Pages, or equivalent.

Required items:

- Frontend app deployed
- Production backend API URL configured
- Admin route verified
- Client/customer route verified
- HTTPS enabled
- No internal backend secrets added to frontend environment variables

## LLM Provider Credentials

Required items:

- OpenAI key configured in backend deployment dashboard
- Optional fallback provider keys configured only if used
- No LLM keys stored in repository
- Live LLM readiness endpoint tested after deployment
- Live execution remains owner-governed where required

## Stripe

Required items:

- Stripe mode selected: test or live
- Publishable key configured where frontend requires it
- Secret key configured only in backend/provider dashboard
- Webhook secret configured only in backend/provider dashboard
- Success/cancel URLs configured
- Webhook delivery tested

## Email Notification Provider

Required items:

- SMTP/API provider selected
- Sender email/domain verified
- Owner notification email configured
- Delivery test completed
- Credentials stored only in provider dashboard

## Domain/DNS

Required items:

- Frontend domain configured
- Backend/API domain configured if using custom API domain
- DNS records set correctly
- HTTPS/TLS active
- Redirects checked
- No mixed-content errors

## CORS / Security

Required items:

- CORS locked to production frontend domain
- JWT secret configured
- Admin auth secret configured
- Owner/admin access protected
- Client access does not expose internal logic
- Provider credentials never exposed to client/browser

## Final Rule

Do not paste production secrets into source code, docs, GitHub, screenshots, or chat.

## Release Decision

- Can continue: `True`
- Next step: Backend production host configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_112_PRODUCTION_PROVIDER_SETUP_GUIDE_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", guide["secret_values_included"])
print("can_continue", guide["release_decision"]["can_continue"])
print("STEP_112_OK")