"""
Unified Agent Registry — Single source of truth for the approved 27-agent catalogue.

Rules:
- Exactly 27 client-facing purchasable agents.
- Internal system layers are separate and never exposed as client-selectable agents.
- Package tiers control which agents a workspace can access.
- HITL levels are enforced at execution time, not here.
- Aliases preserve backward compatibility with legacy agent IDs.
"""

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Package tier constants
# ---------------------------------------------------------------------------
STARTER   = "starter"
GROWTH    = "growth"
BUSINESS  = "business"
ENTERPRISE = "enterprise"

TIER_ORDER = [STARTER, GROWTH, BUSINESS, ENTERPRISE]

# ---------------------------------------------------------------------------
# 27 Approved client-facing agents
# ---------------------------------------------------------------------------
AGENT_CATALOGUE: Dict[str, Dict] = {

    # ── Executive / Strategy / Research ────────────────────────────────────
    "head_agent": {
        "name": "Head Agent / CEO",
        "category": "Executive",
        "visibility": "purchasable",
        "architecture": "router+orchestration+dynamic_subagents",
        "hitl_default": "HITL-3",
        "min_package": ENTERPRISE,
        "credit_estimate": 10,
        "role": "Executive intelligence layer — interprets high-level business goals, selects the right specialist agents, coordinates multi-agent workflows, evaluates risk, and provides owner-safe strategic direction.",
        "capabilities": ["Multi-agent orchestration", "Strategic planning", "Risk evaluation", "Dynamic sub-agent spawning", "Owner briefings"],
    },
    "strategist_agent": {
        "name": "Strategist Agent",
        "category": "Strategy",
        "visibility": "purchasable",
        "architecture": "sequential_pipeline",
        "hitl_default": "HITL-1",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Creates business strategies, market positioning, offer frameworks, growth roadmaps, and execution plans tailored to the client's industry and goals.",
        "capabilities": ["Market positioning", "Growth roadmaps", "Offer frameworks", "Competitive strategy", "Execution plans"],
    },
    "business_growth_partnerships_agent": {
        "name": "Business Growth & Partnerships Agent",
        "category": "Strategy",
        "visibility": "purchasable",
        "architecture": "agent+mcp",
        "hitl_default": "HITL-2",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Finds partnership opportunities, referral strategies, affiliate ideas, collaboration plans, and outreach messaging for business development.",
        "capabilities": ["Partnership discovery", "Referral programs", "Affiliate strategy", "Outreach drafts", "Collaboration briefs"],
    },
    "research_agent": {
        "name": "Research Agent",
        "category": "Research",
        "visibility": "purchasable",
        "architecture": "sequential_parallel_pipeline",
        "hitl_default": "HITL-0",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Researches markets, competitors, customers, products, trends, and decision-support information. Separates verified facts from assumptions.",
        "capabilities": ["Market research", "Competitor analysis", "Customer insights", "Trend reports", "Decision briefs"],
    },
    "analytics_agent": {
        "name": "Analytics Agent",
        "category": "Research",
        "visibility": "purchasable",
        "architecture": "agent+mcp_analytics",
        "hitl_default": "HITL-0",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Interprets performance metrics, produces reports, identifies trends, and recommends improvements across sales, marketing, and operations.",
        "capabilities": ["Performance reports", "Funnel analysis", "Trend identification", "KPI dashboards", "Optimisation recommendations"],
    },

    # ── Sales / CRM / Intake ────────────────────────────────────────────────
    "lead_generator_agent": {
        "name": "Lead Generator Agent",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "agent+mcp+sequential_qualification",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Creates lead-generation strategies, ideal customer profiles, qualification criteria, lead magnets, and prospecting workflows.",
        "capabilities": ["ICP profiling", "Lead qualification", "Lead magnets", "Prospecting workflows", "Outreach sequences"],
    },
    "sales_closer_agent": {
        "name": "Sales Closer Agent",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "sequential_pipeline+mcp",
        "hitl_default": "HITL-2",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Creates sales scripts, objection handling guides, proposals, follow-up sequences, and closing strategies to drive deal progression.",
        "capabilities": ["Sales scripts", "Objection handling", "Proposal drafts", "Follow-up sequences", "Closing strategies"],
    },
    "crm_agent": {
        "name": "CRM Agent",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "agent+mcp+write_gates",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Organises contacts, pipeline stages, customer notes, segments, follow-up schedules, and CRM workflows with strict write-gating.",
        "capabilities": ["Pipeline management", "Contact organisation", "Segmentation", "Follow-up scheduling", "CRM workflows"],
    },
    "receptionist_agent": {
        "name": "Receptionist Agent",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "agent+mcp_calendar_crm",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Handles intake questions, appointment requests, lead qualification, FAQs, and front-office communication flows.",
        "capabilities": ["Intake handling", "FAQ responses", "Appointment requests", "Lead qualification", "Front-desk scripts"],
    },
    "demo_trial_agent": {
        "name": "Demo / Trial Agent",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "sequential_onboarding_pipeline",
        "hitl_default": "HITL-1",
        "min_package": BUSINESS,
        "credit_estimate": 2,
        "role": "Creates demos, walkthroughs, onboarding flows, product tours, trial conversion journeys, and activation message sequences.",
        "capabilities": ["Demo scripts", "Product tours", "Onboarding flows", "Trial conversion", "Activation sequences"],
    },

    # ── Marketing / Content / Ads ───────────────────────────────────────────
    "marketing_specialist_agent": {
        "name": "Marketing Specialist Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "router+sequential_campaign_pipeline",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Plans campaigns, funnels, messaging, offers, promotions, launches, and acquisition strategies across all channels.",
        "capabilities": ["Campaign planning", "Funnel design", "Offer creation", "Channel strategy", "Launch plans"],
    },
    "social_media_content_agent": {
        "name": "Social Media Content Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "agent+tools+sequential_content",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Creates social content ideas, captions, calendars, short-form video concepts, hooks, carousels, and platform-specific post structures.",
        "capabilities": ["Content calendars", "Captions", "Hook writing", "Platform strategies", "Carousel scripts"],
    },
    "seo_agent": {
        "name": "SEO Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "agent+mcp+sequential_audit",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Handles keyword strategy, SEO content structure, metadata, internal linking, technical recommendations, and organic growth planning.",
        "capabilities": ["Keyword strategy", "SEO content briefs", "Metadata optimisation", "Technical SEO", "Link strategy"],
    },
    "content_strategy_agent": {
        "name": "Content Strategy Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "sequential_planning+router",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Plans content pillars, calendars, themes, multi-channel campaigns, and long-form strategy across all content types.",
        "capabilities": ["Content pillars", "Editorial calendars", "Campaign themes", "Multi-channel plans", "Content briefs"],
    },
    "ads_optimisation_agent": {
        "name": "Ads Optimisation Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "agent+mcp_ads+router",
        "hitl_default": "HITL-3",
        "min_package": BUSINESS,
        "credit_estimate": 4,
        "role": "Plans and optimises paid ad campaigns, audiences, budgets, copy angles, creative tests, and landing page alignment. All spend requires HITL-3 approval.",
        "capabilities": ["Campaign planning", "Audience targeting", "Ad copy", "Creative briefs", "Budget recommendations"],
    },
    "influencer_outreach_agent": {
        "name": "Influencer Outreach Agent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "agent+mcp_outreach",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Plans influencer campaigns, creator briefs, outreach messages, UGC collaborations, and ambassador programs.",
        "capabilities": ["Creator briefs", "Outreach messages", "Campaign planning", "UGC collaboration", "Ambassador programs"],
    },

    # ── Media / Creative Production ─────────────────────────────────────────
    "ugc_media_agent": {
        "name": "UGC Media Agent",
        "category": "Media",
        "visibility": "purchasable",
        "architecture": "parallel_execution+shared_tools+router",
        "hitl_default": "HITL-3",
        "min_package": BUSINESS,
        "credit_estimate": 8,
        "role": "Creates UGC-style scripts, video concepts, creative briefs, ad videos, social clips, human/avatar media, and media generation plans. All provider spend requires HITL-3 approval.",
        "capabilities": ["UGC scripts", "Video concepts", "Creative briefs", "Avatar/human media", "Ad video planning"],
    },

    # ── Digital / Product / Ecommerce ───────────────────────────────────────
    "website_app_agent": {
        "name": "Website / App Agent",
        "category": "Digital",
        "visibility": "purchasable",
        "architecture": "sequential_pipeline+mcp_cms_code",
        "hitl_default": "HITL-2",
        "min_package": BUSINESS,
        "credit_estimate": 5,
        "role": "Plans websites, apps, landing pages, UX flows, page copy, conversion sections, and digital product structures. Deployment requires HITL-3.",
        "capabilities": ["Website planning", "Landing pages", "UX flows", "Page copy", "App specs"],
    },
    "product_development_agent": {
        "name": "Product Development Agent",
        "category": "Digital",
        "visibility": "purchasable",
        "architecture": "sequential_research_design",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Develops product ideas, features, MVPs, service packages, offer improvements, and customer-aligned product roadmaps.",
        "capabilities": ["Product ideation", "Feature planning", "MVP briefs", "Offer packaging", "Roadmaps"],
    },
    "ecommerce_agent": {
        "name": "Ecommerce Agent",
        "category": "Digital",
        "visibility": "purchasable",
        "architecture": "agent+mcp_ecommerce",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Creates product pages, merchandising ideas, product descriptions, upsells, bundles, ecommerce flows, and store conversion recommendations.",
        "capabilities": ["Product descriptions", "Merchandising", "Upsell flows", "Bundle strategies", "Conversion optimisation"],
    },

    # ── Customer / Retention / Reputation ───────────────────────────────────
    "customer_success_agent": {
        "name": "Customer Success Agent",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+mcp_crm_support",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Improves onboarding, customer health, support follow-up, retention workflows, renewal sequences, and satisfaction campaigns.",
        "capabilities": ["Onboarding flows", "Health checks", "Retention sequences", "Renewal campaigns", "Satisfaction surveys"],
    },
    "email_reply_agent": {
        "name": "Email Reply Agent",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+mcp_email",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Drafts context-aware replies, follow-ups, support responses, sales emails, and professional communication. Requires review before sending.",
        "capabilities": ["Email drafts", "Follow-up sequences", "Support replies", "Sales emails", "Professional comms"],
    },
    "retention_loyalty_agent": {
        "name": "Retention / Loyalty Agent",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+mcp_crm_email_ecommerce",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Creates loyalty programs, win-back flows, retention campaigns, referral incentives, and repeat-purchase lifecycle journeys.",
        "capabilities": ["Loyalty programs", "Win-back flows", "Referral incentives", "Lifecycle campaigns", "Retention analysis"],
    },
    "review_reputation_agent": {
        "name": "Review / Reputation Agent",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+review_support_tools",
        "hitl_default": "HITL-2",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Creates review replies, review request campaigns, reputation recovery workflows, testimonial requests, and customer feedback responses.",
        "capabilities": ["Review replies", "Review requests", "Reputation recovery", "Testimonial campaigns", "Feedback responses"],
    },

    # ── Operations / Finance / Automation ───────────────────────────────────
    "operations_agent": {
        "name": "Operations Agent",
        "category": "Operations",
        "visibility": "purchasable",
        "architecture": "sequential_process_pipeline",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 2,
        "role": "Creates SOPs, process maps, checklists, handoff templates, operational improvements, and quality-control workflows.",
        "capabilities": ["SOP creation", "Process maps", "Checklists", "Handoff templates", "Quality workflows"],
    },
    "finance_admin_agent": {
        "name": "Finance / Admin Agent",
        "category": "Operations",
        "visibility": "purchasable",
        "architecture": "agent+billing_admin_mcp",
        "hitl_default": "HITL-3",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Handles finance/admin drafting, invoice support, credit explanations, billing summaries, and administrative workflows. All money actions require HITL-3.",
        "capabilities": ["Invoice drafts", "Billing summaries", "Admin workflows", "Credit explanations", "Financial planning"],
    },
    "workflow_automation_agent": {
        "name": "Workflow Automation Agent",
        "category": "Operations",
        "visibility": "purchasable",
        "architecture": "agent+mcp+router+dynamic_subagents",
        "hitl_default": "HITL-3",
        "min_package": BUSINESS,
        "credit_estimate": 5,
        "role": "Designs automations, integration flows, trigger/action logic, handoffs, notifications, and operational automation systems. Live automations require HITL-3.",
        "capabilities": ["Automation design", "Integration flows", "Trigger/action logic", "Notification systems", "Workflow handoffs"],
    },
}


# ---------------------------------------------------------------------------
# Internal system layers (NOT client-visible, NOT selectable)
# ---------------------------------------------------------------------------
INTERNAL_AGENTS: Dict[str, Dict] = {
    "orchestration_agent": {
        "name": "Orchestration Agent",
        "category": "System",
        "maps_to": "head_agent",
        "role": "Hidden runtime planner and coordinator for routing, sequencing, and multi-agent execution control.",
    },
    "security_compliance_agent": {
        "name": "Security & Compliance Agent",
        "category": "System",
        "maps_to": "head_agent",
        "role": "Hidden governance, policy, compliance, and risk-control enforcement layer.",
    },
    "qa_testing_agent": {
        "name": "QA Testing Agent",
        "category": "System",
        "maps_to": "operations_agent",
        "role": "Hidden quality assurance and runtime verification layer.",
    },
    "integration_automation_agent": {
        "name": "Integration / Automation Agent",
        "category": "System",
        "maps_to": "workflow_automation_agent",
        "role": "Hidden integration execution layer for backend workflow connectivity and tool routing.",
    },
    "billing_optimisation_agent": {
        "name": "Billing Optimisation Agent",
        "category": "System",
        "maps_to": "finance_admin_agent",
        "role": "Hidden package, billing, and credit enforcement layer.",
    },
    "training_learning_agent": {
        "name": "Training / Learning Agent",
        "category": "System",
        "maps_to": "customer_success_agent",
        "role": "Hidden learning, memory, and feedback governance layer.",
    },
}


# ---------------------------------------------------------------------------
# Backward-compatibility aliases (old ID → current ID)
# ---------------------------------------------------------------------------
AGENT_ALIASES: Dict[str, str] = {
    # Old registry IDs
    "lead_generator_appointment_setter_agent": "lead_generator_agent",
    "social_media_manager_content_creator_agent": "social_media_content_agent",
    "crm_ai_agent": "crm_agent",
    "customer_support_agent": "customer_success_agent",
    "ugc_creative_agent": "ugc_media_agent",
    "paid_ads_agent": "ads_optimisation_agent",
    "analytics_optimisation_agent": "analytics_agent",
    "influencer_collaboration_agent": "influencer_outreach_agent",
    "website_landing_apps_agent": "website_app_agent",
    "website_landing_page_agent": "website_app_agent",
    "custom_websites_landing_pages_apps_developer_agent": "website_app_agent",
    "websites_landing_pages_apps_agent": "website_app_agent",
    "store_builder_agent": "ecommerce_agent",
    "product_research_agent": "research_agent",
    "competitor_intelligence_agent": "research_agent",
    "brand_strategy_agent": "strategist_agent",
    "product_copywriting_agent": "ecommerce_agent",
    "product_image_agent": "ugc_media_agent",
    # Legacy system aliases
    "master_orchestrator_agent": "orchestration_agent",
    "ad_creative_agent": "ads_optimisation_agent",
    "campaign_launch_agent": "ads_optimisation_agent",
    "email_marketing_agent": "marketing_specialist_agent",
    "creative_rotation_agent": "ugc_media_agent",
    "fulfilment_agent": "ecommerce_agent",
    "marketplace_agent": "ecommerce_agent",
    "billing_licence_agent": "crm_agent",
    "reporting_agent": "analytics_agent",
    "quality_assurance_agent": "analytics_agent",
    "integration_agent": "integration_automation_agent",
    "demo_trial_agent_alias": "demo_trial_agent",
}

# ---------------------------------------------------------------------------
# Package entitlement map: tier → set of agent IDs available
# ---------------------------------------------------------------------------
def _agents_for_tier(min_tier: str) -> bool:
    """Return True if agent's min_package is within the given tier."""
    pass  # used inline below


PACKAGE_AGENTS: Dict[str, List[str]] = {
    tier: [
        agent_id
        for agent_id, meta in AGENT_CATALOGUE.items()
        if TIER_ORDER.index(meta["min_package"]) <= TIER_ORDER.index(tier)
    ]
    for tier in TIER_ORDER
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def normalize_agent_id(agent_name: str) -> str:
    cleaned = str(agent_name or "").strip()
    return AGENT_ALIASES.get(cleaned, cleaned)


def list_agents(include_internal: bool = False) -> List[str]:
    ids = list(AGENT_CATALOGUE.keys())
    if include_internal:
        ids += list(INTERNAL_AGENTS.keys())
    return ids


def list_purchasable_agents() -> List[str]:
    return list(AGENT_CATALOGUE.keys())


def list_internal_agents() -> List[str]:
    return list(INTERNAL_AGENTS.keys())


def agents_for_package(package_tier: str) -> List[str]:
    """Return agent IDs available for a given package tier."""
    tier = package_tier.lower() if package_tier else STARTER
    if tier not in PACKAGE_AGENTS:
        return PACKAGE_AGENTS[STARTER]
    return PACKAGE_AGENTS[tier]


def agent_exists(agent_name: str) -> bool:
    normalized = normalize_agent_id(agent_name)
    return normalized in AGENT_CATALOGUE or normalized in INTERNAL_AGENTS


def is_internal_agent(agent_name: str) -> bool:
    return normalize_agent_id(agent_name) in INTERNAL_AGENTS


def is_purchasable_agent(agent_name: str) -> bool:
    return normalize_agent_id(agent_name) in AGENT_CATALOGUE


def get_agent(agent_name: str) -> Dict:
    agent_id = normalize_agent_id(agent_name)
    if agent_id in AGENT_CATALOGUE:
        details = dict(AGENT_CATALOGUE[agent_id])
        details["id"] = agent_id
        return details
    if agent_id in INTERNAL_AGENTS:
        details = dict(INTERNAL_AGENTS[agent_id])
        details["id"] = agent_id
        details["visibility"] = "internal"
        return details
    raise ValueError(f"Unknown agent: {agent_name!r}")


def get_agent_display_name(agent_name: str) -> str:
    return str(get_agent(agent_name).get("name", normalize_agent_id(agent_name)))


def get_agent_role(agent_name: str) -> str:
    return str(get_agent(agent_name).get("role", ""))


def get_agent_category(agent_name: str) -> str:
    return str(get_agent(agent_name).get("category", "General"))


def get_agent_hitl(agent_name: str) -> str:
    return str(get_agent(agent_name).get("hitl_default", "HITL-1"))


def get_agent_min_package(agent_name: str) -> str:
    return str(get_agent(agent_name).get("min_package", STARTER))


def get_agent_credit_estimate(agent_name: str) -> int:
    return int(get_agent(agent_name).get("credit_estimate", 1))


# Precomputed sets for fast lookups
PURCHASABLE_AGENT_IDS: List[str] = list_purchasable_agents()
INTERNAL_AGENT_IDS:   List[str] = list_internal_agents()
ALL_AGENT_IDS:        List[str] = list_agents(include_internal=True)

assert len(PURCHASABLE_AGENT_IDS) == 27, (
    f"Agent catalogue must contain exactly 27 purchasable agents, found {len(PURCHASABLE_AGENT_IDS)}"
)
