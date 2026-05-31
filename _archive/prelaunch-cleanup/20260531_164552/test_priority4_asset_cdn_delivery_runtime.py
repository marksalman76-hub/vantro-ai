
from backend.app.runtime.ai_media_asset_cdn_delivery_runtime import (
    asset_cdn_delivery_runtime_readiness,
    persist_generated_asset_record,
    build_customer_safe_asset_delivery_packet,
    verify_signed_asset_access_packet,
    list_asset_history_for_tenant,
)


def run():
    readiness = asset_cdn_delivery_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    record = persist_generated_asset_record({
        "asset_id": "media_asset_priority4_test",
        "job_id": "media_job_priority4_test",
        "tenant_id": "tenant_priority4_test",
        "provider": "runway",
        "media_type": "ugc_video",
        "filename": "priority4-test.mp4",
    })

    assert record["success"] is True
    assert record["delivery"]["tenant_isolated"] is True
    assert record["delivery"]["signed_access_required"] is True
    assert record["cdn"]["public_bucket_allowed"] is False
    assert record["internal_config_exposed"] is False

    preview_check = verify_signed_asset_access_packet(record["access"]["preview"])
    assert preview_check["valid"] is True
    assert preview_check["governance_preserved"] is True

    delivery_packet = build_customer_safe_asset_delivery_packet(record)
    assert delivery_packet["success"] is True
    assert delivery_packet["preview"]["signed_access_ready"] is True
    assert delivery_packet["download"]["signed_access_ready"] is True
    assert delivery_packet["internal_config_exposed"] is False

    history = list_asset_history_for_tenant("tenant_priority4_test")
    assert history["success"] is True
    assert history["count"] >= 1

    print("PRIORITY4_ASSET_CDN_DELIVERY_RUNTIME_OK")


if __name__ == "__main__":
    run()
