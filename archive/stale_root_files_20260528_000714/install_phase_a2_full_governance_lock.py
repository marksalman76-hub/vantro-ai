from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

approval_path = root / "backend" / "app" / "approval" / "owner_approval_gateway.py"
workflow_path = root / "backend" / "app" / "workflows" / "ecommerce_workflow_engine.py"

for path in [approval_path, workflow_path]:
    backup = backup_dir / f"{path.stem}_before_phase_a2_full_governance_lock_{timestamp}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

approval_path.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

workflow_path.write_text('''from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage


@dataclass
class EcommerceWorkflowPacket:
    tenant_id: str
    workflow_stage: str
    requested_agent: str
    task: str
    region: str
    language: str
    currency: str
    requires_owner_approval: bool
    client_safe: bool
    blocked_reason: str | None = None
    workflow_notes: List[str] = field(default_factory=list)


class EcommerceWorkflowEngine:
    def create_packet(
        self,
        tenant_id: str,
        workflow_stage: str,
        requested_agent: str,
        task: str,
        region: str = "Global",
        language: str = "English",
        currency: str = "USD",
    ) -> EcommerceWorkflowPacket:
        safe_stage = is_safe_generation_workflow_stage(workflow_stage)

        return EcommerceWorkflowPacket(
            tenant_id=tenant_id,
            workflow_stage=workflow_stage,
            requested_agent=requested_agent,
            task=task,
            region=region,
            language=language,
            currency=currency,
            requires_owner_approval=not safe_stage,
            client_safe=True,
            blocked_reason=None if safe_stage else "Unknown workflow stage. Owner approval or admin review required.",
            workflow_notes=[
                "Safe generation workflow accepted.",
                "Client-facing output must remain white-label safe.",
                "Premium quality gate required before client delivery.",
            ] if safe_stage else [
                "Rejected by default because the workflow stage is not recognised."
            ],
        )


def workflow_summary(packet: EcommerceWorkflowPacket) -> Dict[str, object]:
    return {
        "tenant_id": packet.tenant_id,
        "workflow_stage": packet.workflow_stage,
        "requested_agent": packet.requested_agent,
        "task": packet.task,
        "region": packet.region,
        "language": packet.language,
        "currency": packet.currency,
        "requires_owner_approval": packet.requires_owner_approval,
        "client_safe": packet.client_safe,
        "blocked_reason": packet.blocked_reason,
        "workflow_notes": packet.workflow_notes,
    }
''', encoding="utf-8")

print("PHASE_A2_FULL_GOVERNANCE_LOCK_INSTALLED")
print("Backups created in backups folder.")