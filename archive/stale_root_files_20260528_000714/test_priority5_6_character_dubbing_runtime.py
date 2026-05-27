
from backend.app.runtime.ai_media_character_dubbing_runtime import (
    character_dubbing_runtime_readiness,
    create_same_character_profile,
    get_latest_character_profile,
    build_character_continuity_packet,
    create_multilingual_dubbing_profile,
    build_multilingual_dubbing_execution_packet,
)


def run():
    readiness = character_dubbing_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    character = create_same_character_profile({
        "tenant_id": "tenant_priority5_6_test",
        "brand_name": "Test Brand",
        "persona_name": "Primary Creator",
        "reference_asset_id": "asset_reference_test",
        "character_reference": "Consistent creator face and voice reference.",
        "same_face_required": True,
        "voice_style": "natural premium UGC voice",
    })

    assert character["success"] is True
    assert character["identity_lock"]["same_face_required"] is True
    assert character["continuity_rules"]["multi_scene_continuity_required"] is True
    assert character["internal_config_exposed"] is False

    latest = get_latest_character_profile("tenant_priority5_6_test", character["character_id"])
    assert latest["success"] is True

    continuity = build_character_continuity_packet(character, {
        "media_type": "ugc_video",
        "scenes": ["hook", "demo", "proof", "cta"],
    })
    assert continuity["success"] is True
    assert continuity["same_character_required"] is True
    assert continuity["scene_continuity"]["scene_count"] == 4
    assert continuity["provider_payload_additions"]["avoid_identity_drift"] is True

    dubbing = create_multilingual_dubbing_profile({
        "tenant_id": "tenant_priority5_6_test",
        "brand_name": "Test Brand",
        "source_language": "English",
        "target_languages": ["Arabic", "Spanish", "French"],
        "regional_context": "global",
        "tone": "natural, confident, premium",
        "lip_sync_required": True,
    })

    assert dubbing["success"] is True
    assert len(dubbing["target_languages"]) == 3
    assert dubbing["voice_rules"]["localise_idioms"] is True
    assert dubbing["lip_sync_rules"]["lip_sync_required"] is True

    execution = build_multilingual_dubbing_execution_packet(
        dubbing,
        {"asset_id": "source_asset_test"},
        character,
    )

    assert execution["success"] is True
    assert execution["target_language_count"] == 3
    assert execution["language_packets"][0]["same_character_required"] is True
    assert execution["quality_requirements"]["minimum_translation_quality"] == 85
    assert execution["internal_config_exposed"] is False

    print("PRIORITY5_6_CHARACTER_DUBBING_RUNTIME_OK")


if __name__ == "__main__":
    run()
