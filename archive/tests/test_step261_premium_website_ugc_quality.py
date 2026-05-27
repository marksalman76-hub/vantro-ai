import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step261_premium_website_ugc_quality.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "premium-website-ugc-quality.md"

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "premium_website_ugc_quality_intelligence_locked",
    "website_upgrades_all_true": all(record.get("website_agent_upgrades", {}).values()),
    "ugc_upgrades_all_true": all(record.get("ugc_agent_upgrades", {}).values()),
    "quality_rules_all_true": all(record.get("quality_rules", {}).values()),
    "governance_publish_approval": record.get("governance", {}).get("owner_approval_required_for_live_site_publish") is True,
    "governance_campaign_approval": record.get("governance", {}).get("owner_approval_required_for_campaign_launch") is True,
    "doc_created": doc.exists(),
}

print("STEP_261_PREMIUM_WEBSITE_UGC_QUALITY_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_261_PREMIUM_WEBSITE_UGC_QUALITY_OK")
