
from backend.app.runtime.external_action_readiness_classifier import classify_external_action_readiness

ready = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email", "crm", "calendar"],
)
assert ready["external_action_ready"] is True
assert ready["route"] == "external_action_ready"

fallback = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email"],
)
assert fallback["external_action_ready"] is False
assert fallback["route"] == "internal_fallback_required"
assert "crm" in fallback["missing_connections"]
assert "calendar" in fallback["missing_connections"]

approval = classify_external_action_readiness(
    adapter="approval_gated_campaign_adapter",
    connected_integrations=["ads"],
    owner_approved=False,
)
assert approval["route"] == "owner_approval_required"

approved = classify_external_action_readiness(
    adapter="approval_gated_campaign_adapter",
    connected_integrations=["ads"],
    owner_approved=True,
)
assert approved["route"] == "external_action_ready"

print("EXTERNAL_ACTION_READINESS_CLASSIFIER_TEST_PASSED")
