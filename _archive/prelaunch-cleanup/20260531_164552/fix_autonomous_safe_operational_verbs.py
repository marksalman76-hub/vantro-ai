from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "autonomous_governed_action_router.py"

backup_dir = ROOT / "backups" / f"autonomous_safe_operational_verbs_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

content = target.read_text(encoding="utf-8")

old = '''AUTONOMOUS_SAFE_KEYWORDS = {
    "draft", "prepare", "create", "generate", "summarise", "summarize",
    "analyse", "analyze", "research", "outline", "checklist", "plan",
    "recommend", "preview", "framework", "document", "calendar",
    "strategy document", "email draft", "landing page draft",
}
'''

new = '''AUTONOMOUS_SAFE_KEYWORDS = {
    "draft", "prepare", "create", "generate", "summarise", "summarize",
    "analyse", "analyze", "research", "outline", "checklist", "plan",
    "recommend", "preview", "framework", "document", "calendar",
    "strategy document", "email draft", "landing page draft",

    # safe operational execution verbs
    "conduct stakeholder interviews",
    "stakeholder interviews",
    "schedule interview",
    "book interview",
    "create outreach",
    "prepare outreach",
    "draft outreach",
    "analyze competitor",
    "analyse competitor",
    "identify white space",
    "develop messaging",
    "develop core messaging",
    "generate thought leadership",
    "create thought leadership",
    "develop content",
    "create content",
    "build content calendar",
    "create crm task",
    "create calendar placeholder",
}
'''

if old not in content:
    raise SystemExit("SAFE_KEYWORDS_BLOCK_NOT_FOUND")

content = content.replace(old, new)
target.write_text(content, encoding="utf-8")

print("AUTONOMOUS_SAFE_OPERATIONAL_VERBS_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")