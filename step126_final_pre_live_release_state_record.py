from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

state = {
    "step": 126,
    "name": "Final Pre-Live Release State Record",
    "generated_at_utc": now,
    "status": "final_pre_live_release_state_record_created",
    "completed_steps": "51-125",
    "pre_live_release_state": "ready_for_external_provider_setup",
    "secret_values_included": False,
    "locked_state": {
        "core_platform_ready": True,
        "release_docs_ready": True,
        "configuration_packs_ready": True,
        "governance_locked": True,
        "security_locked": True,
        "secret_handling_locked": True,
        "live_validation_blocked_until_external_setup": True,
    },
    "remaining_before_live_validation": [
        "backend host live URL",
        "frontend host live URL",
        "production database connection",
        "backend provider environment variables",
        "frontend public environment variables",
        "LLM provider key",
        "Stripe setup",
        "email provider setup",
        "DNS/custom domain setup if used",
        "CORS production frontend allowlist",
    ],
    "release_decision": {
        "can_continue_documentation": True,
        "can_continue_live_validation": False,
        "can_release_to_production": False,
        "next_step": "prepare_external_provider_setup_action_list",
    },
}

json_path = DATA / "step126_final_pre_live_release_state_record.json"
md_path = DOCS / "STEP_126_FINAL_PRE_LIVE_RELEASE_STATE_RECORD.md"

json_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

locked = "\n".join(
    f"| {key.replace('_', ' ').title()} | `{value}` |"
    for key, value in state["locked_state"].items()
)
remaining = "\n".join(f"- {item}" for item in state["remaining_before_live_validation"])

md = f"""# Step 126 — Final Pre-Live Release State Record

Generated: {now}

## Status

**Result:** Final pre-live release state record created.  
**Completed steps:** `{state["completed_steps"]}`  
**Pre-live release state:** `{state["pre_live_release_state"]}`  
**Secret values included:** No

## Locked State

| Area | Locked / Ready |
|---|---:|
{locked}

## Remaining Before Live Validation

{remaining}

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Release to production now: `False`
- Next step: Prepare external provider setup action list.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_126_FINAL_PRE_LIVE_RELEASE_STATE_RECORD_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("status", state["status"])
print("completed_steps", state["completed_steps"])
print("pre_live_release_state", state["pre_live_release_state"])
print("can_continue_documentation", state["release_decision"]["can_continue_documentation"])
print("can_continue_live_validation", state["release_decision"]["can_continue_live_validation"])
print("can_release_to_production", state["release_decision"]["can_release_to_production"])
print("STEP_126_OK")