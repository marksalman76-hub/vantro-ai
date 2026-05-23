from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step294a_modal_click_fix_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

# Ensure the modal card stops clicks from bubbling to the backdrop.
old = '''          <div
            style={{
              width: 560,
              background: "#fff",
              borderRadius: 26,
              padding: 28,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >'''

new = '''          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: 560,
              background: "#fff",
              borderRadius: 26,
              padding: 28,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >'''

if old not in text and 'onClick={(event) => event.stopPropagation()}' not in text:
    raise SystemExit("ERROR: Modal content block not found.")

if old in text:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_294A_FEEDBACK_MODAL_CLICK_FIX_INSTALLED")
print(f"Backup: {backup}")
print("STEP_294A_OK")