from pathlib import Path
from datetime import datetime
import re

p = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"media_popup_duration_aspect_mismatch_v2_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "UniversalCompleteMediaRunAgentPanel.tsx").write_text(s, encoding="utf-8")

def replace_once(source: str, old: str, new: str) -> str:
    if old not in source:
        raise SystemExit(f"Expected block not found:\n{old[:600]}")
    return source.replace(old, new, 1)

# 1. Add 25 seconds to the dropdown.
s = s.replace(
    'const DURATIONS = ["5", "10", "15", "30", "45", "60"];',
    'const DURATIONS = ["5", "10", "15", "25", "30", "45", "60"];',
)

# 2. Safer defaults: 25s / 16:9 instead of 5s / 9:16.
s = s.replace(
    'const [durationSeconds, setDurationSeconds] = useState("5");',
    'const [durationSeconds, setDurationSeconds] = useState("25");',
)

s = s.replace(
    'const [aspectRatio, setAspectRatio] = useState("9:16");',
    'const [aspectRatio, setAspectRatio] = useState("16:9");',
)

# 3. Add prompt-detection helpers before component export.
helper_marker = "export default function UniversalCompleteMediaRunAgentPanel({"
helpers = r'''
function detectDurationSecondsFromPrompt(prompt: string): string {
  const text = String(prompt || "").toLowerCase();

  const directMatch = text.match(/\b(\d{1,3})\s*(?:seconds|second|secs|sec)\b/);
  if (directMatch?.[1]) {
    return directMatch[1];
  }

  const compactMatch = text.match(/\b(\d{1,3})s\b/);
  if (compactMatch?.[1]) {
    return compactMatch[1];
  }

  return "";
}

function detectAspectRatioFromPrompt(prompt: string): string {
  const text = String(prompt || "").toLowerCase();

  if (text.includes("16:9") || text.includes("landscape") || text.includes("horizontal") || text.includes("youtube")) {
    return "16:9";
  }

  if (text.includes("9:16") || text.includes("vertical") || text.includes("reel") || text.includes("tiktok") || text.includes("shorts")) {
    return "9:16";
  }

  if (text.includes("1:1") || text.includes("square")) {
    return "1:1";
  }

  if (text.includes("4:5")) {
    return "4:5";
  }

  return "";
}

function buildMediaSettingWarning(prompt: string, durationSeconds: string, aspectRatio: string): string {
  const detectedDuration = detectDurationSecondsFromPrompt(prompt);
  const detectedAspectRatio = detectAspectRatioFromPrompt(prompt);
  const warnings: string[] = [];

  if (detectedDuration && detectedDuration !== String(durationSeconds || "")) {
    warnings.push(`Prompt asks for ${detectedDuration}s, but selected duration is ${durationSeconds}s.`);
  }

  if (detectedAspectRatio && detectedAspectRatio !== String(aspectRatio || "")) {
    warnings.push(`Prompt asks for ${detectedAspectRatio}, but selected aspect ratio is ${aspectRatio}.`);
  }

  return warnings.join(" ");
}

function resolveFinalDuration(prompt: string, selectedDuration: string): string {
  return detectDurationSecondsFromPrompt(prompt) || selectedDuration || "25";
}

function resolveFinalAspectRatio(prompt: string, selectedAspectRatio: string): string {
  return detectAspectRatioFromPrompt(prompt) || selectedAspectRatio || "16:9";
}
'''
if "function detectDurationSecondsFromPrompt" not in s:
    s = s.replace(helper_marker, helpers + "\n" + helper_marker, 1)

# 4. Add computed final settings inside component, after mediaConfig useMemo exists.
anchor = "  useEffect(() => {\n    onConfigChange?.(mediaConfig);"
insert = """  const detectedPromptDuration = useMemo(() => detectDurationSecondsFromPrompt(prompt), [prompt]);
  const detectedPromptAspectRatio = useMemo(() => detectAspectRatioFromPrompt(prompt), [prompt]);
  const finalDurationSeconds = useMemo(
    () => resolveFinalDuration(prompt, durationSeconds),
    [prompt, durationSeconds]
  );
  const finalAspectRatio = useMemo(
    () => resolveFinalAspectRatio(prompt, aspectRatio),
    [prompt, aspectRatio]
  );
  const mediaSettingWarning = useMemo(
    () => buildMediaSettingWarning(prompt, durationSeconds, aspectRatio),
    [prompt, durationSeconds, aspectRatio]
  );

  useEffect(() => {
    if (detectedPromptDuration && detectedPromptDuration !== durationSeconds) {
      setDurationSeconds(detectedPromptDuration);
    }
  }, [detectedPromptDuration]);

  useEffect(() => {
    if (detectedPromptAspectRatio && detectedPromptAspectRatio !== aspectRatio) {
      setAspectRatio(detectedPromptAspectRatio);
    }
  }, [detectedPromptAspectRatio]);

"""
if "const detectedPromptDuration = useMemo" not in s:
    s = replace_once(s, anchor, insert + anchor)

# 5. Make payload use final resolved values.
s = s.replace(
    "duration_seconds: directConfig.duration_seconds || durationSeconds,",
    "duration_seconds: finalDurationSeconds || directConfig.duration_seconds || durationSeconds,"
)
s = s.replace(
    "aspect_ratio: directConfig.aspect_ratio || aspectRatio,",
    "aspect_ratio: finalAspectRatio || directConfig.aspect_ratio || aspectRatio,"
)

# Also update mediaConfig source fields if present.
s = s.replace(
    "duration_seconds: durationSeconds,",
    "duration_seconds: finalDurationSeconds || durationSeconds,"
)
s = s.replace(
    "aspect_ratio: aspectRatio,",
    "aspect_ratio: finalAspectRatio || aspectRatio,"
)

# 6. Insert visible final settings panel before advanced controls.
advanced_button = """              <button
                type="button"
                onClick={() => setAdvancedOpen((value) => !value)}
"""
settings_panel = """              <div
                data-complete-media-final-settings="true"
                style={{
                  marginTop: 12,
                  border: mediaSettingWarning
                    ? "1px solid rgba(245,158,11,.35)"
                    : "1px solid rgba(14,207,188,.24)",
                  background: mediaSettingWarning
                    ? "rgba(245,158,11,.08)"
                    : "rgba(14,207,188,.06)",
                  borderRadius: 14,
                  padding: 12,
                  color: "#dbeafe",
                  fontSize: 12,
                  lineHeight: 1.5,
                }}
              >
                <strong style={{ display: "block", color: "#fff", marginBottom: 4 }}>
                  Final media settings
                </strong>
                <span>
                  Duration: {finalDurationSeconds}s · Aspect ratio: {finalAspectRatio}
                  {detectedPromptDuration ? ` · Prompt duration detected: ${detectedPromptDuration}s` : ""}
                  {detectedPromptAspectRatio ? ` · Prompt aspect detected: ${detectedPromptAspectRatio}` : ""}
                </span>
                {mediaSettingWarning ? (
                  <div style={{ marginTop: 8, color: "#fcd34d", fontWeight: 850 }}>
                    {mediaSettingWarning}
                  </div>
                ) : null}
              </div>

"""
if 'data-complete-media-final-settings="true"' not in s:
    s = replace_once(s, advanced_button, settings_panel + advanced_button)

# 7. Add a status warning near the start of runCompleteMediaFromPopup, without relying on prompt.trim block.
run_marker = "  async function runCompleteMediaFromPopup() {"
run_insert = """  async function runCompleteMediaFromPopup() {
    const settingWarning = buildMediaSettingWarning(prompt, durationSeconds, aspectRatio);
    if (settingWarning) {
      setStatusMessage(`Media settings warning: ${settingWarning} Using final resolved popup settings.`);
    }
"""
if "Using final resolved popup settings" not in s:
    s = replace_once(s, run_marker, run_insert)

p.write_text(s, encoding="utf-8")
print("MEDIA_POPUP_DURATION_ASPECT_MISMATCH_V2_FIXED")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")