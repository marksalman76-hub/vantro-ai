from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_package_aware_agent_catalogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

old_default = '''const DEFAULT_AGENTS: string[] = [
  "product_research_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "crm_ai_agent",
];'''

new_default = '''const STARTER_PACKAGE_AGENTS: string[] = [
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

if old_default not in src:
    raise SystemExit("ERROR: DEFAULT_AGENTS block not found.")

src = src.replace(old_default, new_default, 1)

old_after_display = '''    business_growth_partnerships_agent: "Business Growth & Partnerships Agent",
};

function getAgentDisplayName(agentId: string) {'''

new_after_display = '''    business_growth_partnerships_agent: "Business Growth & Partnerships Agent",
};

const ENTERPRISE_PACKAGE_AGENTS: string[] = Object.keys(AGENT_DISPLAY_NAMES);

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
}

function getAgentDisplayName(agentId: string) {'''

if old_after_display not in src:
    raise SystemExit("ERROR: AGENT_DISPLAY_NAMES closing block not found.")

src = src.replace(old_after_display, new_after_display, 1)

old_runtime = '''  const accountPackage = account?.package_name || account?.package || "Active workspace";
  const accountStatus = account?.status || "active";
  const activeAgentCount = account?.active_agents?.length || 0;'''

new_runtime = '''  const accountPackage = account?.package_name || account?.package || "Starter";
  const visibleAgentCatalogue = getPackageAgentCatalogue(accountPackage, account?.active_agents);
  const visibleAgentCount = visibleAgentCatalogue.length;
  const packageAgentLimitLabel = getPackageAgentLimitLabel(accountPackage, visibleAgentCount);
  const accountStatus = account?.status || "active";
  const activeAgentCount = visibleAgentCount;'''

if old_runtime not in src:
    raise SystemExit("ERROR: accountPackage runtime block not found.")

src = src.replace(old_runtime, new_runtime, 1)

old_label = '''                <div style={labelStyle}>Active agents</div>
                <div style={{ display: "grid", gap: 7, maxHeight: 268, overflowY: "auto", paddingRight: 4 }}>
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {'''

new_label = '''                <div style={{ ...labelStyle, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                  <span>Active agents</span>
                  <span style={{ color: "var(--color-brand)", fontWeight: 900 }}>{packageAgentLimitLabel}</span>
                </div>
                <div style={{ display: "grid", gap: 7, maxHeight: visibleAgentCount <= 3 ? "none" : 268, overflowY: visibleAgentCount <= 3 ? "visible" : "auto", paddingRight: visibleAgentCount <= 3 ? 0 : 4 }}>
                  {visibleAgentCatalogue.map((agent) => {'''

if old_label not in src:
    raise SystemExit("ERROR: left active agents render block not found.")

src = src.replace(old_label, new_label, 1)

PAGE.write_text(src, encoding="utf-8")

print("PACKAGE_AWARE_AGENT_CATALOGUE_WIRED")
print(f"Backup: {backup}")
print("Starter agents:", src.count("STARTER_PACKAGE_AGENTS"))
print("Growth agents:", src.count("GROWTH_PACKAGE_AGENTS"))
print("Business agents:", src.count("BUSINESS_PACKAGE_AGENTS"))
print("Enterprise agents:", src.count("ENTERPRISE_PACKAGE_AGENTS"))
print("Visible catalogue installed:", "visibleAgentCatalogue.map" in src)
print("Right column untouched:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))