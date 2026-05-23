from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_execution_workspace_tighten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = """
style={{
                display: "flex",
                flexDirection: "column",
                gap: 10,
                maxHeight: 310,
                overflowY: "auto",
                paddingRight: 4,
              }}
"""

new = """
style={{
                display: "flex",
                flexDirection: "column",
                gap: 8,
                maxHeight: 520,
                overflowY: "auto",
                paddingRight: 6,
                minHeight: 520,
              }}
"""

if old not in text:
    raise SystemExit("Could not locate agent list container.")

text = text.replace(old, new, 1)

old_pipeline = """
[
              ["1", "Execution requested", "Started", "Live"],
              ["2", "Deliverable status", "Ready", "Live"],
              ["3", "Client review", "Pending", "Open"],
              ["4", "Execution ready", "Next", "—"],
            ].map(
"""

new_pipeline = """
[
              ["1", "Execution requested", "Started", "Live"],
              ["2", "Deliverable status", "Ready", "Live"],
              ["3", "Client review", "Pending", "Open"],
              ["4", "Execution ready", "Next", "—"],
              ["5", "Optimisation layer", "Monitoring", "Active"],
            ].map(
"""

if old_pipeline not in text:
    raise SystemExit("Could not locate execution pipeline rows.")

text = text.replace(old_pipeline, new_pipeline, 1)

old_pipeline_gap = """
display: "grid",
              gap: 12,
"""

new_pipeline_gap = """
display: "grid",
              gap: 10,
              minHeight: 520,
"""

text = text.replace(old_pipeline_gap, new_pipeline_gap, 1)

path.write_text(text, encoding="utf-8")

print("EXECUTION_WORKSPACE_EMPTY_SPACE_FIXED")
print(f"Backup: {backup}")