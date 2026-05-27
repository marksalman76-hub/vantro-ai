from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_orchestration_scoring_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

SCORING_BLOCK = r'''

def score_ai_media_orchestration(orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    quality_rules = orchestration_packet.get("quality_rules", {})
    provider_strategy = orchestration_packet.get("provider_strategy", {})
    scene_plan = orchestration_packet.get("scene_plan", [])
    cinematic_direction = orchestration_packet.get("cinematic_direction", {})
    hook_strategy = orchestration_packet.get("hook_strategy", {})

    scores = {
        "brand_fit": 90 if orchestration_packet.get("brand") else 72,
        "cinematic_quality": 92 if cinematic_direction.get("camera_language") and cinematic_direction.get("lighting") else 70,
        "ecommerce_conversion_strength": 91 if hook_strategy.get("hook_direction") and len(scene_plan) >= 4 else 68,
        "character_consistency_readiness": 90 if quality_rules.get("same_character_consistency_required_when_character_present") else 65,
        "provider_fallback_readiness": 94 if provider_strategy.get("fallback_required") and provider_strategy.get("fallback_provider_slots") else 60,
        "multilingual_readiness": 88 if quality_rules.get("multilingual_adaptation_supported") else 62,
        "premium_output_readiness": 95 if quality_rules.get("premium_only") and quality_rules.get("no_placeholder_outputs") else 58,
    }

    overall_score = round(sum(scores.values()) / len(scores), 2)

    if overall_score >= 90:
        readiness_level = "premium_ready"
    elif overall_score >= 80:
        readiness_level = "ready_with_minor_review"
    elif overall_score >= 70:
        readiness_level = "manual_review_recommended"
    else:
        readiness_level = "not_ready_for_provider_execution"

    return {
        "overall_score": overall_score,
        "readiness_level": readiness_level,
        "scores": scores,
        "provider_execution_allowed": overall_score >= 80,
        "manual_review_required": overall_score < 80,
        "recommendations": [
            "Preserve brand and character consistency before provider execution.",
            "Use fallback provider strategy for failed or low-quality provider results.",
            "Reject placeholder/basic media prompts before generation.",
            "Keep ecommerce conversion objective visible in hook, scene flow, and CTA.",
        ],
    }
'''

if "def score_ai_media_orchestration(" not in content:
    insert_before = "\ndef run_shared_ai_media_creative_director"
    if insert_before in content:
        content = content.replace(insert_before, SCORING_BLOCK + insert_before, 1)
    else:
        content += SCORING_BLOCK

if '"orchestration_score": score_ai_media_orchestration(orchestration_packet),' not in content:
    content = content.replace(
        '"adapter_ready_payload": {',
        '"orchestration_score": score_ai_media_orchestration(orchestration_packet),\n        "adapter_ready_payload": {',
        1,
    )

# The direct replacement above can fail because orchestration_packet is being defined inline.
# If so, add score after packet construction and before return.
if '"orchestration_score": score_ai_media_orchestration(orchestration_packet),' in content:
    content = content.replace(
        '        "orchestration_score": score_ai_media_orchestration(orchestration_packet),\n        "adapter_ready_payload": {',
        '        "adapter_ready_payload": {',
        1,
    )

score_attach = '''
    orchestration_packet["orchestration_score"] = score_ai_media_orchestration(orchestration_packet)
'''

if 'orchestration_packet["orchestration_score"] = score_ai_media_orchestration(orchestration_packet)' not in content:
    content = content.replace(
        '    return {\n        "success": True,',
        score_attach + '\n    return {\n        "success": True,',
        1,
    )

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_orchestration_scoring.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    score_ai_media_orchestration,
)


def main():
    result = run_shared_ai_media_creative_director({
        "agent_id": "ugc_video_agent",
        "brand_name": "Premium Brand",
        "product_name": "Premium Product",
        "target_audience": "high-intent ecommerce buyers",
        "objective": "premium conversion-focused UGC video",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
        "region": "global",
    })

    packet = result["orchestration_packet"]
    score = packet["orchestration_score"]

    assert result["success"] is True
    assert score["overall_score"] >= 80
    assert score["provider_execution_allowed"] is True
    assert score["manual_review_required"] is False
    assert "brand_fit" in score["scores"]
    assert "cinematic_quality" in score["scores"]
    assert "ecommerce_conversion_strength" in score["scores"]
    assert "provider_fallback_readiness" in score["scores"]
    assert "premium_output_readiness" in score["scores"]

    direct_score = score_ai_media_orchestration(packet)
    assert direct_score["overall_score"] >= 80

    print("AI_MEDIA_ORCHESTRATION_SCORING_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_ORCHESTRATION_SCORING_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")