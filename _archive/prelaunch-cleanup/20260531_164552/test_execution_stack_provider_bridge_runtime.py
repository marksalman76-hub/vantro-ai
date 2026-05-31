from backend.app.runtime.execution_stack import (
    execute_safe_generation_via_provider_bridge,
    runtime_provider_bridge_readiness,
)


def main():
    ready = runtime_provider_bridge_readiness()

    campaign = execute_safe_generation_via_provider_bridge(
        action_type="marketing_campaign_execution",
        payload={
            "business": "Runtime bridge test ecommerce brand",
            "goal": "Create governed campaign execution plan",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
        preferred_provider="openai",
    )

    image = execute_safe_generation_via_provider_bridge(
        action_type="image_generation",
        payload={
            "brief": "Premium ecommerce product image concept",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
    )

    blocked = execute_safe_generation_via_provider_bridge(
        action_type="scale_campaign",
        payload={
            "budget_increase": 1000,
        },
        tenant_id="client_test",
        actor_role="customer",
        preferred_provider="openai",
    )

    print("EXECUTION_STACK_PROVIDER_BRIDGE_RUNTIME_TEST")
    print("readiness_status", ready["status"])
    print("bridge_loaded", ready["bridge_loaded"])
    print("safe_campaign_supported", ready["safe_campaign_supported"])
    print("safe_image_supported", ready["safe_image_supported"])
    print("safe_video_supported", ready["safe_video_supported"])
    print("campaign_status", campaign["status"])
    print("campaign_runtime_bridge_status", campaign.get("runtime_bridge_status"))
    print("campaign_provider", campaign.get("provider_key"))
    print("campaign_governance", campaign["governance_preserved"])
    print("image_status", image["status"])
    print("image_capability", image.get("capability"))
    print("blocked_status", blocked["status"])
    print("blocked_execution", blocked["execution_status"])
    print("blocked_attempted", blocked["provider_execution_attempted"])
    print("blocked_governance", blocked["governance_preserved"])

    assert ready["status"] == "execution_stack_provider_bridge_ready"
    assert ready["bridge_loaded"] is True
    assert ready["safe_campaign_supported"] is True
    assert ready["safe_image_supported"] is True
    assert ready["safe_video_supported"] is True
    assert campaign["success"] is True
    assert campaign["status"] == "provider_action_ready"
    assert campaign["runtime_bridge_status"] == "provider_registry_routed"
    assert campaign["provider_key"] == "openai"
    assert campaign["governance_preserved"] is True
    assert image["success"] is True
    assert image["capability"] == "image"
    assert blocked["success"] is False
    assert blocked["status"] == "owner_approval_required"
    assert blocked["provider_execution_attempted"] is False
    assert blocked["governance_preserved"] is True

    print("EXECUTION_STACK_PROVIDER_BRIDGE_RUNTIME_OK")


if __name__ == "__main__":
    main()
