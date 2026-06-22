from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
archive = ROOT / "debug_archive" / f"media_debug_noise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
archive.mkdir(parents=True, exist_ok=True)

keep_names = {
    "install_global_universal_media_pipeline_orchestrator.py",
    "verify_global_media_pipeline_stack.py",
}

patterns = [
    "check_failed_universal_media_job_*.py",
    "check_new_universal_media_pipeline_job.py",
    "inspect_failed_video_child_job_*.py",
    "failed_*_report*.txt",
    "failed_*_status*.txt",
    "new_universal_media_pipeline_job_status.txt",
    "safe_runway_key_diagnostics_report.txt",
    "inspect_*media*.py",
    "inspect_*media*.txt",
    "inspect_backend_universal*.py",
    "inspect_backend_universal*.txt",
    "live_*media*.py",
    "live_*media*.json",
    "poll_specific_media_job_*.py",
    "trigger_*media_job*.py",
    "fetch_media_job_summary_long_timeout.py",
    "media_job_*_full_status.json",
    "live_admin_media_jobs*.json",
    "live_admin_creative_media_assets*.json",
    "run_agent_media_*.txt",
    "render_dependency_audit.txt",
    "async_media_job_foundation_status_area.txt",
    "creative_asset_persistence_area.txt",
    "get_persisted_assets_area.txt",
    "exact_run_agent_blocks.txt",
    "_full_status.json",
    "tatus --short",
    "git",
    "main",
    "npm",
]

moved = []
skipped = []

for pattern in patterns:
    for path in ROOT.glob(pattern):
        if not path.is_file():
            skipped.append((str(path), "not_file"))
            continue
        if path.name in keep_names:
            skipped.append((str(path), "kept"))
            continue
        target = archive / path.name
        counter = 1
        while target.exists():
            target = archive / f"{path.stem}_{counter}{path.suffix}"
            counter += 1
        shutil.move(str(path), str(target))
        moved.append((str(path), str(target)))

report = archive / "DECLUTTER_REPORT.txt"
report.write_text(
    "DECLUTTER_MEDIA_DEBUG_NOISE\n\n"
    + f"Archive: {archive}\n\n"
    + "Moved files:\n"
    + "\n".join(f"- {src} -> {dst}" for src, dst in moved)
    + "\n\nSkipped:\n"
    + "\n".join(f"- {src}: {reason}" for src, reason in skipped)
    + "\n",
    encoding="utf-8",
)

print("DECLUTTER_MEDIA_DEBUG_NOISE_DONE")
print(f"Archive: {archive}")
print(f"Moved: {len(moved)}")
print(f"Report: {report}")
