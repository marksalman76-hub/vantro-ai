import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step260_global_ecommerce_intelligence_expansion.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "global-ecommerce-intelligence-expansion.md"

required_layers = [
    "customer_journey_intelligence",
    "ai_offer_engine",
    "creative_performance_memory",
    "store_conversion_intelligence",
    "competitor_tracking_intelligence",
    "autonomous_ecommerce_operations",
    "executive_dashboard_intelligence",
    "predictive_revenue_engine",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "global_ecommerce_intelligence_expansion_locked",
    "all_layers_present": all(layer in record.get("intelligence_layers", {}) for layer in required_layers),
    "all_layers_enabled": all(record.get("intelligence_layers", {}).get(layer, {}).get("enabled") is True for layer in required_layers),
    "global_agent_scope_25": len(record.get("global_agent_scope", [])) == 25,
    "governance_owner_spend_approval": record.get("governance_rules", {}).get("owner_approval_required_for_spend") is True,
    "governance_no_retraining": record.get("governance_rules", {}).get("no_autonomous_model_retraining") is True,
    "doc_created": doc.exists(),
}

print("STEP_260_GLOBAL_ECOMMERCE_INTELLIGENCE_EXPANSION_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_260_GLOBAL_ECOMMERCE_INTELLIGENCE_EXPANSION_OK")
