from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status


def test_full_provider_stack_visible():
    status = direct_media_provider_execution_status()
    assert status["success"] is True, status
    providers = {item["provider"]: item for item in status["provider_stack"]}
    for key in ["runway", "kling", "heygen", "elevenlabs", "replicate", "openai", "sync"]:
        assert key in providers, status
    assert providers["runway"]["direct_execution_enabled"] is True, providers["runway"]
    assert providers["elevenlabs"]["direct_execution_enabled"] is True, providers["elevenlabs"]
    assert providers["heygen"]["credential_values_exposed"] is False, providers["heygen"]
    assert status["credential_values_exposed"] is False, status


if __name__ == "__main__":
    test_full_provider_stack_visible()
    print("DIRECT_MEDIA_PROVIDER_STACK_VISIBILITY_TEST_PASSED")
