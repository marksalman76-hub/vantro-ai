import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step262_client_success_intelligence.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "client-success-intelligence.md"

required = [
    "prompt_quality_coach",
    "brand_memory_system",
    "client_business_profile_builder",
    "ai_recommendation_feed",
    "performance_scorecards",
    "campaign_playbooks",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "client_success_intelligence_locked",
    "all_layers_present": all(layer in record.get("client_success_layers", {}) for layer in required),
    "all_layers_enabled": all(record.get("client_success_layers", {}).get(layer, {}).get("enabled") is True for layer in required),
    "quality_rules_all_true": all(record.get("quality_rules", {}).values()),
    "governance_owner_approval_present": record.get("governance", {}).get("high_risk_actions_require_owner_approval") is True,
    "doc_created": doc.exists(),
}

print("STEP_262_CLIENT_SUCCESS_INTELLIGENCE_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_262_CLIENT_SUCCESS_INTELLIGENCE_OK")
