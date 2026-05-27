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
