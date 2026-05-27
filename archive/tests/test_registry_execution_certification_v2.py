import requests

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
        "workflow_stage": "marketing_campaign",
        "requested_agent": agent_id,
        "task": f"Create a premium execution-ready output for {agent_id}",
        "action_type": "marketing_campaign_execution",
        "owner_approved": True,
        "actor_role": "owner",
        "requested_credits": 1,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/run-agent",
            json=payload,
            headers=headers,
            timeout=90,
        )

        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        success = bool(data.get("success"))

        if response.status_code == 200 and success:
            passed.append(agent_id)
            print(f"{agent_id}: PASS")
        else:
            failed.append({
                "agent": agent_id,
                "status": response.status_code,
                "response": data,
            })
            print(f"{agent_id}: FAIL")

    except Exception as exc:
        failed.append({
            "agent": agent_id,
            "exception": str(exc),
        })
        print(f"{agent_id}: EXCEPTION")

print("\n")
print("REGISTRY_EXECUTION_CERTIFICATION_V2_RESULTS")
print("PASSED_COUNT", len(passed))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)

if len(failed) == 0:
    print("REGISTRY_EXECUTION_CERTIFICATION_V2_PASSED")