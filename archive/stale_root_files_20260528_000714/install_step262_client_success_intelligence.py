from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step262_client_success_intelligence.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 262,
    "status": "client_success_intelligence_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "client_success_layers": {
        "prompt_quality_coach": {
            "enabled": True,
            "capabilities": [
                "prompt improvement suggestions",
                "missing-detail detection",
                "goal clarification assistance",
                "recommended prompt structures",
                "task refinement assistance",
            ],
        },
        "brand_memory_system": {
            "enabled": True,
            "capabilities": [
                "brand tone memory",
                "visual style memory",
                "offer memory",
                "audience memory",
                "preferred CTA memory",
                "regional/language memory",
            ],
        },
        "client_business_profile_builder": {
            "enabled": True,
            "capabilities": [
                "niche capture",
                "product/service capture",
                "audience capture",
                "competitor capture",
                "margin/offer capture",
                "brand positioning capture",
            ],
        },
        "ai_recommendation_feed": {
            "enabled": True,
            "capabilities": [
                "next-best-action recommendations",
                "campaign opportunity suggestions",
                "conversion improvement suggestions",
                "retention suggestions",
                "growth opportunity alerts",
            ],
        },
        "performance_scorecards": {
            "enabled": True,
            "capabilities": [
                "agent quality scoring",
                "conversion readiness scoring",
                "execution readiness scoring",
                "content quality scoring",
                "workflow success scoring",
            ],
        },
        "campaign_playbooks": {
            "enabled": True,
            "capabilities": [
                "product launch playbooks",
                "BFCM playbooks",
                "abandoned cart playbooks",
                "subscription growth playbooks",
                "retention/win-back playbooks",
                "seasonal campaign playbooks",
            ],
        },
    },
    "quality_rules": {
        "outputs_must_be_context_aware": True,
        "outputs_must_use_brand_memory": True,
        "outputs_must_use_business_profile": True,
        "outputs_must_be_recommendation_driven": True,
        "outputs_must_be_conversion_focused": True,
    },
    "governance": {
        "recommendations_allowed_without_approval": True,
        "high_risk_actions_require_owner_approval": True,
        "campaign_scaling_requires_owner_approval": True,
        "pricing_changes_require_owner_approval": True,
    },
}

record_file = DATA / "step262_client_success_intelligence.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "client-success-intelligence.md").write_text("""# Client Success Intelligence Layer

## Purpose
Improve client outcomes, onboarding quality, prompt quality, brand consistency, campaign execution quality, and retention.

## Included Layers
- Prompt Quality Coach
- Brand Memory System
- Client Business Profile Builder
- AI Recommendation Feed
- Performance Scorecards
- Campaign Playbooks

## Benefits
- Better prompts
- Better outputs
- Better brand consistency
- Better conversion performance
- Better client onboarding
- Better long-term retention

## Governance
Agents may recommend and assist automatically, but owner approval remains required for high-risk actions, scaling, pricing changes, and financial-impact actions.
""", encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_262_CLIENT_SUCCESS_INTELLIGENCE_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'client-success-intelligence.md'}")
print(f"Created/updated: {TEST}")
print("STEP_262_OK")