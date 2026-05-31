from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP = ROOT / "backups" / f"global_approved_agent_runtime_registry_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

APPROVED_BLOCK = '''APPROVED_GOVERNED_EXECUTION_AGENTS = {
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
}

'''

def main():
    text = MAIN.read_text(encoding="utf-8", errors="replace")

    if "APPROVED_GOVERNED_EXECUTION_AGENTS" not in text:
        marker = "class HealthResponse(BaseModel):"
        idx = text.find(marker)
        if idx == -1:
            raise RuntimeError("HealthResponse marker not found")
        text = text[:idx] + APPROVED_BLOCK + text[idx:]

    old = '''and requested_agent in {
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
            }'''

    new = "and requested_agent in APPROVED_GOVERNED_EXECUTION_AGENTS"

    if old in text:
        text = text.replace(old, new, 1)

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "main.py").write_text(MAIN.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    MAIN.write_text(text, encoding="utf-8")

    print("GLOBAL_APPROVED_AGENT_RUNTIME_REGISTRY_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN)

if __name__ == "__main__":
    main()