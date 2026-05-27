import os

from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge
from backend.app.runtime.provider_connector_registry import execute_provider_action


def main():
    original_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        openai_ready = execute_provider_action(
            provider_key="openai",
            action_type="marketing_campaign_execution",
            payload={"business": "Quality bridge test", "goal": "Verify quality loop"},
            capability="text",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        runtime_ready = execute_safe_generation_via_provider_bridge(
            action_type="marketing_campaign_execution",
            payload={"business": "Runtime quality bridge", "goal": "Verify runtime quality loop"},
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
            preferred_provider="openai",
        )

        image_ready = execute_provider_action(
            provider_key="image_provider",
            action_type="image_generation",
            payload={"brief": "Premium product image"},
            capability="image",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        blocked = execute_safe_generation_via_provider_bridge(
            action_type="scale_campaign",
            payload={"budget_increase": 1000},
            tenant_id="client_test",
            actor_role="customer",
            preferred_provider="openai",
        )

        print("QUALITY_LOOP_PROVIDER_BRIDGE_TEST")
        print("openai_status", openai_ready["status"])
        print("openai_quality_loop", openai_ready.get("quality_loop_applied"))
        print("openai_quality_status", openai_ready.get("quality", {}).get("status"))
        print("openai_finalisation", openai_ready.get("finalisation_status"))
        print("openai_retry_decision", openai_ready.get("quality_retry_decision", {}).get("decision"))
        print("runtime_bridge_status", runtime_ready.get("runtime_bridge_status"))
        print("runtime_quality_loop", runtime_ready.get("quality_loop_applied"))
        print("image_quality_loop", image_ready.get("quality_loop_applied"))
        print("image_finalisation", image_ready.get("finalisation_status"))
        print("blocked_status", blocked["status"])
        print("blocked_attempted", blocked["provider_execution_attempted"])
        print("governance", runtime_ready["governance_preserved"])

        assert openai_ready["success"] is True
        assert openai_ready["status"] == "provider_action_ready"
        assert openai_ready["quality_loop_applied"] is True
        assert "quality" in openai_ready
        assert "quality_retry_decision" in openai_ready
        assert openai_ready["client_secret_exposure"] is False

        assert runtime_ready["success"] is True
        assert runtime_ready["runtime_bridge_status"] == "provider_registry_routed"
        assert runtime_ready["quality_loop_applied"] is True
        assert runtime_ready["governance_preserved"] is True

        assert image_ready["success"] is True
        assert image_ready["quality_loop_applied"] is True
        assert "quality" in image_ready

        assert blocked["success"] is False
        assert blocked["status"] == "owner_approval_required"
        assert blocked["provider_execution_attempted"] is False

        print("QUALITY_LOOP_PROVIDER_BRIDGE_OK")

    finally:
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key


if __name__ == "__main__":
    main()
