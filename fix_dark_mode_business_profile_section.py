from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_dark_business_profile_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

marker = "BUSINESS PROFILE INTELLIGENCE"
idx = s.find(marker)
if idx == -1:
    raise SystemExit("Business Profile Intelligence marker not found.")

start = s.rfind("<section", 0, idx)
if start == -1:
    raise SystemExit("Could not find Business Profile section start.")

next_section = s.find("\n        <section", idx + 1)
if next_section == -1:
    raise SystemExit("Could not find next section boundary.")

section = s[start:next_section]
original = section

# Override the section card surface after cardStyle spread.
section = section.replace(
    "...cardStyle,",
    '''...cardStyle,
            background: darkModeEnabled ? "linear-gradient(180deg, rgba(8, 18, 40, .96), rgba(5, 14, 31, .98))" : "#fff",
            border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2",
            boxShadow: darkModeEnabled ? "0 24px 80px rgba(0,0,0,.34)" : "0 18px 50px rgba(15,23,42,.07)",''',
    1,
)

# Darken card/input surfaces inside this section only.
replacements = [
    ('background: "#fff"', 'background: darkModeEnabled ? "rgba(8, 20, 44, .88)" : "#fff"'),
    ('background: "#f8fafc"', 'background: darkModeEnabled ? "rgba(15, 23, 42, .86)" : "#f8fafc"'),
    ('background: "rgba(238,242,255,.50)"', 'background: darkModeEnabled ? "rgba(79,70,229,.14)" : "rgba(238,242,255,.50)"'),
    ('border: "1px solid #e5eaf2"', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2"'),
    ('border: "1px solid rgba(79,70,229,.10)"', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.26)" : "1px solid rgba(79,70,229,.10)"'),
    ('border: "1px solid rgba(79,70,229,.18)"', 'border: darkModeEnabled ? "1px solid rgba(129,140,248,.38)" : "1px solid rgba(79,70,229,.18)"'),
    ('color: "#0f172a"', 'color: darkModeEnabled ? "#f8fafc" : "#0f172a"'),
    ('color: "#334155"', 'color: darkModeEnabled ? "#dbeafe" : "#334155"'),
    ('color: "#475569"', 'color: darkModeEnabled ? "#cbd5e1" : "#475569"'),
    ('color: "#64748b"', 'color: darkModeEnabled ? "#94a3b8" : "#64748b"'),
    ('color: "#4f46e5"', 'color: darkModeEnabled ? "#a5b4fc" : "#4f46e5"'),
    ('boxShadow: "0 10px 28px rgba(15,23,42,.04)"', 'boxShadow: darkModeEnabled ? "0 16px 44px rgba(0,0,0,.26)" : "0 10px 28px rgba(15,23,42,.04)"'),
]

changed = 0
for old, new in replacements:
    count = section.count(old)
    if count:
        section = section.replace(old, new)
        changed += count
        print(f"REPLACED {count}: {old}")

# Make textarea/input surfaces explicitly readable in this section.
section = section.replace(
    'fontFamily: "inherit",',
    '''fontFamily: "inherit",
                      background: darkModeEnabled ? "rgba(2, 12, 27, .84)" : "#fff",
                      color: darkModeEnabled ? "#f8fafc" : "#0f172a",
                      border: darkModeEnabled ? "1px solid rgba(129,140,248,.34)" : "1px solid rgba(79,70,229,.20)",''',
)

if section == original:
    raise SystemExit("No changes made. Stopping.")

s = s[:start] + section + s[next_section:]
target.write_text(s, encoding="utf-8")

print("DARK_MODE_BUSINESS_PROFILE_SECTION_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")
print(f"Total targeted replacements: {changed}")