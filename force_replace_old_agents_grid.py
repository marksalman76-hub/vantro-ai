from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "AgentsSection.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

if not COMPONENT.exists():
    raise SystemExit("FAILED: frontend/src/components/AgentsSection.tsx does not exist")

backup = BACKUP_DIR / f"page_before_force_agents_section_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

if 'import { AgentsSection } from "@/components/AgentsSection";' not in s:
    import_anchor = 'import Link from "next/link";'
    if import_anchor not in s:
        raise SystemExit("FAILED: Link import marker not found")
    s = s.replace(import_anchor, import_anchor + '\nimport { AgentsSection } from "@/components/AgentsSection";', 1)

start = s.find('<section id="agents"')
end = s.find('<section id="workflow"', start)

if start == -1 or end == -1:
    raise SystemExit("FAILED: old agents section markers not found")

replacement = '''<AgentsSection />

      '''

s = s[:start] + replacement + s[end:]

PAGE.write_text(s, encoding="utf-8")

print("OLD_AGENTS_GRID_REPLACED_WITH_PREMIUM_27_AGENT_SECTION")
print(f"Backup: {backup}")