from __future__ import annotations

from typing import Dict


SAFE_GENERATION_WORKFLOW_STAGES = {
    "client_live_execution",

    "marketing_campaign",
    "content_generation",
    "sales_follow_up",
    "crm_optimisation",
    "customer_support",
    "seo_strategy",
    "product_research",
    "competitor_analysis",
    "brand_strategy",
    "store_optimisation",
    "website_landing_page",
    "product_development",
    "product_copywriting",
    "ugc_creative",
    "product_image_direction",
    "paid_ads_strategy",
    "analytics_optimisation",
    "influencer_outreach",
    "reception_intake",
    "business_growth",
    "strategic_planning",
    "head_agent_review",
    "orchestration_review",
    "security_compliance_review",
    "integration_automation_review",
    "live_execution_readiness_test",
}

SAFE_GENERATION_ACTION_TYPES = {
    "content_generation",
    "marketing_campaign_execution",
    "strategy_generation",
    "draft_generation",
    "analysis_generation",
    "crm_recommendation",
    "support_response_generation",
    "seo_plan_generation",
    "sales_follow_up_generation",
    "website_brief_generation",
    "product_brief_generation",
    "creative_brief_generation",
    "analytics_report_generation",
    "influencer_outreach_generation",

    # Controlled execution-stack preparation actions.
    "create_shopify_product_page",
    "create_landing_page_brief",
    "create_ugc_video_brief",
    "create_product_image_brief",
    "create_ad_copy_brief",
    "prepare_email_campaign",
    "prepare_influencer_outreach",
    "prepare_customer_support_reply",
    "prepare_analytics_report",
    "execute_live_integration_action",
}

REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL = {
    "send_email",
    "send_sms",
    "create_crm_contact",
    "create_crm_opportunity",
    "update_crm_record",
    "publish_content",
    "launch_campaign",
    "website_deploy_execution",
    "billing_payment_execution",

    # Execution-stack owner-gated actions.
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
}

PROHIBITED_AUTONOMOUS_ACTION_TYPES = {
    "increase_ad_spend",
    "change_ad_budget",
    "change_campaign_budget",
    "scale_campaign_budget",
    "scale_campaign",
    "approve_contract",
    "approve_paid_collaboration",
    "purchase_inventory",
    "charge_customer",
    "change_subscription_price",
}

AGENT_DEFAULT_WORKFLOW_STAGE: Dict[str, str] = {
    "head_agent": "head_agent_review",
    "strategist_agent": "strategic_planning",
    "business_growth_partnerships_agent": "business_growth",
    "lead_generator_appointment_setter_agent": "sales_follow_up",
    "marketing_specialist_agent": "marketing_campaign",
    "social_media_manager_content_creator_agent": "content_generation",
    "seo_agent": "seo_strategy",
    "email_reply_agent": "content_generation",
    "crm_ai_agent": "crm_optimisation",
    "sales_closer_agent": "sales_follow_up",
    "receptionist_agent": "reception_intake",
    "customer_support_agent": "customer_support",
    "ecommerce_agent": "store_optimisation",
    "product_research_agent": "product_research",
    "competitor_intelligence_agent": "competitor_analysis",
    "brand_strategy_agent": "brand_strategy",
    "store_builder_agent": "store_optimisation",
    "website_landing_apps_agent": "website_landing_page",
    "product_development_agent": "product_development",
    "product_copywriting_agent": "product_copywriting",
    "ugc_creative_agent": "ugc_creative",
    "product_image_agent": "product_image_direction",
    "paid_ads_agent": "paid_ads_strategy",
    "analytics_optimisation_agent": "analytics_optimisation",
    "influencer_collaboration_agent": "influencer_outreach",
    "orchestration_agent": "orchestration_review",
    "security_compliance_agent": "security_compliance_review",
    "integration_automation_agent": "integration_automation_review",
}


def is_safe_generation_workflow_stage(workflow_stage: str) -> bool:
    return str(workflow_stage or "").strip() in SAFE_GENERATION_WORKFLOW_STAGES


def is_safe_generation_action_type(action_type: str) -> bool:
    return str(action_type or "").strip() in SAFE_GENERATION_ACTION_TYPES


def is_real_world_action_requiring_owner_approval(action_type: str) -> bool:
    return str(action_type or "").strip() in REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL


def is_prohibited_autonomous_action(action_type: str) -> bool:
    return str(action_type or "").strip() in PROHIBITED_AUTONOMOUS_ACTION_TYPES


def get_default_workflow_stage(agent_id: str) -> str:
    return AGENT_DEFAULT_WORKFLOW_STAGE.get(str(agent_id or "").strip(), "content_generation")


def registry_summary() -> Dict[str, object]:
    return {
        "success": True,
        "safe_generation_workflow_stage_count": len(SAFE_GENERATION_WORKFLOW_STAGES),
        "safe_generation_action_type_count": len(SAFE_GENERATION_ACTION_TYPES),
        "real_world_owner_approval_action_count": len(REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL),
        "prohibited_autonomous_action_count": len(PROHIBITED_AUTONOMOUS_ACTION_TYPES),
        "agent_default_workflow_count": len(AGENT_DEFAULT_WORKFLOW_STAGE),
    }
