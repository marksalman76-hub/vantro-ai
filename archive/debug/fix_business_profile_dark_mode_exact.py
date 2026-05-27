from pathlib import Path
from datetime import datetime

target = Path("frontend/src/app/client/page.tsx")

content = target.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_business_profile_dark_exact_{timestamp}.tsx"

backup.write_text(content, encoding="utf-8")

start_marker = 'Business profile intelligence ✨'
start = content.find(start_marker)

if start == -1:
    raise SystemExit("Could not find Business Profile section.")

section_start = content.rfind("<section", 0, start)
section_end = content.find("</section>", start)

if section_start == -1 or section_end == -1:
    raise SystemExit("Could not isolate Business Profile section.")

section_end += len("</section>")

section = content[section_start:section_end]
original = section

replacements = [
    ('background: "#fff"', 'background: darkModeEnabled ? "rgba(15,23,42,.92)" : "#fff"'),
    ('background: "rgba(238,242,255,.95)"', 'background: darkModeEnabled ? "rgba(79,70,229,.20)" : "rgba(238,242,255,.95)"'),
    ('background: "rgba(238,242,255,.50)"', 'background: darkModeEnabled ? "rgba(30,41,59,.88)" : "rgba(238,242,255,.50)"'),
    ('background: "rgba(238,242,255,.45)"', 'background: darkModeEnabled ? "rgba(30,41,59,.82)" : "rgba(238,242,255,.45)"'),

    ('color: "#0f172a"', 'color: darkModeEnabled ? "#f8fafc" : "#0f172a"'),
    ('color: "#334155"', 'color: darkModeEnabled ? "#cbd5e1" : "#334155"'),
    ('color: "#475569"', 'color: darkModeEnabled ? "#94a3b8" : "#475569"'),
    ('color: "#64748b"', 'color: darkModeEnabled ? "#94a3b8" : "#64748b"'),
    ('color: "#4f46e5"', 'color: darkModeEnabled ? "#a5b4fc" : "#4f46e5"'),

    ('border: "1px solid rgba(15,23,42,.08)"', 'border: darkModeEnabled ? "1px solid rgba(148,163,184,.16)" : "1px solid rgba(15,23,42,.08)"'),
    ('border: "1px solid rgba(79,70,229,.12)"', 'border: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid rgba(79,70,229,.12)"'),
    ('border: "1px solid rgba(79,70,229,.10)"', 'border: darkModeEnabled ? "1px solid rgba(129,140,248,.22)" : "1px solid rgba(79,70,229,.10)"'),
    ('border: "1px solid rgba(79,70,229,.18)"', 'border: darkModeEnabled ? "1px solid rgba(129,140,248,.34)" : "1px solid rgba(79,70,229,.18)"'),

    ('boxShadow: "0 14px 38px rgba(15,23,42,.04)"', 'boxShadow: darkModeEnabled ? "0 18px 44px rgba(0,0,0,.32)" : "0 14px 38px rgba(15,23,42,.04)"'),
    ('boxShadow: "0 10px 28px rgba(15,23,42,.04)"', 'boxShadow: darkModeEnabled ? "0 14px 34px rgba(0,0,0,.28)" : "0 10px 28px rgba(15,23,42,.04)"'),
]

total = 0

for old, new in replacements:
    count = section.count(old)
    if count:
        section = section.replace(old, new)
        total += count
        print(f"REPLACED {count}: {old}")

if section == original:
    raise SystemExit("No replacements applied.")

content = content[:section_start] + section + content[section_end:]

target.write_text(content, encoding="utf-8")

print("\nBUSINESS_PROFILE_DARK_MODE_EXACT_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")
print(f"Total replacements: {total}")