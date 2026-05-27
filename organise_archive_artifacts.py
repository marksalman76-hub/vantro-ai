from pathlib import Path
import shutil

root = Path.cwd()
archive_root = root / "archive"

if not archive_root.exists():
    raise SystemExit("archive folder not found")

buckets = {
    "installers": ("install_", "add_", "apply_", "update_"),
    "tests": ("test_",),
    "live-verification": ("live_", "verify_"),
    "wire-scripts": ("wire_",),
    "debug": ("inspect_", "check_", "find_", "force_", "fix_", "output_", "portal_", "package_"),
}

for bucket in buckets:
    (archive_root / bucket).mkdir(parents=True, exist_ok=True)

moved = 0

for stale_folder in archive_root.glob("stale_root_files_*"):
    if not stale_folder.is_dir():
        continue

    for item in list(stale_folder.iterdir()):
        if item.is_dir():
            continue

        name = item.name
        destination_bucket = None

        for bucket, prefixes in buckets.items():
            if name.startswith(prefixes):
                destination_bucket = bucket
                break

        if destination_bucket is None:
            destination_bucket = "debug"

        destination = archive_root / destination_bucket / name

        if destination.exists():
            stem = destination.stem
            suffix = destination.suffix
            i = 2
            while True:
                renamed = archive_root / destination_bucket / f"{stem}_{i}{suffix}"
                if not renamed.exists():
                    destination = renamed
                    break
                i += 1

        shutil.move(str(item), str(destination))
        moved += 1

    try:
        stale_folder.rmdir()
    except OSError:
        pass

print("ARCHIVE_ORGANISED")
print(f"Moved files: {moved}")
print("Created/used:")
for bucket in buckets:
    print(f"- archive/{bucket}")