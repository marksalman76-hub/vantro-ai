from backend.app.runtime.direct_media_provider_execution_runtime import (
    build_universal_complete_media_plan,
    universal_complete_media_status,
    start_universal_complete_media_workflow,
)


def test_universal_complete_media_status():
    status = universal_complete_media_status()
    assert status["success"] is True, status
    assert status["universal_not_ecommerce_only"] is True, status
    assert "avatar_likeness" in status["supported_controls"], status
    assert "facial_features" in status["supported_controls"], status
    assert "ethnicity_or_cultural_appearance" in status["supported_controls"], status
    assert status["credential_values_exposed"] is False, status


def test_universal_complete_media_plan_controls():
    plan = build_universal_complete_media_plan({
        "prompt": "Create a cinematic fitness coaching reel.",
        "language": "Spanish",
        "age_range": "adult",
        "gender_presentation": "male",
        "ethnicity_or_cultural_appearance": "Mediterranean appearance",
        "avatar_likeness": "ultra-human realistic presenter",
        "facial_features": "strong jawline, expressive eyes",
        "expressions": "confident and encouraging",
        "duration_seconds": 5,
    })
    assert plan["success"] is True, plan
    assert plan["quality_requirements"]["universal_not_ecommerce_only"] is True, plan
    assert plan["quality_requirements"]["natural_non_robotic_audio"] is True, plan
    assert plan["quality_requirements"]["audio_video_synchronisation_required"] is True, plan
    assert "Spanish" in plan["voice_prompt"], plan["voice_prompt"]
    assert "ultra-human realistic presenter" in plan["visual_prompt"], plan["visual_prompt"]
    assert "strong jawline" in plan["visual_prompt"], plan["visual_prompt"]


def test_universal_complete_media_owner_gate():
    result = start_universal_complete_media_workflow({
        "prompt": "Create a short media file.",
        "owner_approved": False,
    })
    assert result["status"] == "blocked_owner_approval_required", result
    assert result["credential_values_exposed"] is False, result


def test_universal_complete_media_prompt_required():
    result = start_universal_complete_media_workflow({
        "owner_approved": True,
    })
    assert result["status"] == "blocked_missing_prompt", result
    assert result["credential_values_exposed"] is False, result


if __name__ == "__main__":
    test_universal_complete_media_status()
    test_universal_complete_media_plan_controls()
    test_universal_complete_media_owner_gate()
    test_universal_complete_media_prompt_required()
    print("UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_TEST_PASSED")
