from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_full_dark_workspace_surface_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

replacements = [
    (
        'background: "#fff"',
        'background: darkModeEnabled ? "rgba(3, 18, 42, 0.86)" : "#fff"',
    ),
    (
        'background: "var(--color-bg-light)"',
        'background: darkModeEnabled ? "rgba(8, 25, 52, 0.92)" : "var(--color-bg-light)"',
    ),
    (
        'border: "1px solid #e5eaf2"',
        'border: darkModeEnabled ? "1px solid rgba(99,102,241,.22)" : "1px solid #e5eaf2"',
    ),
    (
        'border: "1px solid #eef2f7"',
        'border: darkModeEnabled ? "1px solid rgba(99,102,241,.18)" : "1px solid #eef2f7"',
    ),
    (
        'color: "var(--color-dark)"',
        'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)"',
    ),
    (
        'color: "var(--color-mid)"',
        'color: darkModeEnabled ? "#cbd5e1" : "var(--color-mid)"',
    ),
    (
        'color: "var(--color-muted)"',
        'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)"',
    ),
    (
        'boxShadow: "0 18px 50px rgba(15,23,42,.07)"',
        'boxShadow: darkModeEnabled ? "0 22px 70px rgba(0,0,0,.30)" : "0 18px 50px rgba(15,23,42,.07)"',
    ),
]

changed = 0
for old, new in replacements:
    count = s.count(old)
    if count:
        s = s.replace(old, new)
        changed += count
        print(f"REPLACED {count}: {old}")

# Strengthen page background / shell if exact token exists.
s = s.replace(
    'background: darkModeEnabled ? "#0f172a" : "var(--color-page)"',
    'background: darkModeEnabled ? "linear-gradient(180deg, #071022 0%, #0b1220 45%, #07111f 100%)" : "var(--color-page)"',
)

# Improve input/textarea dark-mode readability.
s = s.replace(
    'background: "#fff",\n                      color: "var(--color-dark)",',
    'background: darkModeEnabled ? "rgba(2, 12, 27, 0.88)" : "#fff",\n                      color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",',
)

# Add global dark-mode placeholder support inside component if not already present.
marker = "CLIENT_WORKSPACE_DARK_PLACEHOLDER_STYLE_V1"
if marker not in s:
    insert = '''
      {/* CLIENT_WORKSPACE_DARK_PLACEHOLDER_STYLE_V1 */}
      <style>{`
        textarea::placeholder,
        input::placeholder {
          color: ${darkModeEnabled ? "rgba(203,213,225,.72)" : ""};
        }
      `}</style>
'''
    pos = s.find("<main")
    if pos != -1:
        s = s[:pos] + insert + s[pos:]

if changed < 10:
    raise SystemExit(f"Only changed {changed} occurrences. Stopping to avoid weak dark-mode pass.")

target.write_text(s, encoding="utf-8")

print("FULL_DARK_MODE_WORKSPACE_SURFACE_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")
print(f"Total replacements: {changed}")