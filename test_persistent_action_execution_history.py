
from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
    list_action_execution_history,
    action_execution_history_readiness,
)

payload = {
    "execution_status": "autonomously_executed",
    "performed_actual_action": True,
    "deliverable": {
        "adapter": "stakeholder_interview_outreach_adapter",
        "actions_performed": [
            {"type": "email_draft_created", "status": "created"},
            {"type": "crm_task_created", "status": "created"},
        ],
    },
}

record = record_action_execution(
    tenant_id="tenant_test",
    packet_id="packet_test_001",
    assigned_agent="marketing_specialist_agent",
    execution_payload=payload,
)

assert record["performed_actual_action"] is True
assert record["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(record["actions_performed"]) == 2

history = list_action_execution_history(tenant_id="tenant_test", limit=10)
assert history["success"] is True
assert history["count"] >= 1
assert history["records"][0]["tenant_id"] == "tenant_test"

readiness = action_execution_history_readiness()
assert readiness["success"] is True

print("PERSISTENT_ACTION_EXECUTION_HISTORY_TEST_PASSED")
