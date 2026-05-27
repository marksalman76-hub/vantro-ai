from backend.app.runtime.cross_agent_workflow_orchestration import (
    can_head_agent_orchestrate,
    complete_cross_agent_task,
    create_cross_agent_orchestration,
    fail_cross_agent_task,
    get_cross_agent_orchestration,
    readiness,
)


def main():
    ready = readiness()

    orchestration = create_cross_agent_orchestration(
        orchestration_id="test_orchestration_001",
        workflow_id="test_orchestration_workflow_001",
        tenant_id="client_test",
        head_agent_id="head_agent",
        active_agent_count=3,
        objective={
            "workflow_type": "marketing_campaign_execution",
            "goal": "Create ecommerce campaign using specialist agents",
        },
        tasks=[
            {
                "task_id": "task_marketing_001",
                "assigned_agent_id": "marketing_specialist_agent",
                "task_type": "content_generation",
                "payload": {"brief": "Campaign angle"},
            },
            {
                "task_id": "task_email_001",
                "assigned_agent_id": "email_reply_agent",
                "task_type": "email_copy_generation",
                "payload": {"brief": "Launch email"},
            },
            {
                "task_id": "task_spend_001",
                "assigned_agent_id": "marketing_specialist_agent",
                "task_type": "scale_campaign",
                "payload": {"budget_increase": 1000},
            },
        ],
    )

    completed_one = complete_cross_agent_task(
        orchestration_id="test_orchestration_001",
        task_id="task_marketing_001",
        result={"output": "premium campaign angle"},
    )

    failed = fail_cross_agent_task(
        orchestration_id="test_orchestration_001",
        task_id="task_email_001",
        error={"temporary_error": "provider timeout"},
    )

    completed_two = complete_cross_agent_task(
        orchestration_id="test_orchestration_001",
        task_id="task_email_001",
        result={"output": "premium launch email"},
    )

    blocked_complete = complete_cross_agent_task(
        orchestration_id="test_orchestration_001",
        task_id="task_spend_001",
        result={"attempt": "should not complete"},
    )

    fetched = get_cross_agent_orchestration("test_orchestration_001")

    not_allowed = create_cross_agent_orchestration(
        orchestration_id="test_orchestration_blocked_001",
        workflow_id="test_orchestration_blocked_workflow_001",
        tenant_id="client_test",
        head_agent_id="marketing_specialist_agent",
        active_agent_count=1,
        objective={"workflow_type": "marketing_campaign_execution"},
        tasks=[],
    )

    print("CROSS_AGENT_WORKFLOW_ORCHESTRATION_TEST")
    print("readiness_status", ready["status"])
    print("can_head_agent", can_head_agent_orchestrate("head_agent", 3))
    print("cannot_single_agent", can_head_agent_orchestrate("head_agent", 1))
    print("orchestration_status", orchestration["status"])
    print("task_count", len(orchestration["tasks"]))
    print("completed_one_task_status", [t for t in completed_one["tasks"] if t["task_id"] == "task_marketing_001"][0]["status"])
    print("failed_orchestration_status", failed["status"])
    print("failed_task_status", [t for t in failed["tasks"] if t["task_id"] == "task_email_001"][0]["status"])
    print("completed_two_task_status", [t for t in completed_two["tasks"] if t["task_id"] == "task_email_001"][0]["status"])
    print("blocked_complete_status", blocked_complete["status"])
    print("blocked_complete_execution", blocked_complete.get("execution_status"))
    print("blocked_task_owner_approval", [t for t in fetched["tasks"] if t["task_id"] == "task_spend_001"][0]["owner_approval_required"])
    print("event_count", len(fetched["events"]))
    print("not_allowed_status", not_allowed["status"])
    print("governance", fetched["governance_preserved"])

    assert ready["status"] == "cross_agent_workflow_orchestration_ready"
    assert can_head_agent_orchestrate("head_agent", 3) is True
    assert can_head_agent_orchestrate("head_agent", 1) is False
    assert orchestration["success"] is True
    assert len(orchestration["tasks"]) == 3
    assert [t for t in orchestration["tasks"] if t["task_id"] == "task_spend_001"][0]["status"] == "blocked_pending_owner_approval"
    assert [t for t in completed_one["tasks"] if t["task_id"] == "task_marketing_001"][0]["status"] == "completed"
    assert failed["status"] == "requires_recovery"
    assert [t for t in failed["tasks"] if t["task_id"] == "task_email_001"][0]["status"] == "retry_ready"
    assert [t for t in completed_two["tasks"] if t["task_id"] == "task_email_001"][0]["status"] == "completed"
    assert blocked_complete["success"] is False
    assert blocked_complete["status"] == "blocked_pending_owner_approval"
    assert [t for t in fetched["tasks"] if t["task_id"] == "task_spend_001"][0]["owner_approval_required"] is True
    assert len(fetched["events"]) >= 4
    assert not_allowed["status"] == "head_agent_orchestration_not_allowed"
    assert fetched["governance_preserved"] is True

    print("CROSS_AGENT_WORKFLOW_ORCHESTRATION_OK")


if __name__ == "__main__":
    main()
