from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DOCS = ROOT / "docs"
DATA = ROOT / "backend" / "app" / "data"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

readiness = {
    "step": 104,
    "name": "Production Endpoint / Domain Readiness Template",
    "generated_at_utc": now,
    "status": "production_endpoint_readiness_template_created",
    "production_checks": {
        "backend_health_endpoint": {
            "required": True,
            "expected_path": "/health",
            "status": "pending_live_url",
        },
        "admin_dashboard_url": {
            "required": True,
            "status": "pending_live_url",
        },
        "client_portal_url": {
            "required": True,
            "status": "pending_live_url",
        },
        "cors_allowed_origins": {
            "required": True,
            "status": "pending_production_domain",
        },
        "https_tls": {
            "required": True,
            "status": "pending_live_domain",
        },
        "custom_domain": {
            "required_for_final_release": True,
            "status": "pending_or_optional_before_soft_launch",
        },
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "create_live_endpoint_validation_script_once_backend_frontend_urls_are_known",
    },
}

json_path = DATA / "step104_production_endpoint_readiness.json"
md_path = DOCS / "STEP_104_PRODUCTION_ENDPOINT_DOMAIN_READINESS.md"

json_path.write_text(json.dumps(readiness, indent=2), encoding="utf-8")

md = f"""# Step 104 — Production Endpoint / Domain Readiness

Generated: {now}

## Status

**Result:** Production endpoint/domain readiness template created.

## Required Production URLs

| Item | Required | Status |
|---|---:|---|
| Backend health endpoint `/health` | Yes | Pending live URL |
| Admin dashboard URL | Yes | Pending live URL |
| Client portal URL | Yes | Pending live URL |
| CORS allowed origins | Yes | Pending production domain |
| HTTPS/TLS | Yes | Pending live domain |
| Custom domain | Required for final polished release | Pending or optional before soft launch |

## Release Notes

Before final release lock, the system needs:

1. Live backend URL
2. Live frontend URL
3. Confirmed `/health` response
4. Confirmed admin dashboard access
5. Confirmed client portal access
6. Confirmed frontend-to-backend CORS compatibility
7. Confirmed HTTPS/TLS production access

## Next Step

Create a live endpoint validation script once backend and frontend production URLs are known.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_104_PRODUCTION_ENDPOINT_READINESS_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("status", readiness["status"])
print("STEP_104_OK")