from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_package_agent_rule_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

old_lists = '''const STARTER_PACKAGE_AGENTS: string[] = [
  "product_research_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
];

const GROWTH_PACKAGE_AGENTS: string[] = [
  "product_research_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "crm_ai_agent",
  "email_reply_agent",
  "analytics_optimisation_agent",
];

const BUSINESS_PACKAGE_AGENTS: string[] = [
  "product_research_agent",
  "competitor_intelligence_agent",
  "brand_strategy_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "paid_ads_agent",
  "analytics_optimisation_agent",
  "email_reply_agent",
  "crm_ai_agent",
];

const DEFAULT_AGENTS: string[] = STARTER_PACKAGE_AGENTS;'''

new_lists = '''const DEFAULT_AGENTS: string[] = [
  "product_research_agent",
  "competitor_intelligence_agent",
  "brand_strategy_agent",
  "store_builder_agent",
  "website_landing_apps_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "paid_ads_agent",
  "analytics_optimisation_agent",
  "email_reply_agent",
  "crm_ai_agent",
  "seo_agent",
  "social_media_manager_content_creator_agent",
  "influencer_collaboration_agent",
  "lead_generator_appointment_setter_agent",
  "sales_closer_agent",
  "receptionist_agent",
  "product_development_agent",
  "ecommerce_agent",
  "customer_support_agent",
  "business_growth_partnerships_agent",
];'''

if old_lists not in src:
    raise SystemExit("ERROR: Old hardcoded package agent lists not found.")

src = src.replace(old_lists, new_lists, 1)

old_logic = '''const ENTERPRISE_PACKAGE_AGENTS: string[] = Object.keys(AGENT_DISPLAY_NAMES);

function getPackageAgentCatalogue(packageName: string, activeAgents?: string[]) {
  if (activeAgents && Array.isArray(activeAgents) && activeAgents.length > 0) {
    return activeAgents;
  }

  const normalisedPackage = String(packageName || "").toLowerCase();

  if (normalisedPackage.includes("enterprise")) return ENTERPRISE_PACKAGE_AGENTS;
  if (normalisedPackage.includes("business")) return BUSINESS_PACKAGE_AGENTS;
  if (normalisedPackage.includes("growth")) return GROWTH_PACKAGE_AGENTS;
  if (normalisedPackage.includes("starter")) return STARTER_PACKAGE_AGENTS;

  return STARTER_PACKAGE_AGENTS;
}

function getPackageAgentLimitLabel(packageName: string, visibleCount: number) {
  const normalisedPackage = String(packageName || "").toLowerCase();

  if (normalisedPackage.includes("enterprise")) return `${visibleCount} available`;
  if (normalisedPackage.includes("business")) return `${visibleCount}/10 available`;
  if (normalisedPackage.includes("growth")) return `${visibleCount}/7 available`;
  if (normalisedPackage.includes("starter")) return `${visibleCount}/3 available`;

  return `${visibleCount} available`;
}'''

new_logic = '''const ENTERPRISE_RESERVED_AGENT_IDS = new Set([
  "head_agent",
  "orchestration_agent",
  "multi_agent_orchestration_agent",
]);

const NON_ENTERPRISE_AGENT_CATALOGUE: string[] = Object.keys(AGENT_DISPLAY_NAMES).filter(
  (agentId) => !ENTERPRISE_RESERVED_AGENT_IDS.has(agentId)
);

const ENTERPRISE_PACKAGE_AGENTS: string[] = Object.keys(AGENT_DISPLAY_NAMES);

function getPackageAgentLimit(packageName: string) {
  const normalisedPackage = String(packageName || "").toLowerCase();

  if (normalisedPackage.includes("enterprise")) return null;
  if (normalisedPackage.includes("business")) return 10;
  if (normalisedPackage.includes("growth")) return 7;
  if (normalisedPackage.includes("starter")) return 3;

  return 3;
}

function getPackageAgentCatalogue(packageName: string, activeAgents?: string[]) {
  const normalisedPackage = String(packageName || "").toLowerCase();
  const allowedBaseCatalogue = normalisedPackage.includes("enterprise")
    ? ENTERPRISE_PACKAGE_AGENTS
    : NON_ENTERPRISE_AGENT_CATALOGUE;

  const cleanActiveAgents = (activeAgents || []).filter((agentId) =>
    allowedBaseCatalogue.includes(agentId)
  );

  if (cleanActiveAgents.length > 0) {
    return cleanActiveAgents;
  }

  return allowedBaseCatalogue;
}

function getPackageAgentLimitLabel(packageName: string, visibleCount: number) {
  const packageLimit = getPackageAgentLimit(packageName);

  if (packageLimit === null) return `${visibleCount} available`;

  return `${visibleCount}/${packageLimit} active`;
}'''

if old_logic not in src:
    raise SystemExit("ERROR: Old package catalogue logic block not found.")

src = src.replace(old_logic, new_logic, 1)

PAGE.write_text(src, encoding="utf-8")

print("PACKAGE_AGENT_CATALOGUE_RULES_FIXED")
print(f"Backup: {backup}")
print("Hardcoded Starter/Growth/Business agent lists removed:", all(x not in src for x in ["STARTER_PACKAGE_AGENTS", "GROWTH_PACKAGE_AGENTS", "BUSINESS_PACKAGE_AGENTS"]))
print("Non-enterprise catalogue installed:", "NON_ENTERPRISE_AGENT_CATALOGUE" in src)
print("Reserved enterprise-only agents installed:", "ENTERPRISE_RESERVED_AGENT_IDS" in src)
print("Right column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))