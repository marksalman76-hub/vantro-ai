from backend.app.runtime.ai_media_execution_router import (
    ai_media_execution_router_readiness,
    list_ai_media_router_results,
    route_ai_media_request,
)


def main():
    readiness = ai_media_execution_router_readiness()
    assert readiness["status"] == "ready"
    assert readiness["connects_creative_registry_to_provider_execution"] is True
    assert readiness["layout_changes"] is False

    prepared = route_ai_media_request(
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
        preferred_model="runway",
        live_keys_available=False,
        owner_approved=False,
        entitlement_active=True,
    )
    assert prepared["status"] == "prepared"
    assert prepared["selected_model"] == "runway"
    assert prepared["provider"] == "runway"
    assert prepared["execution_allowed"] is False
    assert prepared["provider_execution_packet"]["execution_allowed"] is False

    routed = route_ai_media_request(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="product image",
        objective="Create a premium product hero image",
        product_or_offer="Hydrating serum",
        target_platform="Shopify product page",
        region="Australia",
        requested_style="premium ecommerce studio image",
        brand_colours=["#111827", "#C8A96A"],
        preferred_model="openai_image",
        live_keys_available=True,
        owner_approved=True,
        entitlement_active=True,
    )
    assert routed["status"] == "routed"
    assert routed["execution_allowed"] is True
    assert routed["provider_execution_packet"]["provider"] == "openai"
    assert "creative_director_plan" in routed["provider_execution_packet"]["payload"]

    blocked = route_ai_media_request(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="image",
        objective="Create a premium image",
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_ai_media_router_results(tenant_id="tenant_test")
    assert listed["count"] >= 2

    print("AI_MEDIA_EXECUTION_ROUTER_OK")


if __name__ == "__main__":
    main()
