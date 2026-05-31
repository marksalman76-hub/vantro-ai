from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass1_declutter_{timestamp}.tsx"

if not PAGE.exists():
    raise FileNotFoundError(f"Missing client page: {PAGE}")

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# ---------------------------------------------------------------------
# Premium UX Pass 1
# Safe visual-only transformations.
# No business logic, API calls, state names, routes, handlers, or payloads touched.
# ---------------------------------------------------------------------

replacements = {
    # Harsh borders -> softer enterprise surfaces
    'border: "1px solid #e5e7eb"': 'border: "1px solid rgba(15, 23, 42, 0.08)"',
    "border: '1px solid #e5e7eb'": "border: '1px solid rgba(15, 23, 42, 0.08)'",
    'border: "1px solid #e2e8f0"': 'border: "1px solid rgba(15, 23, 42, 0.08)"',
    "border: '1px solid #e2e8f0'": "border: '1px solid rgba(15, 23, 42, 0.08)'",
    'border: "1px solid #dbeafe"': 'border: "1px solid rgba(37, 99, 235, 0.14)"',
    "border: '1px solid #dbeafe'": "border: '1px solid rgba(37, 99, 235, 0.14)'",
    'border: "1px solid #bfdbfe"': 'border: "1px solid rgba(37, 99, 235, 0.16)"',
    "border: '1px solid #bfdbfe'": "border: '1px solid rgba(37, 99, 235, 0.16)'",

    # Very sharp surfaces -> premium radius
    "borderRadius: 8": "borderRadius: 14",
    "borderRadius: 10": "borderRadius: 16",
    "borderRadius: 12": "borderRadius: 18",
    "borderRadius: '8px'": "borderRadius: '14px'",
    'borderRadius: "8px"': 'borderRadius: "14px"',
    "borderRadius: '10px'": "borderRadius: '16px'",
    'borderRadius: "10px"': 'borderRadius: "16px"',
    "borderRadius: '12px'": "borderRadius: '18px'",
    'borderRadius: "12px"': 'borderRadius: "18px"',

    # Strong blue-heavy backgrounds -> softer premium blue wash
    'background: "#eff6ff"': 'background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))"',
    "background: '#eff6ff'": "background: 'linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))'",
    'backgroundColor: "#eff6ff"': 'background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))"',
    "backgroundColor: '#eff6ff'": "background: 'linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))'",

    # Plain white cards -> subtle layered white
    'background: "#ffffff"': 'background: "rgba(255, 255, 255, 0.94)"',
    "background: '#ffffff'": "background: 'rgba(255, 255, 255, 0.94)'",
    'backgroundColor: "#ffffff"': 'background: "rgba(255, 255, 255, 0.94)"',
    "backgroundColor: '#ffffff'": "background: 'rgba(255, 255, 255, 0.94)'",

    # Over-heavy text black -> softer enterprise ink
    'color: "#111827"': 'color: "#0f172a"',
    "color: '#111827'": "color: '#0f172a'",
    'color: "#1f2937"': 'color: "#172033"',
    "color: '#1f2937'": "color: '#172033'",

    # Muted text consistency
    'color: "#6b7280"': 'color: "#64748b"',
    "color: '#6b7280'": "color: '#64748b'",
    'color: "#4b5563"': 'color: "#475569"',
    "color: '#4b5563'": "color: '#475569'",
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Add soft elevation to bordered card-like style objects that do not already have a shadow nearby.
# Conservative: only adds shadow immediately after clear border declarations.
text = re.sub(
    r'(border:\s*["\']1px solid rgba\(15, 23, 42, 0\.08\)["\'],\s*)',
    r'\1\n                    boxShadow: "0 18px 55px rgba(15, 23, 42, 0.06)",\n                    backdropFilter: "blur(10px)",\n                    WebkitBackdropFilter: "blur(10px)",\n                    ',
    text,
)

# Reduce visual noise from excessive all-caps/status-style labels where possible.
text = text.replace("fontWeight: 800", "fontWeight: 700")
text = text.replace("fontWeight: 900", "fontWeight: 760")

# Improve cramped common padding values where present.
text = text.replace("padding: 12", "padding: 16")
text = text.replace("padding: '12px'", "padding: '16px'")
text = text.replace('padding: "12px"', 'padding: "16px"')
text = text.replace("padding: '12px 14px'", "padding: '14px 16px'")
text = text.replace('padding: "12px 14px"', 'padding: "14px 16px"')
text = text.replace("padding: '14px 16px'", "padding: '16px 18px'")
text = text.replace('padding: "14px 16px"', 'padding: "16px 18px"')

# Protect from accidental no-op.
if text == original:
    print("WARNING: No visual replacements were applied. Page may use a different styling pattern.")

PAGE.write_text(text, encoding="utf-8")

# Verification test
TEST = ROOT / "test_client_portal_ux_pass1_declutter.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS1_DECLUTTER_RESULTS")
print("page_exists", PAGE.exists())
print("characters", len(text))
print("lines", len(text.splitlines()))
print("soft_border_count", text.count("rgba(15, 23, 42, 0.08)"))
print("soft_shadow_count", text.count("0 18px 55px rgba(15, 23, 42, 0.06)"))
print("backdrop_blur_count", text.count("backdropFilter"))
print("enterprise_ink_count", text.count("#0f172a"))
print("muted_text_count", text.count("#64748b"))

assert PAGE.exists()
assert "Execution Workspace" in text
assert "Deliverables" in text
assert "Execution Timeline" in text
assert "Workspace Actions" in text
assert len(text.splitlines()) > 1000
assert text.count("rgba(15, 23, 42, 0.08)") >= 1

print("CLIENT_PORTAL_UX_PASS1_DECLUTTER_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS1_DECLUTTER_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")