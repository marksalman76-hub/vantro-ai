"""
Ecommerce Workflow Engine

Creates controlled ecommerce workflow packets for agent execution.
This does not spend money or scale campaigns. Any spend/budget/scaling action
must be routed through the Owner Approval Gateway.
"""

from dataclasses import dataclass, field
from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage
from typing import Dict, List, Optional


WORKFLOW_STAGES = [
    "client_setup",
    "product_research",
    "brand_creation",
    "store_creation",
    "creative_production",
    "influencer_collaboration",
    "campaign_preparation",
    "customer_support",
    "analytics_optimisation",
    "reporting",
]


APPROVAL_GATED_STAGES = [
    "paid_campaign_launch",
    "budget_change",
    "campaign_scaling",
    "paid_influencer_collaboration",
    "supplier_commitment",
    "major_strategy_change",
]


@dataclass
class EcommerceWorkflowPacket:
    tenant_id: str
    workflow_stage: str
    requested_agent: str
    task: str
    region: str = "Global"
    language: str = "English"
    currency: str = "USD"
    requires_owner_approval: bool = False
    client_safe: bool = True
    blocked_reason: Optional[str] = None
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
        if workflow_stage not in WORKFLOW_STAGES and workflow_stage not in APPROVAL_GATED_STAGES:
            return EcommerceWorkflowPacket(
                tenant_id=tenant_id,
                workflow_stage=workflow_stage,
                requested_agent=requested_agent,
                task=task,
                region=region,
                language=language,
                currency=currency,
                requires_owner_approval=True,
                client_safe=True,
                blocked_reason="Unknown workflow stage. Owner approval or admin review required.",
                workflow_notes=["Rejected by default because the workflow stage is not recognised."],
            )

        requires_owner_approval = workflow_stage in APPROVAL_GATED_STAGES

        notes = [
            "Workflow packet created.",
            "Client-facing output must remain white-label safe.",
            "Premium quality gate required before client delivery.",
        ]

        if requires_owner_approval:
            notes.append("This stage requires owner approval before execution.")

        return EcommerceWorkflowPacket(
            tenant_id=tenant_id,
            workflow_stage=workflow_stage,
            requested_agent=requested_agent,
            task=task,
            region=region,
            language=language,
            currency=currency,
            requires_owner_approval=requires_owner_approval,
            client_safe=True,
            workflow_notes=notes,
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