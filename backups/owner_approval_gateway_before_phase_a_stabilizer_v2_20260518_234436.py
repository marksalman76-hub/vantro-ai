"""
Owner Approval Gateway

Hard-governs any action involving spend, budget changes, scaling,
contracts, major commitments, or strategy changes.
"""

from dataclasses import dataclass
from typing import Dict, List


APPROVAL_REQUIRED_ACTIONS: List[str] = [
    "increase_ad_spend",
    "change_campaign_budget",
    "scale_campaign",
    "launch_paid_campaign",
    "paid_influencer_collaboration",
    "commission_agreement",
    "usage_rights_contract",
    "large_product_seeding",
    "large_supplier_order",
    "large_refund_batch",
    "major_strategy_change",
    "package_override",
    "licence_override",
]


AUTONOMOUS_ALLOWED_ACTIONS: List[str] = [
    "product_research",
    "competitor_analysis",
    "brand_generation",
    "ugc_script_generation",
    "product_image_direction",
    "product_image_generation",
    "ad_copy_generation",
    "website_content_generation",
    "product_copy_generation",
    "influencer_shortlist",
    "influencer_outreach_draft",
    "low_risk_follow_up",
    "customer_support_reply",
    "analytics_report",
    "creative_refresh_recommendation",
    "workflow_log_update",
]


@dataclass
class ApprovalDecision:
    action_type: str
    requires_owner_approval: bool
    approved: bool
    status: str
    reason: str


class OwnerApprovalGateway:
    def evaluate_action(self, action_type: str, owner_approved: bool = False) -> ApprovalDecision:
        if action_type in APPROVAL_REQUIRED_ACTIONS:
            if owner_approved:
                return ApprovalDecision(
                    action_type=action_type,
                    requires_owner_approval=True,
                    approved=True,
                    status="approved",
                    reason="Owner approval confirmed.",
                )

            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=True,
                approved=False,
                status="paused_pending_owner_approval",
                reason="This action requires explicit owner approval before execution.",
            )

        if action_type in AUTONOMOUS_ALLOWED_ACTIONS:
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=False,
                approved=True,
                status="autonomous_allowed",
                reason="This action is allowed to run autonomously.",
            )

        return ApprovalDecision(
            action_type=action_type,
            requires_owner_approval=True,
            approved=False,
            status="rejected_unknown_action",
            reason="Unknown actions are rejected by default until owner approval rules are defined.",
        )


def approval_summary(decision: ApprovalDecision) -> Dict[str, object]:
    return {
        "action_type": decision.action_type,
        "requires_owner_approval": decision.requires_owner_approval,
        "approved": decision.approved,
        "status": decision.status,
        "reason": decision.reason,
    }