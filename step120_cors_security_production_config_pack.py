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
    "step": 120,
    "name": "CORS/Security Production Configuration Pack",
    "generated_at_utc": now,
    "status": "cors_security_production_config_pack_created",
    "secret_values_included": False,
    "security_requirements": {
        "required_backend_env_vars": [
            "FRONTEND_URL",
            "BACKEND_URL",
            "JWT_SECRET",
            "ADMIN_AUTH_SECRET",
            "OWNER_ADMIN_EMAIL",
            "APP_ENV"
        ],
        "required_cors_controls": [
            "production frontend domain explicitly allowed",
            "wildcard origins disabled in production",
            "localhost allowed only in development",
            "credentials/cookies configured only if needed",
            "preflight requests verified",
            "blocked origins tested"
        ],
        "required_security_controls": [
            "JWT/admin secret configured outside repository",
            "owner/admin routes protected",
            "client routes cannot access internal logic",
            "provider credentials never exposed to frontend",
            "production errors do not expose stack traces or secrets",
            "audit logging enabled",
            "one-time client link reuse blocked and flagged",
            "tenant isolation enforced",
            "paid entitlement checks enforced",
            "learning/governance internals blocked from client access"
        ],
        "required_validation": [
            "production frontend can call backend without CORS error",
            "unknown origin is blocked",
            "admin route protection confirmed",
            "client route cannot access internal configuration",
            "secret/env endpoints do not exist or are protected",
            "provider readiness endpoints do not print secrets",
            "security regression passes before final release"
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "production_readiness_matrix_refresh",
    },
}

json_path = DATA / "step120_cors_security_production_config_pack.json"
md_path = DOCS / "STEP_120_CORS_SECURITY_PRODUCTION_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

env_vars = "\n".join(f"- `{item}`" for item in pack["security_requirements"]["required_backend_env_vars"])
cors = "\n".join(f"- {item}" for item in pack["security_requirements"]["required_cors_controls"])
security = "\n".join(f"- {item}" for item in pack["security_requirements"]["required_security_controls"])
validation = "\n".join(f"- {item}" for item in pack["security_requirements"]["required_validation"])

md = f"""# Step 120 — CORS/Security Production Configuration Pack

Generated: {now}

## Status

**Result:** CORS/security production configuration pack created.  
**Secret values included:** No

## Required Backend Environment Variables

Configure only inside backend deployment/provider dashboard.

{env_vars}

## Required CORS Controls

{cors}

## Required Security Controls

{security}

## Required Production Validation

{validation}

## Security Rules

- No wildcard CORS in production.
- No secrets in frontend runtime.
- No internal prompts, learning logic, provider routing, governance internals, or backend configuration exposed to clients.
- Owner/admin routes must remain protected.
- Tenant isolation and paid entitlement checks must remain enforced.
- One-time client links must be blocked, logged, and flagged on reuse.
- Security regression must pass before final owner release approval.

## Release Decision

- Can continue: `True`
- Next step: Production readiness matrix refresh.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_120_CORS_SECURITY_PRODUCTION_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_120_OK")