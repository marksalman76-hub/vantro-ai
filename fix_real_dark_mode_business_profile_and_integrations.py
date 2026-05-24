from pathlib import Path
from datetime import datetime

TARGET = Path("frontend/src/app/client/page.tsx")

content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"client_page_before_real_dark_mode_sections_{timestamp}.tsx"

backup_path.write_text(content, encoding="utf-8")

replacements = [
    ('background: "#fff"', 'background: darkModeEnabled ? "#111827" : "#fff"'),
    ('color: "#0f172a"', 'color: darkModeEnabled ? "#f8fafc" : "#0f172a"'),
    ('color: "#334155"', 'color: darkModeEnabled ? "#cbd5e1" : "#334155"'),
    ('color: "#475569"', 'color: darkModeEnabled ? "#94a3b8" : "#475569"'),
    ('color: "#64748b"', 'color: darkModeEnabled ? "#94a3b8" : "#64748b"'),
    (
        'border: "1px solid rgba(15,23,42,.08)"',
        'border: darkModeEnabled ? "1px solid rgba(148,163,184,.18)" : "1px solid rgba(15,23,42,.08)"'
    ),
    (
        'boxShadow: "0 14px 38px rgba(15,23,42,.04)"',
        'boxShadow: darkModeEnabled ? "0 14px 38px rgba(0,0,0,.45)" : "0 14px 38px rgba(15,23,42,.04)"'
    ),
    (
        'background: "rgba(238,242,255,.45)"',
        'background: darkModeEnabled ? "rgba(30,41,59,.82)" : "rgba(238,242,255,.45)"'
    ),
    (
        'background: "rgba(238,242,255,.50)"',
        'background: darkModeEnabled ? "rgba(30,41,59,.88)" : "rgba(238,242,255,.50)"'
    ),
    (
        'background: "rgba(238,242,255,.95)"',
        'background: darkModeEnabled ? "rgba(79,70,229,.22)" : "rgba(238,242,255,.95)"'
    ),
    (
        'border: "1px solid #e5eaf2"',
        'border: darkModeEnabled ? "1px solid rgba(148,163,184,.18)" : "1px solid #e5eaf2"'
    ),
    (
        'background: "#eef2f7"',
        'background: darkModeEnabled ? "#1e293b" : "#eef2f7"'
    ),
]

replacement_count = 0

for old, new in replacements:
    count = content.count(old)
    if count:
        content = content.replace(old, new)
        replacement_count += count
        print(f"REPLACED {count}: {old}")

TARGET.write_text(content, encoding="utf-8")

print("\nREAL_DARK_MODE_BUSINESS_PROFILE_AND_INTEGRATIONS_FIXED")
print(f"Backup: {backup_path}")
print(f"Updated: {TARGET}")
print(f"Total replacements: {replacement_count}")