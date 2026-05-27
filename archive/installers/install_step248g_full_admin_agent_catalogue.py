from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step248g_full_admin_agent_catalogue.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_step248g_{timestamp}.tsx"
backup.write_text(ADMIN_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

text = ADMIN_PAGE.read_text(encoding="utf-8")

start = text.find("const ADMIN_AGENT_OPTIONS = [")
end = text.find("];", start)

if start == -1 or end == -1:
    raise RuntimeError("ADMIN_AGENT_OPTIONS block not found")

end = end + 2

full_catalogue = '''const ADMIN_AGENT_OPTIONS = [
  ["master_orchestrator_agent", "Master Orchestrator Agent"],
  ["product_research_agent", "Product Research Agent"],
  ["competitor_intelligence_agent", "Competitor Intelligence Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["website_landing_page_agent", "Website / Landing Page Agent"],
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["product_image_direction_agent", "Product Image Direction Agent"],
  ["ad_creative_agent", "Ad Creative Agent"],
  ["campaign_launch_agent", "Campaign Launch Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
  ["creative_rotation_agent", "Creative Rotation Agent"],
  ["email_marketing_agent", "Email Marketing Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["fulfilment_agent", "Fulfilment Agent"],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
  ["seo_agent", "SEO Agent"],
  ["marketplace_agent", "Marketplace Agent"],
  ["billing_licence_agent", "Billing and Licence Agent"],
  ["reporting_agent", "Reporting Agent"],
  ["quality_assurance_agent", "Quality Assurance Agent"],
  ["integration_agent", "Integration Agent"],
  ["security_compliance_agent", "Security and Compliance Agent"],
  ["demo_trial_agent", "Demo / Trial Agent"],
];'''

text = text[:start] + full_catalogue + text[end:]

text = text.replace(
    "Owner/admin can run one agent or multiple agents for internal operations, demos, and testing.",
    "Owner/admin can run one agent, multiple selected agents, or any agent from the full 25-agent catalogue for internal operations, demos, and testing."
)

ADMIN_PAGE.write_text(text, encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import re
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore")

match = re.search(r"const ADMIN_AGENT_OPTIONS = \[(.*?)\];", text, re.S)
agent_count = len(re.findall(r'\["[^"]+",\s*"[^"]+"\]', match.group(1))) if match else 0
lower = text.lower()

required_agents = [
    "master_orchestrator_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "website_landing_page_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_direction_agent",
    "ad_creative_agent",
    "campaign_launch_agent",
    "analytics_optimisation_agent",
    "creative_rotation_agent",
    "email_marketing_agent",
    "customer_support_agent",
    "fulfilment_agent",
    "influencer_collaboration_agent",
    "seo_agent",
    "marketplace_agent",
    "billing_licence_agent",
    "reporting_agent",
    "quality_assurance_agent",
    "integration_agent",
    "security_compliance_agent",
    "demo_trial_agent",
]

checks = {
    "admin_page_exists": admin_page.exists(),
    "agent_catalogue_count_25": agent_count == 25,
    "all_required_agents_present": all(agent in text for agent in required_agents),
    "multi_agent_admin_copy_present": "full 25-agent catalogue" in lower,
    "selected_admin_agents_present": "selectedadminagents" in lower,
    "run_selected_agents_present": "run selected agents" in lower,
}

print("STEP_248G_FULL_ADMIN_AGENT_CATALOGUE_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("admin_agent_count", agent_count)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_248G_FULL_ADMIN_AGENT_CATALOGUE_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_248G_FULL_ADMIN_AGENT_CATALOGUE_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_248G_OK")