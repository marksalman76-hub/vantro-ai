from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

checkpoint = {
    "step": 135,
    "name": "External Setup Execution Checkpoint",
    "generated_at_utc": now,
    "status": "external_setup_execution_checkpoint_created",
    "completed_steps": "51-134",
    "secret_values_included": False,
    "selected_stack": {
        "backend": "Render",
        "frontend": "Vercel",
        "database": "Supabase",
        "llm": "OpenAI",
        "payments": "Stripe"
    },
    "external_execution_order": [
        "Create Supabase project",
        "Copy Supabase DATABASE_URL into Render only",
        "Create Render backend Web Service",
        "Configure Render required env vars",
        "Deploy Render backend",
        "Confirm Render backend /health URL",
        "Create Vercel frontend project",
        "Configure Vercel public env vars only",
        "Deploy Vercel frontend",
        "Copy Vercel frontend URL into Render FRONTEND_URL",
        "Lock Render CORS to Vercel frontend URL",
        "Redeploy/restart Render backend",
        "Run live validation command pack"
    ],
    "manual_inputs_needed_next": [
        "Render live backend URL",
        "Vercel live frontend URL",
        "Supabase project created confirmation",
        "Render env vars configured confirmation",
        "Vercel public env vars configured confirmation"
    ],
    "release_decision": {
        "documentation_can_continue": True,
        "external_setup_can_begin": True,
        "live_validation_can_continue": False,
        "production_release_can_be_approved": False,
        "next_step": "start_external_provider_setup_supabase_first",
    },
}

json_path = DATA / "step135_external_setup_execution_checkpoint.json"
md_path = DOCS / "STEP_135_EXTERNAL_SETUP_EXECUTION_CHECKPOINT.md"

json_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

stack_rows = "\n".join(
    f"| {key.title()} | {value} |"
    for key, value in checkpoint["selected_stack"].items()
)
order = "\n".join(f"{i}. {item}" for i, item in enumerate(checkpoint["external_execution_order"], start=1))
inputs = "\n".join(f"- {item}" for item in checkpoint["manual_inputs_needed_next"])

md = f"""# Step 135 — External Setup Execution Checkpoint

Generated: {now}

## Status

**Result:** External setup execution checkpoint created.  
**Completed steps:** `{checkpoint["completed_steps"]}`  
**Secret values included:** No

## Selected Stack

| Layer | Provider |
|---|---|
{stack_rows}

## External Execution Order

{order}

## Manual Inputs Needed Next

{inputs}

## Current Release Decision

| Decision | Value |
|---|---:|
| Documentation can continue | `{checkpoint["release_decision"]["documentation_can_continue"]}` |
| External setup can begin | `{checkpoint["release_decision"]["external_setup_can_begin"]}` |
| Live validation can continue | `{checkpoint["release_decision"]["live_validation_can_continue"]}` |
| Production release can be approved | `{checkpoint["release_decision"]["production_release_can_be_approved"]}` |

## Next Action

Start external provider setup with Supabase first.

## Secret Rule

Do not paste Supabase, Render, Vercel, OpenAI, Stripe, JWT, admin, SMTP, or database secret values into this repository, docs, screenshots, chat, or frontend variables.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_135_EXTERNAL_SETUP_EXECUTION_CHECKPOINT_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", checkpoint["secret_values_included"])
print("external_setup_can_begin", checkpoint["release_decision"]["external_setup_can_begin"])
print("live_validation_can_continue", checkpoint["release_decision"]["live_validation_can_continue"])
print("production_release_can_be_approved", checkpoint["release_decision"]["production_release_can_be_approved"])
print("STEP_135_OK")