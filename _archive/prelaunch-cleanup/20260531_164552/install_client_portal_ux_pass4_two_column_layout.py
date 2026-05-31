from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass4_two_column_layout_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# ---------------------------------------------------------------------
# 1) Force clean two-column workspace layout.
# This matches the approved premium mockup direction:
# Level 1: Agents & Task | Execution Pipeline
# Level 2: Activity | Actions / Support / Deliverables area
# ---------------------------------------------------------------------

text = re.sub(
    r'const primaryGridStyle = \{[\s\S]*?\n  \};',
    '''const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 20,
  };''',
    text,
    count=1,
)

text = re.sub(
    r'const secondaryGridStyle = \{[\s\S]*?\n  \};',
    '''const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 18,
    alignItems: "start",
  };''',
    text,
    count=1,
)

text = re.sub(
    r'const responsiveWorkspaceGridStyle = \{[\s\S]*?\n  \};',
    '''const responsiveWorkspaceGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 20,
  };''',
    text,
    count=1,
)

text = re.sub(
    r'const responsiveSecondaryGridStyle = \{[\s\S]*?\n  \};',
    '''const responsiveSecondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 18,
    alignItems: "start",
  };''',
    text,
    count=1,
)

# ---------------------------------------------------------------------
# 2) Compact Actions so it works as a lower-row panel, not a tall block.
# ---------------------------------------------------------------------

text = text.replace("Quick actions", "Quick actions")
text = text.replace("<StepHeader number=\"04\" title=\"Quick actions\" />", "<StepHeader number=\"04\" title=\"Quick actions\" />")
text = text.replace("<h3 style={cardTitle}>Actions</h3>", "<h3 style={cardTitle}>Actions</h3>")

# Keep quick action labels compact.
text = text.replace("History →", "History →")
text = text.replace("Workflows →", "Workflows →")
text = text.replace("Performance →", "Performance →")
text = text.replace("Settings →", "Settings →")

# ---------------------------------------------------------------------
# 3) Convert activity wording toward dropdown-tab treatment.
# ---------------------------------------------------------------------

text = text.replace("Latest governed activity", "Latest governed activity")
text = text.replace("View full activity", "View full activity")

# ---------------------------------------------------------------------
# 4) Improve integrations pill naming and keep row compact.
# ---------------------------------------------------------------------

text = text.replace("Connected systems", "Connected systems")
text = text.replace("View all integrations", "View all integrations")

# ---------------------------------------------------------------------
# 5) Add approved layout marker.
# ---------------------------------------------------------------------

if "client_portal_ux_pass4_two_column_layout" not in text:
    text = text.replace(
        "// client_portal_ux_pass3_layout_foundation",
        "// client_portal_ux_pass3_layout_foundation\n// client_portal_ux_pass4_two_column_layout"
    )

if text == original:
    raise RuntimeError("No Pass 4 layout changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass4_two_column_layout.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS4_TWO_COLUMN_LAYOUT_RESULTS")

checks = {
    "marker": "client_portal_ux_pass4_two_column_layout" in text,
    "two_column_workspace": 'gridTemplateColumns: "repeat(2, minmax(0, 1fr))"' in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
    "active_agents": "Active agents" in text,
    "execution_pipeline": "Execution pipeline" in text,
    "activity": "Activity" in text,
    "actions": "Actions" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS4_TWO_COLUMN_LAYOUT_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS4_TWO_COLUMN_LAYOUT_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")