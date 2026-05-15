from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

sequence = {
    "step": 131,
    "name": "Render / Vercel / Supabase External Setup Sequence",
    "generated_at_utc": now,
    "status": "render_vercel_supabase_external_setup_sequence_created",
    "completed_steps": "51-130",
    "secret_values_included": False,
    "selected_stack": {
        "backend": "Render",
        "frontend": "Vercel",
        "database": "Supabase",
        "llm": "OpenAI",
        "payments": "Stripe",
    },
    "recommended_sequence": [
        "Create Supabase project first",
        "Copy Supabase database connection string into Render DATABASE_URL only",
        "Create Render backend web service",
        "Configure Render backend env vars",
        "Deploy Render backend",
        "Confirm Render /health endpoint",
        "Create Vercel frontend project",
        "Set Vercel BACKEND_URL to Render backend URL",
        "Deploy Vercel frontend",
        "Copy Vercel production URL",
        "Update Render FRONTEND_URL and CORS allowlist to Vercel production URL",
        "Redeploy/restart Render backend after CORS update",
        "Run Step 122 live deployment validation command pack"
    ],
    "blocked_until": [
        "Supabase project exists",
        "Render backend service exists",
        "Vercel frontend project exists",
        "Render backend URL is available",
        "Vercel frontend URL is available",
        "CORS locked to Vercel production URL",
        "Step 122 live validation passes"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "next_step": "create_render_env_var_checklist_for_selected_stack",
    },
}

json_path = DATA / "step131_render_vercel_supabase_external_setup_sequence.json"
md_path = DOCS / "STEP_131_RENDER_VERCEL_SUPABASE_EXTERNAL_SETUP_SEQUENCE.md"

json_path.write_text(json.dumps(sequence, indent=2), encoding="utf-8")

stack_rows = "\n".join(
    f"| {key.title()} | {value} |"
    for key, value in sequence["selected_stack"].items()
)
seq = "\n".join(f"{i}. {item}" for i, item in enumerate(sequence["recommended_sequence"], start=1))
blocked = "\n".join(f"- {item}" for item in sequence["blocked_until"])

md = f"""# Step 131 — Render / Vercel / Supabase External Setup Sequence

Generated: {now}

## Status

**Result:** External setup sequence created.  
**Completed steps:** `{sequence["completed_steps"]}`  
**Secret values included:** No

## Selected Stack

| Layer | Provider |
|---|---|
{stack_rows}

## Recommended Setup Sequence

{seq}

## Blocked Until

{blocked}

## Critical Order Rule

Create and connect Supabase before finalising Render because Render needs the Supabase `DATABASE_URL`.

Deploy Render before finalising Vercel because Vercel needs the Render `BACKEND_URL`.

After Vercel is deployed, update Render with the final Vercel `FRONTEND_URL` and CORS allowlist.

## Secret Handling Rule

Do not paste database URLs, API keys, Stripe secrets, JWT secrets, admin secrets, or SMTP passwords into files, docs, screenshots, GitHub, frontend variables, or chat.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Render env var checklist for selected stack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_131_RENDER_VERCEL_SUPABASE_EXTERNAL_SETUP_SEQUENCE_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", sequence["secret_values_included"])
print("backend", sequence["selected_stack"]["backend"])
print("frontend", sequence["selected_stack"]["frontend"])
print("database", sequence["selected_stack"]["database"])
print("can_continue_documentation", sequence["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", sequence["release_decision"]["can_continue_live_validation"])
print("STEP_131_OK")