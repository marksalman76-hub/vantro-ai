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
    "step": 121,
    "name": "Production Readiness Matrix Refresh",
    "generated_at_utc": now,
    "overall_status": "production_configuration_packs_complete_pending_live_external_setup",
    "completed_steps": "51-120",
    "active_step": 121,
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
        "external_configuration_checklists": {"status": "complete", "percent": 100},
        "backend_config_pack": {"status": "complete", "percent": 100},
        "frontend_config_pack": {"status": "complete", "percent": 100},
        "database_config_pack": {"status": "complete", "percent": 100},
        "llm_config_pack": {"status": "complete", "percent": 100},
        "stripe_config_pack": {"status": "complete", "percent": 100},
        "email_config_pack": {"status": "complete", "percent": 100},
        "domain_dns_config_pack": {"status": "complete", "percent": 100},
        "cors_security_config_pack": {"status": "complete", "percent": 100},
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
        "next_step": "create_live_deployment_validation_command_pack",
    },
}

values = [item["percent"] for item in matrix["matrix"].values()]
matrix["overall_percent"] = round(sum(values) / len(values), 2)

json_path = DATA / "step121_production_readiness_matrix_refresh.json"
md_path = DOCS / "STEP_121_PRODUCTION_READINESS_MATRIX_REFRESH.md"

json_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

rows = "\n".join(
    f"| {name.replace('_', ' ').title()} | {details['status']} | {details['percent']}% |"
    for name, details in matrix["matrix"].items()
)

md = f"""# Step 121 — Production Readiness Matrix Refresh

Generated: {now}

## Overall Status

**Status:** `{matrix["overall_status"]}`  
**Completed steps:** `{matrix["completed_steps"]}`  
**Overall production readiness:** `{matrix["overall_percent"]}%`

## Matrix

| Area | Status | Complete |
|---|---|---:|
{rows}

## Completed Since Step 108

- Backend production host configuration pack
- Frontend production host configuration pack
- Database production configuration pack
- LLM provider production configuration pack
- Stripe production configuration pack
- Email notification production configuration pack
- Domain/DNS production configuration pack
- CORS/security production configuration pack

## Remaining Release Items

- Live provider credentials configured externally
- Live backend deployment confirmed
- Live frontend deployment confirmed
- Live database connection confirmed
- Live LLM execution confirmed
- Live payment configuration confirmed
- Final security regression completed
- Final owner release approval completed

## Release Decision

- Can continue: `True`
- Next step: Create live deployment validation command pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_121_PRODUCTION_READINESS_MATRIX_REFRESH_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("overall_status", matrix["overall_status"])
print("overall_percent", matrix["overall_percent"])
print("completed_steps", matrix["completed_steps"])
print("can_continue", matrix["release_decision"]["can_continue"])
print("STEP_121_OK")