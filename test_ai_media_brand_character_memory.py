from backend.app.runtime.ai_media_brand_character_memory import (
    ai_media_brand_character_memory_readiness,
    enrich_ai_media_payload_with_memory,
    get_ai_media_memory_context,
    list_ai_media_memory,
    save_brand_memory,
    save_campaign_style_memory,
    save_character_memory,
)


def main():
    readiness = ai_media_brand_character_memory_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_brand_consistency"] is True
    assert readiness["supports_character_consistency"] is True
    assert readiness["layout_changes"] is False

    brand = save_brand_memory(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        brand_colours=["#111827", "#C8A96A"],
        typography_style="premium editorial sans-serif",
        visual_style="cinematic realistic ecommerce studio style",
        product_identity="Hydrating serum with clean premium skincare positioning",
        forbidden_styles=["cheap stock photo", "cartoon unless requested"],
        region_preferences={"United States": "direct-response tone"},
        platform_preferences={"TikTok": "fast hook and creator framing"},
    )
    assert brand["status"] == "saved"

    character = save_character_memory(
        tenant_id="tenant_test",
        character_name="Primary Creator",
        reference_id="creator_reference_001",
        face_consistency_notes="Use same face and similar styling across campaign assets.",
        voice_notes="Warm, confident, natural creator voice.",
        age_range="25-34",
        gender_presentation="female-presenting",
        ethnicity_or_regional_style="regionally adaptable",
        accent_or_language_style="US English by default",
        usage_rules=["Do not imply medical claims", "Keep expression realistic"],
    )
    assert character["character_memory"]["same_face_required"] is True

    campaign = save_campaign_style_memory(
        tenant_id="tenant_test",
        campaign_name="Hydrating Serum Launch",
        target_platform="TikTok",
        media_type="ugc video",
        style_rules=["Fast 2-second hook", "Close-up product texture shot", "Natural bathroom/vanity scene"],
        winning_hooks=["My skin looked dull until I tried this"],
        winning_visual_patterns=["before-after lighting shift", "handheld creator proof"],
        avoided_patterns=["overly polished corporate ad"],
        performance_notes="Creator-led product proof performs best.",
    )
    assert campaign["status"] == "saved"

    context = get_ai_media_memory_context(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        target_platform="TikTok",
        media_type="ugc video",
    )
    assert context["memory_context"]["brand_colours"] == ["#111827", "#C8A96A"]
    assert context["memory_context"]["same_face_required"] is True
    assert context["memory_context"]["winning_hooks"]

    enriched = enrich_ai_media_payload_with_memory(
        tenant_id="tenant_test",
        payload={
            "brand_name": "Demo Brand",
            "target_platform": "TikTok",
            "media_type": "ugc video",
            "product_or_offer": "Hydrating serum",
        },
    )
    assert enriched["status"] == "enriched"
    assert enriched["payload"]["brand_colours"] == ["#111827", "#C8A96A"]
    assert enriched["payload"]["character_reference"] == "creator_reference_001"

    listed = list_ai_media_memory(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("AI_MEDIA_BRAND_CHARACTER_MEMORY_OK")


if __name__ == "__main__":
    main()
