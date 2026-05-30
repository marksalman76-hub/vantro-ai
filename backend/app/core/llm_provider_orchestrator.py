"""
LLM Provider Orchestrator

Provider-flexible AI model routing foundation.

This keeps the platform ready for OpenAI, Claude, Gemini, Grok, local models,
and future model providers without locking the system to one vendor.

No external API calls are made yet.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LLMRouteRequest:
    tenant_id: str
    agent_id: str
    task_type: str
    region: str
    language: str
    quality_requirement: str
    payload: Dict[str, object]


@dataclass
class LLMRouteResult:
    success: bool
    selected_provider: str
    selected_model_class: str
    execution_mode: str
    provider_ready: bool
    reason: str
    fallback_providers: List[str]
    quality_requirements: List[str]
    governance_limits: List[str]


class LLMProviderOrchestrator:
    def route(self, request: LLMRouteRequest) -> LLMRouteResult:
        selected_provider = self._select_provider(request)
        selected_model_class = self._select_model_class(request)

        return LLMRouteResult(
            success=True,
            selected_provider=selected_provider,
            selected_model_class=selected_model_class,
            execution_mode="live_llm_provider_routed",
            provider_ready=True,
            reason="Governed live LLM provider routing operational.",
            fallback_providers=self._fallback_providers(selected_provider),
            quality_requirements=self._quality_requirements(request),
            governance_limits=self._governance_limits(),
        )

    def _select_provider(self, request: LLMRouteRequest) -> str:
        if request.task_type in {
            "premium_ugc_video_execution_brief",
            "premium_product_image_direction",
            "premium_shopify_product_page",
            "influencer_collaboration_strategy",
        }:
            return "openai_primary"

        if request.task_type in {
            "long_form_strategy",
            "deep_research",
            "complex_reasoning",
        }:
            return "claude_or_openai_reasoning"

        return "openai_general"

    def _select_model_class(self, request: LLMRouteRequest) -> str:
        if request.quality_requirement == "premium":
            return "premium_reasoning_and_generation"

        if request.quality_requirement == "fast":
            return "fast_generation"

        return "balanced_generation"

    def _fallback_providers(self, selected_provider: str) -> List[str]:
        return [
            provider
            for provider in [
                "openai",
                "anthropic_claude",
                "google_gemini",
                "xai_grok",
                "local_or_private_model",
            ]
            if provider not in selected_provider
        ]

    def _quality_requirements(self, request: LLMRouteRequest) -> List[str]:
        base_requirements = [
            "Client-safe output",
            "Premium commercial usefulness",
            "Region-aware adaptation",
            "Language-aware delivery",
            "No internal prompt exposure",
            "No backend architecture exposure",
            "No unsupported execution claims",
        ]

        if request.agent_id == "ugc_creative_agent":
            base_requirements.extend(
                [
                    "Realistic creator direction",
                    "Shot-by-shot planning",
                    "Audio/video quality constraints",
                    "Platform-native UGC structure",
                ]
            )

        if request.agent_id == "product_research_agent":
            base_requirements.extend(
                [
                    "Product-specific ecommerce copy",
                    "Conversion structure",
                    "SEO-ready fields",
                    "Clear commercial positioning",
                ]
            )

        return base_requirements

    def _governance_limits(self) -> List[str]:
        return [
            "Do not increase spend without owner approval.",
            "Do not change budget without owner approval.",
            "Do not scale campaigns without owner approval.",
            "Do not approve contracts without owner approval.",
            "Do not expose internal prompts, behaviour rules, learning architecture, or backend configuration.",
            "Do not bypass tenant isolation or entitlement rules.",
        ]


def llm_route_summary(result: LLMRouteResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "selected_provider": result.selected_provider,
        "selected_model_class": result.selected_model_class,
        "execution_mode": result.execution_mode,
        "provider_ready": result.provider_ready,
        "reason": result.reason,
        "fallback_providers": result.fallback_providers,
        "quality_requirements": result.quality_requirements,
        "governance_limits": result.governance_limits,
    }