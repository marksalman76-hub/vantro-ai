from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_remove_old_execution_dom_mutations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

original = src

patterns = [
    r"\n\s*function applyPremiumExecutionSectionLayout\(\)\s*\{[\s\S]*?\n\s*\}",
    r"\n\s*function applyHorizontalExecutionLayout\(\)\s*\{[\s\S]*?\n\s*\}",
    r"\n\s*applyPremiumExecutionSectionLayout\(\);?",
    r"\n\s*applyHorizontalExecutionLayout\(\);?",
]

for pattern in patterns:
    src = re.sub(pattern, "\n", src, flags=re.MULTILINE)

if src == original:
    raise SystemExit("ERROR: No old execution DOM mutation code was removed.")

PAGE.write_text(src, encoding="utf-8")

print("OLD_EXECUTION_DOM_LAYOUT_MUTATIONS_REMOVED")
print(f"Backup: {backup}")
print("Removed applyPremiumExecutionSectionLayout/applyHorizontalExecutionLayout if present.")
print("Remaining applyPremiumExecutionSectionLayout:", src.count("applyPremiumExecutionSectionLayout"))
print("Remaining applyHorizontalExecutionLayout:", src.count("applyHorizontalExecutionLayout"))