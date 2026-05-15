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
    "step": 124,
    "name": "External Live Setup Manual Checkpoint",
    "generated_at_utc": now,
    "status": "external_live_setup_manual_checkpoint_created",
    "completed_steps": "51-123",
    "secret_values_included": False,
    "manual_external_items_remaining": {
        "backend_host_created": False,
        "frontend_host_created": False,
        "production_database_created": False,
        "backend_environment_variables_configured": False,
        "frontend_public_environment_variables_configured": False,
        "llm_provider_key_configured": False,
        "stripe_configured": False,
        "email_provider_configured": False,
        "domain_dns_configured": False,
        "cors_locked_to_production_frontend": False,
        "live_backend_url_confirmed": False,
        "live_frontend_url_confirmed": False
    },
    "release_blocked_until": [
        "live backend URL is available",
        "live frontend URL is available",
        "required provider dashboard environment variables are configured",
        "production database is connected",
        "CORS is locked to production frontend",
        "security regression passes",
        "owner approves final release"
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "reason": "Live validation requires external provider setup and live URLs.",
        "next_step": "production_release_pause_and_external_setup_summary",
    },
}

json_path = DATA / "step124_external_live_setup_manual_checkpoint.json"
md_path = DOCS / "STEP_124_EXTERNAL_LIVE_SETUP_MANUAL_CHECKPOINT.md"

json_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

items = "\n".join(
    f"| {key.replace('_', ' ').title()} | {'Done' if value else 'Pending'} |"
    for key, value in checkpoint["manual_external_items_remaining"].items()
)
blocked = "\n".join(f"- {item}" for item in checkpoint["release_blocked_until"])

md = f"""# Step 124 — External Live Setup Manual Checkpoint

Generated: {now}

## Status

**Result:** External live setup manual checkpoint created.  
**Completed steps:** `{checkpoint["completed_steps"]}`  
**Secret values included:** No

## Manual External Items Remaining

| Item | Status |
|---|---|
{items}

## Release Blocked Until

{blocked}

## Current Decision

| Decision | Value |
|---|---|
| Can continue documentation | `{checkpoint["release_decision"]["can_continue_documentation"]}` |
| Can continue live validation | `{checkpoint["release_decision"]["can_continue_live_validation"]}` |
| Reason | {checkpoint["release_decision"]["reason"]} |

## Required Action Before Live Validation

External provider setup must be completed in provider dashboards.  
Do not enter secret values into repository files, docs, screenshots, or chat.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Production release pause and external setup summary.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_124_EXTERNAL_LIVE_SETUP_MANUAL_CHECKPOINT_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("completed_steps", checkpoint["completed_steps"])
print("secret_values_included", checkpoint["secret_values_included"])
print("can_continue_documentation", checkpoint["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", checkpoint["release_decision"]["can_continue_live_validation"])
print("STEP_124_OK")