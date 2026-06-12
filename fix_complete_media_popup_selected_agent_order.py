from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"complete_media_popup_selected_agent_order_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

line = '  const [selectedPopupAgent, setSelectedPopupAgent] = useState("auto");\n'

if line not in text:
    raise SystemExit("SELECTED_POPUP_AGENT_STATE_LINE_NOT_FOUND")

# Remove current misplaced state line.
text = text.replace(line, "", 1)

# Insert it immediately after portalMode so it exists before primaryAgent is calculated.
marker = '  const portalMode: "admin" | "client" = mode === "admin" ? "admin" : "client";\n'
if marker not in text:
    raise SystemExit("PORTAL_MODE_MARKER_NOT_FOUND")

text = text.replace(marker, marker + "\n" + line, 1)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
portal_index = verify.find(marker)
state_index = verify.find(line)
primary_index = verify.find("  const primaryAgent =")

if state_index == -1 or primary_index == -1:
    raise SystemExit("ORDER_VERIFY_MARKERS_NOT_FOUND")

if not (portal_index < state_index < primary_index):
    raise SystemExit("SELECTED_POPUP_AGENT_ORDER_STILL_INVALID")

print("COMPLETE_MEDIA_POPUP_SELECTED_AGENT_ORDER_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")