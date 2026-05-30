from backend.app.runtime.queue_isolation_policy import (
    classify_workload,
    get_queue_policy,
    export_queue_isolation_snapshot,
    redis_activation_required,
    live_external_execution_enabled_by_default,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    cases = {
        "run_agent": "client_agent_execution",
        "openai_live_generation": "provider_generation",
        "crm_task_created": "external_integration_action",
        "email_draft_created": "external_integration_action",
        "calendar_event_created": "external_integration_action",
        "weekly_report": "reporting",
        "dead_letter_retry": "retry_reconciliation",
        "admin_audit": "admin_internal",
    }

    for action, expected in cases.items():
        assert_equal(classify_workload(action), expected, action)

    provider = get_queue_policy("openai_live_generation")
    assert_equal(provider.requires_owner_approval, True, "provider owner approval")
    assert_equal(provider.live_external_safe_default, False, "provider live default disabled")

    integration = get_queue_policy("crm_task_created")
    assert_equal(integration.requires_owner_approval, True, "integration owner approval")
    assert_equal(integration.live_external_safe_default, False, "integration live default disabled")

    client = get_queue_policy("run_agent")
    assert_equal(client.requires_owner_approval, False, "client normal execution approval")
    assert_equal(client.live_external_safe_default, True, "client normal execution safe")

    assert_equal(redis_activation_required(), True, "redis activation required")
    assert_equal(live_external_execution_enabled_by_default(), False, "live external default")

    snapshot = export_queue_isolation_snapshot()
    required = [
        "client_agent_execution",
        "provider_generation",
        "external_integration_action",
        "reporting",
        "retry_reconciliation",
        "admin_internal",
    ]
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise AssertionError(f"Missing queue policies: {missing}")

    print("QUEUE_ISOLATION_POLICY_TEST_PASSED")
    print("Queue groups:", ", ".join(sorted(snapshot.keys())))


if __name__ == "__main__":
    main()
