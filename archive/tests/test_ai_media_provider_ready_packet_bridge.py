from backend.app.runtime.provider_connector_registry import (
    extract_ai_media_provider_ready_packet,
    enrich_provider_payload_with_ai_media_packet,
)


def main():
    provider_packet = {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "execution_allowed": True,
        "manual_review_required": False,
        "primary_provider_slot": "video_generation_provider",
        "fallback_provider_slots": ["ugc_avatar_provider"],
        "provider_parameters": {"aspect_ratio_priority": "9:16"},
        "continuity_controls": {"same_face_required": True},
        "multilingual_controls": {"multilingual_required": True},
        "fallback_controls": {"fallback_enabled": True},
        "governance_controls": {"do_not_publish_without_governance": True},
        "quality_controls": {"premium_only": True},
    }

    payload = {
        "creative_direction": {
            "orchestration_packet": {
                "provider_ready_execution_packet": provider_packet
            }
        }
    }

    extracted = extract_ai_media_provider_ready_packet(payload)
    assert extracted["packet_type"] == "provider_ready_ai_media_execution_packet"

    enriched = enrich_provider_payload_with_ai_media_packet(payload)
    assert enriched["provider_payload_enriched"] is True
    assert enriched["provider_packet_type"] == "provider_ready_ai_media_execution_packet"
    assert enriched["provider_execution_allowed"] is True
    assert enriched["provider_primary_slot"] == "video_generation_provider"
    assert enriched["provider_parameters"]["aspect_ratio_priority"] == "9:16"
    assert enriched["provider_continuity_controls"]["same_face_required"] is True
    assert enriched["provider_multilingual_controls"]["multilingual_required"] is True
    assert enriched["provider_governance_controls"]["do_not_publish_without_governance"] is True
    assert enriched["provider_quality_controls"]["premium_only"] is True

    unchanged = enrich_provider_payload_with_ai_media_packet({"normal": "payload"})
    assert unchanged == {"normal": "payload"}

    print("AI_MEDIA_PROVIDER_READY_PACKET_BRIDGE_OK")


if __name__ == "__main__":
    main()
