
from backend.app.runtime.global_real_provider_connector_layer import (
    global_real_provider_connector_readiness,
    classify_connector_family,
    build_global_connector_execution_packet,
)


def run():
    readiness = global_real_provider_connector_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["scope"] == "platform_wide_multi_agent"
    assert readiness["credential_values_exposed"] is False

    cases = [
        ("marketing_specialist_agent", "marketing_campaign", "create_ad_copy_brief", "llm_content"),
        ("crm_ai_agent", "crm_optimisation", "crm_recommendation", "business_execution"),
        ("website_landing_apps_agent", "website_landing_page", "create_landing_page_brief", "llm_content"),
        ("analytics_optimisation_agent", "analytics_optimisation", "analytics_report_generation", "llm_content"),
        ("product_image_agent", "product_image_direction", "create_product_image_brief", "media_generation"),
        ("customer_support_agent", "customer_support", "support_response_generation", "llm_content"),
    ]

    for agent, stage, action, expected_family in cases:
        payload = {
            "tenant_id": "tenant_test",
            "requested_agent": agent,
            "workflow_stage": stage,
            "action_type": action,
            "task": f"Test global connector for {agent}",
        }

        family = classify_connector_family(payload)
        assert family["success"] is True
        assert family["connector_family"] == expected_family

        packet = build_global_connector_execution_packet(payload)
        assert packet["success"] is True
        assert packet["scope"] == "platform_wide_multi_agent"
        assert packet["connector_contract"]["tenant_isolation_required"] is True
        assert packet["credential_values_exposed"] is False
        assert packet["governance_preserved"] is True

    print("GLOBAL_REAL_PROVIDER_CONNECTOR_LAYER_OK")


if __name__ == "__main__":
    run()
