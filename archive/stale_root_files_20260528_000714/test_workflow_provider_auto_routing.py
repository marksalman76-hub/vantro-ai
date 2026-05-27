from backend.app.runtime.workflow_provider_auto_routing import (
    classify_workflow_provider_category,
    list_workflow_provider_routes,
    route_workflow_to_provider_bridge,
    workflow_provider_routing_readiness,
)


def main():
    readiness = workflow_provider_routing_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True
    assert readiness["owner_approval_required_for_spend_scaling_contracts"] is True

    assert classify_workflow_provider_category("send_email", {"provider": "gmail"}) == "email"
    assert classify_workflow_provider_category("create_shopify_product", {"task": "product draft"}) == "ecommerce"
    assert classify_workflow_provider_category("generate_ugc_video", {"task": "ugc avatar"}) == "video"

    routed = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_email_test",
        agent_id="email_reply_agent",
        action_type="send_email_draft",
        workflow_payload={"channel": "email", "task": "reply"},
        available_providers=["gmail"],
        entitlement_active=True,
    )
    assert routed["status"] == "routed"
    assert routed["provider_execution_packet"]["execution_allowed"] is True
    assert routed["provider_execution_packet"]["provider"] == "gmail"

    gated = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_ads_test",
        agent_id="marketing_specialist_agent",
        action_type="scale_campaign",
        workflow_payload={"provider": "meta_ads", "change_budget": True},
        available_providers=["meta_ads"],
        entitlement_active=True,
    )
    assert gated["status"] == "pending_owner_approval"
    assert gated["provider_execution_packet"]["execution_allowed"] is False
    assert gated["provider_execution_packet"]["owner_approval_required"] is True

    blocked = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_blocked_test",
        agent_id="crm_agent",
        action_type="create_crm_note",
        workflow_payload={"provider": "ghl"},
        available_providers=["ghl"],
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"
    assert blocked["provider_execution_packet"]["execution_allowed"] is False

    listed = list_workflow_provider_routes(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("WORKFLOW_PROVIDER_AUTO_ROUTING_OK")


if __name__ == "__main__":
    main()
