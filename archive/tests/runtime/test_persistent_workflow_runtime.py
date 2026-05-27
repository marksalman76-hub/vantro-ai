from backend.app.runtime.persistent_workflow_runtime import (
    advance_workflow,
    complete_workflow,
    create_workflow,
    fail_workflow,
    get_workflow,
    readiness,
)


def main():
    ready = readiness()

    workflow = create_workflow(
        workflow_id="test_safe_workflow_001",
        workflow_type="marketing_campaign_execution",
        payload={"business": "Workflow test brand", "goal": "Create campaign"},
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
        max_retries=2,
    )

    advanced = advance_workflow(
        workflow_id="test_safe_workflow_001",
        step_result={"provider_bridge": "ready"},
    )

    failed = fail_workflow(
        workflow_id="test_safe_workflow_001",
        error={"temporary_error": "provider timeout"},
    )

    completed = complete_workflow(
        workflow_id="test_safe_workflow_001",
        result={"final_status": "verified"},
    )

    blocked = create_workflow(
        workflow_id="test_blocked_workflow_001",
        workflow_type="scale_campaign",
        payload={"budget_increase": 1000},
        tenant_id="client_test",
        actor_role="customer",
    )

    blocked_advance = advance_workflow("test_blocked_workflow_001")

    fetched = get_workflow("test_safe_workflow_001")

    print("PERSISTENT_WORKFLOW_RUNTIME_TEST")
    print("readiness_status", ready["status"])
    print("workflow_status", workflow["status"])
    print("advanced_status", advanced["status"])
    print("advanced_step", advanced["current_step"])
    print("failed_status", failed["status"])
    print("failed_retry_count", failed["retry_count"])
    print("completed_status", completed["status"])
    print("blocked_status", blocked["status"])
    print("blocked_owner_approval", blocked["owner_approval_required"])
    print("blocked_advance_status", blocked_advance["status"])
    print("fetched_event_count", len(fetched["events"]))
    print("governance", completed["governance_preserved"])

    assert ready["status"] == "persistent_workflow_runtime_ready"
    assert workflow["status"] == "pending"
    assert advanced["status"] == "in_progress"
    assert advanced["current_step"] == 1
    assert failed["status"] == "retry_ready"
    assert failed["retry_count"] == 1
    assert completed["status"] == "completed"
    assert blocked["status"] == "blocked_pending_owner_approval"
    assert blocked["owner_approval_required"] is True
    assert blocked_advance["success"] is False
    assert blocked_advance["status"] == "blocked_pending_owner_approval"
    assert len(fetched["events"]) >= 4
    assert completed["governance_preserved"] is True

    print("PERSISTENT_WORKFLOW_RUNTIME_OK")


if __name__ == "__main__":
    main()
