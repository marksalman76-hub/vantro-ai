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
    "step": 133,
    "name": "Vercel Environment Variable Checklist",
    "generated_at_utc": now,
    "status": "vercel_env_var_checklist_created",
    "completed_steps": "51-132",
    "secret_values_included": False,
    "vercel_allowed_public_env_vars": {
        "FRONTEND_URL": "Vercel production frontend URL",
        "BACKEND_URL": "Render production backend URL",
        "STRIPE_PUBLISHABLE_KEY": "Stripe public publishable key only"
    },
    "vercel_forbidden_env_vars": [
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
        "SHOPIFY_API_SECRET",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_DB_PASSWORD",
        "any private API key",
        "any database connection string",
        "any backend-only token"
    ],
    "required_vercel_checks": [
        "Vercel FRONTEND_URL points to the deployed frontend URL",
        "Vercel BACKEND_URL points to the Render backend URL",
        "No backend secrets exist in Vercel env vars",
        "No database credentials exist in Vercel env vars",
        "Customer portal does not expose internal logic",
        "Admin dashboard does not expose raw secrets",
        "Frontend successfully calls Render backend after deployment",
        "Render CORS allows the Vercel production URL only"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "create_supabase_connection_checklist_for_selected_stack",
    },
}

json_path = DATA / "step133_vercel_env_var_checklist.json"
md_path = DOCS / "STEP_133_VERCEL_ENV_VAR_CHECKLIST.md"

json_path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")

allowed_rows = "\n".join(
    f"| `{key}` | {value} |"
    for key, value in checklist["vercel_allowed_public_env_vars"].items()
)
forbidden = "\n".join(f"- `{item}`" for item in checklist["vercel_forbidden_env_vars"])
checks = "\n".join(f"- {item}" for item in checklist["required_vercel_checks"])

md = f"""# Step 133 — Vercel Environment Variable Checklist

Generated: {now}

## Status

**Result:** Vercel environment variable checklist created.  
**Completed steps:** `{checklist["completed_steps"]}`  
**Secret values included:** No

## Allowed Vercel Public Environment Variables

Only these public/client-safe values are allowed in Vercel.

| Variable | Purpose |
|---|---|
{allowed_rows}

## Forbidden Vercel Environment Variables

Never add these to Vercel or frontend runtime.

{forbidden}

## Required Vercel Checks

{checks}

## Vercel Env Var Rules

- Vercel must only receive frontend-safe public/config values.
- Render receives backend secrets.
- Supabase database credentials stay in Render only.
- OpenAI/Stripe secret/JWT/admin secrets stay in Render only.
- Client portal must not expose internal prompts, learning logic, provider routing, governance rules, backend configuration, or secrets.
- Admin dashboard may show safe operational state only.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Supabase connection checklist for selected stack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_133_VERCEL_ENV_VAR_CHECKLIST_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", checklist["secret_values_included"])
print("can_continue_documentation", checklist["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", checklist["release_decision"]["can_continue_live_validation"])
print("STEP_133_OK")