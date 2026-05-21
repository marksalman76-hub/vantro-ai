from __future__ import annotations

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
