from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status


def test_direct_media_provider_status_runtime_available():
    result = direct_media_provider_execution_status()
    assert result["success"] is True, result
    assert result["direct_media_provider_execution_ready"] is True, result
    assert result["credential_values_exposed"] is False, result
    assert "runway" in result["supported_video_providers"], result
    assert "elevenlabs" in result["supported_audio_providers"], result


if __name__ == "__main__":
    test_direct_media_provider_status_runtime_available()
    print("DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_TEST_PASSED")
