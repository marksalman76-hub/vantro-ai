from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_remaining_play_demo_icon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Remove the remaining secondary demo/play button, even if the text was already removed.
s = re.sub(
    r'\s*<a[^>]*className="[^"]*(hero__cta|btn)[^"]*(secondary|ghost|outline)[^"]*"[^>]*>.*?<Play[^>]*/>.*?</a>',
    '',
    s,
    flags=re.DOTALL | re.IGNORECASE,
)

s = re.sub(
    r'\s*<button[^>]*className="[^"]*(hero__cta|btn)[^"]*(secondary|ghost|outline)[^"]*"[^>]*>.*?<Play[^>]*/>.*?</button>',
    '',
    s,
    flags=re.DOTALL | re.IGNORECASE,
)

# Remove any standalone Play icon button left in the hero CTA row.
s = re.sub(
    r'\s*<a[^>]*>\s*<Play[^>]*/>\s*</a>',
    '',
    s,
    flags=re.DOTALL | re.IGNORECASE,
)

s = re.sub(
    r'\s*<button[^>]*>\s*<Play[^>]*/>\s*</button>',
    '',
    s,
    flags=re.DOTALL | re.IGNORECASE,
)

PAGE.write_text(s, encoding="utf-8")

print("REMAINING_PLAY_DEMO_ICON_REMOVED")
print(f"Backup: {backup}")