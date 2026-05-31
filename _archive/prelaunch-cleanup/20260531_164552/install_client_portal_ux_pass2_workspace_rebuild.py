from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()

PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass2_workspace_rebuild_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text

backup.write_text(original, encoding="utf-8")

# -------------------------------------------------------------------
# GRID FOUNDATION UPGRADE
# -------------------------------------------------------------------

text = text.replace(
'''const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,300px),1fr))",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 16,
  };''',
'''const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "1.05fr 1.2fr 1fr 0.9fr",
    gap: 20,
    alignItems: "stretch",
    marginBottom: 20,
  };'''
)

text = text.replace(
'''const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,340px),1fr))",
    gap: 18,
    alignItems: "stretch",
  };''',
'''const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "1.15fr 1fr",
    gap: 22,
    alignItems: "start",
  };'''
)

# -------------------------------------------------------------------
# RESPONSIVE GRID IMPROVEMENT
# -------------------------------------------------------------------

responsive_injection = '''
  const responsiveWorkspaceGridStyle = {
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

marker = 'const modalContentGridStyle = {'

if responsive_injection not in text:
    text = text.replace(marker, responsive_injection + '\n' + marker)

# -------------------------------------------------------------------
# CARD FOUNDATION UPGRADE
# -------------------------------------------------------------------

text = text.replace(
'padding: 16,',
'''padding: 20,
                      minHeight: "100%",'''
)

text = text.replace(
'padding: 18,',
'''padding: 22,'''
)

# -------------------------------------------------------------------
# AGENT PANEL IMPROVEMENTS
# -------------------------------------------------------------------

text = text.replace(
'Active agents',
'Purchased & active agents'
)

text = text.replace(
'Select agents, define task, and execute.',
'Select approved agents, define a business objective, and launch governed execution.'
)

# -------------------------------------------------------------------
# TASK SECTION SPACING FIX
# -------------------------------------------------------------------

text = text.replace(
'display: "grid", gap: 16',
'display: "grid", gap: 22'
)

text = text.replace(
'display: "flex", gap: 12',
'display: "flex", gap: 16, alignItems: "flex-start"'
)

# -------------------------------------------------------------------
# EXECUTION PIPELINE CLEANUP
# -------------------------------------------------------------------

text = text.replace(
'Governed execution pipeline',
'Execution pipeline'
)

text = text.replace(
'Every AI deliverable flows through approval, optimisation, workflow validation, and governed execution before deployment.',
'Every deliverable passes through governed validation, approval control, optimisation, and execution readiness before deployment.'
)

# -------------------------------------------------------------------
# QUICK ACTIONS CLEANUP
# -------------------------------------------------------------------

text = text.replace(
'Workspace actions',
'Workspace controls'
)

# -------------------------------------------------------------------
# EXECUTION WORKSPACE COPY CLEANUP
# -------------------------------------------------------------------

text = text.replace(
'Client deliverables will appear here',
'Execution deliverables'
)

text = text.replace(
'Campaign outputs, approvals, execution flows, creative assets, billing events, and governed automation actions will appear after execution.',
'Generated deliverables, approvals, media assets, workflow outputs, and execution results appear here after governed processing.'
)

# -------------------------------------------------------------------
# TIMELINE HEADER CLEANUP
# -------------------------------------------------------------------

text = text.replace(
'Execution timeline',
'Activity feed'
)

text = text.replace(
'Live governed execution events connected',
'Governed activity tracking connected'
)

# -------------------------------------------------------------------
# REDUCE VISUAL WEIGHT
# -------------------------------------------------------------------

text = text.replace(
'fontWeight: 950',
'fontWeight: 800'
)

text = text.replace(
'fontWeight: 900',
'fontWeight: 760'
)

# -------------------------------------------------------------------
# ADD PREMIUM CARD DEPTH
# -------------------------------------------------------------------

text = text.replace(
'boxShadow: "0 12px 30px rgba(15,23,42,0.05)"',
'boxShadow: "0 20px 55px rgba(15,23,42,0.06)"'
)

# -------------------------------------------------------------------
# USE RESPONSIVE GRID
# -------------------------------------------------------------------

text = text.replace(
'<section style={primaryGridStyle}>',
'<section style={responsiveWorkspaceGridStyle}>'
)

text = text.replace(
'<section style={secondaryGridStyle}>',
'<section style={responsiveSecondaryGridStyle}>'
)

# -------------------------------------------------------------------
# SAFETY
# -------------------------------------------------------------------

if text == original:
    raise RuntimeError("No workspace rebuild changes applied.")

PAGE.write_text(text, encoding="utf-8")

# -------------------------------------------------------------------
# TEST
# -------------------------------------------------------------------

TEST = ROOT / "test_client_portal_ux_pass2_workspace_rebuild.py"

TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS2_WORKSPACE_REBUILD_RESULTS")

checks = {
    "responsive_workspace_grid": "responsiveWorkspaceGridStyle" in text,
    "responsive_secondary_grid": "responsiveSecondaryGridStyle" in text,
    "workspace_controls_copy": "Workspace controls" in text,
    "activity_feed_copy": "Activity feed" in text,
    "execution_deliverables_copy": "Execution deliverables" in text,
    "agent_copy": "Purchased & active agents" in text,
    "premium_shadow": "0 20px 55px rgba(15,23,42,0.06)" in text,
    "governed_activity_copy": "Governed activity tracking connected" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS2_WORKSPACE_REBUILD_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS2_WORKSPACE_REBUILD_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")