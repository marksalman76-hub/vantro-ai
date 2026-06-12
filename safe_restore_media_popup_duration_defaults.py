from pathlib import Path
from datetime import datetime

p = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"safe_restore_media_popup_duration_defaults_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "UniversalCompleteMediaRunAgentPanel.tsx").write_text(s, encoding="utf-8")

s = s.replace(
    'const DURATIONS = ["5", "10", "15", "30", "45", "60"];',
    'const DURATIONS = ["5", "10", "15", "25", "30", "45", "60"];',
)

s = s.replace(
    'const [durationSeconds, setDurationSeconds] = useState("5");',
    'const [durationSeconds, setDurationSeconds] = useState("25");',
)

s = s.replace(
    'const [aspectRatio, setAspectRatio] = useState("9:16");',
    'const [aspectRatio, setAspectRatio] = useState("16:9");',
)

p.write_text(s, encoding="utf-8")
print("SAFE_MEDIA_POPUP_DURATION_DEFAULTS_RESTORED")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")