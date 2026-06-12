from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"complete_media_popup_onresult_prop_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

if "onResult?: (deliverable: any) => void;" not in text:
    old = '''  onConfigChange?: (config: CompleteMediaConfig) => void;
}) {'''
    new = '''  onConfigChange?: (config: CompleteMediaConfig) => void;
  onResult?: (deliverable: any) => void;
}) {'''
    if old not in text:
        raise SystemExit("PROPS_TYPE_INSERT_MARKER_NOT_FOUND")
    text = text.replace(old, new)

if "onResult," not in text:
    old = '''  mode = "client",
  onConfigChange,
}: {'''
    new = '''  mode = "client",
  onConfigChange,
  onResult,
}: {'''
    if old not in text:
        raise SystemExit("PROPS_DESTRUCTURE_INSERT_MARKER_NOT_FOUND")
    text = text.replace(old, new)

if "onResult?.(result);" not in text:
    old = '''      window.dispatchEvent(
        new CustomEvent("universal-complete-media-run-now", {
          detail: {
            endpoint,
            payload,
            result,
            native_popup_execution: true,
          },
        })
      );'''
    new = '''      onResult?.(result);

      window.dispatchEvent(
        new CustomEvent("universal-complete-media-run-now", {
          detail: {
            endpoint,
            payload,
            result,
            native_popup_execution: true,
          },
        })
      );'''
    if old not in text:
        raise SystemExit("ONRESULT_CALL_INSERT_MARKER_NOT_FOUND")
    text = text.replace(old, new)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "onResult?: (deliverable: any) => void;",
    "onResult,",
    "onResult?.(result);",
    "data-true-direct-complete-media-popup",
    "Create complete media now",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("COMPLETE_MEDIA_POPUP_ONRESULT_PROP_RESTORED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")