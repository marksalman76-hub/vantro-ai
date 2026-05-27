
from backend.app.runtime.real_provider_activation_layer import (
    real_provider_activation_readiness,
    provider_readiness,
    select_provider_for_media,
    real_provider_execution_gate,
    build_real_provider_activation_packet,
)


def run():
    readiness = real_provider_activation_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["credential_values_exposed"] is False
    assert readiness["governance_preserved"] is True
    assert "openai" in readiness["providers"]

    openai = provider_readiness("openai")
    assert openai["success"] is True
    assert openai["credential_values_exposed"] is False

    selection = select_provider_for_media("ugc video")
    assert selection["success"] is True
    assert selection["provider_chain"][0] in {"runway", "kling", "heygen", "replicate"}

    gate = real_provider_execution_gate("openai", {
        "tenant_id": "tenant_test",
        "agent_id": "ugc_creative_agent",
        "task": "test task",
    })
    assert gate["success"] is True
    assert gate["credential_values_exposed"] is False
    assert gate["internal_config_exposed"] is False

    packet = build_real_provider_activation_packet({
        "tenant_id": "tenant_test",
        "agent_id": "ugc_creative_agent",
        "task": "Generate UGC brief",
        "media_type": "ugc video",
    })
    assert packet["success"] is True
    assert packet["runtime"] == "real_provider_activation_layer"
    assert packet["credential_values_exposed"] is False
    assert packet["governance_preserved"] is True

    print("REAL_PROVIDER_ACTIVATION_LAYER_OK")


if __name__ == "__main__":
    run()
