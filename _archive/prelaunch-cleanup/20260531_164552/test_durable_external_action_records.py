
from backend.app.runtime.durable_external_action_records import (
    record_external_actions,
    list_external_action_records,
    external_action_records_readiness,
)

deliverable = {
    "deliverable_id": "deliverable_test",
    "adapter": "stakeholder_interview_outreach_adapter",
    "actions_performed": [
        {
            "type": "crm_task_created",
            "status": "executed",
            "provider": "governed_crm_runtime",
            "task_id": "crm_task_test",
        },
        {
            "type": "email_draft_created",
            "status": "executed",
            "provider": "governed_email_runtime",
            "draft_id": "email_draft_test",
        },
        {
            "type": "calendar_event_created",
            "status": "executed",
            "provider": "governed_calendar_runtime",
            "event_id": "calendar_event_test",
        },
    ],
}

result = record_external_actions(
    tenant_id="tenant_test",
    execution_id="exec_test",
    packet_id="packet_test",
    assigned_agent="crm_ai_agent",
    deliverable=deliverable,
)

assert result["success"] is True
assert result["record_count"] == 3
assert result["records"][0]["provider_reference_id"] == "crm_task_test"

listed = list_external_action_records(tenant_id="tenant_test", limit=10)
assert listed["success"] is True
assert listed["count"] >= 3
assert any(item["provider_reference_id"] == "email_draft_test" for item in listed["records"])

ready = external_action_records_readiness()
assert ready["success"] is True

print("DURABLE_EXTERNAL_ACTION_RECORDS_TEST_PASSED")
