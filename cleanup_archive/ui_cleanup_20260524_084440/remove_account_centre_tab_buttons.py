from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_remove_account_tabs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

pattern = re.compile(
    r'\n\s*<div style=\{\{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 \}\}>\s*'
    r'\{\[\s*'
    r'\["settings", "⚙️ Settings"\],\s*'
    r'\["profile", "👤 Profile"\],\s*'
    r'\["password-reset", "🔐 Password reset"\],\s*'
    r'\["two-factor-authentication", "🛡️ 2FA"\],\s*'
    r'\]\.map\(\(\[key, label\]\) => \(\s*'
    r'<button[\s\S]*?</button>\s*'
    r'\)\)\}\s*'
    r'</div>',
    re.MULTILINE,
)

text, count = pattern.subn("", text)

if count != 1:
    raise SystemExit(f"Expected to remove 1 account tab row, removed {count}")

path.write_text(text, encoding="utf-8")

print("ACCOUNT_CENTRE_TAB_BUTTONS_REMOVED")
print(f"Backup: {backup}")