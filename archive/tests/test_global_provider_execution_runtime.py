
from backend.app.runtime.global_provider_execution_runtime import (
    global_provider_execution_readiness,
    get_agent_capabilities,
    build_global_provider_chain,
    build_global_provider_execution_packet,
)


def run():
    readiness = global_provider_execution_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["scope"] == "platform_wide_multi_agent"
    assert readiness["agent_count"] >= 20
    assert readiness["credential_values_exposed"] is False

    for agent_id in [
        "ugc_creative_agent",
        "product_image_agent",
        "website_landing_apps_agent",
        "paid_ads_agent",
        "crm_ai_agent",
        "customer_support_agent",
        "analytics_optimisation_agent",
    ]:
        caps = get_agent_capabilities(agent_id)
        assert caps["success"] is True
        assert caps["capability_count"] >= 1

    route = build_global_provider_chain("product_image_agent", {
        "tenant_id": "tenant_test",
        "workflow_stage": "product_image_direction",
        "action_type": "create_product_image_brief",
        "task": "Create premium product image direction",
    })
    assert route["success"] is True
    assert "openai" in route["provider_chain"]
    assert any(provider in route["provider_chain"] for provider in ["replicate", "runway"])

    packet = build_global_provider_execution_packet({
        "tenant_id": "tenant_test",
        "requested_agent": "website_landing_apps_agent",
        "workflow_stage": "website_landing_page",
        "action_type": "create_landing_page_brief",
        "task": "Create a landing page brief",
    })
    assert packet["success"] is True
    assert packet["scope"] == "platform_wide_multi_agent"
    assert packet["applies_to_all_agents"] is True
    assert packet["credential_values_exposed"] is False
    assert packet["governance_preserved"] is True

    print("GLOBAL_PROVIDER_EXECUTION_RUNTIME_OK")


if __name__ == "__main__":
    run()
