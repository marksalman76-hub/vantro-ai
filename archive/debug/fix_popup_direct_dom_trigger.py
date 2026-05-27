from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_popup_direct_dom_trigger_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# Replace Preview trigger with a direct hash + scroll fallback.
s = re.sub(
    r'onClick=\{\(\)\s*=>\s*\{\s*window\.location\.hash\s*=\s*"media-preview-popup";\s*\}\}',
    'onClick={(event) => { event.preventDefault(); window.location.href = "#media-preview-popup"; }}',
    s,
    count=1,
)

# Also handle older dedicated state trigger if still present.
s = s.replace(
    'onClick={() => setShowMediaPreviewOverlay(true)}',
    'onClick={(event) => { event.preventDefault(); window.location.href = "#media-preview-popup"; }}',
    1,
)

target.write_text(s, encoding="utf-8")

print("POPUP_DIRECT_DOM_TRIGGER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")