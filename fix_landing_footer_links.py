from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_footer_links_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Convert common footer placeholders to real links.
links = {
    "Platform": "#platform",
    "Agents": "#agents",
    "Studio": "#studio",
    "API & MCP": "#features",
    "Changelog": "#features",
    "About": "#platform",
    "Blog": "#features",
    "Careers": "/support-request",
    "Press": "/support-request",
    "Contact": "/support-request",
    "Docs": "#workflow",
    "Templates": "#studio",
    "Status": "#features",
    "Security": "#features",
    "Privacy": "/privacy-policy",
    "Terms": "/terms-of-service",
    "Cookies": "/privacy-policy",
    "Licenses": "/terms-of-service",
}

for label, href in links.items():
    s = re.sub(
        rf'<a(?![^>]*href=)([^>]*)>\s*{re.escape(label)}\s*</a>',
        rf'<a href="{href}"\1>{label}</a>',
        s,
    )

# Fix social links if currently plain anchors.
social_links = {
    "X": "https://x.com",
    "LinkedIn": "https://www.linkedin.com",
    "YouTube": "https://www.youtube.com",
    "Discord": "/support-request",
}

for label, href in social_links.items():
    s = re.sub(
        rf'<a(?![^>]*href=)([^>]*)>\s*{re.escape(label)}\s*</a>',
        rf'<a href="{href}" target="_blank" rel="noreferrer"\1>{label}</a>' if href.startswith("http") else rf'<a href="{href}"\1>{label}</a>',
        s,
    )

PAGE.write_text(s, encoding="utf-8")

print("LANDING_FOOTER_LINKS_FIXED")
print(f"Backup: {backup}")