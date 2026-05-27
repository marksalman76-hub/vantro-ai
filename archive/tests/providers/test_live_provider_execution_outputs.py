from backend.app.runtime.live_provider_execution_outputs import (
    execute_live_provider_packet,
    list_live_provider_executions,
    live_provider_execution_readiness,
)


def main():
    readiness = live_provider_execution_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    prepared = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_test",
        agent_id="email_reply_agent",
        provider="gmail",
        action_type="send_email_draft",
        payload={"subject": "Test", "body": "Prepared test email"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=False,
        entitlement_active=True,
    )
    assert prepared["status"] == "prepared"
    assert prepared["external_execution_performed"] is False
    assert prepared["provider_output"]["format"] == "email_packet"

    executed = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_openai_test",
        agent_id="marketing_specialist_agent",
        provider="openai",
        action_type="generate_campaign_copy",
        payload={"brand": "Demo Brand", "region": "Australia", "task": "campaign copy"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=True,
    )
    assert executed["status"] == "executed"
    assert executed["external_execution_performed"] is True
    assert executed["provider_output"]["format"] == "text"

    gated = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_ads_test",
        agent_id="marketing_specialist_agent",
        provider="meta_ads",
        action_type="scale_campaign",
        payload={"increase_ad_spend": True},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=True,
    )
    assert gated["status"] == "pending_owner_approval"
    assert gated["external_execution_performed"] is False

    blocked = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_blocked_test",
        agent_id="crm_agent",
        provider="ghl",
        action_type="create_note",
        payload={"note": "Test note"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_live_provider_executions(tenant_id="tenant_test")
    assert listed["count"] >= 4

    print("LIVE_PROVIDER_EXECUTION_OUTPUTS_OK")


if __name__ == "__main__":
    main()
