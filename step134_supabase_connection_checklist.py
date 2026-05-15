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
    "step": 134,
    "name": "Supabase Connection Checklist",
    "generated_at_utc": now,
    "status": "supabase_connection_checklist_created",
    "completed_steps": "51-133",
    "secret_values_included": False,
    "supabase_connection_rules": {
        "database_provider": "Supabase",
        "database_type": "Postgres",
        "render_env_var": "DATABASE_URL",
        "vercel_allowed": False,
        "frontend_exposure_allowed": False,
        "service_role_frontend_allowed": False,
    },
    "required_supabase_checks": [
        "Supabase project created",
        "Supabase project region selected",
        "Production database available",
        "Connection string copied only into Render DATABASE_URL",
        "Database SSL requirement confirmed",
        "Supabase service role key kept out of Vercel/frontend",
        "Database password not stored in repository",
        "Backups/restore policy confirmed",
        "Production and test data separation confirmed",
        "Render backend can connect to Supabase after deployment"
    ],
    "forbidden_locations_for_database_credentials": [
        "Vercel environment variables",
        "frontend runtime",
        "GitHub repository",
        "docs",
        "screenshots",
        "chat",
        "client/browser runtime",
        "committed .env files"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "create_external_setup_execution_checkpoint",
    },
}

json_path = DATA / "step134_supabase_connection_checklist.json"
md_path = DOCS / "STEP_134_SUPABASE_CONNECTION_CHECKLIST.md"

json_path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")

rules_rows = "\n".join(
    f"| {key.replace('_', ' ').title()} | `{value}` |"
    for key, value in checklist["supabase_connection_rules"].items()
)
checks = "\n".join(f"- {item}" for item in checklist["required_supabase_checks"])
forbidden = "\n".join(f"- {item}" for item in checklist["forbidden_locations_for_database_credentials"])

md = f"""# Step 134 — Supabase Connection Checklist

Generated: {now}

## Status

**Result:** Supabase connection checklist created.  
**Completed steps:** `{checklist["completed_steps"]}`  
**Secret values included:** No

## Supabase Connection Rules

| Rule | Value |
|---|---|
{rules_rows}

## Required Supabase Checks

{checks}

## Forbidden Locations For Database Credentials

{forbidden}

## Supabase Safety Rules

- `DATABASE_URL` must be entered in Render only.
- Vercel must not receive Supabase database credentials.
- Supabase service role key must never be exposed to frontend/client runtime.
- Database passwords and direct connection strings must not be committed, screenshotted, or pasted into chat.
- Backend connectivity must be verified after Render deployment.
- Backup and restore readiness must be confirmed before final release approval.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create external setup execution checkpoint.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_134_SUPABASE_CONNECTION_CHECKLIST_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", checklist["secret_values_included"])
print("database_provider", checklist["supabase_connection_rules"]["database_provider"])
print("render_env_var", checklist["supabase_connection_rules"]["render_env_var"])
print("vercel_allowed", checklist["supabase_connection_rules"]["vercel_allowed"])
print("can_continue_documentation", checklist["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", checklist["release_decision"]["can_continue_live_validation"])
print("STEP_134_OK")
