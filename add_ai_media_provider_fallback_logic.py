from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_provider_fallback_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

FALLBACK_BLOCK = r'''

def build_provider_fallback_execution_plan(orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    provider_strategy = orchestration_packet.get("provider_strategy", {})
    orchestration_score = orchestration_packet.get("orchestration_score", {})
    adapter_payload = orchestration_packet.get("adapter_ready_payload", {})

    primary_provider = provider_strategy.get("primary_provider_slot", "multi_modal_generation_provider")
    fallback_providers = provider_strategy.get("fallback_provider_slots", [])

    fallback_steps = []

    fallback_steps.append({
        "step": 1,
        "provider_slot": primary_provider,
        "execution_role": "primary_generation_attempt",
        "allowed": orchestration_score.get("provider_execution_allowed", True),
        "failure_triggers": [
            "provider_timeout",
            "provider_error",
            "low_quality_result",
            "brand_mismatch",
            "character_inconsistency",
            "policy_or_safety_rejection",
        ],
    })

    for index, fallback_provider in enumerate(fallback_providers, start=2):
        fallback_steps.append({
            "step": index,
            "provider_slot": fallback_provider,
            "execution_role": "fallback_generation_attempt",
            "allowed": True,
            "inherits_payload": True,
            "payload_adjustment": "preserve creative direction, simplify provider-specific execution constraints if needed",
            "failure_triggers": [
                "provider_timeout",
                "provider_error",
                "low_quality_result",
                "brand_mismatch",
                "character_inconsistency",
            ],
        })

    fallback_steps.append({
        "step": len(fallback_steps) + 1,
        "provider_slot": "manual_review_queue",
        "execution_role": "human_review_or_owner_review",
        "allowed": True,
        "trigger": "all_provider_attempts_failed_or_quality_score_below_threshold",
        "required_action": "review creative brief, provider payload, quality issues, and retry recommendation",
    })

    return {
        "fallback_enabled": True,
        "execution_mode": "primary_then_fallback_provider_chain",
        "primary_provider_slot": primary_provider,
        "fallback_provider_slots": fallback_providers,
        "manual_review_final_step": True,
        "quality_threshold": 80,
        "score_at_plan_time": orchestration_score.get("overall_score"),
        "adapter_payload_present": bool(adapter_payload),
        "fallback_steps": fallback_steps,
        "rules": {
            "preserve_brand_memory": True,
            "preserve_character_consistency": True,
            "preserve_cinematic_direction": True,
            "preserve_ecommerce_objective": True,
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
        },
    }
'''

if "def build_provider_fallback_execution_plan(" not in content:
    insert_before = "\ndef readiness"
    if insert_before in content:
        content = content.replace(insert_before, FALLBACK_BLOCK + insert_before, 1)
    else:
        content += FALLBACK_BLOCK

attach_block = '''
    orchestration_packet["provider_fallback_execution_plan"] = build_provider_fallback_execution_plan(orchestration_packet)
'''

if 'orchestration_packet["provider_fallback_execution_plan"] = build_provider_fallback_execution_plan(orchestration_packet)' not in content:
    content = content.replace(
        '    orchestration_packet["orchestration_score"] = score_ai_media_orchestration(orchestration_packet)',
        '    orchestration_packet["orchestration_score"] = score_ai_media_orchestration(orchestration_packet)\n' + attach_block,
        1,
    )

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_provider_fallback_logic.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    build_provider_fallback_execution_plan,
)


def main():
    result = run_shared_ai_media_creative_director({
        "agent_id": "ad_creative_agent",
        "brand_name": "Fallback Test Brand",
        "product_name": "Fallback Test Product",
        "target_audience": "online shoppers",
        "objective": "conversion-focused ecommerce ad",
        "platform": "Meta",
        "media_type": "ugc video",
        "language": "English",
        "region": "global",
    })

    packet = result["orchestration_packet"]
    fallback_plan = packet["provider_fallback_execution_plan"]

    assert result["success"] is True
    assert fallback_plan["fallback_enabled"] is True
    assert fallback_plan["manual_review_final_step"] is True
    assert fallback_plan["primary_provider_slot"] == "video_generation_provider"
    assert len(fallback_plan["fallback_steps"]) >= 3
    assert fallback_plan["rules"]["preserve_brand_memory"] is True
    assert fallback_plan["rules"]["preserve_character_consistency"] is True
    assert fallback_plan["rules"]["do_not_publish_without_governance"] is True
    assert fallback_plan["rules"]["owner_review_required_for_spend_or_campaign_scaling"] is True

    direct_plan = build_provider_fallback_execution_plan(packet)
    assert direct_plan["fallback_enabled"] is True
    assert direct_plan["adapter_payload_present"] is True

    print("AI_MEDIA_PROVIDER_FALLBACK_LOGIC_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_PROVIDER_FALLBACK_LOGIC_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")