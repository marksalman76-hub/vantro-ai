from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass7_compact_agents_integrations_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Compact agent/task split so task box stays aligned.
text = text.replace(
    'gridTemplateColumns: "minmax(300px, 0.92fr) minmax(360px, 1.08fr)"',
    'gridTemplateColumns: "280px minmax(0,1fr)"'
)

text = text.replace(
    'padding: "13px 14px"',
    'padding: "9px 11px"'
)

text = text.replace(
    'fontSize: 13,\n                          fontWeight: 760,',
    'fontSize: 12.5,\n                          fontWeight: 700,'
)

text = text.replace(
    'borderRadius: 16,\n                          cursor: "pointer",',
    'borderRadius: 12,\n                          cursor: "pointer",'
)

# Make task box cleaner and aligned.
text = text.replace(
    'rows={6}',
    'rows={5}'
)

text = text.replace(
    'boxShadow: "inset 0 1px 2px rgba(15, 23, 42, 0.04)",',
    'boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",'
)

# Convert integrations grid/cards closer to pills.
text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))"',
    'gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))"'
)

text = text.replace(
    '''<div key={integration.integration_key} style={{ border: "1px solid #e5eaf2", borderRadius: 16, padding: 18,
                      minHeight: "100%",
                      background: "linear-gradient(180deg,#ffffff,#fbfdff)",
                      boxShadow: "0 6px 24px rgba(15,23,42,0.04)" }}>''',
    '''<div key={integration.integration_key} style={{ border: "1px solid rgba(15,23,42,0.08)", borderRadius: 18, padding: 12,
                      minHeight: 0,
                      background: "#ffffff",
                      boxShadow: "0 4px 18px rgba(15,23,42,0.035)" }}>'''
)

# Hide noisy detail rows by making them visually smaller.
text = text.replace(
    'marginTop: 12, color: "#64748b", fontSize: 11.5, lineHeight: 1.35',
    'marginTop: 6, color: "#64748b", fontSize: 10.5, lineHeight: 1.25'
)

text = text.replace(
    'marginTop: 8, color: "#64748b", fontSize: 11.5, lineHeight: 1.35',
    'marginTop: 4, color: "#64748b", fontSize: 10.5, lineHeight: 1.25'
)

# Make integration action buttons smaller.
text = text.replace(
    'padding: "9px 12px"',
    'padding: "6px 9px"'
)

# Marker.
if "client_portal_ux_pass7_compact_agents_integrations" not in text:
    text = text.replace(
        "// client_portal_ux_pass6_agents_integrations",
        "// client_portal_ux_pass6_agents_integrations\n// client_portal_ux_pass7_compact_agents_integrations"
    )

if text == original:
    raise RuntimeError("No Pass 7 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass7_compact_agents_integrations.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS7_COMPACT_AGENTS_INTEGRATIONS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass7_compact_agents_integrations" in text,
    "compact_agent_grid": 'gridTemplateColumns: "280px minmax(0,1fr)"' in text,
    "compact_agent_padding": 'padding: "9px 11px"' in text,
    "compact_integrations": 'gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))"' in text,
    "task_rows": "rows={5}" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS7_COMPACT_AGENTS_INTEGRATIONS_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS7_COMPACT_AGENTS_INTEGRATIONS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")