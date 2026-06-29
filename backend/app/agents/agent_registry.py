"""
Unified Agent Registry — Single source of truth for the approved 22-agent catalogue.

Rules:
- Exactly 22 client-facing purchasable agents.
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
# 22 Approved client-facing agents
# ---------------------------------------------------------------------------
AGENT_CATALOGUE: Dict[str, Dict] = {

    # ── Executive / Strategy / Research ────────────────────────────────────
    "head_agent": {
        "name": "Head Agent / CEO",
        "display_name": "Victoria Chen",
        "category": "Executive",
        "visibility": "purchasable",
        "architecture": "router+orchestration+dynamic_subagents",
        "hitl_default": "HITL-3",
        "min_package": STARTER,
        "credit_estimate": 10,
        "role": "Executive intelligence layer — interprets high-level business goals, selects the right specialist agents, coordinates multi-agent workflows, evaluates risk, and provides owner-safe strategic direction.",
        "capabilities": ["Multi-agent orchestration", "Strategic planning", "Risk evaluation", "Dynamic sub-agent spawning", "Owner briefings"],
    },
    "strategist_agent": {
        "name": "Strategist Agent",
        "display_name": "Marcus Rodriguez",
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
        "display_name": "Priya Kapoor",
        "category": "Strategy",
        "visibility": "purchasable",
        "architecture": "agent+mcp",
        "hitl_default": "HITL-2",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Finds partnership opportunities, referral strategies, affiliate ideas, collaboration plans, and outreach messaging for business development.",
        "capabilities": ["Partnership discovery", "Referral programs", "Affiliate strategy", "Outreach drafts", "Collaboration briefs"],
    },
    "research_analytics_agent": {
        "name": "Research & Analytics Agent",
        "display_name": "David Nakamura",
        "category": "Research",
        "visibility": "purchasable",
        "architecture": "agent+tools+mcp_search_analytics",
        "hitl_default": "HITL-0",
        "min_package": STARTER,
        "credit_estimate": 2,
        "role": "Combines market research, competitive intelligence, and data analytics in one agent. Gathers information from web sources and internal data, interprets metrics and KPIs, identifies trends, and delivers actionable insights — covering both research and analytics in one output.",
        "capabilities": ["Market research", "Competitive intelligence", "KPI analysis", "Trend identification", "Funnel analysis", "Insight summaries"],
    },

    # ── Sales / CRM / Intake ────────────────────────────────────────────────
    "lead_generator_agent": {
        "name": "Lead Generator Agent",
        "display_name": "Sarah Mitchell",
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
        "display_name": "James O'Brien",
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
        "display_name": "Elena Rossi",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "agent+mcp+write_gates",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 2,
        "role": "Organises contacts, pipeline stages, customer notes, segments, follow-up schedules, and CRM workflows with strict write-gating.",
        "capabilities": ["Pipeline management", "Contact organisation", "Segmentation", "Follow-up scheduling", "CRM workflows"],
    },
    "intake_trial_agent": {
        "name": "Intake & Trial Agent",
        "display_name": "Alex Thompson",
        "category": "Sales",
        "visibility": "purchasable",
        "architecture": "sequential_pipeline+router",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 2,
        "role": "Handles the full prospect intake pipeline: qualifying inbound enquiries, routing to the right team, booking discovery calls and demos, managing trial activations, and converting trial users to paying customers. Covers receptionist and demo/trial workflows in one agent.",
        "capabilities": ["Lead qualification", "Enquiry routing", "Demo booking", "Trial activation", "Onboarding handoff", "CRM entry"],
    },

    # ── Marketing / Content / Ads ───────────────────────────────────────────
    "marketing_specialist_agent": {
        "name": "Marketing Specialist Agent",
        "display_name": "Lisa Patel",
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
        "display_name": "Jordan Blake",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "agent+tools+sequential_content",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Creates social content ideas, captions, calendars, short-form video concepts, hooks, carousels, and platform-specific post structures.",
        "capabilities": ["Content calendars", "Captions", "Hook writing", "Platform strategies", "Carousel scripts"],
    },
    "seo_content_agent": {
        "name": "SEO & Content Agent",
        "display_name": "Sophie Laurent",
        "category": "Marketing",
        "visibility": "purchasable",
        "architecture": "sequential_pipeline+router",
        "hitl_default": "HITL-1",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Handles keyword strategy, SEO content briefs, metadata, technical recommendations, content pillars, editorial calendars, multi-channel content plans, and organic growth strategy. Covers the full SEO-to-content pipeline in one agent.",
        "capabilities": ["Keyword strategy", "SEO content briefs", "Editorial calendars", "Content pillars", "Technical SEO", "Organic growth plans"],
    },
    "ads_optimisation_agent": {
        "name": "Ads Optimisation Agent",
        "display_name": "Mikhail Sokolov",
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
        "display_name": "Jasmine Wu",
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
        "display_name": "Chris Anderson",
        "category": "Media",
        "visibility": "purchasable",
        "architecture": "parallel_execution+shared_tools+router",
        "hitl_default": "HITL-3",
        "min_package": GROWTH,
        "credit_estimate": 8,
        "role": "Creates UGC-style scripts, video concepts, creative briefs, ad videos, social clips, human/avatar media, and media generation plans. All provider spend requires HITL-3 approval.",
        "capabilities": ["UGC scripts", "Video concepts", "Creative briefs", "Avatar/human media", "Ad video planning"],
    },

    # ── Digital / Product / Ecommerce ───────────────────────────────────────
    "website_app_agent": {
        "name": "Website / App Agent",
        "display_name": "Emma Richardson",
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
        "display_name": "Gabriel Santos",
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
        "display_name": "Olivia Chen",
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
    "customer_lifecycle_agent": {
        "name": "Customer Lifecycle Agent",
        "display_name": "Rachel Kim",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+mcp_crm_email_ecommerce",
        "hitl_default": "HITL-2",
        "min_package": GROWTH,
        "credit_estimate": 3,
        "role": "Manages the full post-purchase customer journey: onboarding, health monitoring, retention playbooks, loyalty programmes, win-back flows, referral incentives, and renewal sequences. Covers customer success and retention in one agent.",
        "capabilities": ["Onboarding flows", "Health score models", "Retention playbooks", "Loyalty programmes", "Win-back flows", "Referral programmes"],
    },
    "email_reply_agent": {
        "name": "Email Reply Agent",
        "display_name": "Thomas Berg",
        "category": "Support",
        "visibility": "purchasable",
        "architecture": "agent+mcp_email",
        "hitl_default": "HITL-1",
        "min_package": STARTER,
        "credit_estimate": 1,
        "role": "Drafts context-aware replies, follow-ups, support responses, sales emails, and professional communication. Requires review before sending.",
        "capabilities": ["Email drafts", "Follow-up sequences", "Support replies", "Sales emails", "Professional comms"],
    },
    "review_reputation_agent": {
        "name": "Review / Reputation Agent",
        "display_name": "Nicole Moreau",
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
    "ops_automation_agent": {
        "name": "Ops & Automation Agent",
        "display_name": "Kevin O'Malley",
        "category": "Operations",
        "visibility": "purchasable",
        "architecture": "sequential_process_pipeline+agent+mcp+router",
        "hitl_default": "HITL-3",
        "min_package": STARTER,
        "credit_estimate": 4,
        "role": "Designs SOPs, process maps, checklists, and quality-control workflows — then specifies the automations that eliminate manual overhead. Covers process design and automation architecture in one agent. Live automation activation requires HITL-3.",
        "capabilities": ["SOP creation", "Process maps", "Automation design", "Integration flows", "Trigger/action logic", "Quality workflows"],
    },
    "finance_admin_agent": {
        "name": "Finance / Admin Agent",
        "display_name": "Yuki Tanaka",
        "category": "Operations",
        "visibility": "purchasable",
        "architecture": "agent+billing_admin_mcp",
        "hitl_default": "HITL-3",
        "min_package": BUSINESS,
        "credit_estimate": 3,
        "role": "Handles finance/admin drafting, invoice support, credit explanations, billing summaries, and administrative workflows. All money actions require HITL-3.",
        "capabilities": ["Invoice drafts", "Billing summaries", "Admin workflows", "Credit explanations", "Financial planning"],
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
        "maps_to": "ops_automation_agent",
        "role": "Hidden quality assurance and runtime verification layer.",
    },
    "integration_automation_agent": {
        "name": "Integration / Automation Agent",
        "category": "System",
        "maps_to": "ops_automation_agent",
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
        "maps_to": "customer_lifecycle_agent",
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
    "customer_support_agent": "customer_lifecycle_agent",
    "ugc_creative_agent": "ugc_media_agent",
    "paid_ads_agent": "ads_optimisation_agent",
    "analytics_optimisation_agent": "research_analytics_agent",
    "influencer_collaboration_agent": "influencer_outreach_agent",
    "website_landing_apps_agent": "website_app_agent",
    "website_landing_page_agent": "website_app_agent",
    "custom_websites_landing_pages_apps_developer_agent": "website_app_agent",
    "websites_landing_pages_apps_agent": "website_app_agent",
    "store_builder_agent": "ecommerce_agent",
    "product_research_agent": "research_analytics_agent",
    "competitor_intelligence_agent": "research_analytics_agent",
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
    "reporting_agent": "research_analytics_agent",
    "quality_assurance_agent": "research_analytics_agent",
    "integration_agent": "integration_automation_agent",
    "demo_trial_agent_alias": "intake_trial_agent",
    # Merged agent aliases
    "seo_agent": "seo_content_agent",
    "content_strategy_agent": "seo_content_agent",
    "operations_agent": "ops_automation_agent",
    "workflow_automation_agent": "ops_automation_agent",
    "customer_success_agent": "customer_lifecycle_agent",
    "retention_loyalty_agent": "customer_lifecycle_agent",
    # Merge: receptionist_agent + demo_trial_agent → intake_trial_agent
    "receptionist_agent": "intake_trial_agent",
    "demo_trial_agent": "intake_trial_agent",
    # Merge: research_agent + analytics_agent → research_analytics_agent
    "research_agent": "research_analytics_agent",
    "analytics_agent": "research_analytics_agent",
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

assert len(PURCHASABLE_AGENT_IDS) == 22, (
    f"Agent catalogue must contain exactly 22 purchasable agents, found {len(PURCHASABLE_AGENT_IDS)}"
)


# ---------------------------------------------------------------------------
# Platform-level financial governance policy
# ---------------------------------------------------------------------------
# These are PLATFORM CONSTANTS — they cannot be changed by agent config,
# user settings, or any runtime flag. They are enforced in:
#   - agent_executor.py  (prompt injection + output scanning)
#   - agent_worker.py    (output interception before job completion)
#   - routes/agents.py   (submission-time check against governance matrix)
#
# Rule: agents SUGGEST financial actions; humans APPROVE them.
# No agent may spend money, commit budget, scale paid resources, place orders,
# sign agreements, or trigger any other financial action autonomously.
AGENTS_MAY_NOT_SPEND           = True   # No agent may spend money autonomously
AGENTS_MAY_NOT_SCALE_PAID      = True   # No agent may scale paid resources autonomously
AGENTS_MAY_NOT_SIGN_AGREEMENTS = True   # No agent may sign or commit to agreements
AGENTS_SUGGEST_FINANCIALS_ONLY = True   # Agents suggest budgets/spend; humans approve


# ---------------------------------------------------------------------------
# Agent Governance — per-agent rules, quality specs, and team compatibility
# ---------------------------------------------------------------------------
AGENT_GOVERNANCE: Dict[str, Dict] = {

    # ── Executive / Strategy / Research ────────────────────────────────────

    "head_agent": {
        "team_role": "lead",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "strategic_alignment", "completeness", "risk_awareness", "timeliness"],
        "compatible_teams": ["campaign", "website_growth", "lead_growth", "retention", "product_launch"],
        "overlap_agents": ["strategist_agent", "marketing_specialist_agent"],
        "overlap_rule": "head_agent orchestrates across all domains; strategist_agent and marketing_specialist_agent handle dedicated deep-dives within their domains.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "strategic",
        "success_metrics": ["business goals achieved within defined scope", "multi-agent tasks completed without escalation", "owner briefings rated actionable"],
        "failure_modes": ["ambiguous goal interpretation leading to wrong agent selection", "cascading errors from misconfigured sub-agent chain", "scope creep causing runaway token spend"],
    },

    "strategist_agent": {
        "team_role": "lead",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["strategic_alignment", "completeness", "usefulness", "market_relevance", "clarity"],
        "compatible_teams": ["campaign", "website_growth", "lead_growth", "product_launch"],
        "overlap_agents": ["head_agent", "marketing_specialist_agent", "business_growth_partnerships_agent"],
        "overlap_rule": "strategist_agent focuses on pure business strategy and positioning; head_agent delegates cross-domain coordination; marketing_specialist_agent focuses on campaign execution.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "strategic",
        "success_metrics": ["strategy documents rated actionable by client", "roadmap clarity score high", "positioning differentiation clearly articulated"],
        "failure_modes": ["overly generic strategies lacking industry context", "plans without execution timelines", "missing competitive differentiation"],
    },

    "business_growth_partnerships_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["relevance", "usefulness", "completeness", "brand_fit", "timeliness"],
        "compatible_teams": ["lead_growth", "campaign", "product_launch"],
        "overlap_agents": ["lead_generator_agent", "influencer_outreach_agent", "strategist_agent"],
        "overlap_rule": "business_growth_partnerships_agent focuses on strategic partnership deals and referral programs; lead_generator_agent handles direct pipeline prospecting; influencer_outreach_agent handles creator-specific collaborations.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "strategic",
        "success_metrics": ["partnership opportunities identified and qualified", "outreach messaging conversion rates", "referral program structure completeness"],
        "failure_modes": ["partnerships proposed without audience alignment checks", "outreach templates that feel generic", "missing ROI framing for partnership proposals"],
    },

    "research_analytics_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "completeness", "timeliness", "source_quality", "relevance", "usefulness", "clarity"],
        "compatible_teams": ["campaign", "website_growth", "lead_growth", "product_launch", "retention"],
        "overlap_agents": ["strategist_agent", "ops_automation_agent"],
        "overlap_rule": "research_analytics_agent gathers external/market intelligence and interprets internal performance data in one output; strategist_agent converts research into actionable business strategy; ops_automation_agent focuses on process efficiency, not metric interpretation.",
        "spend_requires_approval": False,
        "scaling_requires_approval": False,
        "publication_requires_approval": False,
        "recommendation_type": "analytical",
        "success_metrics": ["research findings clearly distinguish facts from assumptions", "KPI reports delivered on schedule", "trend identifications confirmed by subsequent performance", "competitor and market coverage is comprehensive", "optimisation recommendations adopted and yield measurable lift"],
        "failure_modes": ["conflating unverified claims with verified facts", "research scope too broad causing analysis paralysis", "drawing conclusions from statistically insufficient data", "missing seasonality or external factors in trend analysis", "reporting metrics without context or benchmarks"],
    },

    # ── Sales / CRM / Intake ────────────────────────────────────────────────

    "lead_generator_agent": {
        "team_role": "lead",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["relevance", "accuracy", "completeness", "usefulness", "timeliness"],
        "compatible_teams": ["lead_growth", "campaign"],
        "overlap_agents": ["crm_agent", "sales_closer_agent", "business_growth_partnerships_agent"],
        "overlap_rule": "lead_generator_agent owns top-of-funnel ICP profiling and prospecting; crm_agent manages pipeline tracking and follow-up scheduling; sales_closer_agent takes leads once qualified and ready to close.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "tactical",
        "success_metrics": ["qualified lead volume generated per period", "ICP accuracy confirmed by sales team", "lead magnet conversion rates"],
        "failure_modes": ["targeting too broad an ICP reducing lead quality", "lead magnets misaligned with offer", "prospecting sequences too aggressive causing unsubscribes"],
    },

    "sales_closer_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["usefulness", "brand_fit", "completeness", "relevance", "clarity"],
        "compatible_teams": ["lead_growth"],
        "overlap_agents": ["lead_generator_agent", "crm_agent", "email_reply_agent"],
        "overlap_rule": "sales_closer_agent creates closing strategy and scripts; lead_generator_agent handles upstream prospecting; crm_agent tracks deal status; email_reply_agent drafts individual correspondence.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "tactical",
        "success_metrics": ["deal conversion rate improvement", "objection handling coverage completeness", "proposal quality rated high by sales team"],
        "failure_modes": ["generic scripts not tailored to the offer or industry", "objection handling missing the real buying blockers", "follow-up cadences too infrequent to maintain momentum"],
    },

    "crm_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "completeness", "timeliness", "usefulness", "data_integrity"],
        "compatible_teams": ["lead_growth", "retention"],
        "overlap_agents": ["lead_generator_agent", "customer_lifecycle_agent", "email_reply_agent"],
        "overlap_rule": "crm_agent manages pipeline data, segmentation, and workflow logic; lead_generator_agent defines the upstream ICP and prospecting; customer_lifecycle_agent designs post-purchase lifecycle campaigns.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "operational",
        "success_metrics": ["CRM data accuracy and completeness", "follow-up task completion rates", "pipeline stage progression velocity"],
        "failure_modes": ["write-gating bypassed leading to dirty data", "segmentation logic that creates overlap between audiences", "missing contact deduplication rules"],
    },

    "intake_trial_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "brand_fit", "timeliness", "clarity", "usefulness", "completeness", "relevance"],
        "compatible_teams": ["lead_growth", "retention", "product_launch"],
        "overlap_agents": ["customer_lifecycle_agent", "email_reply_agent", "sales_closer_agent", "marketing_specialist_agent"],
        "overlap_rule": "intake_trial_agent handles first-touch intake, enquiry routing, demo booking, and trial conversion in one pipeline; customer_lifecycle_agent manages post-activation health and retention; sales_closer_agent focuses on closing conversations; email_reply_agent handles ongoing correspondence.",
        "spend_requires_approval": False,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "operational",
        "success_metrics": ["intake response accuracy rated by staff", "appointment and demo booking conversion rate", "FAQ deflection rate reducing manual workload", "trial-to-paid conversion rate", "onboarding activation milestones reached"],
        "failure_modes": ["FAQ responses contradicting current offer or policy", "intake scripts that feel robotic or impersonal", "missing escalation path for complex queries", "demo scripts that showcase features rather than outcomes", "onboarding flows too complex for self-service", "activation sequences not personalised to use case"],
    },

    # ── Marketing / Content / Ads ───────────────────────────────────────────

    "marketing_specialist_agent": {
        "team_role": "both",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "completeness", "usefulness", "strategic_alignment", "timeliness"],
        "compatible_teams": ["campaign", "lead_growth", "product_launch"],
        "overlap_agents": ["strategist_agent", "ads_optimisation_agent", "seo_content_agent", "social_media_content_agent"],
        "overlap_rule": "marketing_specialist_agent plans campaigns holistically and coordinates channels; ads_optimisation_agent handles paid media execution; seo_content_agent owns long-form content planning and SEO strategy; strategist_agent owns top-level business positioning.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "strategic",
        "success_metrics": ["campaign launch readiness completeness", "funnel stage coverage across the campaign", "channel strategy alignment with ICP"],
        "failure_modes": ["campaigns not tied to a clear conversion goal", "over-reliance on single channel without diversification", "offer messaging inconsistency across touchpoints"],
    },

    "social_media_content_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "creativity", "engagement_potential", "completeness", "timeliness"],
        "compatible_teams": ["campaign", "product_launch", "retention"],
        "overlap_agents": ["seo_content_agent", "ugc_media_agent", "marketing_specialist_agent"],
        "overlap_rule": "social_media_content_agent writes platform-specific post content; seo_content_agent sets the high-level calendar, pillar strategy, and SEO direction; ugc_media_agent produces actual video/media assets.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "creative",
        "success_metrics": ["content calendar coverage completeness", "hook engagement rates on published posts", "platform-specific format compliance"],
        "failure_modes": ["hooks that don't stop the scroll", "content calendar not aligned to campaign themes", "platform-specific format rules ignored (e.g. aspect ratios, character limits)"],
    },

    "seo_content_agent": {
        "team_role": "lead",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "completeness", "timeliness", "technical_correctness", "usefulness", "brand_fit", "strategic_alignment"],
        "compatible_teams": ["website_growth", "campaign", "product_launch"],
        "overlap_agents": ["website_app_agent", "research_analytics_agent", "social_media_content_agent", "marketing_specialist_agent"],
        "overlap_rule": "seo_content_agent owns keyword strategy, metadata, technical SEO, content pillars, and editorial calendars; website_app_agent implements technical site changes; social_media_content_agent executes platform-specific post content; marketing_specialist_agent plans campaigns holistically.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "technical",
        "success_metrics": ["keyword rankings improvements within 90 days", "organic traffic trend positive", "editorial calendar adherence rate", "content pillar coverage across all funnel stages"],
        "failure_modes": ["keyword targets too competitive for domain authority level", "content pillars not differentiated from competitors", "editorial calendar too ambitious for team capacity", "technical recommendations not actioned due to dev dependency"],
    },

    "ads_optimisation_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "brand_fit", "usefulness", "strategic_alignment", "timeliness"],
        "compatible_teams": ["campaign", "lead_growth", "product_launch"],
        "overlap_agents": ["marketing_specialist_agent", "ugc_media_agent", "social_media_content_agent"],
        "overlap_rule": "ads_optimisation_agent handles paid media strategy, audience, and budget optimisation; marketing_specialist_agent owns holistic campaign coordination; ugc_media_agent produces creative assets for ads.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "tactical",
        "success_metrics": ["ROAS improvement relative to baseline", "cost-per-acquisition trending downward", "creative test insights implemented in next iteration"],
        "failure_modes": ["launching ads without HITL-3 spend approval", "audience targeting overlapping causing internal bid competition", "creatives not rotated leading to ad fatigue"],
    },

    "influencer_outreach_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "relevance", "usefulness", "completeness", "timeliness"],
        "compatible_teams": ["campaign", "product_launch"],
        "overlap_agents": ["ugc_media_agent", "business_growth_partnerships_agent", "social_media_content_agent"],
        "overlap_rule": "influencer_outreach_agent manages creator discovery, briefs, and outreach for paid/gifted campaigns; ugc_media_agent produces internal UGC media assets; business_growth_partnerships_agent handles strategic brand partnerships.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "tactical",
        "success_metrics": ["creator brief clarity and completeness", "outreach response rates", "campaign alignment with brand guidelines"],
        "failure_modes": ["creator selection not aligned to ICP audience", "briefs too restrictive killing authentic creator voice", "missing FTC disclosure requirements in outreach plan"],
    },

    # ── Media / Creative Production ─────────────────────────────────────────

    "ugc_media_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "creativity", "completeness", "engagement_potential", "technical_quality"],
        "compatible_teams": ["campaign", "product_launch"],
        "overlap_agents": ["social_media_content_agent", "ads_optimisation_agent", "influencer_outreach_agent"],
        "overlap_rule": "ugc_media_agent produces media assets (scripts, video concepts, creative briefs); social_media_content_agent writes post copy; ads_optimisation_agent determines where and how media is placed in paid campaigns.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "creative",
        "success_metrics": ["creative asset completion rate within brief scope", "ad creative CTR vs. industry benchmark", "HITL-3 approvals obtained before any provider spend"],
        "failure_modes": ["media generation triggered without HITL-3 approval", "UGC scripts not adapted for target platform format", "avatar/human media misaligned with brand tone"],
    },

    # ── Digital / Product / Ecommerce ───────────────────────────────────────

    "website_app_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["technical_correctness", "usefulness", "completeness", "brand_fit", "clarity"],
        "compatible_teams": ["website_growth", "product_launch"],
        "overlap_agents": ["seo_content_agent", "ecommerce_agent", "product_development_agent"],
        "overlap_rule": "website_app_agent plans and builds digital properties and UX flows; seo_content_agent provides technical and keyword guidance for those properties; ecommerce_agent focuses on store conversion and product page layer.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "technical",
        "success_metrics": ["page conversion rate improvement post-launch", "UX flow completion rates", "deployment approved and live without rollback"],
        "failure_modes": ["deployment triggered without HITL-3 approval", "UX flows designed without user journey mapping", "copy and design not aligned to conversion goal"],
    },

    "product_development_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["usefulness", "market_relevance", "completeness", "strategic_alignment", "clarity"],
        "compatible_teams": ["product_launch", "website_growth"],
        "overlap_agents": ["strategist_agent", "ecommerce_agent", "research_analytics_agent"],
        "overlap_rule": "product_development_agent translates market insights into product features and MVPs; strategist_agent provides the business strategy context; ecommerce_agent handles store and merchandising execution of the resulting product.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "strategic",
        "success_metrics": ["MVP brief completeness and actionability", "feature roadmap alignment with customer pain points", "offer packaging adoption by sales team"],
        "failure_modes": ["feature bloat in MVP reducing speed to market", "product roadmap not grounded in customer research", "missing pricing and packaging strategy in offer design"],
    },

    "ecommerce_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "usefulness", "completeness", "accuracy", "timeliness"],
        "compatible_teams": ["campaign", "product_launch", "website_growth"],
        "overlap_agents": ["website_app_agent", "marketing_specialist_agent", "customer_lifecycle_agent"],
        "overlap_rule": "ecommerce_agent optimises product pages, bundles, and store flows; website_app_agent handles site structure and UX architecture; customer_lifecycle_agent manages post-purchase lifecycle.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "tactical",
        "success_metrics": ["add-to-cart and checkout conversion rate improvements", "average order value increase via upsells and bundles", "product description quality rated high by merchandising team"],
        "failure_modes": ["product descriptions not SEO-optimised", "bundle logic not aligned to actual purchase behaviour", "upsell flows that interrupt rather than enhance purchase journey"],
    },

    # ── Customer / Retention / Reputation ───────────────────────────────────

    "customer_lifecycle_agent": {
        "team_role": "lead",
        "lead_agent_allowed": True,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["usefulness", "brand_fit", "completeness", "timeliness", "accuracy", "engagement_potential"],
        "compatible_teams": ["retention", "lead_growth", "campaign"],
        "overlap_agents": ["email_reply_agent", "intake_trial_agent", "crm_agent"],
        "overlap_rule": "customer_lifecycle_agent manages the full post-purchase journey including onboarding, health monitoring, loyalty programmes, and win-back flows; email_reply_agent handles individual correspondence drafts; crm_agent tracks segments and triggers campaigns.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "operational",
        "success_metrics": ["customer health score improvements", "churn rate reduction", "loyalty program enrolment rate", "win-back campaign reactivation rate", "satisfaction survey NPS uplift"],
        "failure_modes": ["health checks triggered too infrequently to catch at-risk customers", "onboarding flows not adapted to different customer segments", "loyalty incentives that erode margin without driving behaviour change", "win-back campaigns sent too late after churn event"],
    },

    "email_reply_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "clarity", "usefulness", "accuracy", "timeliness"],
        "compatible_teams": ["lead_growth", "retention", "campaign"],
        "overlap_agents": ["crm_agent", "customer_lifecycle_agent", "marketing_specialist_agent"],
        "overlap_rule": "email_reply_agent drafts individual emails and sequences; crm_agent tracks the contact and schedules follow-up; marketing_specialist_agent plans broadcast email campaigns.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "operational",
        "success_metrics": ["email reply quality rated high by reviewing staff", "follow-up sequence open and reply rates", "tone and brand voice consistency across drafts"],
        "failure_modes": ["sending emails without human review (HITL bypass)", "generic templates not personalised to recipient context", "follow-up sequences that feel spammy or too high frequency"],
    },

    "review_reputation_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["brand_fit", "accuracy", "timeliness", "usefulness", "clarity"],
        "compatible_teams": ["retention", "campaign"],
        "overlap_agents": ["customer_lifecycle_agent", "social_media_content_agent"],
        "overlap_rule": "review_reputation_agent handles public review responses and reputation campaigns; customer_lifecycle_agent manages private satisfaction, health, and loyalty workflows; social_media_content_agent creates brand-building social content.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": True,
        "recommendation_type": "operational",
        "success_metrics": ["average review rating improvement over 90 days", "review request campaign response rate", "reputation recovery case resolution time"],
        "failure_modes": ["review replies that sound defensive or inauthentic", "review requests sent at wrong point in customer journey", "negative review escalations not flagged for human handling"],
    },

    # ── Operations / Finance / Automation ───────────────────────────────────

    "ops_automation_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": True,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "completeness", "usefulness", "clarity", "timeliness", "technical_correctness"],
        "compatible_teams": ["lead_growth", "retention", "website_growth"],
        "overlap_agents": ["finance_admin_agent", "crm_agent"],
        "overlap_rule": "ops_automation_agent creates SOPs, process maps, and designs automated system integrations and trigger/action flows; finance_admin_agent handles finance-specific admin processes with HITL-3 money-action gating; crm_agent configures CRM-specific workflow rules.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "operational",
        "success_metrics": ["SOP adoption rate by team", "process map completeness and usability rating", "automation error rate below threshold in production", "manual task hours eliminated per automation deployed", "HITL-3 approval obtained before any live automation activation"],
        "failure_modes": ["live automations activated without HITL-3 approval", "SOPs written at wrong abstraction level for the target audience", "trigger/action logic not tested with edge cases", "integration flows missing error handling and fallback notifications"],
    },

    "finance_admin_agent": {
        "team_role": "supporting",
        "lead_agent_allowed": False,
        "supporting_agent_allowed": True,
        "can_spawn_subagents": False,
        "weekly_report_enabled": True,
        "quality_dimensions": ["accuracy", "completeness", "timeliness", "data_integrity", "clarity"],
        "compatible_teams": ["lead_growth", "retention"],
        "overlap_agents": ["ops_automation_agent"],
        "overlap_rule": "finance_admin_agent handles finance/billing drafts and admin workflows with strict HITL-3 money-action gating; ops_automation_agent handles non-financial process design and system-level automation flows.",
        "spend_requires_approval": True,
        "scaling_requires_approval": True,
        "publication_requires_approval": False,
        "recommendation_type": "operational",
        "success_metrics": ["invoice and billing accuracy rate", "admin workflow turnaround time", "HITL-3 approval compliance rate on money actions"],
        "failure_modes": ["financial actions executed without HITL-3 approval", "billing summaries with calculation errors", "admin workflows not accounting for compliance or audit trail requirements"],
    },

}


# ---------------------------------------------------------------------------
# Platform-level pre-built team templates
# ---------------------------------------------------------------------------
PLATFORM_TEAM_TEMPLATES: List[Dict] = [
    {
        "id": "campaign_team",
        "name": "Campaign Team",
        "description": "Full campaign execution: strategy, content, media, and paid ads",
        "lead_agent_id": "marketing_specialist_agent",
        "agent_ids": ["marketing_specialist_agent", "social_media_content_agent", "ugc_media_agent", "ads_optimisation_agent"],
        "min_package": GROWTH,
        "is_platform": True,
    },
    {
        "id": "website_growth_team",
        "name": "Website Growth Team",
        "description": "Drive organic growth: SEO, content, website optimisation, and analytics",
        "lead_agent_id": "seo_content_agent",
        "agent_ids": ["seo_content_agent", "website_app_agent", "research_analytics_agent"],
        "min_package": GROWTH,
        "is_platform": True,
    },
    {
        "id": "lead_growth_team",
        "name": "Lead Growth Team",
        "description": "Build and convert pipeline: lead gen, CRM, sales, and email",
        "lead_agent_id": "lead_generator_agent",
        "agent_ids": ["lead_generator_agent", "crm_agent", "sales_closer_agent", "email_reply_agent"],
        "min_package": GROWTH,
        "is_platform": True,
    },
    {
        "id": "retention_team",
        "name": "Retention Team",
        "description": "Keep customers: lifecycle management, loyalty programs, email, and analytics",
        "lead_agent_id": "customer_lifecycle_agent",
        "agent_ids": ["customer_lifecycle_agent", "email_reply_agent", "research_analytics_agent"],
        "min_package": GROWTH,
        "is_platform": True,
    },
    {
        "id": "product_launch_team",
        "name": "Product Launch Team",
        "description": "Launch new products: strategy, development, marketing, social, and ecommerce",
        "lead_agent_id": "strategist_agent",
        "agent_ids": ["strategist_agent", "product_development_agent", "marketing_specialist_agent", "social_media_content_agent", "ecommerce_agent"],
        "min_package": BUSINESS,
        "is_platform": True,
    },
]


# ---------------------------------------------------------------------------
# Governance helper functions
# ---------------------------------------------------------------------------

def get_agent_governance(agent_name: str) -> Dict:
    """Return governance spec for an agent. Returns empty dict if not found."""
    agent_id = normalize_agent_id(agent_name)
    return dict(AGENT_GOVERNANCE.get(agent_id, {}))


def can_be_lead_agent(agent_name: str) -> bool:
    return bool(get_agent_governance(agent_name).get("lead_agent_allowed", True))


def can_spawn_subagents(agent_name: str) -> bool:
    return bool(get_agent_governance(agent_name).get("can_spawn_subagents", False))


def get_compatible_teams(agent_name: str) -> List[str]:
    return list(get_agent_governance(agent_name).get("compatible_teams", []))


def get_team_role(agent_name: str) -> str:
    return str(get_agent_governance(agent_name).get("team_role", "supporting"))
