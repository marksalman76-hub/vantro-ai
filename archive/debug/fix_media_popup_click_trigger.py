from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_media_popup_click_trigger_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

pattern = re.compile(
    r'''<a\s+href="#media-preview-popup"\s+style=\{\{(?P<style>[\s\S]*?)\}\}\s*>\s*Preview in popup\s*</a>''',
    re.MULTILINE,
)

m = pattern.search(s)
if not m:
    raise SystemExit("Hash popup link trigger not found.")

replacement = '''<button
                    type="button"
                    onClick={() => {
                      window.location.hash = "media-preview-popup";
                    }}
                    style={{
''' + m.group("style").replace('textDecoration: "none",', '').replace('display: "inline-flex",', '') + '''
                    }}
                  >
                    Preview in popup
                  </button>'''

s = s[:m.start()] + replacement + s[m.end():]

target.write_text(s, encoding="utf-8")

print("MEDIA_POPUP_CLICK_TRIGGER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")