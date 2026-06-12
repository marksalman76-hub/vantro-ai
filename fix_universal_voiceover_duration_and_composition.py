from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
BACKUP_DIR = ROOT / "backups" / f"universal_voiceover_duration_composition_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

insert_marker = "\ndef _ucm_provider_safe_visual_prompt"
if insert_marker not in text:
    raise SystemExit("VOICE_HELPER_INSERT_MARKER_NOT_FOUND")

if "def _ucm_provider_safe_voice_prompt" not in text:
    helper = r'''

def _ucm_provider_safe_voice_prompt(prompt: str, duration_seconds: int | float = 5) -> str:
    """
    Keep voiceover close to the target clip duration.
    Approximate spoken English at 2.2 words/sec for clear promo narration.
    """
    clean = " ".join(str(prompt or "").split()).strip()
    duration = max(3.0, float(duration_seconds or 5))
    max_words = max(8, int(duration * 2.2))

    # Prefer quoted voiceover line if present.
    quoted = re.findall(r"[“\"]([^”\"]{8,260})[”\"]", clean)
    if quoted:
        clean = " ".join(quoted).strip()

    words = clean.split()
    if len(words) > max_words:
        clean = " ".join(words[:max_words]).strip()

    return clean

'''
    text = text.replace(insert_marker, helper + insert_marker, 1)

old_audio = '''            audio_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["audio_provider"],
                "media_type": "audio",
                "prompt": plan["voice_prompt"],
                "owner_approved": True,
                "owner_approval_granted": True,
            })'''

new_audio = '''            provider_voice_prompt = _ucm_provider_safe_voice_prompt(
                plan["voice_prompt"],
                controls["duration_seconds"],
            )

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_audio_generation",
                "video_job_id": video_result.get("job_id"),
                "video_provider_job_id": video_result.get("provider_job_id"),
                "timed_plan": plan.get("timed_plan"),
                "voice_prompt_character_count": len(plan.get("voice_prompt") or ""),
                "provider_voice_prompt_character_count": len(provider_voice_prompt),
                "provider_voice_prompt_words": len(provider_voice_prompt.split()),
            })

            audio_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["audio_provider"],
                "media_type": "audio",
                "prompt": provider_voice_prompt,
                "owner_approved": True,
                "owner_approval_granted": True,
            })'''

if old_audio not in text:
    raise SystemExit("AUDIO_RESULT_CALL_BLOCK_NOT_FOUND")

text = text.replace(old_audio, new_audio, 1)

# Replace risky filter chain in _ucm_compose_with_sync.
old_filter_block = '''        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=async=1:first_pts=0",
        "-shortest",
        "-movflags",
        "+faststart",'''

new_filter_block = '''        "-ac",
        "2",
        "-ar",
        "44100",
        "-shortest",
        "-movflags",
        "+faststart",'''

if old_filter_block not in text:
    raise SystemExit("FFMPEG_FILTER_BLOCK_NOT_FOUND")

text = text.replace(old_filter_block, new_filter_block, 1)

# Also improve sync strategy marker.
text = text.replace(
    '"sync_strategy": "normalise_audio_resample_async_shortest_faststart",',
    '"sync_strategy": "safe_stereo_44100hz_aac_shortest_faststart",',
    1,
)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "def _ucm_provider_safe_voice_prompt",
    "provider_voice_prompt = _ucm_provider_safe_voice_prompt",
    '"prompt": provider_voice_prompt',
    '"-ac"',
    '"2"',
    '"-ar"',
    '"44100"',
    "safe_stereo_44100hz_aac_shortest_faststart",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("UNIVERSAL_VOICEOVER_DURATION_AND_COMPOSITION_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")