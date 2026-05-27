
from backend.app.runtime.ai_media_management_delivery_runtime import (
    media_management_delivery_runtime_readiness,
    register_generation_queue_item,
    build_operator_generation_management_summary,
    build_provider_health_summary,
    mark_generation_for_retry,
    mark_generation_for_moderation,
    build_customer_safe_media_delivery_packet,
    build_customer_media_delivery_history,
)


def run():
    readiness = media_management_delivery_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    queue_item = register_generation_queue_item({
        "job_id": "media_job_priority7_8_test",
        "asset_id": "media_asset_priority7_8_test",
        "tenant_id": "tenant_priority7_8_test",
        "brand_name": "Test Brand",
        "media_type": "ugc_video",
        "provider": "runway",
        "status": "queued",
        "customer_safe_status": "Queued",
    })

    assert queue_item["success"] is True
    assert queue_item["internal_config_exposed"] is False
    assert queue_item["governance_preserved"] is True

    summary = build_operator_generation_management_summary("tenant_priority7_8_test")
    assert summary["success"] is True
    assert summary["queue_count"] >= 1
    assert summary["layout_changes"] is False

    health = build_provider_health_summary([
        {"provider": "runway", "configured": False, "missing_env": ["RUNWAY_API_KEY"], "capabilities": ["text_to_video"]},
        {"provider": "kling", "configured": True, "missing_env": [], "capabilities": ["image_to_video"]},
    ])
    assert health["success"] is True
    assert health["provider_count"] == 2
    assert health["ready_count"] == 1
    assert health["internal_config_exposed"] is False

    retry = mark_generation_for_retry(queue_item)
    assert retry["status"] == "retry_queued"
    assert retry["customer_safe_status"] == "Retrying"

    moderation = mark_generation_for_moderation(queue_item)
    assert moderation["status"] == "needs_review"
    assert moderation["moderation_status"] == "review_required"
    assert moderation["customer_visible"] is False

    delivery = build_customer_safe_media_delivery_packet({
        "tenant_id": "tenant_priority7_8_test",
        "asset_id": "media_asset_priority7_8_test",
        "job_id": "media_job_priority7_8_test",
        "media_type": "ugc_video",
        "customer_safe_status": "Ready for review",
        "delivery": {"secure_download_ready": True},
        "access": {
            "preview": {"expires_at": "2099-01-01T00:00:00+00:00"},
            "download": {"expires_at": "2099-01-01T00:15:00+00:00"},
        },
    })

    assert delivery["success"] is True
    assert delivery["white_label_ready"] is True
    assert delivery["tenant_isolated"] is True
    assert delivery["internal_config_exposed"] is False

    history = build_customer_media_delivery_history("tenant_priority7_8_test")
    assert history["success"] is True
    assert history["count"] >= 1
    assert history["white_label_ready"] is True

    print("PRIORITY7_8_MEDIA_MANAGEMENT_DELIVERY_RUNTIME_OK")


if __name__ == "__main__":
    run()
