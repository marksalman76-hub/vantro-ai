
from backend.app.runtime.action_adapter_execution_layer import (
    classify_action_adapter,
    execute_action_adapter,
)

interview_packet = {
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
}
assert classify_action_adapter(interview_packet) == "stakeholder_interview_outreach_adapter"
interview_result = execute_action_adapter(interview_packet, tenant_id="tenant_test")
assert interview_result["performed_actual_action"] is True
assert interview_result["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(interview_result["actions_performed"]) >= 2

competitor_packet = {
    "implementation_action": "Analyze competitor positioning and identify white space",
}
competitor_result = execute_action_adapter(competitor_packet)
assert competitor_result["adapter"] == "competitor_research_adapter"
assert competitor_result["performed_actual_action"] is True

content_packet = {
    "implementation_action": "Generate thought leadership content series including white papers and webinars",
}
content_result = execute_action_adapter(content_packet)
assert content_result["adapter"] == "content_asset_creation_adapter"
assert content_result["performed_actual_action"] is True

risky_packet = {
    "implementation_action": "Launch paid campaign and increase budget",
}
risky_result = execute_action_adapter(risky_packet)
assert risky_result["performed_actual_action"] is False
assert risky_result["owner_approval_required"] is True
assert risky_result["execution_status"] == "blocked_owner_approval_required"

print("ACTION_ADAPTER_EXECUTION_LAYER_TEST_PASSED")
