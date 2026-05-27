from backend.app.runtime.governed_provider_execution import (
    capability_for_action,
    execute_governed_provider_action,
    is_safe_generation_action,
    readiness,
)


def main():
    ready = readiness()

    campaign = execute_governed_provider_action(
        action_type="marketing_campaign_execution",
        payload={
            "business": "Test ecommerce brand",
            "goal": "Generate premium campaign plan",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
        preferred_provider="openai",
    )

    image = execute_governed_provider_action(
        action_type="image_generation",
        payload={
            "brief": "Premium ecommerce product image concept",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
    )

    blocked = execute_governed_provider_action(
        action_type="scale_campaign",
        payload={
            "budget_increase": 500,
        },
        tenant_id="client_test",
        actor_role="customer",
        preferred_provider="openai",
    )

    ignored = execute_governed_provider_action(
        action_type="unknown_internal_action",
        payload={},
        tenant_id="client_test",
        actor_role="customer",
    )

    print("GOVERNED_PROVIDER_EXECUTION_BRIDGE_TEST")
    print("readiness_status", ready["status"])
    print("campaign_status", campaign["status"])
    print("campaign_bridge", campaign["bridge"])
    print("campaign_runtime_bridge_status", campaign["runtime_bridge_status"])
    print("campaign_provider", campaign["provider_key"])
    print("campaign_governance", campaign["governance_preserved"])
    print("image_capability", image["capability"])
    print("image_runtime_bridge_status", image["runtime_bridge_status"])
    print("blocked_status", blocked["status"])
    print("blocked_execution", blocked["execution_status"])
    print("blocked_attempted", blocked["provider_execution_attempted"])
    print("ignored_status", ignored["status"])
    print("safe_campaign", is_safe_generation_action("marketing_campaign_execution"))
    print("safe_scale_campaign", is_safe_generation_action("scale_campaign"))
    print("capability_video", capability_for_action("video_generation"))

    assert ready["status"] == "governed_provider_execution_bridge_ready"
    assert campaign["success"] is True
    assert campaign["bridge"] == "governed_provider_execution"
    assert campaign["runtime_bridge_status"] == "provider_registry_routed"
    assert campaign["provider_key"] == "openai"
    assert campaign["governance_preserved"] is True
    assert image["capability"] == "image"
    assert image["runtime_bridge_status"] == "provider_registry_routed"
    assert blocked["success"] is False
    assert blocked["status"] == "owner_approval_required"
    assert blocked["provider_execution_attempted"] is False
    assert ignored["success"] is False
    assert ignored["status"] == "not_routed_to_provider_registry"
    assert is_safe_generation_action("marketing_campaign_execution") is True
    assert is_safe_generation_action("scale_campaign") is False
    assert capability_for_action("video_generation") == "video"

    print("GOVERNED_PROVIDER_EXECUTION_BRIDGE_OK")


if __name__ == "__main__":
    main()
