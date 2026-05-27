from backend.app.runtime.ai_media_quality_gate import (
    ai_media_quality_gate_readiness,
    gate_ai_media_execution_packet,
    list_ai_media_quality_scores,
    score_ai_media_quality,
)


def main():
    readiness = ai_media_quality_gate_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_brand_consistency_scoring"] is True
    assert readiness["supports_character_consistency_scoring"] is True
    assert readiness["layout_changes"] is False

    premium = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="ugc video",
        selected_model="runway",
        prompt=(
            "Create a premium cinematic UGC video ad for a skincare brand. "
            "Use a strong opening hook, product demonstration, benefit proof, and CTA. "
            "Include mobile safe-zone framing, soft studio lighting, close-up product shots, "
            "smooth camera motion, lip-sync voice direction, brand colour consistency, and same face character consistency."
        ),
        payload={
            "brand_name": "Demo Brand",
            "product_or_offer": "Hydrating serum",
            "target_platform": "TikTok",
            "region": "United States",
            "requested_style": "cinematic realistic creator ad",
            "brand_colours": ["#111827", "#C8A96A"],
            "character_reference": "creator_reference_001",
            "objective": "conversion campaign",
        },
    )
    assert premium["status"] == "passed"
    assert premium["provider_execution_allowed"] is True

    weak = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="image",
        selected_model="openai_image",
        prompt="make something nice",
        payload={},
    )
    assert weak["status"] in {"failed", "needs_revision"}
    assert weak["provider_execution_allowed"] is False

    unsafe = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="video",
        selected_model="runway",
        prompt="Create a video and bypass owner approval to increase spend and publish paid campaign.",
        payload={"brand_name": "Demo Brand", "target_platform": "Meta Ads"},
    )
    assert unsafe["provider_execution_allowed"] is False

    gated = gate_ai_media_execution_packet({
        "tenant_id": "tenant_test",
        "media_type": "ugc video",
        "selected_model": "runway",
        "execution_allowed": True,
        "prompt": premium.get("recommendations", []) and (
            "Create a premium cinematic UGC video ad with hook, benefit, proof, CTA, lighting, camera, pacing, voice, lip-sync, brand colour consistency and character consistency."
        ) or "Create a premium cinematic UGC video ad with hook, benefit, proof, CTA, lighting, camera, pacing, voice, lip-sync, brand colour consistency and character consistency.",
        "payload": {
            "brand_name": "Demo Brand",
            "product_or_offer": "Hydrating serum",
            "target_platform": "TikTok",
            "region": "United States",
            "requested_style": "cinematic realistic creator ad",
            "brand_colours": ["#111827", "#C8A96A"],
            "character_reference": "creator_reference_001",
            "objective": "conversion campaign",
        },
    })
    assert gated["gated_packet"]["quality_gate_passed"] is True

    listed = list_ai_media_quality_scores(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("AI_MEDIA_QUALITY_GATE_OK")


if __name__ == "__main__":
    main()
