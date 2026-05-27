from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    select_cinematic_parameter_preset,
)


def main():
    ugc = run_shared_ai_media_creative_director({
        "agent_id": "ugc_video_agent",
        "brand_name": "UGC Brand",
        "product_name": "UGC Product",
        "objective": "premium UGC ad",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
    })["orchestration_packet"]["cinematic_parameter_preset"]

    assert ugc["preset_key"] == "premium_ugc_video"
    assert "9:16" in ugc["aspect_ratios"]
    assert ugc["provider_parameter_guidance"]["aspect_ratio_priority"] == "9:16"

    product = select_cinematic_parameter_preset(
        agent_id="product_image_agent",
        media_type="product image",
        objective="premium product photography",
        platform="website",
        language="English",
    )
    assert product["preset_key"] == "product_photography"

    luxury = select_cinematic_parameter_preset(
        agent_id="ad_creative_agent",
        media_type="video",
        objective="luxury cinematic ecommerce ad",
        platform="Instagram",
        language="English",
    )
    assert luxury["preset_key"] == "luxury_cinematic_ad"

    direct = select_cinematic_parameter_preset(
        agent_id="marketing_specialist_agent",
        media_type="video",
        objective="conversion direct response ad",
        platform="Meta",
        language="English",
    )
    assert direct["preset_key"] == "direct_response_ad"

    multilingual = select_cinematic_parameter_preset(
        agent_id="ugc_video_agent",
        media_type="ugc video dubbing",
        objective="multilingual ad variant",
        platform="TikTok",
        language="Arabic",
    )
    assert multilingual["preset_key"] == "multilingual_dubbing"

    print("AI_MEDIA_CINEMATIC_PARAMETER_PRESETS_OK")


if __name__ == "__main__":
    main()
