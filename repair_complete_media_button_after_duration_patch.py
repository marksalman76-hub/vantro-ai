from pathlib import Path
from datetime import datetime
import re

p = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"repair_complete_media_button_after_duration_patch_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "UniversalCompleteMediaRunAgentPanel.tsx").write_text(s, encoding="utf-8")

# Keep the safe UI fixes.
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

# Remove final resolved references from submit payload so click handler cannot fail on a hook/order issue.
s = s.replace(
    "duration_seconds: finalDurationSeconds || directConfig.duration_seconds || durationSeconds,",
    "duration_seconds: durationSeconds,"
)

s = s.replace(
    "aspect_ratio: finalAspectRatio || directConfig.aspect_ratio || aspectRatio,",
    "aspect_ratio: aspectRatio,"
)

s = s.replace(
    "duration_seconds: finalDurationSeconds || durationSeconds,",
    "duration_seconds: durationSeconds,"
)

s = s.replace(
    "aspect_ratio: finalAspectRatio || aspectRatio,",
    "aspect_ratio: aspectRatio,"
)

# Make the visible final settings panel use plain state values, not computed hook values.
s = s.replace("Duration: {finalDurationSeconds}s · Aspect ratio: {finalAspectRatio}", "Duration: {durationSeconds}s · Aspect ratio: {aspectRatio}")

# Remove the extra warning at the very top of runCompleteMediaFromPopup if it was inserted.
s = s.replace(
'''  async function runCompleteMediaFromPopup() {
    const settingWarning = buildMediaSettingWarning(prompt, durationSeconds, aspectRatio);
    if (settingWarning) {
      setStatusMessage(`Media settings warning: ${settingWarning} Using final resolved popup settings.`);
    }
''',
'''  async function runCompleteMediaFromPopup() {
'''
)

# Ensure the create button is explicitly a normal button, not an accidental submit button.
s = s.replace(
'''              <button
                className="primary"
                data-complete-media-native-execution="true"
                onClick={runCompleteMediaFromPopup}
''',
'''              <button
                type="button"
                className="primary"
                data-complete-media-native-execution="true"
                onClick={() => void runCompleteMediaFromPopup()}
'''
)

p.write_text(s, encoding="utf-8")
print("COMPLETE_MEDIA_BUTTON_REPAIRED_AFTER_DURATION_PATCH")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")