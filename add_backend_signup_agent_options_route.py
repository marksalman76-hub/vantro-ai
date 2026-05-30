from pathlib import Path
from datetime import datetime

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("backend_signup_agent_options_route_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

route_block = '''
# Signup Agent Selection Package Options Route
@app.get("/signup-agent-selection/options/{plan}")
def signup_agent_selection_options(plan: str):
    clean_plan = str(plan or "starter").strip().lower()
    if clean_plan not in {"starter", "growth", "business", "enterprise"}:
        clean_plan = "starter"

    package_limits = {
        "starter": 3,
        "growth": 7,
        "business": 10,
        "enterprise": 27,
    }

    reserved_enterprise_only = {"head_agent", "orchestration_agent"}

    agents = [
        {"agent_id": "strategist_agent", "name": "Strategist Agent", "enterprise_only": False},
        {"agent_id": "business_growth_partnerships_agent", "name": "Business Growth & Partnerships Agent", "enterprise_only": False},
        {"agent_id": "lead_generator_appointment_setter_agent", "name": "Lead Generator / Appointment Setter Agent", "enterprise_only": False},
        {"agent_id": "marketing_specialist_agent", "name": "Marketing Specialist Agent", "enterprise_only": False},
        {"agent_id": "social_media_manager_content_creator_agent", "name": "Social Media Manager / Content Creator Agent", "enterprise_only": False},
        {"agent_id": "seo_agent", "name": "SEO Agent", "enterprise_only": False},
        {"agent_id": "email_reply_agent", "name": "Email Reply Agent", "enterprise_only": False},
        {"agent_id": "crm_ai_agent", "name": "CRM AI Agent", "enterprise_only": False},
        {"agent_id": "receptionist_agent", "name": "Receptionist Agent", "enterprise_only": False},
        {"agent_id": "custom_websites_landing_pages_apps_agent", "name": "Custom Websites, Landing Pages & Apps Agent", "enterprise_only": False},
        {"agent_id": "product_development_agent", "name": "Product Development Agent", "enterprise_only": False},
        {"agent_id": "ecommerce_agent", "name": "Ecommerce Agent", "enterprise_only": False},
        {"agent_id": "ugc_creative_agent", "name": "UGC Creative Agent", "enterprise_only": False},
        {"agent_id": "analytics_optimisation_agent", "name": "Analytics Optimisation Agent", "enterprise_only": False},
        {"agent_id": "analytics_intelligence_agent", "name": "Analytics Intelligence Agent", "enterprise_only": False},
        {"agent_id": "product_research_agent", "name": "Product Research Agent", "enterprise_only": False},
        {"agent_id": "ad_creative_agent", "name": "Ad Creative Agent", "enterprise_only": False},
        {"agent_id": "product_image_agent", "name": "Product Image Agent", "enterprise_only": False},
        {"agent_id": "influencer_collaboration_agent", "name": "Influencer Collaboration Agent", "enterprise_only": False},
        {"agent_id": "demo_trial_agent", "name": "Demo / Trial Agent", "enterprise_only": False},

        {"agent_id": "head_agent", "name": "Head Agent", "enterprise_only": True},
        {"agent_id": "orchestration_agent", "name": "Orchestration Agent", "enterprise_only": True},
        {"agent_id": "security_compliance_agent", "name": "Security & Compliance Agent", "enterprise_only": True},
        {"agent_id": "integration_automation_agent", "name": "Integration / Automation Agent", "enterprise_only": True},
        {"agent_id": "qa_testing_agent", "name": "QA / Testing Agent", "enterprise_only": True},
        {"agent_id": "billing_optimisation_agent", "name": "Billing Optimisation Agent", "enterprise_only": True},
        {"agent_id": "training_learning_agent", "name": "Training / Learning Agent", "enterprise_only": True},
    ]

    if clean_plan != "enterprise":
        selectable_agents = [a for a in agents if a["agent_id"] not in reserved_enterprise_only]
    else:
        selectable_agents = agents

    return {
        "success": True,
        "plan": clean_plan,
        "package_tier": clean_plan,
        "agent_limit": package_limits[clean_plan],
        "selection_locked_after_activation": True,
        "owner_approval_required_for_changes": True,
        "enterprise_only_agent_ids": sorted(list(reserved_enterprise_only)),
        "agents": selectable_agents,
        "agent_count": len(selectable_agents),
        "credential_values_exposed": False,
        "client_safe": True,
    }
'''

if "/signup-agent-selection/options/{plan}" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

print("BACKEND_SIGNUP_AGENT_OPTIONS_ROUTE_ADDED")
print("Backup:", backup)