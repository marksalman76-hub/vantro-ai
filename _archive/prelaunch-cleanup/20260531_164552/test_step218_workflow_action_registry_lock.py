from backend.app.approval.owner_approval_gateway import (
    AUTONOMOUS_ALLOWED_ACTIONS,
    APPROVAL_REQUIRED_ACTIONS,
    OwnerApprovalGateway,
)
from backend.app.workflows.ecommerce_workflow_engine import EcommerceWorkflowEngine

checks = {}

workflow_engine = EcommerceWorkflowEngine()
approval_gateway = OwnerApprovalGateway()

workflow_packet = workflow_engine.create_packet(
    tenant_id="client_step203_001",
    workflow_stage="store_creation",
    requested_agent="product_copywriting_agent",
    task="Step 218 workflow registry lock.",
    region="Global",
    language="English",
    currency="USD",
)

approval_decision = approval_gateway.evaluate_action(
    action_type="product_copy_generation",
    owner_approved=True,
)

checks["store_creation_workflow_accepted"] = workflow_packet.blocked_reason is None
checks["store_creation_client_safe"] = workflow_packet.client_safe is True
checks["product_copy_generation_autonomous_registered"] = "product_copy_generation" in AUTONOMOUS_ALLOWED_ACTIONS
checks["product_copy_generation_approved"] = approval_decision.approved is True
checks["product_copy_generation_status_valid"] = approval_decision.status == "autonomous_allowed"

checks["spend_actions_still_owner_gated"] = all(action in APPROVAL_REQUIRED_ACTIONS for action in [
    "increase_ad_spend",
    "change_campaign_budget",
    "scale_campaign",
    "launch_paid_campaign",
    "paid_influencer_collaboration",
    "usage_rights_contract",
])

blocked_decision = approval_gateway.evaluate_action(
    action_type="launch_paid_campaign",
    owner_approved=False,
)

approved_decision = approval_gateway.evaluate_action(
    action_type="launch_paid_campaign",
    owner_approved=True,
)

checks["paid_campaign_blocked_without_owner"] = blocked_decision.approved is False
checks["paid_campaign_approved_with_owner"] = approved_decision.approved is True

print("STEP_218_WORKFLOW_ACTION_REGISTRY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_218_WORKFLOW_ACTION_REGISTRY_LOCK_OK")