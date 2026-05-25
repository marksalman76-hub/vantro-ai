"""
Unified Agent Registry

Single source of truth for the approved premium agent catalogue.

Rules:
- Purchasable agents can be shown to clients and activated by entitlement.
- Internal-only agents are backend/system agents and must not be exposed as
  client-purchasable agents.
- Orchestration Agent is not the same as Head Agent.
- Head Agent remains an optional purchasable executive intelligence layer.
"""

from typing import Dict, List, Optional


AGENT_CATALOGUE: Dict[str, Dict[str, object]] = {
    # Purchasable client-facing agents
    "head_agent": {
        "name": "Head Agent",
        "category": "executive",
        "visibility": "purchasable",
        "role": "Executive intelligence layer that reviews agent outputs, flags weaknesses, summarises recommendations, and supports owner decision-making.",
    },
    "strategist_agent": {
        "name": "Strategist Agent",
        "category": "strategy",
        "visibility": "purchasable",
        "role": "Identifies strategic opportunities, positioning improvements, partnerships, diversification options, and growth pathways.",
    },
    "business_growth_partnerships_agent": {
        "name": "Business Growth & Partnerships Agent",
        "category": "growth",
        "visibility": "purchasable",
        "role": "Finds growth channels, partnership opportunities, referral opportunities, and business development pathways.",
    },
    "lead_generator_appointment_setter_agent": {
        "name": "Lead Generator / Appointment Setter Agent",
        "category": "sales",
        "visibility": "purchasable",
        "role": "Finds leads, qualifies prospects, prepares outreach, manages follow-ups, and supports appointment-setting workflows.",
    },
    "marketing_specialist_agent": {
        "name": "Marketing Specialist Agent",
        "category": "marketing",
        "visibility": "purchasable",
        "role": "Creates marketing campaigns, channel plans, offers, positioning, campaign calendars, and execution-ready campaign briefs.",
    },
    "social_media_manager_content_creator_agent": {
        "name": "Social Media Manager / Content Creator Agent",
        "category": "content",
        "visibility": "purchasable",
        "role": "Creates social content, captions, posting plans, content calendars, engagement ideas, and platform-specific creative direction.",
    },
    "seo_agent": {
        "name": "SEO Agent",
        "category": "seo",
        "visibility": "purchasable",
        "role": "Handles keyword strategy, SEO content planning, page optimisation, technical SEO recommendations, and local SEO improvement plans.",
    },
    "email_reply_agent": {
        "name": "Email Reply Agent",
        "category": "email",
        "visibility": "purchasable",
        "role": "Drafts context-aware inbound and outbound email replies, follow-ups, objection responses, and customer communication drafts.",
    },
    "crm_ai_agent": {
        "name": "CRM AI Agent",
        "category": "crm",
        "visibility": "purchasable",
        "role": "Manages CRM insights, lead scoring, pipeline recommendations, follow-up timing, segmentation, and CRM data improvement tasks.",
    },
    "sales_closer_agent": {
        "name": "Sales / Closer Agent",
        "category": "sales",
        "visibility": "purchasable",
        "role": "Supports quote follow-up, objection handling, proposal follow-up, closing assistance, and deal progression.",
    },
    "receptionist_agent": {
        "name": "Receptionist Agent",
        "category": "frontline",
        "visibility": "purchasable",
        "role": "Handles reception-style customer enquiries, intake, triage, appointment request handling, and front-desk communication support.",
    },
    "customer_support_agent": {
        "name": "Customer Support Agent",
        "category": "support",
        "visibility": "purchasable",
        "role": "Handles customer support responses, FAQs, issue triage, support summaries, and service recovery drafts.",
    },
    "ecommerce_agent": {
        "name": "Ecommerce Agent",
        "category": "ecommerce",
        "visibility": "purchasable",
        "role": "Supports ecommerce operations, product merchandising, conversion improvements, store optimisation, and ecommerce growth execution.",
    },
    "product_research_agent": {
        "name": "Product Research Agent",
        "category": "research",
        "visibility": "purchasable",
        "role": "Researches product opportunities, product-market fit signals, customer demand, product gaps, and product validation angles.",
    },
    "competitor_intelligence_agent": {
        "name": "Competitor Intelligence Agent",
        "category": "research",
        "visibility": "purchasable",
        "role": "Analyses competitors, positioning, offers, strengths, weaknesses, gaps, risks, and differentiation opportunities.",
    },
    "brand_strategy_agent": {
        "name": "Brand Strategy Agent",
        "category": "brand",
        "visibility": "purchasable",
        "role": "Develops brand positioning, tone, messaging, value proposition, differentiation, and customer perception strategy.",
    },
    "store_builder_agent": {
        "name": "Store Builder Agent",
        "category": "store",
        "visibility": "purchasable",
        "role": "Plans ecommerce store structure, product collections, user journeys, merchandising sections, and store build requirements.",
    },
    "website_landing_apps_agent": {
        "name": "Website / Landing Page / Apps Agent",
        "category": "development",
        "visibility": "purchasable",
        "role": "Creates website, landing page, app, and conversion-flow briefs, structures, copy blocks, and implementation-ready specifications.",
    },
    "product_development_agent": {
        "name": "Product Development Agent",
        "category": "product",
        "visibility": "purchasable",
        "role": "Supports product improvement, feature planning, offer packaging, product roadmap ideas, and customer-aligned product development.",
    },
    "product_copywriting_agent": {
        "name": "Product Copywriting Agent",
        "category": "copywriting",
        "visibility": "purchasable",
        "role": "Writes product descriptions, benefit-led copy, offer copy, product page copy, and conversion-focused ecommerce copy.",
    },
    "ugc_creative_agent": {
        "name": "UGC Creative Agent",
        "category": "creative",
        "visibility": "purchasable",
        "role": "Creates UGC video concepts, hooks, scripts, creator briefs, shot lists, and performance-focused creative angles.",
    },
    "product_image_agent": {
        "name": "Product Image Agent",
        "category": "media",
        "visibility": "purchasable",
        "role": "Creates product image direction, visual concepts, shot guidance, product presentation ideas, and image optimisation briefs.",
    },
    "paid_ads_agent": {
        "name": "Paid Ads Agent",
        "category": "advertising",
        "visibility": "purchasable",
        "role": "Creates paid advertising strategy, campaign structure, ad angles, audience ideas, and optimisation recommendations without approving spend increases.",
    },
    "analytics_optimisation_agent": {
        "name": "Analytics Optimisation Agent",
        "category": "analytics",
        "visibility": "purchasable",
        "role": "Analyses performance, funnel metrics, conversion issues, campaign results, and optimisation opportunities.",
    },
    "influencer_collaboration_agent": {
        "name": "Influencer Collaboration Agent",
        "category": "collaboration",
        "visibility": "purchasable",
        "role": "Identifies creator-fit opportunities, prepares outreach, follow-ups, collaboration briefs, and influencer campaign tracking support.",
    },
    "operations_manager_agent": {
        "name": "Operations Manager Agent",
        "category": "operations",
        "visibility": "purchasable",
        "role": "Coordinates operational workflows, process improvements, task planning, execution readiness, team handoffs, and day-to-day business efficiency recommendations.",
    },

    # Internal-only backend/system agents
    "orchestration_agent": {
        "name": "Orchestration Agent",
        "category": "system",
        "visibility": "internal",
        "role": "Internal backend coordination layer for routing, sequencing, dependency handling, and multi-agent execution control.",
    },
    "security_compliance_agent": {
        "name": "Security & Compliance Agent",
        "category": "system",
        "visibility": "internal",
        "role": "Internal governance, security, policy, compliance, and risk-control support agent.",
    },
    "integration_automation_agent": {
        "name": "Integration / Automation Agent",
        "category": "system",
        "visibility": "internal",
        "role": "Internal integration and automation support layer for backend workflow connectivity and tool routing.",
    },
}


AGENT_ALIASES: Dict[str, str] = {
    "master_orchestrator_agent": "orchestration_agent",
    "website_landing_page_agent": "website_landing_apps_agent",
    "custom_websites_landing_pages_apps_developer_agent": "website_landing_apps_agent",
    "websites_landing_pages_apps_agent": "website_landing_apps_agent",
    "product_image_direction_agent": "product_image_agent",
    "ad_creative_agent": "paid_ads_agent",
    "campaign_launch_agent": "paid_ads_agent",
    "email_marketing_agent": "marketing_specialist_agent",
    "creative_rotation_agent": "ugc_creative_agent",
    "fulfilment_agent": "ecommerce_agent",
    "marketplace_agent": "ecommerce_agent",
    "billing_licence_agent": "crm_ai_agent",
    "reporting_agent": "analytics_optimisation_agent",
    "quality_assurance_agent": "analytics_optimisation_agent",
    "integration_agent": "integration_automation_agent",
    "demo_trial_agent": "strategist_agent",
}


def normalize_agent_id(agent_name: str) -> str:
    cleaned = str(agent_name or "").strip()
    return AGENT_ALIASES.get(cleaned, cleaned)


def list_agents(include_internal: bool = True) -> List[str]:
    if include_internal:
        return list(AGENT_CATALOGUE.keys())
    return [
        agent_id
        for agent_id, details in AGENT_CATALOGUE.items()
        if details.get("visibility") == "purchasable"
    ]


def list_purchasable_agents() -> List[str]:
    return list_agents(include_internal=False)


def list_internal_agents() -> List[str]:
    return [
        agent_id
        for agent_id, details in AGENT_CATALOGUE.items()
        if details.get("visibility") == "internal"
    ]


def agent_exists(agent_name: str) -> bool:
    return normalize_agent_id(agent_name) in AGENT_CATALOGUE


def is_internal_agent(agent_name: str) -> bool:
    agent_id = normalize_agent_id(agent_name)
    details = AGENT_CATALOGUE.get(agent_id)
    return bool(details and details.get("visibility") == "internal")


def is_purchasable_agent(agent_name: str) -> bool:
    agent_id = normalize_agent_id(agent_name)
    details = AGENT_CATALOGUE.get(agent_id)
    return bool(details and details.get("visibility") == "purchasable")


def get_agent(agent_name: str) -> Dict[str, object]:
    agent_id = normalize_agent_id(agent_name)
    if agent_id not in AGENT_CATALOGUE:
        raise ValueError(f"Unknown agent: {agent_name}")
    details = dict(AGENT_CATALOGUE[agent_id])
    details["id"] = agent_id
    return details


def get_agent_display_name(agent_name: str) -> str:
    return str(get_agent(agent_name).get("name", normalize_agent_id(agent_name)))


def get_agent_role(agent_name: str) -> str:
    return str(get_agent(agent_name).get("role", ""))


def get_agent_category(agent_name: str) -> str:
    return str(get_agent(agent_name).get("category", "general"))


def get_agent_visibility(agent_name: str) -> str:
    return str(get_agent(agent_name).get("visibility", "purchasable"))


PURCHASABLE_AGENT_IDS: List[str] = list_purchasable_agents()
INTERNAL_AGENT_IDS: List[str] = list_internal_agents()
ALL_AGENT_IDS: List[str] = list_agents(include_internal=True)