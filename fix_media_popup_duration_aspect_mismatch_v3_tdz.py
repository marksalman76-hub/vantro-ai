from pathlib import Path
from datetime import datetime

p = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"media_popup_duration_aspect_mismatch_v3_tdz_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "UniversalCompleteMediaRunAgentPanel.tsx").write_text(s, encoding="utf-8")

# Fix TDZ/build issue:
# mediaConfig is declared before finalDurationSeconds/finalAspectRatio,
# so it must not reference those final computed values.
s = s.replace(
    "duration_seconds: finalDurationSeconds || durationSeconds,",
    "duration_seconds: durationSeconds,"
)

s = s.replace(
    "aspect_ratio: finalAspectRatio || aspectRatio,",
    "aspect_ratio: aspectRatio,"
)

# Keep the actual submit payload protected.
# If an earlier replacement accidentally removed final payload resolution, restore it.
s = s.replace(
    "duration_seconds: directConfig.duration_seconds || durationSeconds,",
    "duration_seconds: finalDurationSeconds || directConfig.duration_seconds || durationSeconds,"
)

s = s.replace(
    "aspect_ratio: directConfig.aspect_ratio || aspectRatio,",
    "aspect_ratio: finalAspectRatio || directConfig.aspect_ratio || aspectRatio,"
)

p.write_text(s, encoding="utf-8")
print("MEDIA_POPUP_DURATION_ASPECT_TDZ_FIXED")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")