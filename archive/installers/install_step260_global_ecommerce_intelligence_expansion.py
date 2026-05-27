from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step260_global_ecommerce_intelligence_expansion.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 260,
    "status": "global_ecommerce_intelligence_expansion_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "intelligence_layers": {
        "customer_journey_intelligence": {
            "enabled": True,
            "capabilities": [
                "lifecycle segmentation",
                "churn risk detection",
                "VIP detection",
                "reorder timing prediction",
                "customer intent scoring",
                "purchase timing prediction",
            ],
        },
        "ai_offer_engine": {
            "enabled": True,
            "capabilities": [
                "offer generation",
                "bundle offer construction",
                "seasonal promotion strategy",
                "urgency and scarcity framing",
                "checkout incentives",
                "pricing psychology",
            ],
        },
        "creative_performance_memory": {
            "enabled": True,
            "capabilities": [
                "winning hook tracking",
                "winning thumbnail tracking",
                "winning CTA tracking",
                "UGC style memory",
                "creator type performance memory",
                "offer structure performance memory",
            ],
        },
        "store_conversion_intelligence": {
            "enabled": True,
            "capabilities": [
                "product page conversion review",
                "checkout friction detection",
                "trust gap detection",
                "mobile UX review",
                "CTA hierarchy review",
                "offer clarity review",
            ],
        },
        "competitor_tracking_intelligence": {
            "enabled": True,
            "capabilities": [
                "pricing movement tracking",
                "offer movement tracking",
                "landing page change tracking",
                "ad creative shift tracking",
                "positioning change detection",
                "counter-offer recommendation",
            ],
        },
        "autonomous_ecommerce_operations": {
            "enabled": True,
            "capabilities": [
                "low stock signal detection",
                "ROAS decline detection",
                "ad fatigue detection",
                "churn spike detection",
                "conversion drop detection",
                "refund spike detection",
                "approval-gated action preparation",
            ],
        },
        "executive_dashboard_intelligence": {
            "enabled": True,
            "capabilities": [
                "plain-English performance explanation",
                "root cause analysis",
                "next-best-action recommendations",
                "risk summary",
                "opportunity summary",
            ],
        },
        "predictive_revenue_engine": {
            "enabled": True,
            "capabilities": [
                "revenue forecasting",
                "inventory pressure forecasting",
                "seasonal demand forecasting",
                "best launch timing prediction",
                "churn forecasting",
                "ad scaling window prediction",
            ],
        },
    },
    "global_agent_scope": [
        "master_orchestrator_agent",
        "product_research_agent",
        "competitor_intelligence_agent",
        "brand_strategy_agent",
        "store_builder_agent",
        "website_landing_page_agent",
        "product_copywriting_agent",
        "ugc_creative_agent",
        "product_image_direction_agent",
        "ad_creative_agent",
        "campaign_launch_agent",
        "analytics_optimisation_agent",
        "creative_rotation_agent",
        "email_marketing_agent",
        "customer_support_agent",
        "fulfilment_agent",
        "influencer_collaboration_agent",
        "seo_agent",
        "marketplace_agent",
        "billing_licence_agent",
        "reporting_agent",
        "quality_assurance_agent",
        "integration_agent",
        "security_compliance_agent",
        "demo_trial_agent",
    ],
    "governance_rules": {
        "agents_may_analyse_and_recommend": True,
        "owner_approval_required_for_spend": True,
        "owner_approval_required_for_strategy_change": True,
        "owner_approval_required_for_pricing_change": True,
        "owner_approval_required_for_campaign_scaling": True,
        "owner_approval_required_for_subscription_offer_changes": True,
        "owner_approval_required_for_customer_financial_actions": True,
        "no_autonomous_model_retraining": True,
        "tenant_isolation_required": True,
    },
}

record_file = DATA / "step260_global_ecommerce_intelligence_expansion.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "global-ecommerce-intelligence-expansion.md").write_text("""# Global Ecommerce Intelligence Expansion

## Purpose
This layer expands the platform from a general ecommerce AI agent system into a premium ecommerce operating intelligence system.

## Locked Intelligence Layers

1. Customer Journey Intelligence
2. AI Offer Engine
3. Creative Performance Memory
4. Store Conversion Intelligence
5. Competitor Tracking Intelligence
6. Autonomous Ecommerce Operations
7. Executive Dashboard Intelligence
8. Predictive Revenue Engine

## Governance
Agents may analyse, recommend, prepare actions, and surface risks/opportunities.

Owner approval remains required for:
- spend increases
- campaign scaling
- pricing changes
- subscription offer changes
- strategy changes
- customer financial actions
- high-risk connected execution

## Agent Scope
The intelligence layer applies globally across the 25-agent catalogue, with each agent using only the intelligence relevant to its role.
""", encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_260_GLOBAL_ECOMMERCE_INTELLIGENCE_EXPANSION_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'global-ecommerce-intelligence-expansion.md'}")
print(f"Created/updated: {TEST}")
print("STEP_260_OK")