from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_enterprise_detection_27_catalogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

# Add missing enterprise-level agents if not already present.
insert_after = '''    business_growth_partnerships_agent: "Business Growth & Partnerships Agent",'''
extra_agents = '''
  head_agent: "Head Agent",
  strategist_agent: "Strategist Agent",
  orchestration_agent: "Orchestration Agent",
  marketing_specialist_agent: "Marketing Specialist Agent",
  operations_manager_agent: "Operations Manager Agent",'''

if "head_agent:" not in src:
    src = src.replace(insert_after, insert_after + extra_agents, 1)

old_enterprise_check = '''  const isEnterprisePackage = String(accountPackage || "").toLowerCase().includes("enterprise");'''

new_enterprise_check = '''  const isEnterprisePackage =
    String(accountPackage || "").toLowerCase().includes("enterprise") ||
    visibleAgentCount >= 20;'''

if old_enterprise_check not in src:
    raise SystemExit("ERROR: isEnterprisePackage block not found.")

src = src.replace(old_enterprise_check, new_enterprise_check, 1)

old_label = '''  if (normalisedPackage.includes("enterprise")) {
    return `${visibleCount}/${visibleCount} available`;
  }'''

new_label = '''  if (normalisedPackage.includes("enterprise") || visibleCount >= 20) {
    return `27/27 available`;
  }'''

if old_label not in src:
    raise SystemExit("ERROR: enterprise label block not found.")

src = src.replace(old_label, new_label, 1)

PAGE.write_text(src, encoding="utf-8")

print("ENTERPRISE_DETECTION_AND_27_CATALOGUE_FIXED")
print(f"Backup: {backup}")
print("Head agent installed:", "head_agent" in src)
print("Strategist installed:", "strategist_agent" in src)
print("Enterprise active count fallback installed:", "visibleAgentCount >= 20" in src)
print("Enterprise label fixed:", "27/27 available" in src)
print("Right column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))