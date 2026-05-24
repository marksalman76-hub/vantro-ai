from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_connect_about_section_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Make sure footer About points to a real about section.
s = s.replace('["About","#platform"]', '["About","#about"]')

# Add id="about" to the first section/class around About content if not already present.
if 'id="about"' not in s:
    about_index = s.find("About")
    if about_index == -1:
        raise SystemExit("FAILED: About text not found")

    # Find the closest opening section/div before the About heading.
    before = s[:about_index]
    match = list(re.finditer(r'<(section|div)\s+className="([^"]+)"', before))
    if not match:
        raise SystemExit("FAILED: no section/div class marker before About")

    last = match[-1]
    insert_pos = last.start()
    original = last.group(0)

    if 'id=' not in original:
        updated = original.replace("<" + last.group(1), "<" + last.group(1) + ' id="about"', 1)
        s = s[:insert_pos] + updated + s[insert_pos + len(original):]

# Smooth scroll support.
if "scroll-behavior: smooth" not in s:
    css_marker = "html, body {"
    if css_marker in s:
        s = s.replace(css_marker, "html { scroll-behavior: smooth; }\n\n" + css_marker, 1)

PAGE.write_text(s, encoding="utf-8")

print("FOOTER_ABOUT_SECTION_CONNECTED")
print(f"Backup: {backup}")