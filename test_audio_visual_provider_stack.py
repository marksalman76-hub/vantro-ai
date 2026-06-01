
from backend.app.runtime.audio_visual_provider_stack import (
    full_provider_stack_status,
    provider_config_status,
    providers_for_agent,
    recommended_stack_for_task,
)

status = full_provider_stack_status()

assert status["success"] is True
assert status["provider_count"] == 6
assert status["credential_values_exposed"] is False

for key in ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]:
    provider = provider_config_status(key)
    assert provider["success"] is True
    assert provider["credential_values_exposed"] is False
    assert "required_env_keys" in provider

assert "runway" in providers_for_agent("ugc_creative_agent")
assert "elevenlabs" in providers_for_agent("ugc_creative_agent")
assert "openai" in providers_for_agent("product_image_agent")

recommendation = recommended_stack_for_task(
    "ugc_creative_agent",
    "Create UGC video with avatar and voiceover"
)

assert "heygen" in recommendation["recommended_order"]
assert "elevenlabs" in recommendation["recommended_order"]

print("AUDIO_VISUAL_PROVIDER_STACK_TEST_PASSED")
print(status)
