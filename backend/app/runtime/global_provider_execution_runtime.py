
from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.real_provider_activation_layer import (
    provider_readiness,
    real_provider_execution_gate,
)


GLOBAL_AGENT_PROVIDER_CAPABILITIES = {
    "head_agent": ["strategy", "analysis", "brief_generation", "orchestration"],
    "strategist_agent": ["strategy", "analysis", "planning"],
    "business_growth_partnerships_agent": ["strategy", "outreach", "partnership_brief"],
    "lead_generator_appointment_setter_agent": ["lead_generation", "email", "crm"],
    "marketing_specialist_agent": ["ad_copy", "campaign_brief", "content", "analysis"],
    "social_media_manager_content_creator_agent": ["social_content", "short_video_brief", "caption_generation"],
    "seo_agent": ["seo_plan", "content", "analysis"],
    "email_reply_agent": ["email", "customer_reply", "support_response"],
    "crm_ai_agent": ["crm", "analysis", "recommendation"],
    "sales_closer_agent": ["sales_copy", "follow_up", "objection_handling"],
    "receptionist_agent": ["intake", "support_response", "routing"],
    "customer_support_agent": ["support_response", "customer_reply", "knowledge_response"],
    "ecommerce_agent": ["product_page", "store_optimisation", "analysis"],
    "product_research_agent": ["research", "analysis", "product_brief"],
    "competitor_intelligence_agent": ["competitor_analysis", "research", "strategy"],
    "brand_strategy_agent": ["brand_strategy", "positioning", "creative_brief"],
    "store_builder_agent": ["store_page", "landing_page", "website_brief"],
    "website_landing_apps_agent": ["website_brief", "landing_page", "app_page", "ui_copy"],
    "product_development_agent": ["product_brief", "product_strategy", "research"],
    "product_copywriting_agent": ["product_copy", "ad_copy", "content"],
    "ugc_creative_agent": ["ugc_brief", "short_video_brief", "creator_direction"],
    "product_image_agent": ["image_brief", "product_image_direction", "visual_direction"],
    "paid_ads_agent": ["ad_copy", "campaign_brief", "creative_brief"],
    "analytics_optimisation_agent": ["analytics", "analysis", "optimisation"],
    "influencer_collaboration_agent": ["outreach", "influencer_brief", "contract_review_support"],
}


CAPABILITY_PROVIDER_MAP = {
    "strategy": ["openai"],
    "analysis": ["openai"],
    "planning": ["openai"],
    "brief_generation": ["openai"],
    "orchestration": ["openai"],
    "outreach": ["openai"],
    "partnership_brief": ["openai"],
    "lead_generation": ["openai"],
    "email": ["openai"],
    "crm": ["openai"],
    "ad_copy": ["openai"],
    "campaign_brief": ["openai"],
    "content": ["openai"],
    "social_content": ["openai"],
    "short_video_brief": ["openai", "runway", "kling", "heygen"],
    "caption_generation": ["openai"],
    "seo_plan": ["openai"],
    "customer_reply": ["openai"],
    "support_response": ["openai"],
    "recommendation": ["openai"],
    "sales_copy": ["openai"],
    "follow_up": ["openai"],
    "objection_handling": ["openai"],
    "intake": ["openai"],
    "routing": ["openai"],
    "knowledge_response": ["openai"],
    "product_page": ["openai"],
    "store_optimisation": ["openai"],
    "research": ["openai"],
    "product_brief": ["openai"],
    "competitor_analysis": ["openai"],
    "brand_strategy": ["openai"],
    "positioning": ["openai"],
    "creative_brief": ["openai", "runway", "kling", "replicate"],
    "store_page": ["openai"],
    "landing_page": ["openai"],
    "website_brief": ["openai"],
    "app_page": ["openai"],
    "ui_copy": ["openai"],
    "product_strategy": ["openai"],
    "product_copy": ["openai"],
    "ugc_brief": ["openai", "runway", "kling", "heygen"],
    "creator_direction": ["openai", "heygen"],
    "image_brief": ["openai", "replicate", "runway"],
    "product_image_direction": ["openai", "replicate", "runway"],
    "visual_direction": ["openai", "replicate", "runway"],
    "analytics": ["openai"],
    "optimisation": ["openai"],
    "influencer_brief": ["openai"],
    "contract_review_support": ["openai"],
}


def normalise_agent_id(agent_id: str) -> str:
    return str(agent_id or "").strip().lower()


def get_agent_capabilities(agent_id: str) -> Dict[str, Any]:
    normalised = normalise_agent_id(agent_id)
    capabilities = GLOBAL_AGENT_PROVIDER_CAPABILITIES.get(normalised, [])

    return {
        "success": bool(capabilities),
        "agent_id": normalised,
        "capabilities": capabilities,
        "capability_count": len(capabilities),
        "global_runtime": True,
        "governance_preserved": True,
        "internal_config_exposed": False,
    }


def infer_capabilities_from_payload(payload: Dict[str, Any]) -> List[str]:
    text = " ".join([
        str(payload.get("action_type", "")),
        str(payload.get("workflow_stage", "")),
        str(payload.get("task", "")),
        str(payload.get("media_type", "")),
        str(payload.get("request", {}).get("media_type", "")) if isinstance(payload.get("request"), dict) else "",
        str(payload.get("input", {}).get("media_type", "")) if isinstance(payload.get("input"), dict) else "",
    ]).lower()

    inferred: List[str] = []

    rules = [
        ("ugc", "ugc_brief"),
        ("video", "short_video_brief"),
        ("image", "image_brief"),
        ("photo", "image_brief"),
        ("website", "website_brief"),
        ("landing", "landing_page"),
        ("email", "email"),
        ("crm", "crm"),
        ("seo", "seo_plan"),
        ("ad", "ad_copy"),
        ("campaign", "campaign_brief"),
        ("analytics", "analytics"),
        ("support", "support_response"),
        ("research", "research"),
        ("competitor", "competitor_analysis"),
        ("strategy", "strategy"),
        ("copy", "product_copy"),
        ("influencer", "influencer_brief"),
    ]

    for keyword, capability in rules:
        if keyword in text and capability not in inferred:
            inferred.append(capability)

    if not inferred:
        inferred.append("brief_generation")

    return inferred


def build_global_provider_chain(agent_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    agent = get_agent_capabilities(agent_id)
    agent_capabilities = agent.get("capabilities", [])
    inferred = infer_capabilities_from_payload(payload)

    combined = []
    for cap in inferred + agent_capabilities:
        if cap not in combined:
            combined.append(cap)

    providers: List[str] = []
    capability_routes: Dict[str, List[str]] = {}

    for capability in combined:
        mapped = CAPABILITY_PROVIDER_MAP.get(capability, ["openai"])
        capability_routes[capability] = mapped
        for provider in mapped:
            if provider not in providers:
                providers.append(provider)

    if "openai" not in providers:
        providers.append("openai")

    readiness = [provider_readiness(provider) for provider in providers]
    configured = [item for item in readiness if item.get("configured")]

    selected = configured[0]["provider"] if configured else providers[0]

    return {
        "success": True,
        "agent_id": normalise_agent_id(agent_id),
        "agent_known": agent["success"],
        "inferred_capabilities": inferred,
        "agent_capabilities": agent_capabilities,
        "combined_capabilities": combined,
        "capability_routes": capability_routes,
        "provider_chain": providers,
        "selected_provider": selected,
        "configured_provider_count": len(configured),
        "provider_readiness": readiness,
        "global_runtime": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def build_global_provider_execution_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent_id = (
        payload.get("requested_agent")
        or payload.get("agent_id")
        or payload.get("agent")
        or "unknown_agent"
    )

    route = build_global_provider_chain(agent_id, payload)
    gate_payload = {
        "tenant_id": payload.get("tenant_id"),
        "agent_id": agent_id,
        "requested_agent": agent_id,
        "task": payload.get("task") or payload.get("action_type"),
        "action_type": payload.get("action_type"),
    }

    gate = real_provider_execution_gate(route["selected_provider"], gate_payload)

    return {
        "success": True,
        "runtime": "global_provider_execution_runtime",
        "scope": "platform_wide_multi_agent",
        "tenant_id": payload.get("tenant_id", "tenant_unknown"),
        "agent_id": normalise_agent_id(agent_id),
        "workflow_stage": payload.get("workflow_stage", ""),
        "action_type": payload.get("action_type", ""),
        "provider_route": route,
        "execution_gate": gate,
        "live_execution_allowed": gate.get("live_execution_allowed", False),
        "execution_mode": (
            "global_real_provider_execution_allowed"
            if gate.get("live_execution_allowed")
            else "global_provider_execution_prepared"
        ),
        "customer_safe_status": (
            "Ready for live provider execution"
            if gate.get("live_execution_allowed")
            else "Prepared; provider credentials or owner live execution not enabled"
        ),
        "applies_to_all_agents": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }


def global_provider_execution_readiness() -> Dict[str, Any]:
    agents = {
        agent_id: get_agent_capabilities(agent_id)
        for agent_id in GLOBAL_AGENT_PROVIDER_CAPABILITIES
    }

    providers = sorted({provider for providers in CAPABILITY_PROVIDER_MAP.values() for provider in providers})
    provider_status = {provider: provider_readiness(provider) for provider in providers}

    return {
        "success": True,
        "runtime": "global_provider_execution_runtime",
        "status": "ready",
        "scope": "platform_wide_multi_agent",
        "agent_count": len(agents),
        "agents": agents,
        "provider_status": provider_status,
        "capabilities": [
            "global_agent_capability_mapping",
            "capability_based_provider_routing",
            "platform_wide_provider_selection",
            "multi_provider_fallback_chain",
            "global_live_execution_gate",
            "credential_safe_provider_readiness",
            "customer_safe_execution_packet",
            "all_agent_generation_support",
        ],
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "layout_changes": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }
