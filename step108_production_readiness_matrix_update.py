from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

matrix = {
    "step": 108,
    "name": "Production Readiness Matrix Update",
    "generated_at_utc": now,
    "overall_status": "production_release_preparation_in_progress",
    "completed_steps": "51-107",
    "active_step": 108,
    "matrix": {
        "core_platform": {"status": "complete", "percent": 100},
        "agent_catalogue": {"status": "complete", "percent": 100},
        "premium_output_quality": {"status": "complete", "percent": 100},
        "white_label_resale_readiness": {"status": "complete", "percent": 100},
        "global_localisation": {"status": "complete", "percent": 100},
        "governed_learning": {"status": "complete", "percent": 100},
        "security_governance": {"status": "complete", "percent": 100},
        "release_lock": {"status": "complete", "percent": 100},
        "local_release_bundle": {"status": "complete", "percent": 100},
        "production_env_template": {"status": "complete", "percent": 100},
        "provider_readiness_records": {"status": "complete", "percent": 100},
        "live_provider_credentials": {"status": "pending_external_configuration", "percent": 0},
        "live_backend_deployment": {"status": "pending_live_url", "percent": 0},
        "live_frontend_deployment": {"status": "pending_live_url", "percent": 0},
        "live_database_connection": {"status": "pending_external_configuration", "percent": 0},
        "live_llm_execution": {"status": "pending_live_credentials", "percent": 0},
        "live_payment_configuration": {"status": "pending_stripe_mode_decision", "percent": 0},
        "final_security_regression": {"status": "pending", "percent": 0},
        "final_owner_release_approval": {"status": "pending", "percent": 0},
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "create_final_external_configuration_checklist",
    },
}

completed_percents = [v["percent"] for v in matrix["matrix"].values()]
matrix["overall_percent"] = round(sum(completed_percents) / len(completed_percents), 2)

json_path = DATA / "step108_production_readiness_matrix.json"
md_path = DOCS / "STEP_108_PRODUCTION_READINESS_MATRIX.md"

json_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

rows = "\n".join(
    f"| {key.replace('_', ' ').title()} | {value['status']} | {value['percent']}% |"
    for key, value in matrix["matrix"].items()
)

md = f"""# Step 108 — Production Readiness Matrix

Generated: {now}

## Overall Status

**Status:** `{matrix["overall_status"]}`  
**Completed steps:** `{matrix["completed_steps"]}`  
**Overall production readiness:** `{matrix["overall_percent"]}%`

## Matrix

| Area | Status | Complete |
|---|---|---:|
{rows}

## Immediate Remaining Release Items

- Live provider credentials configured in deployment dashboards
- Live backend URL confirmed
- Live frontend URL confirmed
- Live database connection confirmed
- Live LLM execution confirmed
- Live payment configuration confirmed
- Final security regression completed
- Final owner release approval completed

## Release Decision

- Can continue: `True`
- Next step: Create final external configuration checklist.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_108_PRODUCTION_READINESS_MATRIX_UPDATED")
print("json_path", json_path)
print("md_path", md_path)
print("overall_status", matrix["overall_status"])
print("overall_percent", matrix["overall_percent"])
print("completed_steps", matrix["completed_steps"])
print("can_continue", matrix["release_decision"]["can_continue"])
print("STEP_108_OK")