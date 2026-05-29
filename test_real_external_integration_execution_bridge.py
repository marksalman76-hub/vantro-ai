
from backend.app.runtime.real_external_integration_execution_bridge import (
    execute_real_external_action,
)

crm_email_calendar = execute_real_external_action(
    adapter="stakeholder_interview_outreach_adapter",
    action_text="Conduct stakeholder interviews and create outreach follow-up tasks",
    tenant_id="tenant_test",
    connected_integrations=["crm", "email", "calendar"],
)

assert crm_email_calendar["success"] is True
assert crm_email_calendar["external_action_executed"] is True
assert "crm" in crm_email_calendar["external_calls"]
assert "email" in crm_email_calendar["external_calls"]
assert "calendar" in crm_email_calendar["external_calls"]

approval_block = execute_real_external_action(
    adapter="approval_gated_campaign_adapter",
    action_text="Launch paid campaign and increase budget",
    tenant_id="tenant_test",
    connected_integrations=["ads"],
    owner_approved=False,
)

assert approval_block["success"] is False
assert approval_block["blocked"] is True
assert approval_block["owner_approval_required"] is True

safe_no_integrations = execute_real_external_action(
    adapter="general_operational_task_adapter",
    action_text="Create healthcare implementation checklist",
    tenant_id="tenant_test",
    connected_integrations=[],
)

assert safe_no_integrations["success"] is True
assert safe_no_integrations["external_action_executed"] is False

print("REAL_EXTERNAL_INTEGRATION_EXECUTION_BRIDGE_TEST_PASSED")
