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
