import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step264_ugc_creator_demographics_persona_controls.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "ugc-creator-demographics-persona-controls.md"

required_controls = [
    "creator_age_range",
    "target_audience_age_range",
    "gender_or_presentation",
    "ethnicity_or_appearance",
    "region_or_country",
    "accent_or_language",
    "creator_archetype",
    "style_or_vibe",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "ugc_creator_demographics_persona_controls_locked",
    "all_creator_controls_present": all(record.get("creator_controls", {}).get(key) is True for key in required_controls),
    "creator_archetypes_present": len(record.get("creator_archetypes", [])) >= 8,
    "anti_stereotyping_rule_present": record.get("safety_rules", {}).get("do_not_stereotype_by_ethnicity_gender_age_or_region") is True,
    "impersonation_guardrail_present": record.get("safety_rules", {}).get("do_not_impersonate_real_people_without_permission") is True,
    "owner_avatar_approval_present": record.get("safety_rules", {}).get("paid_avatar_or_voice_usage_requires_owner_approval") is True,
    "quality_rules_all_true": all(record.get("quality_rules", {}).values()),
    "doc_created": doc.exists(),
}

print("STEP_264_UGC_CREATOR_DEMOGRAPHICS_PERSONA_CONTROLS_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_264_UGC_CREATOR_DEMOGRAPHICS_PERSONA_CONTROLS_OK")
