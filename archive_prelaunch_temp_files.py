from pathlib import Path
from datetime import datetime
import shutil
import json

ROOT = Path(__file__).resolve().parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ARCHIVE = ROOT / "_archive" / "prelaunch-cleanup" / STAMP

KEEP_PATTERNS = {
    "requirements.txt",
    "render.yaml",
    ".gitignore",
}

ARCHIVE_PREFIXES = (
    "install_",
    "fix_",
    "wire_",
    "diagnose_",
    "audit_",
    "live_",
    "test_",
    "create_",
    "find_",
)

ARCHIVE_SUFFIXES = (
    "_report.json",
    "_audit.json",
)

ARCHIVE_EXACT = {
    "audit-ci.json",
    "load_test_failure_profile_report.json",
    "queue_execution_dry_run.py",
    "queue_execution_dry_run_report.json",
    "deferred_activation_items_audit.json",
    "final_activation_closeout_report.json",
    "final_render_smoke_verification_report.json",
}

def should_archive(path: Path) -> bool:
    if path.is_dir():
        return False
    name = path.name

    if name in KEEP_PATTERNS:
        return False

    if name in ARCHIVE_EXACT:
        return True

    if any(name.startswith(prefix) for prefix in ARCHIVE_PREFIXES):
        return True

    if any(name.endswith(suffix) for suffix in ARCHIVE_SUFFIXES):
        return True

    return False

def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    moved = []
    for path in ROOT.iterdir():
        if should_archive(path):
            target = ARCHIVE / path.name
            shutil.move(str(path), str(target))
            moved.append({"from": str(path), "to": str(target)})

    manifest = {
        "archive": str(ARCHIVE),
        "moved_count": len(moved),
        "moved": moved,
        "deleted": False,
        "customer_safe": True,
    }

    (ARCHIVE / "archive_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("PRELAUNCH_TEMP_FILES_ARCHIVED")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()