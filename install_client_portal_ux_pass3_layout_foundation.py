from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass3_layout_foundation_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# ---------------------------------------------------------------------
# 1) Remove hydration-risk responsive grid logic.
# Server/client mismatch was caused by typeof window inside render styles.
# ---------------------------------------------------------------------

old_responsive_workspace = '''  const responsiveWorkspaceGridStyle = {
    display: "grid",
    gridTemplateColumns:
      typeof window !== "undefined" && window.innerWidth < 1200
        ? "1fr"
        : "1.05fr 1.2fr 1fr 0.9fr",
    gap: 20,
    alignItems: "stretch",
    marginBottom: 20,
  };

  const responsiveSecondaryGridStyle = {
    display: "grid",
    gridTemplateColumns:
      typeof window !== "undefined" && window.innerWidth < 1200
        ? "1fr"
        : "1.15fr 1fr",
    gap: 22,
    alignItems: "start",
  };

'''

new_responsive_workspace = '''  const responsiveWorkspaceGridStyle = {
    display: "grid",
    gridTemplateColumns: "minmax(360px, 1.15fr) minmax(260px, 0.85fr) minmax(260px, 0.75fr)",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 20,
  };

  const responsiveSecondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "minmax(360px, 0.9fr) minmax(520px, 1.1fr)",
    gap: 20,
    alignItems: "start",
  };

'''

if old_responsive_workspace in text:
    text = text.replace(old_responsive_workspace, new_responsive_workspace)
else:
    # fallback if previous spacing changed slightly
    start = text.find("const responsiveWorkspaceGridStyle = {")
    end = text.find("const modalContentGridStyle = {", start)
    if start != -1 and end != -1:
        text = text[:start] + new_responsive_workspace + "\n" + text[end:]

# ---------------------------------------------------------------------
# 2) Make original grid constants match the same stable layout.
# ---------------------------------------------------------------------

text = text.replace(
'''const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "1.05fr 1.2fr 1fr 0.9fr",
    gap: 20,
    alignItems: "stretch",
    marginBottom: 20,
  };''',
'''const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "minmax(360px, 1.15fr) minmax(260px, 0.85fr) minmax(260px, 0.75fr)",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 20,
  };'''
)

text = text.replace(
'''const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "1.15fr 1fr",
    gap: 22,
    alignItems: "start",
  };''',
'''const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "minmax(360px, 0.9fr) minmax(520px, 1.1fr)",
    gap: 20,
    alignItems: "start",
  };'''
)

# ---------------------------------------------------------------------
# 3) Improve integrations visual language from large tiles to pills.
# Conservative replacements only; no logic touched.
# ---------------------------------------------------------------------

text = text.replace(
    'StepHeader number="',
    'StepHeader number="'
)

# Soften integration-card style patterns.
text = text.replace(
    'padding: "16px 18px"',
    'padding: "12px 14px"'
)

text = text.replace(
    'padding: "16px 18px",',
    'padding: "12px 14px",'
)

text = text.replace(
    'borderRadius: 18',
    'borderRadius: 16'
)

# Make connected/disconnected controls more pill-like.
text = text.replace(
    'borderRadius: 13',
    'borderRadius: 999'
)

text = text.replace(
    'borderRadius: 14',
    'borderRadius: 999'
)

# ---------------------------------------------------------------------
# 4) Fix the copy/layout so agent section reads more compact and premium.
# ---------------------------------------------------------------------

text = text.replace(
    "Select approved agents, define a business objective, and launch governed execution.",
    "Select approved agents and launch governed execution."
)

text = text.replace(
    "Purchased & active agents",
    "Active agents"
)

text = text.replace(
    "All agents will use the business profile context above.",
    "Runs use your saved business profile."
)

# ---------------------------------------------------------------------
# 5) Make quick actions less cramped.
# ---------------------------------------------------------------------

text = text.replace(
    "Workspace controls",
    "Actions"
)

text = text.replace(
    "View execution history",
    "History"
)

text = text.replace(
    "Manage workflows",
    "Workflows"
)

text = text.replace(
    "Agent performance",
    "Performance"
)

text = text.replace(
    "Workspace settings",
    "Settings"
)

# ---------------------------------------------------------------------
# 6) Prepare timeline language for dropdown/activity tab.
# ---------------------------------------------------------------------

text = text.replace(
    "Activity feed",
    "Activity"
)

text = text.replace(
    "Governed activity tracking connected",
    "Latest governed activity"
)

# ---------------------------------------------------------------------
# 7) Add a safer compact surface helper copy marker for verification.
# ---------------------------------------------------------------------

if "client_portal_ux_pass3_layout_foundation" not in text:
    text = text.replace(
        "export default function ClientPage() {",
        "// client_portal_ux_pass3_layout_foundation\nexport default function ClientPage() {"
    )

if text == original:
    raise RuntimeError("No Pass 3 layout foundation changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass3_layout_foundation.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS3_LAYOUT_FOUNDATION_RESULTS")

checks = {
    "marker": "client_portal_ux_pass3_layout_foundation" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
    "stable_workspace_grid": 'gridTemplateColumns: "minmax(360px, 1.15fr) minmax(260px, 0.85fr) minmax(260px, 0.75fr)"' in text,
    "stable_secondary_grid": 'gridTemplateColumns: "minmax(360px, 0.9fr) minmax(520px, 1.1fr)"' in text,
    "compact_agent_copy": "Select approved agents and launch governed execution." in text,
    "active_agents_copy": "Active agents" in text,
    "latest_activity_copy": "Latest governed activity" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS3_LAYOUT_FOUNDATION_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS3_LAYOUT_FOUNDATION_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")