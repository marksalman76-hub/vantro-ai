from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()

PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass5_premium_inputs_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text

backup.write_text(original, encoding="utf-8")

# -------------------------------------------------------------------
# 1) Remove giant oval textarea styling globally.
# -------------------------------------------------------------------

text = text.replace(
    'borderRadius: 999,',
    'borderRadius: 16,'
)

# -------------------------------------------------------------------
# 2) Improve business profile textareas.
# -------------------------------------------------------------------

text = text.replace(
    'padding: "16px 16px"',
    'padding: "16px 18px"'
)

text = text.replace(
    'fontSize: 13.5,',
    '''fontSize: 13.5,
                    minHeight: 120,'''
)

# -------------------------------------------------------------------
# 3) Rebuild agent selector cards.
# -------------------------------------------------------------------

old_agent_style = '''style={{
                          border: active ? "1px solid #bfdbfe" : "1px solid #e5eaf2",
                          background: active ? "#eff6ff" : "#fff",
                          color: active ? "#2563eb" : "#0f172a",
                          padding: "11px 12px",
                          borderRadius: 11,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 12,
                          fontWeight: 700,
                        }}'''

new_agent_style = '''style={{
                          border: active ? "1px solid #93c5fd" : "1px solid #e5eaf2",
                          background: active
                            ? "linear-gradient(135deg,#eff6ff,#ffffff)"
                            : "#ffffff",
                          color: active ? "#2563eb" : "#0f172a",
                          padding: "14px 16px",
                          borderRadius: 16,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 13,
                          fontWeight: 760,
                          transition: "all 0.18s ease",
                          boxShadow: active
                            ? "0 10px 30px rgba(37,99,235,0.10)"
                            : "0 1px 2px rgba(15,23,42,0.03)",
                        }}'''

text = text.replace(old_agent_style, new_agent_style)

# -------------------------------------------------------------------
# 4) Improve agent section spacing.
# -------------------------------------------------------------------

text = text.replace(
    'display: "grid", gap: 7',
    'display: "grid", gap: 10'
)

text = text.replace(
    'gridTemplateColumns: "minmax(260px,360px) minmax(320px,1fr)"',
    'gridTemplateColumns: "320px minmax(0,1fr)"'
)

# -------------------------------------------------------------------
# 5) Improve task textarea.
# -------------------------------------------------------------------

text = text.replace(
    'borderRadius: 16,',
    'borderRadius: 18,',
    1
)

text = text.replace(
    'rows={6}',
    'rows={7}'
)

# -------------------------------------------------------------------
# 6) Make integrations feel premium.
# -------------------------------------------------------------------

text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))"',
    'gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))"'
)

text = text.replace(
    'padding: 20,\n                      minHeight: "100%", background: "#fff"',
    '''padding: 18,
                      minHeight: "100%",
                      background: "linear-gradient(180deg,#ffffff,#fbfdff)",
                      boxShadow: "0 6px 24px rgba(15,23,42,0.04)"'''
)

# -------------------------------------------------------------------
# 7) Improve integration action buttons.
# -------------------------------------------------------------------

text = text.replace(
    'padding: "8px 10px"',
    'padding: "9px 12px"'
)

# -------------------------------------------------------------------
# 8) Add verification marker.
# -------------------------------------------------------------------

if "client_portal_ux_pass5_premium_inputs" not in text:
    text = text.replace(
        "// client_portal_ux_pass4_two_column_layout",
        "// client_portal_ux_pass4_two_column_layout\n// client_portal_ux_pass5_premium_inputs"
    )

if text == original:
    raise RuntimeError("No Pass 5 changes applied.")

PAGE.write_text(text, encoding="utf-8")

# -------------------------------------------------------------------
# TEST
# -------------------------------------------------------------------

TEST = ROOT / "test_client_portal_ux_pass5_premium_inputs.py"

TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS5_PREMIUM_INPUTS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass5_premium_inputs" in text,
    "agent_selector_width": 'gridTemplateColumns: "320px minmax(0,1fr)"' in text,
    "premium_agent_shadow": "0 10px 30px rgba(37,99,235,0.10)" in text,
    "textarea_minheight": 'minHeight: 120' in text,
    "integration_cards": 'linear-gradient(180deg,#ffffff,#fbfdff)' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS5_PREMIUM_INPUTS_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS5_PREMIUM_INPUTS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")