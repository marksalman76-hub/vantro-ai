from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_half_half_dark_mode_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

insert = r'''
        {/* DARK_MODE_HALF_HALF_CARD_FIX_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            main section,
            main article,
            main aside,
            main div[style*="background: rgb(255, 255, 255)"],
            main div[style*="background-color: rgb(255, 255, 255)"],
            main div[style*="background: white"],
            main div[style*="background-color: white"],
            main button[style*="background: rgb(255, 255, 255)"],
            main button[style*="background-color: rgb(255, 255, 255)"] {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 18px 52px rgba(0,0,0,.26) !important;
            }

            main textarea,
            main input,
            main select {
              background: rgba(3,10,24,.88) !important;
              color: #f8fafc !important;
              border-color: rgba(129,140,248,.34) !important;
            }

            main textarea::placeholder,
            main input::placeholder {
              color: rgba(203,213,225,.72) !important;
            }

            main [style*="color: rgb(15, 23, 42)"],
            main [style*="color: #0f172a"],
            main [style*="color: var(--color-dark)"] {
              color: #f8fafc !important;
            }

            main [style*="color: rgb(100, 116, 139)"],
            main [style*="color: rgb(71, 85, 105)"],
            main [style*="color: #64748b"],
            main [style*="color: #475569"],
            main [style*="color: var(--color-muted)"] {
              color: #94a3b8 !important;
            }

            main [style*="background: rgb(248, 250, 252)"],
            main [style*="background-color: rgb(248, 250, 252)"],
            main [style*="background: #f8fafc"] {
              background: rgba(15,23,42,.86) !important;
            }

            #media-preview-popup,
            #media-preview-popup *,
            [role="dialog"],
            [role="dialog"] * {
              color: initial;
            }
          ` : ``}
        `}</style>
'''

marker = '''      <div style={shellStyle}>'''

if insert.strip() in s:
    print("Dark half-half fix already installed.")
else:
    if marker not in s:
        raise SystemExit("FAILED: shell marker not found")
    s = s.replace(marker, insert + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_DARK_MODE_HALF_HALF_CARDS_FIXED")
print(f"Backup: {backup}")