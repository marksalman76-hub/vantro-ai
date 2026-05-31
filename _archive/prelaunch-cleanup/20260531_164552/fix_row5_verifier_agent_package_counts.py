from pathlib import Path
from datetime import datetime
import re

path = Path("live_verify_billing_stripe_package_automation.py")

if not path.exists():
    raise SystemExit("live_verify_billing_stripe_package_automation.py not found")

text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("row5_verifier_agent_package_counts_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "live_verify_billing_stripe_package_automation.py"
backup.write_text(text, encoding="utf-8")

# Correct verifier expectations to match the locked commercial package rules.
replacements = {
    '"starter": 3': '"starter": 3',
    '"growth": 6': '"growth": 7',
    '"business": 12': '"business": 10',
    '"enterprise": 27': '"enterprise": 27',
    "'starter': 3": "'starter': 3",
    "'growth': 6": "'growth': 7",
    "'business': 12": "'business': 10",
    "'enterprise': 27": "'enterprise': 27",
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Also patch any explicit expected max_selectable_agents blocks.
text = re.sub(
    r'("plan"\s*:\s*"growth"[\s\S]{0,500}?"max_selectable_agents"\s*:\s*)6',
    r'\g<1>7',
    text,
)
text = re.sub(
    r'("plan"\s*:\s*"business"[\s\S]{0,500}?"max_selectable_agents"\s*:\s*)12',
    r'\g<1>10',
    text,
)

# Patch Python dict/list patterns if verifier uses package expectation maps.
text = re.sub(r'("growth"\s*:\s*)6', r'\g<1>7', text)
text = re.sub(r'("business"\s*:\s*)12', r'\g<1>10', text)
text = re.sub(r"('growth'\s*:\s*)6", r"\g<1>7", text)
text = re.sub(r"('business'\s*:\s*)12", r"\g<1>10", text)

path.write_text(text, encoding="utf-8")

print("ROW5_VERIFIER_AGENT_PACKAGE_COUNTS_FIXED")
print("Backup:", backup)
print("Locked package counts: starter=3 growth=7 business=10 enterprise=27")