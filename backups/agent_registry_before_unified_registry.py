"""
Agent Registry

Defines the approved ecommerce agent catalogue and checks whether an agent
exists before runtime execution.
"""

from typing import Dict, List


AGENT_CATALOGUE: Dict[str, Dict[str, str]] = {
    "master_orchestrator_agent": {
        "name": "Master Orchestrator Agent",
        "category": "core",
    },
    "product_research_agent": {
        "name": "Product Research Agent",
        "category": "research",
    },
    "competitor_intelligence_agent": {
        "name": "Competitor Intelligence Agent",
        "category": "research",
    },
    "brand_strategy_agent": {
        "name": "Brand Strategy Agent",
        "category": "brand",
    },
    "store_builder_agent": {
        "name": "Store Builder Agent",
        "category": "store",
    },
    "website_landing_page_agent": {
        "name": "Website / Landing Page Agent",
        "category": "store",
    },
    "product_copywriting_agent": {
        "name": "Product Copywriting Agent",
        "category": "copywriting",
    },
    "ugc_creative_agent": {
        "name": "UGC Creative Agent",
        "category": "creative",
    },
    "product_image_direction_agent": {
        "name": "Product Image Direction Agent",
        "category": "media",
    },
    "ad_creative_agent": {
        "name": "Ad Creative Agent",
        "category": "advertising",
    },
    "campaign_launch_agent": {
        "name": "Campaign Launch Agent",
        "category": "advertising",
    },
    "analytics_optimisation_agent": {
        "name": "Analytics Optimisation Agent",
        "category": "analytics",
    },
    "creative_rotation_agent": {
        "name": "Creative Rotation Agent",
        "category": "creative",
    },
    "email_marketing_agent": {
        "name": "Email Marketing Agent",
        "category": "email",
    },
    "customer_support_agent": {
        "name": "Customer Support Agent",
        "category": "support",
    },
    "fulfilment_agent": {
        "name": "Fulfilment Agent",
        "category": "operations",
    },
    "influencer_collaboration_agent": {
        "name": "Influencer Collaboration Agent",
        "category": "collaboration",
    },
    "seo_agent": {
        "name": "SEO Agent",
        "category": "seo",
    },
    "marketplace_agent": {
        "name": "Marketplace Agent",
        "category": "saas",
    },
    "billing_licence_agent": {
        "name": "Billing and Licence Agent",
        "category": "billing",
    },
    "reporting_agent": {
        "name": "Reporting Agent",
        "category": "reporting",
    },
    "quality_assurance_agent": {
        "name": "Quality Assurance Agent",
        "category": "quality",
    },
    "integration_agent": {
        "name": "Integration Agent",
        "category": "integrations",
    },
    "security_compliance_agent": {
        "name": "Security and Compliance Agent",
        "category": "security",
    },
    "demo_trial_agent": {
        "name": "Demo / Trial Agent",
        "category": "demo",
    },
}


def list_agents() -> List[str]:
    return list(AGENT_CATALOGUE.keys())


def agent_exists(agent_name: str) -> bool:
    return agent_name in AGENT_CATALOGUE


def get_agent(agent_name: str) -> Dict[str, str]:
    if not agent_exists(agent_name):
        raise ValueError(f"Unknown agent: {agent_name}")
    return AGENT_CATALOGUE[agent_name]