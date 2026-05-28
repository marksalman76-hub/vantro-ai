from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan, mark_outcome_plan_decision

sample = """
Immediate next actions
- Create a healthcare technology market research report.
- Develop a compliance checklist for healthcare client onboarding.
- Launch a lead generation campaign targeting healthcare CIOs.
- Prepare a CRM pipeline for pilot opportunities.
"""

plan = create_outcome_action_plan(
    outcome_text=sample,
    source_agent="marketing_specialist_agent",
    owner_approved=False,
)

assert plan["success"] is True
assert plan["action_count"] >= 3
assert plan["approval_summary"]["approval_required_count"] >= 1
assert plan["customer_safe"] is True
assert plan["credential_values_exposed"] is False
assert plan["external_action_performed"] is False

decision = mark_outcome_plan_decision(plan, "approved")
assert decision["success"] is True
assert decision["next_stage"] == "implementation_queue_ready"

print("OUTCOME_ACTION_EXECUTION_RUNTIME_TEST_PASSED")
print({
    "action_count": plan["action_count"],
    "approval_required_count": plan["approval_summary"]["approval_required_count"],
    "safe_auto_ready_count": plan["approval_summary"]["safe_auto_ready_count"],
    "decision_next_stage": decision["next_stage"],
})
