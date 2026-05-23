from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

backup = BACKUPS / f"client_page_before_agent_display_names_{timestamp}.tsx"
backup.write_text(client_page.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

text = client_page.read_text(encoding="utf-8", errors="ignore")

display_map = """
const AGENT_DISPLAY_NAMES: Record<string, string> = {
  head_agent: "Head Agent",
  strategist_agent: "Strategist Agent",
  business_growth_partnerships_agent: "Business Growth & Partnerships Agent",
  lead_generator_appointment_setter_agent: "Lead Generator / Appointment Setter Agent",
  marketing_specialist_agent: "Marketing Specialist Agent",
  social_media_manager_content_creator_agent: "Social Media Manager / Content Creator Agent",
  seo_agent: "SEO Agent",
  email_reply_agent: "Email Reply Agent",
  crm_ai_agent: "CRM AI Agent",
  sales_closer_agent: "Sales / Closer Agent",
  receptionist_agent: "Receptionist Agent",
  customer_support_agent: "Customer Support Agent",
  ecommerce_agent: "Ecommerce Agent",
  product_research_agent: "Product Research Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
  brand_strategy_agent: "Brand Strategy Agent",
  store_builder_agent: "Store Builder Agent",
  website_landing_apps_agent: "Website / Landing Page / Apps Agent",
  product_development_agent: "Product Development Agent",
  product_copywriting_agent: "Product Copywriting Agent",
  ugc_creative_agent: "UGC Creative Agent",
  product_image_agent: "Product Image Agent",
  paid_ads_agent: "Paid Ads Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  influencer_collaboration_agent: "Influencer Collaboration Agent",
};

function agentDisplayName(agentId: string): string {
  return AGENT_DISPLAY_NAMES[agentId] || agentId.replace(/_/g, " ");
}
"""

if "const AGENT_DISPLAY_NAMES" not in text:
    insert_after = text.find("const DEFAULT_AGENTS")
    if insert_after == -1:
        raise RuntimeError("Could not find DEFAULT_AGENTS anchor.")

    next_block = text.find("\n\n", insert_after)
    if next_block == -1:
        raise RuntimeError("Could not find insertion point after DEFAULT_AGENTS.")

    text = text[:next_block] + "\n" + display_map + text[next_block:]

text = text.replace("{agent}", "{agentDisplayName(agent)}")

client_page.write_text(text, encoding="utf-8")

print("CLIENT_AGENT_DISPLAY_NAMES_FIXED")
print(f"Backup: {backup}")