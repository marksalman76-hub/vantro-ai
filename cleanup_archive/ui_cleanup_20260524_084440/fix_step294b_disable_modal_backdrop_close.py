from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step294b_disable_backdrop_close_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    '          onClick={() => setShowRejectModal(false)}\n          style={{',
    '          style={{'
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_294B_BACKDROP_CLOSE_DISABLED")
print(f"Backup: {backup}")
print("STEP_294B_OK")