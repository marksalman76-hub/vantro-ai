from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step266_competitor_calibre_upgrade_plan.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 266,
    "status": "competitor_calibre_upgrade_plan_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "approved_upgrade_tracks": {
        "client_business_profile_setup_ui": {
            "priority": 1,
            "purpose": "Capture niche, products, audience, competitors, offers, margins, regions, brand tone, and goals.",
            "required": True,
        },
        "client_integrations_setup_ui": {
            "priority": 2,
            "purpose": "Let clients connect Shopify, CRM, email marketing, ads, analytics, and support systems.",
            "required": True,
        },
        "brand_memory_prompt_coach_ui": {
            "priority": 3,
            "purpose": "Improve prompt quality, brand consistency, and missing-detail capture.",
            "required": True,
        },
        "ugc_creator_controls_ui": {
            "priority": 4,
            "purpose": "Add UGC age range, gender/presentation, ethnicity/appearance, region, accent, language, archetype, and style controls.",
            "required": True,
        },
        "website_ugc_premium_output_contract_wiring": {
            "priority": 5,
            "purpose": "Wire premium Website and UGC intelligence into runtime outputs, not only documentation.",
            "required": True,
        },
        "live_provider_connection": {
            "priority": 6,
            "purpose": "Connect live OpenAI/provider execution when approved and keep owner controls active.",
            "required": True,
        },
        "shopify_crm_email_real_execution_connectors": {
            "priority": 7,
            "purpose": "Connect real Shopify/CRM/email execution workflows for full-system client value.",
            "required": True,
        },
        "ugc_video_rendering_provider_integration": {
            "priority": 8,
            "purpose": "Connect video/avatar/voice providers for actual cinematic UGC rendering.",
            "required": True,
        },
        "website_builder_polish_and_demo_outputs": {
            "priority": 9,
            "purpose": "Improve website outputs, demos, case studies, and ready-to-show sales assets.",
            "required": True,
        },
    },
    "quality_standard": {
        "must_be_best_in_class": True,
        "must_be_ecommerce_specific": True,
        "must_be_conversion_focused": True,
        "must_be_client_ready": True,
        "must_avoid_generic_outputs": True,
        "must_compete_with_sintra_higgsfield_manus_10web_base44": True,
    },
    "governance": {
        "owner_approval_required_for_spend": True,
        "owner_approval_required_for_live_publish": True,
        "owner_approval_required_for_campaign_launch": True,
        "owner_approval_required_for_provider_costs": True,
        "tenant_isolation_required": True,
        "no_autonomous_model_retraining": True,
    },
}

record_file = DATA / "step266_competitor_calibre_upgrade_plan.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "competitor-calibre-upgrade-plan.md").write_text("""# Competitor-Calibre Product Upgrade Plan

## Purpose
Move the platform from commercial beta into a polished, competitor-calibre ecommerce AI operating system.

## Approved Upgrade Tracks
1. Client Business Profile Setup UI
2. Client Integrations Setup UI
3. Brand Memory + Prompt Coach UI
4. UGC Creator Controls UI
5. Website + UGC Premium Output Contract Wiring
6. Live Provider Connection
7. Shopify / CRM / Email Real Execution Connectors
8. UGC Video Rendering Provider Integration
9. Website Builder Polish + Demo Outputs

## Quality Standard
Outputs must be ecommerce-specific, conversion-focused, client-ready, premium, and non-generic.

## Governance
Owner approval remains required for spend, live publish, campaign launch, provider-cost actions, and high-risk connected execution.
""", encoding="utf-8")

TEST.write_text(r'''
import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step266_competitor_calibre_upgrade_plan.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "competitor-calibre-upgrade-plan.md"

required_tracks = [
    "client_business_profile_setup_ui",
    "client_integrations_setup_ui",
    "brand_memory_prompt_coach_ui",
    "ugc_creator_controls_ui",
    "website_ugc_premium_output_contract_wiring",
    "live_provider_connection",
    "shopify_crm_email_real_execution_connectors",
    "ugc_video_rendering_provider_integration",
    "website_builder_polish_and_demo_outputs",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "competitor_calibre_upgrade_plan_locked",
    "all_upgrade_tracks_present": all(track in record.get("approved_upgrade_tracks", {}) for track in required_tracks),
    "all_tracks_required": all(record.get("approved_upgrade_tracks", {}).get(track, {}).get("required") is True for track in required_tracks),
    "quality_standard_all_true": all(record.get("quality_standard", {}).values()),
    "governance_owner_approval_present": record.get("governance", {}).get("owner_approval_required_for_spend") is True,
    "governance_no_retraining_present": record.get("governance", {}).get("no_autonomous_model_retraining") is True,
    "doc_created": doc.exists(),
}

print("STEP_266_COMPETITOR_CALIBRE_UPGRADE_PLAN_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_266_COMPETITOR_CALIBRE_UPGRADE_PLAN_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_266_COMPETITOR_CALIBRE_UPGRADE_PLAN_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'competitor-calibre-upgrade-plan.md'}")
print(f"Created/updated: {TEST}")
print("STEP_266_OK")