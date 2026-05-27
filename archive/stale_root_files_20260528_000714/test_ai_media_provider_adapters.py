from backend.app.runtime.ai_media_provider_adapters import (
    ai_media_provider_adapters_readiness,
    execute_ai_media_provider_adapter,
    get_provider_adapter_status,
    list_ai_media_provider_adapter_results,
    prepare_provider_payload,
)


def main():
    readiness = ai_media_provider_adapters_readiness()
    assert readiness["status"] == "ready"
    assert readiness["provider_count"] >= 10
    assert readiness["layout_changes"] is False

    openai_status = get_provider_adapter_status("openai")
    assert openai_status["provider"] == "openai"
    assert "OPENAI_API_KEY" in openai_status["required_env"]

    unsupported = get_provider_adapter_status("unknown_provider")
    assert unsupported["status"] == "unsupported"

    prepared = prepare_provider_payload(
        provider="runway",
        media_type="video",
        prompt="Create a cinematic product video.",
        payload={"brand": "Demo Brand"},
    )
    assert prepared["status"] == "prepared"
    assert prepared["prepared_payload"]["internal_config_exposed"] is False

    safe_result = execute_ai_media_provider_adapter(
        provider="runway",
        media_type="video",
        prompt="Create a cinematic product video.",
        payload={"brand": "Demo Brand"},
        owner_approved=False,
        allow_external_execution=False,
    )
    assert safe_result["status"] == "prepared"
    assert safe_result["external_execution_performed"] is False

    risky = execute_ai_media_provider_adapter(
        provider="meta_ads",
        media_type="ad",
        prompt="increase spend and publish paid campaign",
        payload={"brand": "Demo Brand"},
        owner_approved=False,
        allow_external_execution=True,
    )
    assert risky["status"] == "pending_owner_approval"
    assert risky["external_execution_performed"] is False

    listed = list_ai_media_provider_adapter_results(limit=10)
    assert listed["count"] >= 2

    print("AI_MEDIA_PROVIDER_ADAPTERS_OK")


if __name__ == "__main__":
    main()
