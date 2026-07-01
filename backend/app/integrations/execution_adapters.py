"""
Execution Adapters

Controlled adapter stubs for real-world execution.
Adapters prepare auditable execution packets and route through the provider
orchestrator before any future external provider connection.
"""

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.integrations.provider_orchestrator import (
    ProviderOrchestrator,
    ProviderRouteRequest,
    provider_route_summary,
)
from app.integrations.shopify_draft_product_adapter import (
    ShopifyDraftProductAdapter,
    ShopifyDraftProductRequest,
    shopify_draft_product_summary,
)
from app.providers.adapters.arcads import ArcadsProvider
from app.providers.adapters.higgsfield import HiggsfieldProvider
from app.providers.adapters.kling import KlingProvider

logger = logging.getLogger(__name__)


@dataclass
class AdapterResult:
    success: bool
    adapter_name: str
    execution_mode: str
    provider_ready: bool
    message: str
    next_steps: List[str]
    execution_payload: Optional[Dict[str, object]] = None


def _get_kling_credentials(db: Session, workspace_id: str) -> tuple[str, str]:
    """Return (access_key, secret_key) from workspace storage or env vars."""
    access_key = secret_key = ""
    if db and workspace_id:
        try:
            from app.models.agent_system import WorkspaceIntegration
            from app.services.encryption_service import decrypt

            for key_name, attr in (("KLING_ACCESS_KEY", "access"), ("KLING_SECRET_KEY", "secret")):
                row = (
                    db.query(WorkspaceIntegration)
                    .filter(
                        WorkspaceIntegration.workspace_id == workspace_id,
                        WorkspaceIntegration.integration_key == key_name,
                        WorkspaceIntegration.is_active == True,
                    )
                    .first()
                )
                if row:
                    val = decrypt(row.encrypted_value)
                    if attr == "access":
                        access_key = val or ""
                    else:
                        secret_key = val or ""
        except Exception:
            logger.exception("Failed to retrieve Kling credentials for workspace %s", workspace_id)
    return (
        access_key or os.getenv("KLING_ACCESS_KEY", ""),
        secret_key or os.getenv("KLING_SECRET_KEY", ""),
    )


def _get_arcads_api_key(db: Session, workspace_id: str) -> str:
    """Return Arcads API key from workspace storage or env var."""
    if db and workspace_id:
        try:
            from app.models.agent_system import WorkspaceIntegration
            from app.services.encryption_service import decrypt

            row = (
                db.query(WorkspaceIntegration)
                .filter(
                    WorkspaceIntegration.workspace_id == workspace_id,
                    WorkspaceIntegration.integration_key == "ARCADS_API_KEY",
                    WorkspaceIntegration.is_active == True,
                )
                .first()
            )
            if row:
                return decrypt(row.encrypted_value) or ""
        except Exception:
            logger.exception("Failed to retrieve Arcads credentials for workspace %s", workspace_id)
    return os.getenv("ARCADS_API_KEY", "")


def _get_higgsfield_api_key(db: Session, workspace_id: str) -> Optional[str]:
    """
    Retrieve Higgsfield API key for workspace from encrypted storage.
    Returns None if not configured.

    Security: decryption happens only here, never logged or returned to caller.
    """
    if not db:
        return None

    try:
        from app.models.agent_system import WorkspaceIntegration
        from app.services.encryption_service import decrypt

        row = (
            db.query(WorkspaceIntegration)
            .filter(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.integration_key == "HIGGSFIELD_API_KEY",
                WorkspaceIntegration.is_active == True,
            )
            .first()
        )
        if not row:
            return None

        return decrypt(row.encrypted_value)
    except Exception as e:
        logger.exception("Failed to retrieve Higgsfield credentials for workspace %s", workspace_id)
        return None


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


class ExecutionAdapters:
    def __init__(self, db: Optional[Session] = None) -> None:
        self.shopify_adapter_runtime = ShopifyDraftProductAdapter()
        self.provider_orchestrator = ProviderOrchestrator()
        self.db = db

    def execute(self, adapter_name: str, payload: Dict[str, object]) -> AdapterResult:
        adapter_map = {
            "ugc_video_provider_adapter": self._ugc_video_provider_adapter,
            "image_generation_provider_adapter": self._image_generation_provider_adapter,
            "shopify_adapter": self._shopify_adapter,
            "website_builder_adapter": self._website_builder_adapter,
            "influencer_outreach_adapter": self._influencer_outreach_adapter,
            "email_marketing_adapter": self._email_marketing_adapter,
            "analytics_reporting_adapter": self._analytics_reporting_adapter,
            "support_helpdesk_adapter": self._support_helpdesk_adapter,
            "ad_platform_preparation_adapter": self._ad_platform_preparation_adapter,
        }

        handler = adapter_map.get(adapter_name)

        if not handler:
            return AdapterResult(
                success=False,
                adapter_name=adapter_name,
                execution_mode="unsupported",
                provider_ready=False,
                message="No controlled adapter exists for this provider yet.",
                next_steps=["Create a supported adapter before enabling this execution path."],
            )

        return handler(payload)

    def _route_provider(
        self,
        payload: Dict[str, object],
        provider_category: str,
        task_type: str,
    ) -> Dict[str, object]:
        workflow = payload.get("workflow", {})
        approval = payload.get("approval", {})

        route = self.provider_orchestrator.route(
            ProviderRouteRequest(
                tenant_id=str(workflow.get("tenant_id", "unknown_tenant")),
                provider_category=provider_category,
                task_type=task_type,
                region=str(workflow.get("region", "Global")),
                language=str(workflow.get("language", "English")),
                payload=payload,
                owner_approved=bool(approval.get("approved", False)),
            )
        )

        return provider_route_summary(route)

    def _ugc_video_provider_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="ugc_video_generation",
            task_type="ugc_video_brief",
        )

        # Extract workspace_id from payload (tenant_id)
        workflow = payload.get("workflow", {})
        context = payload.get("context", {}) if isinstance(payload.get("context"), dict) else {}
        creative_provider_route = (
            workflow.get("creative_provider_route")
            if isinstance(workflow.get("creative_provider_route"), dict)
            else context.get("creative_provider_route")
        )
        video_route = creative_provider_route.get("video", {}) if isinstance(creative_provider_route, dict) else {}
        image_route = creative_provider_route.get("image", {}) if isinstance(creative_provider_route, dict) else {}
        selected_video_provider = video_route.get("provider")
        selected_video_model = video_route.get("model")
        selected_video_model_id = video_route.get("model_id") or selected_video_model
        workspace_id = str(workflow.get("tenant_id", ""))
        media_request = workflow.get("media_request") if isinstance(workflow.get("media_request"), dict) else {}
        if not media_request and isinstance(context.get("media_request"), dict):
            media_request = context.get("media_request")
        language = str(workflow.get("language") or media_request.get("language") or "English")
        voiceover = workflow.get("voiceover") if isinstance(workflow.get("voiceover"), dict) else {}

        live_enabled = _truthy(os.getenv("HIGGSFIELD_LIVE_EXECUTION_ENABLED"))
        execution_surface = os.getenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp").strip().lower()

        provider_connected = False
        provider_ready = False
        provider_instance = None
        execution_mode = "provider_orchestrated_safe_stub"

        if execution_surface == "kling_direct":
            access_key, secret_key = _get_kling_credentials(self.db, workspace_id)
            kling = KlingProvider(access_key=access_key, secret_key=secret_key)
            provider_connected = kling.is_ready()
            provider_ready = live_enabled and provider_connected
            provider_instance = kling
            execution_mode = "kling_direct_live" if provider_ready else "provider_orchestrated_safe_stub"

        elif execution_surface == "arcads":
            arcads_key = _get_arcads_api_key(self.db, workspace_id)
            arcads = ArcadsProvider(api_key=arcads_key)
            provider_connected = arcads.is_ready()
            provider_ready = live_enabled and provider_connected
            provider_instance = arcads
            execution_mode = "arcads_live" if provider_ready else "provider_orchestrated_safe_stub"

        else:
            # Higgsfield MCP (claude_code_mcp) or legacy HTTP
            higgsfield = HiggsfieldProvider()
            higgsfield_api_key = None

            if execution_surface == "claude_code_mcp":
                provider_connected = higgsfield.is_mcp_ready()
                provider_ready = live_enabled and provider_connected
                execution_mode = "higgsfield_mcp_live" if provider_ready else "provider_orchestrated_safe_stub"
            else:
                if workspace_id and self.db:
                    higgsfield_api_key = _get_higgsfield_api_key(self.db, workspace_id)
                if not higgsfield_api_key:
                    higgsfield_api_key = os.getenv("HIGGSFIELD_API_KEY", "")
                if higgsfield_api_key and selected_video_provider == "higgsfield":
                    higgsfield.set_api_key(higgsfield_api_key)
                    provider_connected = True
                    provider_ready = live_enabled and higgsfield.is_ready()
                execution_mode = "higgsfield_live" if provider_ready else "provider_orchestrated_safe_stub"

            provider_instance = higgsfield

        next_steps: list[str] = []
        if not provider_ready:
            if execution_surface == "kling_direct":
                next_steps = [
                    "Set KLING_ACCESS_KEY and KLING_SECRET_KEY environment variables.",
                    "Set HIGGSFIELD_LIVE_EXECUTION_ENABLED=true.",
                ]
            elif execution_surface == "arcads":
                next_steps = [
                    "Set ARCADS_API_KEY environment variable.",
                    "Set HIGGSFIELD_LIVE_EXECUTION_ENABLED=true.",
                ]
            else:
                next_steps = [
                    "Run `claude mcp login higgsfield` where the worker executes.",
                    "Set HIGGSFIELD_EXECUTION_SURFACE=claude_code_mcp.",
                    "Set HIGGSFIELD_LIVE_EXECUTION_ENABLED=true after MCP preflight succeeds.",
                    "Alternatively set HIGGSFIELD_EXECUTION_SURFACE=kling_direct with KLING_ACCESS_KEY/KLING_SECRET_KEY.",
                    "Or set HIGGSFIELD_EXECUTION_SURFACE=arcads with ARCADS_API_KEY.",
                ]

        surface_label = {
            "kling_direct": "Kling direct API",
            "arcads": "Arcads API",
            "claude_code_mcp": "Higgsfield MCP",
        }.get(execution_surface, "Higgsfield")

        return AdapterResult(
            success=bool(provider_route["success"]) and provider_ready,
            adapter_name="ugc_video_provider_adapter",
            execution_mode=execution_mode,
            provider_ready=provider_ready,
            message=f"UGC video generation routed to {surface_label}" if provider_ready else "UGC video provider adapter prepared through provider orchestrator.",
            next_steps=next_steps,
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "ugc_video_generation",
                "provider": selected_video_provider,
                "execution_surface": execution_surface,
                "provider_connected": provider_connected,
                "live_execution_enabled": live_enabled,
                "provider_instance": provider_instance,
                "workspace_id": workspace_id,
                "language": language,
                "media_request": media_request,
                "voiceover": voiceover,
                "creative_provider_route": creative_provider_route,
                "selected_video_provider": selected_video_provider,
                "selected_video_model": selected_video_model,
                "selected_video_model_id": selected_video_model_id,
                "selected_image_provider": image_route.get("provider"),
                "selected_image_model": image_route.get("model"),
            },
        )

    def _image_generation_provider_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="image_generation",
            task_type="product_image_generation",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="image_generation_provider_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Product image generation adapter prepared through provider orchestrator.",
            next_steps=[
                "Select premium image generation provider.",
                "Map product, brand, scene, and platform parameters.",
                "Add quality validation for product accuracy and visual artefacts.",
                "Run safe test generation before enabling client delivery.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "image_generation",
                "provider_connected": False,
            },
        )

    def _shopify_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        workflow = payload.get("workflow", {})
        output = payload.get("output", {})

        provider_route = self._route_provider(
            payload=payload,
            provider_category="shopify",
            task_type="shopify_draft_product",
        )

        task = str(workflow.get("task", ""))
        currency = str(workflow.get("currency", "USD"))
        tenant_id = str(workflow.get("tenant_id", "unknown_tenant"))
        region = str(workflow.get("region", "Global"))

        detected_product_name = self._extract_product_name(task)
        detected_product_type = self._extract_product_type(task)
        detected_vendor = self._extract_vendor(region)
        detected_tags = self._build_tags(task, region)

        generated_content = str(
            output.get(
                "content",
                "Premium ecommerce product description generated by the platform.",
            )
        )

        seo_title = f"{detected_product_name} | Premium {detected_product_type}"
        seo_description = (
            f"{detected_product_name} for customers in {region}. "
            f"Premium ecommerce positioning with conversion-focused messaging."
        )

        request = ShopifyDraftProductRequest(
            tenant_id=tenant_id,
            product_title=detected_product_name,
            product_description_html=f"<p>{generated_content}</p>",
            product_type=detected_product_type,
            vendor=detected_vendor,
            price=self._estimate_price(task, currency),
            currency=currency,
            seo_title=seo_title,
            seo_description=seo_description,
            tags=detected_tags,
            image_urls=[],
            publish_live=False,
            owner_approved=False,
        )

        result = self.shopify_adapter_runtime.prepare_product_payload(request)

        return AdapterResult(
            success=result.success and bool(provider_route["success"]),
            adapter_name="shopify_adapter",
            execution_mode="provider_orchestrated_safe_shopify_draft_mode",
            provider_ready=False,
            message=result.message,
            next_steps=[
                "Connect tenant-owned Shopify credentials.",
                "Run Shopify draft product test.",
                "Validate SEO, variants, pricing, and image mapping.",
                "Require approval before live publishing.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "shopify_draft": shopify_draft_product_summary(result),
            },
        )

    def _website_builder_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="website_generation",
            task_type="website_draft",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="website_builder_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Website/landing page builder adapter prepared through provider orchestrator.",
            next_steps=[
                "Map page structure, copy, imagery, offer, brand colours, and CTA sections.",
                "Generate draft page first.",
                "Run client-safe preview before publishing.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "website_generation",
                "provider_connected": False,
            },
        )

    def _influencer_outreach_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="influencer_outreach",
            task_type="influencer_outreach",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="influencer_outreach_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Influencer outreach adapter prepared through provider orchestrator.",
            next_steps=[
                "Select outreach channel provider.",
                "Map creator profile, contact method, outreach message, and follow-up cadence.",
                "Keep paid collaborations and contracts approval-gated.",
                "Track reply status and collaboration terms.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "influencer_outreach",
                "provider_connected": False,
            },
        )

    def _email_marketing_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="email_marketing",
            task_type="email_campaign_draft",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="email_marketing_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Email marketing adapter prepared through provider orchestrator.",
            next_steps=[
                "Select email platform provider.",
                "Map campaign subject, preview text, body, audience segment, and send schedule.",
                "Create campaign draft first.",
                "Require approval before any large campaign send if risk threshold applies.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "email_marketing",
                "provider_connected": False,
            },
        )

    def _analytics_reporting_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="analytics_reporting",
            task_type="analytics_report",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="analytics_reporting_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Analytics reporting adapter prepared through provider orchestrator.",
            next_steps=[
                "Connect Shopify, ad platforms, GA4, or reporting sources.",
                "Map ROAS, CPA, CTR, CPM, conversion rate, AOV, and revenue.",
                "Keep scaling recommendations approval-gated.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "analytics_reporting",
                "provider_connected": False,
            },
        )

    def _support_helpdesk_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="customer_support",
            task_type="support_reply_draft",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="support_helpdesk_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Support/helpdesk adapter prepared through provider orchestrator.",
            next_steps=[
                "Select helpdesk platform.",
                "Map customer message, order status, support category, and response draft.",
                "Escalate chargeback risk, legal threats, and high-value customer issues.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "customer_support",
                "provider_connected": False,
            },
        )

    def _ad_platform_preparation_adapter(self, payload: Dict[str, object]) -> AdapterResult:
        provider_route = self._route_provider(
            payload=payload,
            provider_category="ad_platform_preparation",
            task_type="ad_platform_draft",
        )

        return AdapterResult(
            success=bool(provider_route["success"]),
            adapter_name="ad_platform_preparation_adapter",
            execution_mode="provider_orchestrated_safe_stub",
            provider_ready=False,
            message="Ad platform preparation adapter prepared through provider orchestrator.",
            next_steps=[
                "Map creative, audience, platform, campaign objective, and tracking setup.",
                "Prepare draft campaign only.",
                "Owner approval required before paid launch, budget change, or scaling.",
            ],
            execution_payload={
                "provider_route": provider_route,
                "provider_category": "ad_platform_preparation",
                "provider_connected": False,
            },
        )

    def _extract_product_name(self, task: str) -> str:
        trigger_words = ["for ", "page for "]

        lowered = task.lower()

        for trigger in trigger_words:
            if trigger in lowered:
                split_result = lowered.split(trigger, 1)[1]
                extracted = split_result.split(",")[0].strip()
                if extracted:
                    return extracted.title()

        return "Premium Ecommerce Product"

    def _extract_product_type(self, task: str) -> str:
        lowered = task.lower()

        category_map = {
            "serum": "Skincare",
            "skincare": "Skincare",
            "supplement": "Supplement",
            "watch": "Accessories",
            "fashion": "Fashion",
            "protein": "Fitness",
            "beauty": "Beauty",
            "coffee": "Food & Beverage",
        }

        for keyword, category in category_map.items():
            if keyword in lowered:
                return category

        return "General Ecommerce"

    def _extract_vendor(self, region: str) -> str:
        return f"{region} Premium Brands"

    def _build_tags(self, task: str, region: str) -> List[str]:
        tags = [
            "ai-generated",
            "draft-product",
            region.lower().replace(" ", "-"),
        ]

        lowered = task.lower()

        keyword_tags = [
            "skincare",
            "beauty",
            "fitness",
            "fashion",
            "supplement",
            "coffee",
            "luxury",
            "premium",
        ]

        for tag in keyword_tags:
            if tag in lowered:
                tags.append(tag)

        return sorted(list(set(tags)))

    def _estimate_price(self, task: str, currency: str) -> str:
        lowered = task.lower()

        premium_price_map = {
            "AED": "149.00",
            "USD": "49.00",
            "GBP": "39.00",
            "AUD": "79.00",
            "EUR": "45.00",
        }

        if "premium" in lowered:
            return premium_price_map.get(currency, "49.00")

        return "29.00"


def adapter_summary(result: AdapterResult) -> Dict[str, object]:
    execution_payload = result.execution_payload
    if isinstance(execution_payload, dict):
        execution_payload = {
            key: value
            for key, value in execution_payload.items()
            if key != "provider_instance"
        }

    return {
        "success": result.success,
        "adapter_name": result.adapter_name,
        "execution_mode": result.execution_mode,
        "provider_ready": result.provider_ready,
        "message": result.message,
        "next_steps": result.next_steps,
        "execution_payload": execution_payload,
    }
