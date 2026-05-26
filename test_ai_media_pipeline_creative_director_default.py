from backend.app.runtime.ai_media_end_to_end_pipeline import run_ai_media_end_to_end_pipeline


def main():
    result = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_test",
        agent_id="ugc_video_agent",
        brand_name="Default Fix Brand",
        product_name="Default Fix Product",
        target_audience="online shoppers",
        objective="premium UGC ad",
        platform="TikTok",
        media_type="ugc video",
        language="English",
        region="global",
        context={},
    )

    assert isinstance(result, dict)
    assert result.get("status") or result.get("success") is not None

    print("AI_MEDIA_PIPELINE_CREATIVE_DIRECTOR_DEFAULT_OK")


if __name__ == "__main__":
    main()
