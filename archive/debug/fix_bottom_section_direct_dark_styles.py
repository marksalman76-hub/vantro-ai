from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_bottom_direct_dark_styles_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# Remove the previous bottom CSS overlay if present.
start_marker = "        {/* BOTTOM_SECTION_DARK_CONSISTENCY_V1 */}"
start = s.find(start_marker)
if start != -1:
    style_start = start
    style_end = s.find("</style>", style_start)
    if style_end == -1:
        raise SystemExit("Could not safely remove previous bottom CSS layer.")
    style_end += len("</style>")
    s = s[:style_start] + s[style_end:]

section_marker = '<section className="client-bottom-workspace" style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'
if section_marker not in s:
    fallback = '<section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'
    if fallback not in s:
        raise SystemExit("Bottom section start not found.")
    s = s.replace(fallback, section_marker, 1)

start = s.find(section_marker)
end = s.find("{/* OUTPUT_VIEWER_POPUP_MODAL_LOCKED_V1 */}", start)
if end == -1:
    raise SystemExit("Bottom section end not found.")

bottom = s[start:end]
original = bottom

replacements = [
    ('background: "#fff"', 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff"'),
    ('background: "#f8fafc"', 'background: darkModeEnabled ? "rgba(15,23,42,.86)" : "#f8fafc"'),
    ('background: "var(--color-bg-light)"', 'background: darkModeEnabled ? "rgba(15,23,42,.86)" : "var(--color-bg-light)"'),
    ('background: "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)"', 'background: darkModeEnabled ? "linear-gradient(180deg, rgba(15,23,42,.96), rgba(8,18,40,.98))" : "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)"'),
    ('background: "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)"', 'background: darkModeEnabled ? "linear-gradient(180deg, rgba(15,23,42,.96), rgba(8,18,40,.98))" : "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)"'),
    ('background: "linear-gradient(135deg,var(--color-bg-light) 0%,#f1f5f9 100%)"', 'background: darkModeEnabled ? "linear-gradient(135deg, rgba(3,10,24,.92), rgba(15,23,42,.94))" : "linear-gradient(135deg,var(--color-bg-light) 0%,#f1f5f9 100%)"'),
    ('background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))"', 'background: darkModeEnabled ? "linear-gradient(135deg, rgba(79,70,229,.28), rgba(15,23,42,.94))" : "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))"'),

    ('border: "1px solid #e5eaf2"', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2"'),
    ('border: "1px solid #edf1f6"', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.22)" : "1px solid #edf1f6"'),
    ('border: "1px dashed #dbe4ee"', 'border: darkModeEnabled ? "1px dashed rgba(148,163,184,.34)" : "1px dashed #dbe4ee"'),
    ('borderTop: "1px solid #edf1f6"', 'borderTop: darkModeEnabled ? "1px solid rgba(99,102,241,.22)" : "1px solid #edf1f6"'),
    ('borderTop: "1px solid #eef2f7"', 'borderTop: darkModeEnabled ? "1px solid rgba(99,102,241,.22)" : "1px solid #eef2f7"'),

    ('color: "var(--color-dark)"', 'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)"'),
    ('color: "var(--color-muted)"', 'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)"'),
    ('color: "var(--color-mid)"', 'color: darkModeEnabled ? "#cbd5e1" : "var(--color-mid)"'),
    ('color: "#334155"', 'color: darkModeEnabled ? "#cbd5e1" : "#334155"'),
    ('color: "#94a3b8"', 'color: darkModeEnabled ? "#94a3b8" : "#94a3b8"'),

    ('boxShadow: "0 8px 22px rgba(15,23,42,.035)"', 'boxShadow: darkModeEnabled ? "0 12px 32px rgba(0,0,0,.22)" : "0 8px 22px rgba(15,23,42,.035)"'),
]

count = 0
for old, new in replacements:
    c = bottom.count(old)
    if c:
        bottom = bottom.replace(old, new)
        count += c
        print(f"REPLACED {c}: {old}")

if bottom == original:
    raise SystemExit("No bottom changes made.")

s = s[:start] + bottom + s[end:]
target.write_text(s, encoding="utf-8")

print("BOTTOM_SECTION_DIRECT_DARK_STYLES_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")
print(f"Total replacements: {count}")