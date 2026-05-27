from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_force_white_block_replacement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Directly replace hardcoded white surfaces in the client workspace.
replacements = {
    'background: "#fff"': 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff"',
    'background: "#ffffff"': 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#ffffff"',
    'background: "var(--color-bg-light)"': 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "var(--color-bg-light)"',
    'background: "linear-gradient(135deg,#eff6ff,#ffffff)"': 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "linear-gradient(135deg,#eff6ff,#ffffff)"',
    'background: "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)"': 'background: darkModeEnabled ? "linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98))" : "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)"',
    'background: "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)"': 'background: darkModeEnabled ? "linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98))" : "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)"',
    'border: "1px solid #e5eaf2"': 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2"',
    'border: "1px solid #edf1f6"': 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #edf1f6"',
    'color: "var(--color-dark)"': 'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)"',
    'color: "var(--color-muted)"': 'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)"',
    'color: "#334155"': 'color: darkModeEnabled ? "#cbd5e1" : "#334155"',
    'color: "#64748b"': 'color: darkModeEnabled ? "#94a3b8" : "#64748b"',
}

changed = 0
for old, new in replacements.items():
    count = s.count(old)
    if count:
        s = s.replace(old, new)
        changed += count

# Force + Add integration button to remain clickable.
s = s.replace(
    'whiteSpace: "nowrap",\n            }}\n          >\n            + Add integration',
    'whiteSpace: "nowrap",\n              pointerEvents: "auto",\n              position: "relative",\n              zIndex: 20,\n            }}\n          >\n            + Add integration',
)

TARGET.write_text(s, encoding="utf-8")

print("HARDCODED_WHITE_BLOCKS_REPLACED")
print(f"Replacements applied: {changed}")
print(f"Backup: {backup}")