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
    "step": 129,
    "name": "Supabase Database Setup Pack",
    "generated_at_utc": now,
    "status": "supabase_database_setup_pack_created",
    "completed_steps": "51-128",
    "secret_values_included": False,
    "provider": "Supabase",
    "database_type": "Postgres",
    "required_supabase_actions": [
        "Create a Supabase project",
        "Select a secure region close to target users or backend host",
        "Create/confirm production database",
        "Copy database connection string only into Render DATABASE_URL",
        "Enable SSL connection where required",
        "Confirm backups are enabled according to selected Supabase plan",
        "Keep Supabase service role keys out of frontend runtime",
        "Do not expose database credentials in repository files",
        "Document non-secret project name/region only if needed",
        "Run backend database connectivity validation after Render deploy"
    ],
    "required_render_env_var": "DATABASE_URL",
    "forbidden_frontend_values": [
        "DATABASE_URL",
        "Supabase service role key",
        "database password",
        "direct Postgres connection string"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "vercel_frontend_setup_pack",
    },
}

json_path = DATA / "step129_supabase_database_setup_pack.json"
md_path = DOCS / "STEP_129_SUPABASE_DATABASE_SETUP_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

actions = "\n".join(f"{i}. {item}" for i, item in enumerate(pack["required_supabase_actions"], start=1))
forbidden = "\n".join(f"- `{item}`" for item in pack["forbidden_frontend_values"])

md = f"""# Step 129 — Supabase Database Setup Pack

Generated: {now}

## Status

**Result:** Supabase database setup pack created.  
**Completed steps:** `{pack["completed_steps"]}`  
**Secret values included:** No

## Supabase Settings

| Item | Value |
|---|---|
| Provider | Supabase |
| Database type | Postgres |
| Required Render env var | `DATABASE_URL` |

## Required Supabase Actions

{actions}

## Forbidden Frontend Values

Never add these to Vercel/frontend variables.

{forbidden}

## Supabase Safety Rules

- `DATABASE_URL` belongs in Render backend environment variables only.
- Supabase service role keys must never be exposed to client/browser runtime.
- Do not commit database credentials.
- Do not paste database credentials into chat or screenshots.
- Production and test data should remain separated.
- Backup/restore policy must be confirmed before final production approval.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Vercel frontend setup pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_129_SUPABASE_DATABASE_SETUP_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("provider", pack["provider"])
print("database_type", pack["database_type"])
print("secret_values_included", pack["secret_values_included"])
print("can_continue_documentation", pack["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", pack["release_decision"]["can_continue_live_validation"])
print("STEP_129_OK")