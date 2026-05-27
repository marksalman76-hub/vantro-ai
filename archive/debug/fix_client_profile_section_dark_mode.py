from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_profile_section_dark_mode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

replacements = {
'''style={{ border: "1px solid #e5eaf2", background: "#fff", borderRadius: 999, padding: "9px 13px", fontWeight: 850, cursor: "pointer", color: "var(--color-dark)" }}''':
'''style={{
                  border: darkModeEnabled ? "1px solid rgba(129,140,248,.28)" : "1px solid #e5eaf2",
                  background: darkModeEnabled ? "rgba(15,23,42,.92)" : "#fff",
                  borderRadius: 999,
                  padding: "9px 13px",
                  fontWeight: 850,
                  cursor: "pointer",
                  color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",
                }}''',

'''<div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>''':
'''<div style={{
                    border: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #edf1f6",
                    borderRadius: 16,
                    padding: 14,
                    background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                    boxShadow: darkModeEnabled ? "0 16px 42px rgba(0,0,0,.24)" : "none",
                  }}>''',

'''<div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>''':
'''<div style={{ fontSize: 11, color: darkModeEnabled ? "#a5b4fc" : "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>''',

'''<div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>''':
'''<div style={{ marginTop: 8, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>''',

'''<div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>
                      Business profile
                    </div>''':
'''<div style={{ fontSize: 11, color: darkModeEnabled ? "#a5b4fc" : "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>
                      Business profile
                    </div>''',

'''<div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>
                      {businessProfile.business_name || "Not saved yet"}
                    </div>''':
'''<div style={{ marginTop: 6, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)", fontWeight: 900 }}>
                      {businessProfile.business_name || "Not saved yet"}
                    </div>''',

'''<div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>''':
'''<div style={{ marginTop: 5, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>''',

'''color: "#0f172a",
                        background: "#fff",''':
'''color: darkModeEnabled ? "#f8fafc" : "#0f172a",
                        background: darkModeEnabled ? "rgba(3,10,24,.86)" : "#fff",'''
}

changed = 0
for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new)
        changed += 1
    else:
        print("WARNING: marker not found:", old[:90])

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_PROFILE_SECTION_DARK_MODE_FIXED")
print(f"Markers changed: {changed}")
print(f"Backup: {backup}")