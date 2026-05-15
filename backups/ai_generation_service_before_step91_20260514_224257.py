"""
AI Generation Service

Central generation layer for premium ecommerce agent outputs.
Improved structured extraction layer for premium ecommerce realism.
LLM provider orchestration integrated.
"""

from dataclasses import dataclass
from typing import Dict
import re

from backend.app.media.product_image_prompt_engine import (
    ProductImagePromptEngine,
    ProductImagePromptRequest,
)
from backend.app.media.ugc_prompt_engine import (
    UGCPromptEngine,
    UGCPromptRequest,
)

from backend.app.core.llm_provider_orchestrator import (
    LLMProviderOrchestrator,
    LLMRouteRequest,
    llm_route_summary,
)

from backend.app.core.llm_provider_execution_adapter import (
    LLMProviderExecutionAdapter,
    LLMProviderExecutionRequest,
    provider_execution_summary,
)


@dataclass
class GenerationRequest:
    tenant_id: str
    requested_agent: str
    workflow_stage: str
    task: str
    region: str
    language: str
    currency: str


class AIGenerationService:
    def __init__(self) -> None:
        self.product_image_engine = ProductImagePromptEngine()
        self.ugc_prompt_engine = UGCPromptEngine()
        self.llm_orchestrator = LLMProviderOrchestrator()
        self.provider_execution_adapter = LLMProviderExecutionAdapter()

    def generate(self, request: GenerationRequest) -> Dict[str, object]:
        route_result = self._build_llm_route(request)

        if request.requested_agent == "ugc_creative_agent":
            result = self._generate_ugc_output(request)

        elif request.requested_agent == "influencer_collaboration_agent":
            result = self._generate_influencer_output(request)

        elif request.requested_agent == "analytics_optimisation_agent":
            result = self._generate_analytics_output(request)

        elif request.requested_agent in {
            "product_image_direction_agent",
            "product_image_agent",
            "ad_creative_image_agent",
        }:
            result = self._generate_product_image_output(request)

        elif request.workflow_stage == "store_creation" or request.requested_agent in {
            "store_builder_agent",
            "product_copywriting_agent",
            "product_research_agent",
        }:
            result = self._generate_product_page_output(request)

        else:
            result = self._generate_general_output(request)

        result["llm_routing"] = llm_route_summary(route_result)

        provider_execution_result = self.provider_execution_adapter.execute(
            LLMProviderExecutionRequest(
                tenant_id=request.tenant_id,
                agent_id=request.requested_agent,
                task_type=result.get("output_type", self._resolve_task_type(request)),
                selected_provider=route_result.selected_provider,
                selected_model_class=route_result.selected_model_class,
                region=request.region,
                language=request.language,
                payload={
                    "task": request.task,
                    "workflow_stage": request.workflow_stage,
                    "generated_output_type": result.get("output_type"),
                    "client_safe": result.get("client_safe", True),
                },
            )
        )

        result["provider_execution"] = provider_execution_summary(provider_execution_result)

        result["governance_protection"] = {
            "internal_prompt_exposure_blocked": True,
            "backend_architecture_exposure_blocked": True,
            "tenant_isolation_required": True,
            "owner_approval_required_for_sensitive_actions": True,
            "governed_learning_enabled": True,
        }

        return result

    def _build_llm_route(self, request: GenerationRequest):
        task_type = self._resolve_task_type(request)

        route_request = LLMRouteRequest(
            tenant_id=request.tenant_id,
            agent_id=request.requested_agent,
            task_type=task_type,
            region=request.region,
            language=request.language,
            quality_requirement="premium",
            payload={
                "task": request.task,
                "workflow_stage": request.workflow_stage,
            },
        )

        return self.llm_orchestrator.route(route_request)

    def _resolve_task_type(self, request: GenerationRequest) -> str:
        if request.requested_agent == "ugc_creative_agent":
            return "premium_ugc_video_execution_brief"

        if request.requested_agent in {
            "product_image_direction_agent",
            "product_image_agent",
            "ad_creative_image_agent",
        }:
            return "premium_product_image_direction"

        if request.requested_agent in {
            "store_builder_agent",
            "product_copywriting_agent",
            "product_research_agent",
        }:
            return "premium_shopify_product_page"

        if request.requested_agent == "influencer_collaboration_agent":
            return "influencer_collaboration_strategy"

        return "general_ecommerce_generation"

    def _generate_ugc_output(self, request: GenerationRequest) -> Dict[str, object]:
        product_name = self._extract_product_name(request.task)
        target_audience = self._extract_target_audience(request.task)

        ugc_request = UGCPromptRequest(
            product_name=product_name,
            product_category=self._detect_product_category(request.task),
            target_audience=target_audience,
            region=request.region,
            language=request.language,
            currency=request.currency,
            creator_age_range=self._extract_age_range(target_audience),
            creator_gender=self._extract_gender(target_audience),
            creator_ethnicity="region-appropriate and campaign-selectable",
            creator_accent=f"{request.region} appropriate accent",
            platform="TikTok, Meta Reels, Instagram Reels, YouTube Shorts",
            tone="natural, premium, trustworthy, emotionally believable",
        )

        result = self.ugc_prompt_engine.build_prompt(ugc_request)

        return {
            "client_safe": True,
            "output_type": "premium_ugc_video_execution_brief",
            "product_name": product_name,
            "content": result["production_brief"],
            "ugc_prompt": result,
            "sections": {
                "creator_profile": result["creator_profile"],
                "shot_plan": result["shot_plan"],
                "audio_quality_requirements": result["audio_quality_requirements"],
                "video_quality_requirements": result["video_quality_requirements"],
                "quality_rejection_rules": result["quality_rejection_rules"],
                "provider_execution_packet": result["provider_execution_packet"],
                "premium_expansion_layer": {
                    "ugc_quality_level": "premium_global_ugc_ad_standard",
                    "competitor_benchmark_reference": [
                        "higgsfield",
                        "sintra",
                        "top_performing_tiktok_shop_creatives",
                        "high_conversion_meta_reels_ads",
                    ],
                    "optimisation_focus": [
                        "hook_strength",
                        "creator_authenticity",
                        "scroll_stopping_opening",
                        "product_believability",
                        "native_platform_feel",
                        "clear_conversion_intent",
                        "audio_visual_realism",
                    ],
                    "creative_requirements": [
                        "first_three_seconds_must_create_curiosity",
                        "creator_delivery_must_feel_unscripted",
                        "product_benefit_must_be_visible_or_demonstrated",
                        "avoid_overproduced_ad_language",
                        "include_platform_native_caption_direction",
                        "include objection-handling angle",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "local_creator_style_applied": True,
                        "regional_buyer_psychology_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "paid_collaboration_requires_owner_approval": True,
                    },
                },
            },
        }

    def _generate_product_image_output(self, request: GenerationRequest) -> Dict[str, object]:
        product_name = self._extract_product_name(request.task)

        image_request = ProductImagePromptRequest(
            product_name=product_name,
            product_category=self._detect_product_category(request.task),
            target_audience=self._extract_target_audience(request.task),
            region=request.region,
            language=request.language,
            currency=request.currency,
            brand_style="premium, commercial, conversion-focused, ecommerce-ready",
            image_type="premium ecommerce product image",
            platform="Shopify, Meta Ads, TikTok Shop, Landing Pages",
            scene_direction=(
                "Use realistic commercial product photography composition, "
                "premium lighting, mobile-friendly framing, clean backgrounds, "
                "and platform-native visual direction."
            ),
        )

        result = self.product_image_engine.build_prompt(image_request)

        return {
            "client_safe": True,
            "output_type": "premium_product_image_direction",
            "product_name": product_name,
            "content": result["production_brief"],
            "image_prompt": result,
            "sections": {
                "composition_requirements": result["composition_requirements"],
                "realism_requirements": result["realism_requirements"],
                "quality_rejection_rules": result["quality_rejection_rules"],
            },
        }

    def _generate_product_page_output(self, request: GenerationRequest) -> Dict[str, object]:
        product_name = self._extract_product_name(request.task)
        target_audience = self._extract_target_audience(request.task)

        html = (
            f"<section>"
            f"<h1>{product_name}</h1>"
            f"<p>Designed for {target_audience} in {request.region}, this premium ecommerce offer is positioned to support trust, conversion, and strong customer perception.</p>"

            f"<h2>Why customers will love it</h2>"
            f"<ul>"
            f"<li><strong>Benefit-led positioning:</strong> Clear commercial value communicated quickly.</li>"
            f"<li><strong>Trust-focused structure:</strong> Premium language, proof cues, and low-friction buying psychology.</li>"
            f"<li><strong>Conversion-ready messaging:</strong> Designed to improve clarity and buying confidence.</li>"
            f"</ul>"

            f"<h2>Who it is for</h2>"
            f"<p>{target_audience}</p>"

            f"<h2>Commercial positioning</h2>"
            f"<p>Use strong product visuals, concise benefit-first copy, FAQ support, social proof, and mobile-first formatting.</p>"

            f"<h2>Recommended conversion structure</h2>"
            f"<ul>"
            f"<li>Strong headline</li>"
            f"<li>Benefit-first bullet points</li>"
            f"<li>Visual proof</li>"
            f"<li>Trust signals</li>"
            f"<li>Objection handling</li>"
            f"<li>Soft but confident CTA</li>"
            f"</ul>"
            f"</section>"
        )

        return {
            "client_safe": True,
            "output_type": "premium_shopify_product_page",
            "product_name": product_name,
            "target_audience": target_audience,
            "content": html,
            "sections": {
                "headline": product_name,
                "target_audience": target_audience,
                "benefits": [
                    "Benefit-led product positioning",
                    "Trust-building ecommerce copy",
                    "Conversion-focused offer structure",
                    "Region-aware buying psychology adaptation",
                    "Mobile-first ecommerce optimisation",
                    "Premium perceived value positioning",
                ],
                "conversion_requirements": [
                    "Clear above-the-fold value proposition",
                    "Benefit-first bullet points",
                    "Objection handling",
                    "FAQ-ready structure",
                    "Strong call-to-action",
                    "Trust badge positioning",
                    "Social proof placement",
                    "Mobile conversion optimisation",
                    "Checkout friction reduction",
                    "Platform-native ecommerce structure",
                ],
                "premium_expansion_layer": {
                    "storefront_quality_level": "premium_global_ecommerce_standard",
                    "competitor_benchmark_reference": [
                        "10web",
                        "base44",
                        "shopify_plus",
                        "high_conversion_dtc_brands",
                    ],
                    "optimisation_focus": [
                        "conversion_rate",
                        "trust_building",
                        "visual_hierarchy",
                        "buyer_confidence",
                        "mobile_performance",
                        "platform_native_structure",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "local_buyer_psychology_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                    },
                },
            },
        }

    def _generate_influencer_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "influencer_collaboration_strategy",
            "content": (
                f"Premium influencer collaboration strategy for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on creators with authentic audience trust, "
                f"high engagement quality, commercial content quality, and strong product-category alignment. "
                f"Task: {request.task}"
            ),
        }

    def _generate_analytics_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "analytics_recommendation",
            "content": (
                f"Premium analytics recommendation for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on conversion rate, CPA, ROAS, CTR, "
                f"creative fatigue, funnel performance, and scaling opportunities."
            ),
        }

    def _generate_general_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "general_ecommerce_agent_output",
            "content": (
                f"Premium region-aware ecommerce output for {request.region} in {request.language}, "
                f"using {request.currency}. Adapted to local buyer psychology, "
                f"commercial expectations, trust signals, and ecommerce best practices."
            ),
        }

    def _extract_product_name(self, task: str) -> str:
        patterns = [
            r"for\s+([A-Z][A-Za-z0-9\s]+?)(?:,|\stargeting|\sfor women|\sfor men|\sin\s)",
            r"images for\s+([A-Z][A-Za-z0-9\s]+?)(?:,|\stargeting|\sin\s)",
            r"page for\s+([A-Z][A-Za-z0-9\s]+?)(?:,|\stargeting|\sin\s)",
        ]

        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Premium Ecommerce Product"

    def _extract_target_audience(self, task: str) -> str:
        lowered = task.lower()

        targeting_match = re.search(r"targeting\s+(.+?)(?:\.|$)", lowered)

        if targeting_match:
            audience = targeting_match.group(1).strip()
            audience = audience.replace(" in the ", " in ")
            return audience.capitalize()

        return "Premium ecommerce buyers"

    def _extract_age_range(self, audience: str) -> str:
        match = re.search(r"(\d{2}\s?(?:to|-)\s?\d{2})", audience)

        if match:
            return match.group(1).replace(" to ", "-")

        return "25-40"

    def _extract_gender(self, audience: str) -> str:
        lowered = audience.lower()

        if "women" in lowered or "female" in lowered:
            return "female"

        if "men" in lowered or "male" in lowered:
            return "male"

        return "flexible based on campaign brief"

    def _detect_product_category(self, task: str) -> str:
        lowered = task.lower()

        category_map = {
            "skincare": "skincare",
            "serum": "skincare",
            "beauty": "beauty",
            "supplement": "supplement",
            "fashion": "fashion",
            "coffee": "food_and_beverage",
            "protein": "fitness",
            "watch": "accessories",
            "electronics": "electronics",
            "fragrance": "fragrance",
        }

        for keyword, category in category_map.items():
            if keyword in lowered:
                return category

        return "general_ecommerce"
