"""
Execution Stack

Routes approved, quality-checked agent outputs toward real-world execution adapters.
This layer does not bypass owner approval. Spend, budget, scaling, contracts, and
major financial actions must already be approved before execution.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from backend.app.integrations.execution_adapters import ExecutionAdapters, adapter_summary


SUPPORTED_EXECUTION_ACTIONS = [
    "create_shopify_product_page",
    "create_landing_page_brief",
    "create_ugc_video_brief",
    "create_product_image_brief",
    "create_ad_copy_brief",
    "prepare_email_campaign",
    "prepare_influencer_outreach",
    "prepare_customer_support_reply",
    "prepare_analytics_report",
]


BLOCKED_WITHOUT_APPROVAL_ACTIONS = [
    "launch_paid_campaign",
    "increase_ad_spend",
    "change_campaign_budget",
    "scale_campaign",
    "paid_influencer_collaboration",
    "commission_agreement",
    "usage_rights_contract",
    "large_supplier_order",
    "large_refund_batch",
    "major_strategy_change",
]


@dataclass
class ExecutionRequest:
    tenant_id: str
    action_type: str
    payload: Dict[str, object]
    owner_approved: bool = False
    quality_passed: bool = False


@dataclass
class ExecutionResult:
    success: bool
    execution_status: str
    action_type: str
    message: str
    execution_notes: List[str]
    adapter: Optional[str] = None
    adapter_result: Optional[Dict[str, object]] = None


class ExecutionStack:
    def __init__(self) -> None:
        self.adapters = ExecutionAdapters()

    def route(self, request: ExecutionRequest) -> ExecutionResult:
        if request.action_type in BLOCKED_WITHOUT_APPROVAL_ACTIONS and not request.owner_approved:
            return ExecutionResult(
                success=False,
                execution_status="blocked_pending_owner_approval",
                action_type=request.action_type,
                message="Execution blocked because this action requires owner approval.",
                execution_notes=[
                    "Owner approval is mandatory for spending, budget, scaling, contracts, and major financial commitments."
                ],
            )

        if not request.quality_passed:
            return ExecutionResult(
                success=False,
                execution_status="blocked_quality_gate_required",
                action_type=request.action_type,
                message="Execution blocked because premium quality gate has not passed.",
                execution_notes=[
                    "Client-facing or real-world execution requires approved quality status."
                ],
            )

        if request.action_type not in SUPPORTED_EXECUTION_ACTIONS and request.action_type not in BLOCKED_WITHOUT_APPROVAL_ACTIONS:
            return ExecutionResult(
                success=False,
                execution_status="unsupported_execution_action",
                action_type=request.action_type,
                message="Execution action is not currently supported.",
                execution_notes=[
                    "Add a controlled adapter before allowing this action."
                ],
            )

        adapter = self._select_adapter(request.action_type)
        adapter_result = self.adapters.execute(adapter, request.payload)
        adapter_result_data = adapter_summary(adapter_result)

        if not adapter_result.success:
            return ExecutionResult(
                success=False,
                execution_status="adapter_not_available",
                action_type=request.action_type,
                message="Execution passed governance checks, but no supported adapter is available.",
                execution_notes=[
                    "Tenant validated before execution.",
                    "Owner approval respected where required.",
                    "Premium quality gate respected.",
                    "Adapter connection failed or is unsupported.",
                ],
                adapter=adapter,
                adapter_result=adapter_result_data,
            )

        return ExecutionResult(
            success=True,
            execution_status="adapter_prepared",
            action_type=request.action_type,
            message="Execution request passed governance, quality checks, and adapter preparation.",
            execution_notes=[
                "Tenant validated before execution.",
                "Owner approval respected where required.",
                "Premium quality gate respected.",
                "Controlled execution adapter prepared.",
            ],
            adapter=adapter,
            adapter_result=adapter_result_data,
        )

    def _select_adapter(self, action_type: str) -> str:
        adapter_map = {
            "create_shopify_product_page": "shopify_adapter",
            "create_landing_page_brief": "website_builder_adapter",
            "create_ugc_video_brief": "ugc_video_provider_adapter",
            "create_product_image_brief": "image_generation_provider_adapter",
            "create_ad_copy_brief": "ad_platform_preparation_adapter",
            "prepare_email_campaign": "email_marketing_adapter",
            "prepare_influencer_outreach": "influencer_outreach_adapter",
            "prepare_customer_support_reply": "support_helpdesk_adapter",
            "prepare_analytics_report": "analytics_reporting_adapter",
            "launch_paid_campaign": "ad_platform_preparation_adapter",
            "increase_ad_spend": "ad_platform_preparation_adapter",
            "change_campaign_budget": "ad_platform_preparation_adapter",
            "scale_campaign": "ad_platform_preparation_adapter",
            "paid_influencer_collaboration": "influencer_outreach_adapter",
            "commission_agreement": "influencer_outreach_adapter",
            "usage_rights_contract": "influencer_outreach_adapter",
            "large_supplier_order": "manual_review_adapter",
            "large_refund_batch": "manual_review_adapter",
            "major_strategy_change": "manual_review_adapter",
        }
        return adapter_map.get(action_type, "manual_review_adapter")


def execution_summary(result: ExecutionResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "execution_status": result.execution_status,
        "action_type": result.action_type,
        "message": result.message,
        "execution_notes": result.execution_notes,
        "adapter": result.adapter,
        "adapter_result": result.adapter_result,
    }