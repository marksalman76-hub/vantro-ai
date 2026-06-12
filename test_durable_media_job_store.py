from backend.app.runtime.durable_media_job_store import get_media_job_store


def main():
    store = get_media_job_store()

    payload = {
        "prompt": "Create a 30 second cinematic epoxy flooring promo with voiceover.",
        "duration_seconds": 30,
        "output_type": "Complete video with voiceover",
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent", "ugc_creative_agent"],
        "human_mode": "Use client-uploaded face/likeness",
        "uploaded_likeness_asset_id": "asset_face_test_001",
        "explicit_likeness_consent": True,
        "gender_presentation": "client supplied",
        "age_range": "client supplied",
        "ethnicity_or_cultural_appearance": "client supplied",
        "expressions": "confident, warm, natural",
        "eye_contact": "direct to camera",
        "gestures": "natural hand gestures",
        "cinematic_style": "premium commercial",
        "camera_angles": "wide before shot, close roller detail, final reveal",
        "lighting": "bright showroom lighting",
        "voice_style": "natural, confident, non-robotic",
        "tone": "premium and trustworthy",
    }

    created = store.create_job(payload)
    assert created["job_id"]
    assert created["creative_controls"]["duration_seconds"] == 30
    assert created["creative_controls"]["human"]["human_mode"] == "Use client-uploaded face/likeness"
    assert created["creative_controls"]["human"]["explicit_likeness_consent"] is True
    assert created["credit_estimate"]["segment_count"] == 3
    assert created["credit_estimate"]["includes_audio"] is True

    updated = store.update_status(
        created["job_id"],
        "queued",
        progress={"stage": "queued", "percent": 5},
        event={"event": "queued_for_worker"},
    )
    assert updated["status"] == "queued"
    assert updated["progress"]["stage"] == "queued"

    asseted = store.add_asset(created["job_id"], {
        "asset_type": "final_video",
        "storage_backend": "local_dev",
        "storage_key": "test/final.mp4",
        "preview_url": "local://test/final.mp4",
    })
    assert len(asseted["assets"]) == 1

    loaded = store.get_job(created["job_id"])
    assert loaded["success"] is True
    assert loaded["status"] == "queued"
    assert loaded["credential_values_exposed"] is False

    listed = store.list_jobs(limit=5)
    assert listed["success"] is True
    assert listed["count"] >= 1

    print("DURABLE_MEDIA_JOB_STORE_TEST_PASSED")
    print("job_id:", created["job_id"])
    print("estimated_credits:", created["credit_estimate"]["estimated_credits"])
    print("segment_count:", created["credit_estimate"]["segment_count"])


if __name__ == "__main__":
    main()
