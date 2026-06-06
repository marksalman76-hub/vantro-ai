from backend.app.runtime.canonical_entitlement_activation_runtime import (
    activate_entitlement_once,
    evaluate_execution_entitlement,
    owner_admin_override_entitlement,
    validate_agent_selection,
    validate_package_downgrade,
)
from uuid import uuid4


def tenant(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def test_package_limits_enforced():
    result = validate_agent_selection(
        "starter",
        ["strategist_agent", "marketing_specialist_agent", "seo_agent", "email_reply_agent"],
    )
    assert result["activation_allowed"] is False
    assert result["over_limit"] is True


def test_activation_lock_enforced():
    tenant_id = tenant("test_entitlement_lock_tenant")
    first = activate_entitlement_once(
        tenant_id=tenant_id,
        package="starter",
        selected_agents=["strategist_agent", "marketing_specialist_agent"],
        actor_role="client",
        source="test",
    )
    assert first["success"] is True
    second = activate_entitlement_once(
        tenant_id=tenant_id,
        package="starter",
        selected_agents=["seo_agent"],
        actor_role="client",
        source="test",
    )
    assert second["success"] is False
    assert second["reason"] == "activation_locked"


def test_owner_admin_override_works():
    tenant_id = tenant("test_entitlement_owner_override_tenant")
    activate_entitlement_once(
        tenant_id=tenant_id,
        package="starter",
        selected_agents=["strategist_agent"],
        actor_role="client",
        source="test",
    )
    override = owner_admin_override_entitlement(
        tenant_id=tenant_id,
        package="growth",
        selected_agents=["strategist_agent", "marketing_specialist_agent", "seo_agent"],
        actor_role="owner_admin",
        source="test",
    )
    assert override["success"] is True
    assert "seo_agent" in override["entitlement"]["active_agents"]


def test_unentitled_agent_blocked():
    tenant_id = tenant("test_unentitled_agent_blocked_tenant")
    activate_entitlement_once(
        tenant_id=tenant_id,
        package="starter",
        selected_agents=["strategist_agent"],
        actor_role="client",
        source="test",
    )
    decision = evaluate_execution_entitlement(
        tenant_id=tenant_id,
        requested_agent="seo_agent",
        actor_role="client",
    )
    assert decision["execution_allowed"] is False
    assert decision["error"] == "requested_agent_not_activated"


def test_downgrade_enforcement():
    result = validate_package_downgrade(
        "business",
        "starter",
        ["strategist_agent", "marketing_specialist_agent", "seo_agent", "email_reply_agent"],
    )
    assert result["downgrade_allowed"] is False
    assert result["agents_to_deactivate_required"] == 1


if __name__ == "__main__":
    test_package_limits_enforced()
    test_activation_lock_enforced()
    test_owner_admin_override_works()
    test_unentitled_agent_blocked()
    test_downgrade_enforcement()
    print("CANONICAL_ENTITLEMENT_ACTIVATION_RUNTIME_PASSED")
