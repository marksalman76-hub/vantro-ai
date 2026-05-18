from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_agent_display_names_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

insert_after = "const DEFAULT_AGENTS: string[] = [];\n"

helper = '''
const AGENT_DISPLAY_NAMES: Record<string, string> = {
  master_orchestrator_agent: "Master Orchestrator Agent",
  product_research_agent: "Product Research Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
  brand_strategy_agent: "Brand Strategy Agent",
  store_builder_agent: "Store Builder Agent",
  website_landing_apps_agent: "Website / Landing Page Agent",
  product_copywriting_agent: "Product Copywriting Agent",
  ugc_creative_agent: "UGC Creative Agent",
  product_image_agent: "Product Image Agent",
  paid_ads_agent: "Paid Ads Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  email_reply_agent: "Email Reply Agent",
  crm_ai_agent: "CRM AI Agent",
  seo_agent: "SEO Agent",
  social_media_manager_content_creator_agent: "Social Media Manager Agent",
  influencer_collaboration_agent: "Influencer Collaboration Agent",
  lead_generator_appointment_setter_agent: "Lead Generator / Appointment Setter Agent",
  sales_closer_agent: "Sales / Closer Agent",
  receptionist_agent: "Receptionist Agent",
  product_development_agent: "Product Development Agent",
  ecommerce_agent: "Ecommerce Agent",
  customer_support_agent: "Customer Support Agent",
  general_ecommerce_agent: "General Ecommerce Agent",
  business_growth_partnerships_agent: "Business Growth & Partnerships Agent",
};

function getAgentDisplayName(agentId: string) {
  return AGENT_DISPLAY_NAMES[agentId] ||
    agentId
      .replace(/_/g, " ")
      .replace(/\\b\\w/g, (letter) => letter.toUpperCase());
}
'''

if "function getAgentDisplayName(agentId: string)" not in text:
    text = text.replace(insert_after, insert_after + helper + "\n", 1)

text = text.replace(
    "{agent}",
    "{getAgentDisplayName(agent)}",
    1,
)

text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))"',
    'gridTemplateColumns: "minmax(260px,360px) minmax(320px,1fr)"',
    1,
)

text = text.replace(
    'padding: "9px 10px",',
    'padding: "11px 12px",',
    1,
)

text = text.replace(
    'fontSize: 12,',
    'fontSize: 13,',
    1,
)

path.write_text(text, encoding="utf-8")

print("CLIENT_AGENT_DISPLAY_NAMES_FIXED")
print(f"Backup: {backup}")