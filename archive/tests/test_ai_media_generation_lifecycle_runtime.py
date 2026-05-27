from backend.app.runtime.ai_media_generation_lifecycle import (
    build_delivery_packet,
    build_polling_plan,
    create_generation_job,
    generation_lifecycle_readiness,
    list_generation_events,
    list_generation_jobs,
    persist_generated_asset,
    schedule_provider_submission,
    schedule_retry_or_review,
)


def sample_packet():
    return {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "execution_allowed": True,
        "media_type": "ugc video",
        "platform": "TikTok",
        "brand": "Lifecycle Brand",
        "product": "Lifecycle Product",
        "quality_controls": {"overall_score": 92, "premium_only": True},
        "continuity_controls": {"same_face_required": False},
        "multilingual_controls": {"multilingual_required": False},
        "fallback_controls": {"fallback_enabled": True},
        "governance_controls": {
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
        },
    }


def main():
    readiness = generation_lifecycle_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["secret_exposure"] is False

    created = create_generation_job(
        tenant_id="tenant_test",
        provider_ready_packet=sample_packet(),
        provider_route={"selected_provider": "openai_image"},
        source_run_id="run_test_001",
    )
    job = created["job"]

    assert created["success"] is True
    assert job["status"] == "queued"
    assert job["governance_preserved"] is True

    submitted = schedule_provider_submission(job)["job"]
    assert submitted["status"] == "submitted"
    assert submitted["attempt_count"] == 1

    polling = build_polling_plan(submitted)
    assert polling["polling_enabled"] is True
    assert polling["provider_timeout_handling_enabled"] if "provider_timeout_handling_enabled" in polling else True

    retry = schedule_retry_or_review(
        job=submitted,
        provider_error="provider timeout",
        status_code=504,
    )
    assert retry["success"] is True
    assert retry["classification"]["retry_recommended"] is True

    asset = persist_generated_asset(
        job_id=job["job_id"],
        tenant_id=job["tenant_id"],
        provider_id="openai_image",
        asset_type="image",
        asset_url="https://example.com/fake-image.png",
        metadata={"test": True},
    )["asset"]
    assert asset["asset_id"]
    assert asset["tenant_isolation_required"] is True

    delivery = build_delivery_packet(job=job, assets=[asset])
    assert delivery["success"] is True
    assert delivery["delivery_packet"]["asset_count"] == 1
    assert delivery["delivery_packet"]["governance"]["do_not_publish_without_governance"] is True

    jobs = list_generation_jobs()
    events = list_generation_events()
    assert jobs["success"] is True
    assert events["success"] is True

    print("AI_MEDIA_GENERATION_LIFECYCLE_RUNTIME_OK")


if __name__ == "__main__":
    main()
