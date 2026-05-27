from backend.app.runtime.ai_media_prompt_template_pack import (
    ai_media_prompt_template_pack_readiness,
    list_ai_media_prompt_templates,
    list_rendered_ai_media_prompts,
    recommend_ai_media_prompt_template,
    render_ai_media_prompt_template,
)


def main():
    readiness = ai_media_prompt_template_pack_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_ugc_video_ads"] is True
    assert readiness["supports_avatar_lip_sync"] is True
    assert readiness["layout_changes"] is False

    templates = list_ai_media_prompt_templates()
    assert templates["count"] >= 8

    rec = recommend_ai_media_prompt_template(
        media_type="ugc video",
        target_platform="TikTok",
        objective="conversion ad",
    )
    assert rec["recommended_template_id"] == "ugc_video_ad"

    rendered = render_ai_media_prompt_template(
        tenant_id="tenant_test",
        template_id="ugc_video_ad",
        context={
            "brand_name": "Demo Brand",
            "product_or_offer": "Hydrating serum",
            "target_platform": "TikTok",
            "audience": "busy skincare buyers",
            "benefit": "hydrated-looking skin",
            "cta": "Shop now",
            "hook": "My skin looked dull until I tried this",
            "proof": "visible glow after application",
            "brand_style": "premium realistic creator ad",
            "brand_colours": ["#111827", "#C8A96A"],
            "region": "United States",
        },
    )
    assert rendered["status"] == "ready"
    assert "Demo Brand" in rendered["prompt"]
    assert "TikTok" in rendered["prompt"]

    missing = render_ai_media_prompt_template(
        tenant_id="tenant_test",
        template_id="avatar_lip_sync",
        context={"brand_name": "Demo Brand"},
    )
    assert missing["status"] == "needs_context"
    assert "character_reference" in missing["missing_fields"]

    listed = list_rendered_ai_media_prompts(tenant_id="tenant_test")
    assert listed["count"] >= 2

    print("AI_MEDIA_PROMPT_TEMPLATE_PACK_OK")


if __name__ == "__main__":
    main()
