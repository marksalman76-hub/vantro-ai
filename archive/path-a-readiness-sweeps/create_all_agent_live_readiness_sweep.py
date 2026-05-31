from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "all_agent_live_readiness_sweep.cmd"

AGENTS = [
    "marketing_specialist_agent",
    "crm_ai_agent",
    "email_reply_agent",
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_appointment_setter_agent",
    "social_media_manager_content_creator_agent",
    "seo_agent",
    "sales_closer_agent",
    "receptionist_agent",
    "customer_support_agent",
    "ecommerce_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "website_landing_page_apps_agent",
    "product_development_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "paid_ads_agent",
    "analytics_optimisation_agent",
    "influencer_collaboration_agent",
]

lines = [
    '@echo off',
    'cd /d "C:\\Users\\User\\Desktop\\ecommerce-ai-agent-platform"',
    'set ADMIN_PLATFORM_TOKEN=2352d6b0a5e9f6cb76624b8373a041a9d04735af172ce0c5e88442676cb80c2f',
    'echo ALL_AGENT_LIVE_READINESS_SWEEP_STARTED',
]

for agent in AGENTS:
    lines += [
        f'echo ==================== {agent} ====================',
        (
            'curl -s -X POST https://api.trance-formation.com.au/run-agent '
            '-H "Authorization: Bearer %ADMIN_PLATFORM_TOKEN%" '
            '-H "Content-Type: application/json" '
            f'-d "{{\\"requested_agent\\":\\"{agent}\\",\\"workflow_stage\\":\\"specialist_execution\\",\\"action_type\\":\\"run_agent\\",\\"task\\":\\"Run a controlled one-sentence live provider readiness verification for this agent. Do not perform external actions. Do not spend. Return only a short confirmation.\\",\\"tenant_id\\":\\"owner_admin_test\\",\\"actor_role\\":\\"owner_admin\\",\\"customer_safe\\":true,\\"connected_integrations\\":[]}}"'
        ),
        'echo.',
    ]

lines += [
    'echo ALL_AGENT_LIVE_READINESS_SWEEP_COMPLETE',
]

OUT.write_text("\n".join(lines), encoding="utf-8")

print("ALL_AGENT_LIVE_READINESS_SWEEP_CREATED")
print("Run this next:")
print("all_agent_live_readiness_sweep.cmd")