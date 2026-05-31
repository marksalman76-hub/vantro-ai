import os

from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge
from backend.app.runtime.provider_connector_registry import execute_provider_action


def main():
    original_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        missing_key = execute_provider_action(
            provider_key="openai",
            action_type="marketing_campaign_execution",
            payload={"business": "Missing key test", "goal": "Verify safe fallback"},
            capability="text",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        runtime_missing_key = execute_safe_generation_via_provider_bridge(
            action_type="marketing_campaign_execution",
            payload={"business": "Runtime missing key test", "goal": "Verify bridge fallback"},
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
            preferred_provider="openai",
        )

        blocked = execute_safe_generation_via_provider_bridge(
            action_type="scale_campaign",
            payload={"budget_increase": 1000},
            tenant_id="client_test",
            actor_role="customer",
            preferred_provider="openai",
        )

        print("REAL_OPENAI_PROVIDER_EXECUTION_PATH_TEST")
        print("missing_key_status", missing_key["status"])
        print("missing_key_attempted", missing_key["provider_execution_attempted"])
        print("missing_key_configured", missing_key["real_provider_configured"])
        print("missing_key_secret_exposure", missing_key["client_secret_exposure"])
        print("runtime_status", runtime_missing_key["status"])
        print("runtime_bridge_status", runtime_missing_key.get("runtime_bridge_status"))
        print("runtime_attempted", runtime_missing_key["provider_execution_attempted"])
        print("blocked_status", blocked["status"])
        print("blocked_execution", blocked["execution_status"])
        print("blocked_attempted", blocked["provider_execution_attempted"])

        assert missing_key["success"] is True
        assert missing_key["status"] == "provider_action_ready"
        assert missing_key["provider_execution_attempted"] is False
        assert missing_key["real_provider_configured"] is False
        assert missing_key["client_secret_exposure"] is False

        assert runtime_missing_key["success"] is True
        assert runtime_missing_key["status"] == "provider_action_ready"
        assert runtime_missing_key["runtime_bridge_status"] == "provider_registry_routed"
        assert runtime_missing_key["provider_execution_attempted"] is False

        assert blocked["success"] is False
        assert blocked["status"] == "owner_approval_required"
        assert blocked["provider_execution_attempted"] is False

        print("REAL_OPENAI_PROVIDER_EXECUTION_PATH_OK")

    finally:
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key


if __name__ == "__main__":
    main()
