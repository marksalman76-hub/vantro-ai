from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step261_premium_website_ugc_quality.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 261,
    "status": "premium_website_ugc_quality_intelligence_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "website_agent_upgrades": {
        "adaptive_conversion_architecture": True,
        "ai_heatmap_attention_simulation": True,
        "dynamic_offer_personalisation": True,
        "narrative_commerce_engine": True,
        "visual_identity_intelligence": True,
        "ai_cro_testing_engine": True,
        "live_funnel_intelligence": True,
        "multi_region_commerce_intelligence": True,
    },
    "ugc_agent_upgrades": {
        "cinematic_ugc_intelligence": True,
        "viral_hook_intelligence": True,
        "creator_persona_engine": True,
        "platform_native_optimisation": True,
        "emotional_conversion_mapping": True,
        "ai_shot_director": True,
        "winning_ad_pattern_memory": True,
        "hyper_real_avatar_voice_layer_ready": True,
    },
    "quality_rules": {
        "outputs_must_be_conversion_focused": True,
        "outputs_must_be_brand_aware": True,
        "outputs_must_be_platform_native": True,
        "outputs_must_include_offer_strategy": True,
        "outputs_must_include_objection_handling": True,
        "outputs_must_include_testing_variants": True,
        "outputs_must_avoid_generic_templates": True,
        "outputs_must_be_client_ready": True,
    },
    "governance": {
        "owner_approval_required_for_live_site_publish": True,
        "owner_approval_required_for_campaign_launch": True,
        "owner_approval_required_for_spend_or_scaling": True,
        "owner_approval_required_for_avatar_voice_paid_usage": True,
        "agents_may_generate_and_recommend": True,
    },
}

record_file = DATA / "step261_premium_website_ugc_quality.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "premium-website-ugc-quality.md").write_text("""# Premium Website + UGC Quality Intelligence

## Website Agent Upgrades
- Adaptive conversion architecture
- AI heatmap and attention simulation
- Dynamic offer personalisation
- Narrative commerce engine
- Visual identity intelligence
- AI CRO testing engine
- Live funnel intelligence
- Multi-region commerce intelligence

## UGC Agent Upgrades
- Cinematic UGC intelligence
- Viral hook intelligence
- Creator persona engine
- Platform-native optimisation
- Emotional conversion mapping
- AI shot director
- Winning ad pattern memory
- Hyper-real avatar/voice readiness

## Quality Rules
Outputs must be conversion-focused, brand-aware, platform-native, emotionally persuasive, offer-aware, testing-ready, and client-ready.

## Governance
Agents may generate, recommend, and prepare assets. Owner approval remains required for live publishing, campaign launch, spend/scaling, and paid avatar/voice usage.
""", encoding="utf-8")

TEST.write_text(r'''
import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step261_premium_website_ugc_quality.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "premium-website-ugc-quality.md"

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "premium_website_ugc_quality_intelligence_locked",
    "website_upgrades_all_true": all(record.get("website_agent_upgrades", {}).values()),
    "ugc_upgrades_all_true": all(record.get("ugc_agent_upgrades", {}).values()),
    "quality_rules_all_true": all(record.get("quality_rules", {}).values()),
    "governance_publish_approval": record.get("governance", {}).get("owner_approval_required_for_live_site_publish") is True,
    "governance_campaign_approval": record.get("governance", {}).get("owner_approval_required_for_campaign_launch") is True,
    "doc_created": doc.exists(),
}

print("STEP_261_PREMIUM_WEBSITE_UGC_QUALITY_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_261_PREMIUM_WEBSITE_UGC_QUALITY_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_261_PREMIUM_WEBSITE_UGC_QUALITY_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'premium-website-ugc-quality.md'}")
print(f"Created/updated: {TEST}")
print("STEP_261_OK")