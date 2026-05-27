from backend.app.runtime.provider_connector_registry import (
    PROVIDER_CONNECTORS,
    action_requires_owner_approval,
    choose_provider_for_capability,
    execute_provider_action,
    list_provider_connectors,
    readiness,
)


def main():
    registry = list_provider_connectors(include_secret_status=True)
    ready = readiness()

    text_provider = choose_provider_for_capability("text", "openai")
    image_provider = choose_provider_for_capability("image")
    video_provider = choose_provider_for_capability("video")

    safe_action = execute_provider_action(
        provider_key="openai",
        action_type="marketing_campaign_execution",
        capability="text",
        payload={"brief": "Create governed ecommerce campaign plan."},
        actor_role="owner_admin",
        tenant_id="owner_admin_test",
    )

    blocked_spend = execute_provider_action(
        provider_key="openai",
        action_type="scale_campaign",
        capability="text",
        payload={"budget_increase": 500},
        actor_role="customer",
        tenant_id="client_test",
    )

    print("GLOBAL_PROVIDER_CONNECTOR_REGISTRY_TEST")
    print("provider_count", len(PROVIDER_CONNECTORS))
    print("registry_success", registry["success"])
    print("readiness_status", ready["status"])
    print("text_provider", text_provider)
    print("image_provider", image_provider)
    print("video_provider", video_provider)
    print("safe_action_status", safe_action["status"])
    print("safe_action_governance", safe_action["governance_preserved"])
    print("safe_action_secret_exposure", safe_action["client_secret_exposure"])
    print("blocked_spend_status", blocked_spend["status"])
    print("blocked_spend_execution", blocked_spend["execution_status"])
    print("blocked_spend_governance", blocked_spend["governance_preserved"])
    print("approval_rule_scale_campaign", action_requires_owner_approval("scale_campaign"))

    assert len(PROVIDER_CONNECTORS) >= 6
    assert registry["success"] is True
    assert ready["status"] == "global_provider_connector_registry_ready"
    assert text_provider == "openai"
    assert image_provider in {"openai", "gemini", "image_provider"}
    assert video_provider in {"gemini", "video_provider"}
    assert safe_action["success"] is True
    assert safe_action["provider_execution_attempted"] is False
    assert safe_action["governance_preserved"] is True
    assert safe_action["client_secret_exposure"] is False
    assert blocked_spend["success"] is False
    assert blocked_spend["status"] == "owner_approval_required"
    assert blocked_spend["provider_execution_attempted"] is False
    assert blocked_spend["governance_preserved"] is True

    print("GLOBAL_PROVIDER_CONNECTOR_REGISTRY_OK")


if __name__ == "__main__":
    main()
