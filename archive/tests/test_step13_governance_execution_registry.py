import requests

from backend.app.core.governance_execution_registry import (
    registry_summary,
    get_default_workflow_stage,
)

BASE_URL = "http://127.0.0.1:8000"

AGENTS = [
    "head_agent",
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_appointment_setter_agent",
    "marketing_specialist_agent",
    "social_media_manager_content_creator_agent",
    "seo_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "sales_closer_agent",
    "receptionist_agent",
    "customer_support_agent",
    "ecommerce_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "website_landing_apps_agent",
    "product_development_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "paid_ads_agent",
    "analytics_optimisation_agent",
    "influencer_collaboration_agent",
]

print("GOVERNANCE_REGISTRY_SUMMARY", registry_summary())

headers = {
    "Content-Type": "application/json",
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "owner",
}

passed = []
failed = []

for agent_id in AGENTS:
    payload = {
        "tenant_id": "client_demo_001",
        "workflow_stage": get_default_workflow_stage(agent_id),
        "requested_agent": agent_id,
        "task": f"Create a premium real-world task-ready output for {agent_id}.",
        "action_type": "content_generation",
        "owner_approved": True,
        "actor_role": "owner",
        "requested_credits": 1,
    }

    response = requests.post(f"{BASE_URL}/run-agent", json=payload, headers=headers, timeout=90)

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    if response.status_code == 200 and data.get("success") is True:
        passed.append(agent_id)
        print(f"{agent_id}: PASS")
    else:
        failed.append({"agent": agent_id, "status": response.status_code, "response": data})
        print(f"{agent_id}: FAIL")

print("STEP_13_EXECUTION_CERTIFICATION_RESULTS")
print("PASSED_COUNT", len(passed))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)

if not failed:
    print("STEP_13_ALL_25_AGENTS_EXECUTION_READY")
