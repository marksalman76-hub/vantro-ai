import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step265_advanced_commerce_intelligence.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "advanced-commerce-intelligence.md"

required_layers = [
    "ai_commerce_brain",
    "self_improving_creative_lab",
    "autonomous_retention_engine",
    "ai_storefront_personalisation",
    "product_opportunity_intelligence",
    "ai_pricing_intelligence",
    "ai_influencer_network_graph",
    "full_ai_video_ad_studio",
    "ai_commerce_simulation_engine",
    "multi_agent_executive_council",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "advanced_commerce_intelligence_locked",
    "all_advanced_layers_present": all(record.get("advanced_layers", {}).get(layer) is True for layer in required_layers),
    "capabilities_present_for_all_layers": all(len(record.get("capabilities", {}).get(layer, [])) >= 3 for layer in required_layers),
    "owner_spend_approval_present": record.get("governance", {}).get("owner_approval_required_for_spend") is True,
    "owner_pricing_approval_present": record.get("governance", {}).get("owner_approval_required_for_pricing_changes") is True,
    "owner_campaign_approval_present": record.get("governance", {}).get("owner_approval_required_for_campaign_scaling") is True,
    "no_retraining_rule_present": record.get("governance", {}).get("no_autonomous_model_retraining") is True,
    "doc_created": doc.exists(),
}

print("STEP_265_ADVANCED_COMMERCE_INTELLIGENCE_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_265_ADVANCED_COMMERCE_INTELLIGENCE_OK")
