"""
Provider Orchestrator

Provider-flexible orchestration layer for real-world execution.
This keeps the platform premium, white-label, and not locked to one provider.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ProviderRouteRequest:
    tenant_id: str
    provider_category: str
    task_type: str
    region: str
    language: str
    payload: Dict[str, object]
    owner_approved: bool = False


@dataclass
class ProviderRouteResult:
    success: bool
    provider_category: str
    selected_provider: Optional[str]
    execution_mode: str
    provider_ready: bool
    message: str
    quality_requirements: List[str]
    approval_required: bool


class ProviderOrchestrator:
    def route(self, request: ProviderRouteRequest) -> ProviderRouteResult:
        selected_provider = self._select_provider(request)

        approval_required = request.task_type in {
            "paid_campaign_launch",
            "campaign_scaling",
            "budget_change",
            "paid_creator_collaboration",
            "usage_rights_contract",
        }

        if approval_required and not request.owner_approved:
            return ProviderRouteResult(
                success=False,
                provider_category=request.provider_category,
                selected_provider=selected_provider,
                execution_mode="blocked_pending_owner_approval",
                provider_ready=False,
                message="Provider execution blocked because owner approval is required.",
                quality_requirements=self._quality_requirements(request.provider_category),
                approval_required=True,
            )

        return ProviderRouteResult(
            success=True,
            provider_category=request.provider_category,
            selected_provider=selected_provider,
            execution_mode="provider_route_prepared",
            provider_ready=False,
            message="Provider route prepared. Real provider credentials/API connection not enabled yet.",
            quality_requirements=self._quality_requirements(request.provider_category),
            approval_required=approval_required,
        )

    def _select_provider(self, request: ProviderRouteRequest) -> str:
        provider_map = {
            "ugc_video_generation": "premium_ugc_video_provider_pending_selection",
            "image_generation": "premium_product_image_provider_pending_selection",
            "shopify": "shopify_admin_api",
            "email_marketing": "email_provider_pending_selection",
            "influencer_outreach": "creator_outreach_provider_pending_selection",
            "analytics_reporting": "analytics_provider_pending_selection",
            "website_generation": "white_label_site_builder_pending_selection",
            "customer_support": "helpdesk_provider_pending_selection",
        }

        return provider_map.get(request.provider_category, "manual_review_provider")

    def _quality_requirements(self, provider_category: str) -> List[str]:
        if provider_category == "ugc_video_generation":
            return [
                "Accurate lip sync",
                "Natural multilingual voice",
                "No facial distortion",
                "No audio lag",
                "Commercial usage rights",
                "Region-aware creator presentation",
                "Provider API or controlled automation path",
            ]

        if provider_category == "image_generation":
            return [
                "Product shape preservation",
                "Realistic lighting",
                "No label hallucination",
                "No low-resolution artefacts",
                "Commercial usage rights",
                "Store/ad/landing-page-ready outputs",
            ]

        if provider_category == "shopify":
            return [
                "Draft product creation first",
                "Tenant-owned credentials",
                "No live publish without approval",
                "SEO metadata support",
                "Image/media mapping support",
            ]

        return [
            "Secure credential handling",
            "Client-safe output",
            "White-label compatibility",
            "Audit logging required",
        ]


def provider_route_summary(result: ProviderRouteResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "provider_category": result.provider_category,
        "selected_provider": result.selected_provider,
        "execution_mode": result.execution_mode,
        "provider_ready": result.provider_ready,
        "message": result.message,
        "quality_requirements": result.quality_requirements,
        "approval_required": result.approval_required,
    }