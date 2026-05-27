from backend.app.runtime.ai_media_brand_character_memory import (
    save_brand_memory,
    save_campaign_style_memory,
    save_character_memory,
)
from backend.app.runtime.ai_media_end_to_end_pipeline import (
    ai_media_end_to_end_pipeline_readiness,
    list_ai_media_pipeline_runs,
    run_ai_media_end_to_end_pipeline,
)


def main():
    readiness = ai_media_end_to_end_pipeline_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_memory_to_template_to_provider_packet"] is True
    assert readiness["layout_changes"] is False

    save_brand_memory(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        brand_colours=["#111827", "#C8A96A"],
        visual_style="cinematic realistic ecommerce studio style",
        product_identity="Premium skincare serum",
    )

    save_character_memory(
        tenant_id="tenant_pipeline",
        character_name="Primary Creator",
        reference_id="creator_reference_pipeline",
        face_consistency_notes="Keep same face across assets.",
        voice_notes="Warm confident creator voice.",
    )

    save_campaign_style_memory(
        tenant_id="tenant_pipeline",
        campaign_name="Serum Launch",
        target_platform="TikTok",
        media_type="ugc video",
        style_rules=["fast hook", "close-up product shot", "natural creator scene"],
        winning_hooks=["My skin looked dull until I tried this"],
        winning_visual_patterns=["texture close-up", "creator proof shot"],
    )

    result = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        media_type="ugc video",
        objective="Create a premium conversion ad for skincare buyers",
        product_or_offer="Hydrating serum",
        target_platform="TikTok",
        region="United States",
        audience="busy skincare buyers",
        benefit="hydrated-looking skin",
        cta="Shop now",
        requested_style="cinematic realistic creator ad",
        preferred_provider="runway",
        owner_approved=True,
        entitlement_active=True,
        live_keys_available=False,
        context={
            "hook": "My skin looked dull until I tried this",
            "proof": "visible glow after application",
        },
    )

    assert result["status"] in {"prepared", "ready_for_provider_execution"}
    assert result["memory_enrichment"]["status"] == "enriched"
    assert result["rendered_prompt"]["status"] == "ready"
    assert result["quality_gate"]["provider_execution_allowed"] is True
    assert result["multi_provider_packet"]["active_provider"] == "runway"
    assert result["adapter_payload"]["status"] == "prepared"
    assert result["layout_changes"] is False

    blocked = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        media_type="image",
        objective="Create image",
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_ai_media_pipeline_runs(tenant_id="tenant_pipeline")
    assert listed["count"] >= 1

    print("AI_MEDIA_END_TO_END_PIPELINE_OK")


if __name__ == "__main__":
    main()
