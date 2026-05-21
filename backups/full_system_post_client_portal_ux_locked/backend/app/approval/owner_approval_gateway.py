from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from backend.app.core.governance_execution_registry import (
    is_prohibited_autonomous_action,
    is_real_world_action_requiring_owner_approval,
    is_safe_generation_action_type,
)


@dataclass
class ApprovalDecision:
    action_type: str
    requires_owner_approval: bool
    approved: bool
    status: str
    reason: str


class OwnerApprovalGateway:
    def evaluate_action(self, action_type: str, owner_approved: bool = False) -> ApprovalDecision:
        action = str(action_type or "").strip()

        if is_prohibited_autonomous_action(action):
            return ApprovalDecision(
                action_type=action,
                requires_owner_approval=True,
                approved=False,
                status="rejected_prohibited_autonomous_action",
                reason="This action cannot be completed autonomously and requires explicit owner control.",
            )

        if is_safe_generation_action_type(action):
            return ApprovalDecision(
                action_type=action,
                requires_owner_approval=False,
                approved=True,
                status="approved_safe_generation",
                reason="Safe generation action approved by governance execution registry.",
            )

        if is_real_world_action_requiring_owner_approval(action):
            return ApprovalDecision(
                action_type=action,
                requires_owner_approval=True,
                approved=bool(owner_approved),
                status="approved_by_owner" if owner_approved else "awaiting_owner_approval",
                reason="Real-world action requires owner approval.",
            )

        if owner_approved:
            return ApprovalDecision(
                action_type=action,
                requires_owner_approval=True,
                approved=True,
                status="approved_by_owner",
                reason="Owner approved governed action.",
            )

        return ApprovalDecision(
            action_type=action,
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
