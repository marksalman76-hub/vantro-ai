from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
REPORTS = ROOT / "release_reports"
DOCS = ROOT / "docs"
BACKUPS = ROOT / "backups"

for p in [REPORTS, DOCS, BACKUPS]:
    p.mkdir(parents=True, exist_ok=True)

env_template = """# Ecommerce AI Agent Platform — Production Environment Template
# Do NOT commit real secrets.
# Configure these only inside Render/Vercel/Supabase/R2/S3/Stripe production dashboards.

# Stripe live billing
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_STARTER=
STRIPE_PRICE_GROWTH=
STRIPE_PRICE_ENTERPRISE=

# Media/object storage
MEDIA_STORAGE_PROVIDER=supabase
MEDIA_STORAGE_BUCKET=
MEDIA_STORAGE_PUBLIC_BASE_URL=
MEDIA_STORAGE_ACCESS_KEY=
MEDIA_STORAGE_SECRET_KEY=
MEDIA_STORAGE_REGION=

# Supabase optional storage/runtime
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=

# App URLs
NEXT_PUBLIC_APP_URL=
NEXT_PUBLIC_API_BASE_URL=
BACKEND_PUBLIC_URL=
FRONTEND_PUBLIC_URL=

# Security/session
JWT_SECRET=
SESSION_SECRET=
COOKIE_SECURE=true
"""

runbook = """# Ecommerce AI Agent Platform — Final Production Launch Runbook

## Current Release State

The platform is in launch-candidate / pre-commercial-release state.

Confirmed:
- Frontend build passing
- Backend compile passing
- Durable media persistence installed
- Production storage adapter installed
- Stripe/billing runtime present
- Entitlement/commercial controls verified
- Client deliverable review UX installed
- Release lock passed

## Required Production Setup

### 1. Stripe Live Mode

Configure in production environment only:
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- live price IDs for packages

Required live test:
1. Create a real test customer.
2. Start subscription checkout.
3. Confirm subscription active.
4. Confirm tenant/package activation.
5. Confirm failed payment policy is not shifting billing cycle.
6. Confirm cancellation respects month-to-month terms.

### 2. Production Media Storage

Recommended first option: Supabase Storage.

Configure:
- MEDIA_STORAGE_PROVIDER=supabase
- MEDIA_STORAGE_BUCKET
- MEDIA_STORAGE_PUBLIC_BASE_URL
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

Required test:
1. Prepare upload reference.
2. Upload one image.
3. Persist asset metadata.
4. Confirm latest deliverable returns image_url/download_url.
5. Confirm client portal renders asset.

### 3. Real Client Walkthrough

Run:
1. Create/activate client account.
2. Client logs in.
3. Client runs allowed agent.
4. Deliverable appears.
5. Client opens full deliverable modal.
6. Client approves.
7. Client rejects with feedback.
8. Client credit/package rules remain enforced.
9. Owner/admin remains unrestricted.

### 4. Deployment Monitoring

Before public traffic:
- uptime monitor on frontend
- uptime monitor on backend
- error logging
- backup verification
- rollback command verified
- production secrets checked
- no secrets committed to repo

## Known Non-Blocking Warning

Next.js middleware convention warning:
- migrate middleware to proxy later.
- currently non-blocking.
"""

launch_checklist = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "project": "ecommerce-ai-agent-platform",
    "release_profile": "production_launch_candidate",
    "must_complete_before_public_launch": [
        "Configure Stripe live environment variables in production only.",
        "Configure object storage environment variables in production only.",
        "Run one live Stripe subscription flow.",
        "Run one full real customer onboarding walkthrough.",
        "Verify client deliverable media renders from durable object storage.",
        "Verify owner/admin operations remain unrestricted by client credits.",
        "Verify entitlement blocks unpaid/inactive agents.",
        "Verify rollback path.",
        "Verify monitoring and backups.",
    ],
    "do_not_do": [
        "Do not commit secrets.",
        "Do not add more major features before launch.",
        "Do not bypass owner approval for spending/scaling/strategy actions.",
        "Do not expose tenant IDs/internal workflow details in client UI.",
    ],
    "launch_decision": {
        "technical_release_candidate": True,
        "public_launch_blocked_until_live_secrets_and_storage_are_configured": True,
        "recommended_next_action": "Configure production environment and run real live walkthrough.",
    },
}

(ROOT / ".env.production.example").write_text(env_template, encoding="utf-8")
(DOCS / "production-launch-runbook.md").write_text(runbook, encoding="utf-8")
(REPORTS / "batch_i_production_launch_checklist.json").write_text(
    json.dumps(launch_checklist, indent=2),
    encoding="utf-8",
)

print("BATCH_I_PRODUCTION_LAUNCH_PACK_INSTALLED")
print("Created: .env.production.example")
print("Created: docs\\production-launch-runbook.md")
print("Created: release_reports\\batch_i_production_launch_checklist.json")
print("BATCH_I_OK")