from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_remove_execution_layout_useeffects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

original = src

# Remove entire useEffect blocks that contain the old DOM mutation functions.
src = re.sub(
    r"\n\s*useEffect\(\(\)\s*=>\s*\{\s*const applyHorizontalExecutionLayout\s*=\s*\(\)\s*=>\s*\{[\s\S]*?\n\s*\},\s*\[selectedAgents\]\);\s*",
    "\n",
    src,
    flags=re.MULTILINE,
)

src = re.sub(
    r"\n\s*useEffect\(\(\)\s*=>\s*\{\s*const applyPremiumExecutionSectionLayout\s*=\s*\(\)\s*=>\s*\{[\s\S]*?\n\s*\},\s*\[selectedAgents,\s*activeAccountPanel\]\);\s*",
    "\n",
    src,
    flags=re.MULTILINE,
)

if src == original:
    raise SystemExit("ERROR: No execution layout useEffect blocks removed.")

PAGE.write_text(src, encoding="utf-8")

print("EXECUTION_LAYOUT_USEEFFECTS_REMOVED")
print(f"Backup: {backup}")
print("applyHorizontalExecutionLayout count:", src.count("applyHorizontalExecutionLayout"))
print("applyPremiumExecutionSectionLayout count:", src.count("applyPremiumExecutionSectionLayout"))
print("data-premium-flow-proof count:", src.count("data-premium-flow-proof"))
print("Governed execution count:", src.count("Governed execution, every time."))