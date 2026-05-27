
from backend.app.runtime.ai_media_provider_async_runtime import (
    provider_async_runtime_readiness,
    create_async_generation_job,
    poll_async_generation_job,
    cancel_async_generation_job,
    failover_async_generation_job,
    finalise_generated_asset_packet,
)


def run():
    readiness = provider_async_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert "runway" in readiness["providers"]
    assert readiness["governance_preserved"] is True

    job = create_async_generation_job({
        "tenant_id": "tenant_test",
        "media_type": "ugc video",
        "objective": "premium governed generation",
        "preferred_provider": "runway",
    })
    assert job["success"] is True
    assert job["active_provider"] == "runway"
    assert job["governance_preserved"] is True
    assert job["internal_config_exposed"] is False

    polled = poll_async_generation_job(job)
    assert "execution_state" in polled
    assert polled["governance_preserved"] is True

    failed_over = failover_async_generation_job(job, "provider_timeout")
    assert failed_over["execution_state"] in {"fallback_provider_selected", "fallback_provider_missing_key", "dead_letter_owner_review_required"}
    assert failed_over["governance_preserved"] is True

    cancelled = cancel_async_generation_job(job)
    assert cancelled["execution_state"] == "cancelled"

    asset = finalise_generated_asset_packet(job, {
        "status": "completed",
        "external_asset_reference": "provider_asset_test",
        "duration_seconds": 12,
    })
    assert asset["success"] is True
    assert asset["asset_status"] == "prepared_for_secure_delivery"
    assert asset["delivery"]["tenant_isolated"] is True
    assert asset["customer_safe_status"] == "Ready for review"

    print("PRIORITY2_3_PROVIDER_ASYNC_RUNTIME_OK")


if __name__ == "__main__":
    run()
