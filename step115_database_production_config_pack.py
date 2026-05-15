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
    "step": 115,
    "name": "Database Production Configuration Pack",
    "generated_at_utc": now,
    "status": "database_production_config_pack_created",
    "secret_values_included": False,
    "database_requirements": {
        "recommended_type": "Managed Postgres",
        "recommended_providers": [
            "Render Postgres",
            "Supabase",
            "Neon",
            "Railway Postgres",
            "AWS RDS",
            "GCP Cloud SQL",
            "Azure Database for PostgreSQL"
        ],
        "required_env_vars": [
            "DATABASE_URL"
        ],
        "required_controls": [
            "private connection where available",
            "SSL required",
            "automated backups enabled",
            "restore process documented",
            "least privilege database user",
            "production and test databases separated",
            "no database URL committed to repository"
        ],
        "required_validation": [
            "backend can connect to production database",
            "app starts without fallback to local storage",
            "write/read persistence verified",
            "backup policy verified",
            "restore plan documented"
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "llm_provider_production_configuration_pack",
    },
}

json_path = DATA / "step115_database_production_config_pack.json"
md_path = DOCS / "STEP_115_DATABASE_PRODUCTION_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

providers = "\n".join(f"- {item}" for item in pack["database_requirements"]["recommended_providers"])
required_vars = "\n".join(f"- `{item}`" for item in pack["database_requirements"]["required_env_vars"])
controls = "\n".join(f"- {item}" for item in pack["database_requirements"]["required_controls"])
validation = "\n".join(f"- {item}" for item in pack["database_requirements"]["required_validation"])

md = f"""# Step 115 — Database Production Configuration Pack

Generated: {now}

## Status

**Result:** Database production configuration pack created.  
**Secret values included:** No

## Recommended Database Type

Managed Postgres

## Recommended Providers

{providers}

## Required Environment Variables

Add only inside backend deployment/provider dashboard.

{required_vars}

## Required Database Controls

{controls}

## Required Production Validation

{validation}

## Database Safety Rules

- Do not commit `DATABASE_URL`.
- Do not expose database credentials in frontend variables.
- Use separate production and test databases.
- Use SSL and provider security controls.
- Enable backups before release.
- Document restore process before final owner release approval.

## Release Decision

- Can continue: `True`
- Next step: LLM provider production configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_115_DATABASE_PRODUCTION_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_115_OK")