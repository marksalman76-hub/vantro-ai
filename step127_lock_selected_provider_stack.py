from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

stack = {
    "step": 127,
    "name": "Lock Selected Production Provider Stack",
    "generated_at_utc": now,
    "status": "selected_production_provider_stack_locked",
    "completed_steps": "51-126",
    "secret_values_included": False,
    "selected_providers": {
        "backend_host": "Render",
        "frontend_host": "Vercel",
        "database_provider": "Supabase",
        "llm_primary_provider": "OpenAI",
        "payment_provider": "Stripe",
        "email_provider": "pending",
        "domain_dns_provider": "pending",
    },
    "next_required_external_actions": [
        "create Supabase project",
        "copy Supabase database connection string into Render only",
        "create Render backend service",
        "configure Render backend environment variables",
        "deploy backend on Render",
        "create Vercel frontend project",
        "configure Vercel public environment variables",
        "deploy frontend on Vercel",
        "lock Render CORS to Vercel production domain",
        "run live deployment validation command pack"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "reason": "Provider stack selected, but live provider setup and URLs are not completed yet.",
        "next_step": "create_render_backend_setup_pack",
    },
}

json_path = DATA / "step127_selected_provider_stack.json"
md_path = DOCS / "STEP_127_SELECTED_PRODUCTION_PROVIDER_STACK.md"

json_path.write_text(json.dumps(stack, indent=2), encoding="utf-8")

provider_rows = "\n".join(
    f"| {key.replace('_', ' ').title()} | {value} |"
    for key, value in stack["selected_providers"].items()
)
actions = "\n".join(f"- {item}" for item in stack["next_required_external_actions"])

md = f"""# Step 127 — Selected Production Provider Stack

Generated: {now}

## Status

**Result:** Selected production provider stack locked.  
**Completed steps:** `{stack["completed_steps"]}`  
**Secret values included:** No

## Locked Provider Stack

| Layer | Provider |
|---|---|
{provider_rows}

## Next Required External Actions

{actions}

## Important Secret Rule

Do not paste Supabase, Render, Vercel, Stripe, OpenAI, or email provider secrets into repository files, docs, screenshots, or chat.

Secrets must only be entered into the relevant provider dashboard.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Reason: Provider stack selected, but live provider setup and URLs are not completed yet.
- Next step: Create Render backend setup pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_127_SELECTED_PROVIDER_STACK_LOCKED")
print("json_path", json_path)
print("md_path", md_path)
print("backend_host", stack["selected_providers"]["backend_host"])
print("frontend_host", stack["selected_providers"]["frontend_host"])
print("database_provider", stack["selected_providers"]["database_provider"])
print("secret_values_included", stack["secret_values_included"])
print("can_continue_documentation", stack["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", stack["release_decision"]["can_continue_live_validation"])
print("STEP_127_OK")