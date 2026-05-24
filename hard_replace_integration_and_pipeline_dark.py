from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_hard_replace_integration_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")
original = s

replacements = [
    (
        '''border: "1px solid #e5eaf2",
                borderRadius: 12,
                background: "#fff",
                padding: "8px 10px",
                display: "flex",
                alignItems: "center",
                gap: 8,
                minHeight: 48,
                cursor: "pointer",''',
        '''border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",
                borderRadius: 12,
                background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                padding: "8px 10px",
                display: "flex",
                alignItems: "center",
                gap: 8,
                minHeight: 48,
                cursor: "pointer",'''
    ),
    (
        '''background: "#eef2f7",
                  color: "#64748b",''',
        '''background: darkModeEnabled ? "rgba(79,70,229,.24)" : "#eef2f7",
                  color: darkModeEnabled ? "#c7d2fe" : "#64748b",'''
    ),
    (
        '''color: "var(--color-dark)",
                    fontSize: 13,''',
        '''color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",
                    fontSize: 13,'''
    ),
    (
        '''<span style={{ display: "block", color: "var(--color-muted)", fontSize: 12, fontWeight: 800, marginTop: 3 }}>
                  Connect
                </span>''',
        '''<span style={{ display: "block", color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12, fontWeight: 800, marginTop: 3 }}>
                  Connect
                </span>'''
    ),
    (
        '''border: "1px solid #d8dcff",
              borderRadius: 12,
              background: "#fff",
              color: "var(--color-primary)",''',
        '''border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #d8dcff",
              borderRadius: 12,
              background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
              color: darkModeEnabled ? "#c7d2fe" : "var(--color-primary)",'''
    ),
    (
        '''border: "1px solid #e5eaf2",
                      borderRadius: 12,
                      background: "#fff",
                      padding: "8px 10px",
                      boxShadow: "0 8px 20px rgba(15,23,42,.04)",''',
        '''border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",
                      borderRadius: 12,
                      background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                      padding: "8px 10px",
                      boxShadow: darkModeEnabled ? "0 10px 28px rgba(0,0,0,.22)" : "0 8px 20px rgba(15,23,42,.04)",'''
    ),
    (
        '''<div style={{ fontWeight: 900, color: "var(--color-dark)", fontSize: 12 }}>{title}</div>
                    <div style={{ color: "var(--color-muted)", fontSize: 11.5, fontWeight: 800, marginTop: 2 }}>{status}</div>''',
        '''<div style={{ fontWeight: 900, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)", fontSize: 12 }}>{title}</div>
                    <div style={{ color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 11.5, fontWeight: 800, marginTop: 2 }}>{status}</div>'''
    ),
    (
        '''border: "1px solid #dbeafe",
                  borderRadius: 14,
                  background: "linear-gradient(135deg,#eff6ff,#ffffff)",
                  padding: "9px 10px",''',
        '''border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #dbeafe",
                  borderRadius: 14,
                  background: darkModeEnabled ? "rgba(12,24,49,.92)" : "linear-gradient(135deg,#eff6ff,#ffffff)",
                  padding: "9px 10px",'''
    ),
    (
        '''background: "#ffffff",
                    color: "var(--color-brand)",''',
        '''background: darkModeEnabled ? "rgba(79,70,229,.24)" : "#ffffff",
                    color: darkModeEnabled ? "#c7d2fe" : "var(--color-brand)",'''
    ),
    (
        '''<div style={{ fontSize: 12, fontWeight: 900, color: "var(--color-dark)" }}>
                    Governed execution, every time.
                  </div>
                  <div style={{ marginTop: 2, fontSize: 11.5, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                    Tracked, logged, quality-checked, and approval-routed.
                  </div>''',
        '''<div style={{ fontSize: 12, fontWeight: 900, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)" }}>
                    Governed execution, every time.
                  </div>
                  <div style={{ marginTop: 2, fontSize: 11.5, fontWeight: 700, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", lineHeight: 1.35 }}>
                    Tracked, logged, quality-checked, and approval-routed.
                  </div>'''
    ),
]

changed = 0
missing = []

for old, new in replacements:
    count = s.count(old)
    if count == 0:
        missing.append(old[:100].replace("\n", " "))
    else:
        s = s.replace(old, new)
        changed += count

if changed == 0:
    raise SystemExit("FAILED: no replacements applied")

TARGET.write_text(s, encoding="utf-8")

print("HARD_REPLACE_INTEGRATION_AND_PIPELINE_DARK_DONE")
print(f"Replacements applied: {changed}")
print(f"Backup: {backup}")

if missing:
    print("WARNINGS: some markers were not found:")
    for item in missing:
        print("-", item)