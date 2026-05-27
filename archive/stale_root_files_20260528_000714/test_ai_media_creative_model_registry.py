from backend.app.runtime.ai_media_creative_model_registry import (
    ai_media_registry_readiness,
    create_ai_media_execution_packet,
    create_creative_director_plan,
    list_ai_media_execution_packets,
    list_ai_media_models,
    list_creative_director_plans,
)


def main():
    readiness = ai_media_registry_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_image_generation"] is True
    assert readiness["supports_video_generation"] is True
    assert readiness["supports_audio_generation"] is True
    assert readiness["supports_creative_director_layer"] is True

    models = list_ai_media_models()
    assert models["count"] >= 8

    plan = create_creative_director_plan(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="ugc video with voice",
        objective="Create a premium conversion ad for a skincare product",
        product_or_offer="Hydrating serum",
        target_platform="TikTok",
        region="United States",
        requested_style="cinematic realistic creator ad",
        brand_colours=["#111827", "#C8A96A"],
        character_reference="creator_reference_001",
        owner_approved=False,
    )
    assert plan["status"] == "planned"
    assert "runway" in plan["selected_models"] or "kling" in plan["selected_models"]
    assert plan["character_consistency"]["use_same_face_across_outputs"] is True
    assert plan["audio_layer"]["lip_sync_recommended"] is True

    packet = create_ai_media_execution_packet(
        tenant_id="tenant_test",
        plan_id=plan["plan_id"],
        selected_model=plan["selected_models"][0],
        prompt="Create a cinematic UGC ad with premium lighting and a clear product demonstration.",
        media_type="video",
        live_keys_available=False,
        owner_approved=False,
    )
    assert packet["status"] == "prepared"
    assert packet["execution_allowed"] is False

    ready_packet = create_ai_media_execution_packet(
        tenant_id="tenant_test",
        plan_id=plan["plan_id"],
        selected_model="openai_image",
        prompt="Create a premium product hero image with brand-consistent colours.",
        media_type="image",
        live_keys_available=True,
        owner_approved=True,
    )
    assert ready_packet["status"] == "ready_for_execution"
    assert ready_packet["execution_allowed"] is True

    listed_plans = list_creative_director_plans(tenant_id="tenant_test")
    assert listed_plans["count"] >= 1

    listed_packets = list_ai_media_execution_packets(tenant_id="tenant_test")
    assert listed_packets["count"] >= 2

    print("AI_MEDIA_CREATIVE_MODEL_REGISTRY_OK")


if __name__ == "__main__":
    main()
