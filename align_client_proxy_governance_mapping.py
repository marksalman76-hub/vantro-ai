from pathlib import Path
from datetime import datetime
import shutil

backend_target = Path("backend/app/core/governance_execution_registry.py")
frontend_target = Path("frontend/src/app/api/run-agent/route.ts")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backend_backup = backup_dir / f"governance_registry_before_operations_manager_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
frontend_backup = backup_dir / f"run_agent_route_before_governance_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"

shutil.copy2(backend_target, backend_backup)
shutil.copy2(frontend_target, frontend_backup)

backend = backend_target.read_text(encoding="utf-8")
frontend = frontend_target.read_text(encoding="utf-8")

if '"operations_manager_agent": "store_optimisation",' not in backend:
    marker = '    "influencer_collaboration_agent": "influencer_outreach",\n'
    insert = marker + '    "operations_manager_agent": "store_optimisation",\n'
    if marker not in backend:
        raise RuntimeError("Could not find backend operations insertion marker.")
    backend = backend.replace(marker, insert, 1)

mapping_block = '''const AGENT_WORKFLOW_STAGE_MAP: Record<string, string> = {
  head_agent: "head_agent_review",
  strategist_agent: "strategic_planning",
  business_growth_partnerships_agent: "business_growth",
  lead_generator_appointment_setter_agent: "sales_follow_up",
  marketing_specialist_agent: "marketing_campaign",
  social_media_manager_content_creator_agent: "content_generation",
  seo_agent: "seo_strategy",
  email_reply_agent: "content_generation",
  crm_ai_agent: "crm_optimisation",
  sales_closer_agent: "sales_follow_up",
  receptionist_agent: "reception_intake",
  customer_support_agent: "customer_support",
  ecommerce_agent: "store_optimisation",
  product_research_agent: "product_research",
  competitor_intelligence_agent: "competitor_analysis",
  brand_strategy_agent: "brand_strategy",
  store_builder_agent: "store_optimisation",
  website_landing_apps_agent: "website_landing_page",
  product_development_agent: "product_development",
  product_copywriting_agent: "product_copywriting",
  ugc_creative_agent: "ugc_creative",
  product_image_agent: "product_image_direction",
  paid_ads_agent: "paid_ads_strategy",
  analytics_optimisation_agent: "analytics_optimisation",
  influencer_collaboration_agent: "influencer_outreach",
  orchestration_agent: "orchestration_review",
  operations_manager_agent: "store_optimisation",
};

const AGENT_ACTION_TYPE_MAP: Record<string, string> = {
  head_agent: "analysis_generation",
  strategist_agent: "strategy_generation",
  business_growth_partnerships_agent: "strategy_generation",
  lead_generator_appointment_setter_agent: "sales_follow_up_generation",
  marketing_specialist_agent: "marketing_campaign_execution",
  social_media_manager_content_creator_agent: "content_generation",
  seo_agent: "seo_plan_generation",
  email_reply_agent: "draft_generation",
  crm_ai_agent: "crm_recommendation",
  sales_closer_agent: "sales_follow_up_generation",
  receptionist_agent: "support_response_generation",
  customer_support_agent: "support_response_generation",
  ecommerce_agent: "analysis_generation",
  product_research_agent: "analysis_generation",
  competitor_intelligence_agent: "analysis_generation",
  brand_strategy_agent: "strategy_generation",
  store_builder_agent: "website_brief_generation",
  website_landing_apps_agent: "website_brief_generation",
  product_development_agent: "product_brief_generation",
  product_copywriting_agent: "content_generation",
  ugc_creative_agent: "creative_brief_generation",
  product_image_agent: "create_product_image_brief",
  paid_ads_agent: "create_ad_copy_brief",
  analytics_optimisation_agent: "analytics_report_generation",
  influencer_collaboration_agent: "influencer_outreach_generation",
  orchestration_agent: "analysis_generation",
  operations_manager_agent: "analysis_generation",
};

function getDefaultWorkflowStage(agentId: string) {
  return AGENT_WORKFLOW_STAGE_MAP[agentId] || "content_generation";
}

function getDefaultActionType(agentId: string) {
  return AGENT_ACTION_TYPE_MAP[agentId] || "analysis_generation";
}

'''

if "const AGENT_WORKFLOW_STAGE_MAP" not in frontend:
    frontend = frontend.replace(
        'const BACKEND_AUTH_TOKEN =\n  process.env.ADMIN_PLATFORM_TOKEN ||\n  process.env.ADMIN_AUTH_SECRET ||\n  process.env.ADMIN_AUTH_TOKEN ||\n  process.env.BACKEND_AUTH_TOKEN ||\n  "";',
        'const BACKEND_AUTH_TOKEN =\n  process.env.ADMIN_PLATFORM_TOKEN ||\n  process.env.ADMIN_AUTH_SECRET ||\n  process.env.ADMIN_AUTH_TOKEN ||\n  process.env.BACKEND_AUTH_TOKEN ||\n  "";\n\n' + mapping_block,
        1,
    )

frontend = frontend.replace(
    '      workflow_stage: body?.workflow_stage || "client_workspace_execution",\n      action_type: body?.action_type || "agent_execution_request",',
    '      workflow_stage: body?.workflow_stage || getDefaultWorkflowStage(primaryAgent || selectedAgents[0]),\n      action_type: body?.action_type || getDefaultActionType(primaryAgent || selectedAgents[0]),',
)

backend_target.write_text(backend, encoding="utf-8")
frontend_target.write_text(frontend, encoding="utf-8")

print("CLIENT_PROXY_GOVERNANCE_MAPPING_ALIGNED")
print("Backend backup:", backend_backup)
print("Frontend backup:", frontend_backup)