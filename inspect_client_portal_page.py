from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_premium_ux_rebuild_{timestamp}.tsx"

if not PAGE.exists():
    raise FileNotFoundError(f"Missing client page: {PAGE}")

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_PAGE_INSPECTION")
print(f"Page: {PAGE}")
print(f"Backup: {backup}")
print(f"Characters: {len(text)}")
print(f"Lines: {len(text.splitlines())}")

keywords = [
    "Execution Workspace",
    "Deliverables",
    "Execution Timeline",
    "Workspace Actions",
    "Agents",
    "Business Profile",
    "Integrations",
    "Approval",
    "Latest Deliverable",
]

print("\nSECTION_KEYWORD_MATCHES")
for keyword in keywords:
    matches = [m.start() for m in re.finditer(re.escape(keyword), text, re.IGNORECASE)]
    print(f"{keyword}: {len(matches)}")

print("\nTAILWIND_DENSITY_HINTS")
for pattern in ["border", "shadow", "rounded", "bg-", "grid", "space-y", "p-", "gap-"]:
    print(f"{pattern}: {text.count(pattern)}")

print("\nCLIENT_PORTAL_INSPECTION_OK")