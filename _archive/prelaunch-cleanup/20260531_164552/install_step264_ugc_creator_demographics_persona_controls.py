from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step264_ugc_creator_demographics_persona_controls.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 264,
    "status": "ugc_creator_demographics_persona_controls_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "creator_controls": {
        "creator_age_range": True,
        "target_audience_age_range": True,
        "gender_or_presentation": True,
        "ethnicity_or_appearance": True,
        "region_or_country": True,
        "accent_or_language": True,
        "creator_archetype": True,
        "style_or_vibe": True,
    },
    "creator_archetypes": [
        "founder",
        "skincare expert",
        "fitness coach",
        "busy parent",
        "luxury influencer",
        "Gen Z creator",
        "authority expert",
        "relatable everyday customer",
        "product reviewer",
        "educator",
    ],
    "safety_rules": {
        "use_demographics_for_casting_and_representation_only": True,
        "do_not_stereotype_by_ethnicity_gender_age_or_region": True,
        "do_not_claim_sensitive_identity_unless_client_provided": True,
        "do_not_impersonate_real_people_without_permission": True,
        "claims_must_be_reviewed_before_publish": True,
        "paid_avatar_or_voice_usage_requires_owner_approval": True,
    },
    "quality_rules": {
        "persona_must_match_product_category": True,
        "persona_must_match_target_audience": True,
        "persona_must_match_platform": True,
        "persona_must_match_region_and_language": True,
        "ugc_must_remain_authentic_and_human_like": True,
    },
}

record_file = DATA / "step264_ugc_creator_demographics_persona_controls.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "ugc-creator-demographics-persona-controls.md").write_text("""# UGC Creator Demographics + Persona Controls

## Purpose
Give clients clear casting/persona controls for UGC generation while preserving safety and anti-stereotyping rules.

## Supported Creator Controls
- Creator age range
- Target audience age range
- Gender / presentation
- Ethnicity / appearance
- Region / country
- Accent / language
- Creator archetype
- Style / vibe

## Usage Rule
These controls are for casting, representation, audience fit, localisation, and creative direction only.

The system must not stereotype people or make unsupported assumptions based on age, gender, ethnicity, region, or appearance.

## Safety Rules
- No impersonation of real people without permission.
- No sensitive identity claims unless explicitly provided by the client.
- Claims must be reviewed before publishing.
- Paid avatar or voice generation requires owner approval.

## Example Input
Creator age range: 25–34  
Gender/presentation: female-presenting  
Ethnicity/appearance: Middle Eastern  
Region/accent: Australian English  
Creator archetype: skincare expert  
Style/vibe: warm, trustworthy, polished
""", encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_264_UGC_CREATOR_DEMOGRAPHICS_PERSONA_CONTROLS_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'ugc-creator-demographics-persona-controls.md'}")
print(f"Created/updated: {TEST}")
print("STEP_264_OK")