import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step259_revenue_optimisation_intelligence.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "revenue-optimisation-intelligence.md"

required = [
    "upsell_strategy",
    "cross_sell_strategy",
    "bundle_strategy",
    "subscription_strategy",
    "repeat_purchase_strategy",
    "retention_offer_strategy",
    "aov_increase_strategy",
    "ltv_increase_strategy",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "revenue_optimisation_intelligence_locked",
    "required_revenue_capabilities_present": all(record.get("global_revenue_capabilities", {}).get(key) is True for key in required),
    "agent_scope_present": len(record.get("agent_scope", [])) >= 10,
    "strategy_rules_present": len(record.get("strategy_rules", {})) >= 6,
    "governance_owner_approval_present": record.get("governance", {}).get("spend_changes_require_owner_approval") is True,
    "doc_created": doc.exists(),
}

print("STEP_259_REVENUE_OPTIMISATION_INTELLIGENCE_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_259_REVENUE_OPTIMISATION_INTELLIGENCE_OK")
