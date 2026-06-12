from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
BACKUP_DIR = ROOT / "backups" / f"universal_runway_prompt_limit_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

helper_marker = "\ndef _ucm_get_duration_seconds"
if helper_marker not in text:
    raise SystemExit("HELPER_INSERT_MARKER_NOT_FOUND")

if "def _ucm_provider_safe_visual_prompt" not in text:
    helper = r'''

def _ucm_provider_safe_visual_prompt(prompt: str, max_chars: int = 950) -> str:
    """
    Runway promptText currently rejects prompts over 1000 characters.
    Keep universal complete media planning rich internally, but send providers a concise visual prompt.
    This is intentionally broad-media safe and not ecommerce-only.
    """
    clean = " ".join(str(prompt or "").split()).strip()

    if len(clean) <= max_chars:
        return clean

    # Prefer complete sentence boundaries so the provider receives a coherent prompt.
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    selected = []

    for sentence in sentences:
        candidate = " ".join(selected + [sentence]).strip()
        if len(candidate) <= max_chars:
            selected.append(sentence)
        else:
            break

    compressed = " ".join(selected).strip()

    if not compressed:
        compressed = clean[:max_chars].rsplit(" ", 1)[0].strip()

    continuity = (
        " Maintain consistent subjects, hands, props, screens, reflections, lighting, "
        "camera motion, and scene physics. Avoid disappearing objects, warped hands, "
        "mismatched movement, impossible reflections, and sudden scene changes."
    )

    room = max_chars - len(compressed)
    if room > 80 and "Avoid disappearing objects" not in compressed:
        compressed = (compressed + continuity[:room]).strip()

    return compressed[:max_chars].strip()

'''
    text = text.replace(helper_marker, helper + helper_marker, 1)

old_call = '''            video_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["video_provider"],
                "media_type": "video",
                "prompt": plan["visual_prompt"],
                "owner_approved": True,
                "owner_approval_granted": True,
            })'''

new_call = '''            provider_visual_prompt = _ucm_provider_safe_visual_prompt(plan["visual_prompt"], 950)

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_visual_generation",
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "visual_prompt_character_count": len(plan.get("visual_prompt") or ""),
                "provider_visual_prompt_character_count": len(provider_visual_prompt),
                "provider_visual_prompt_limit": 1000,
                "provider_visual_prompt_truncated": len(plan.get("visual_prompt") or "") > len(provider_visual_prompt),
                "started_at": _now(),
            })

            video_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["video_provider"],
                "media_type": "video",
                "prompt": provider_visual_prompt,
                "owner_approved": True,
                "owner_approval_granted": True,
            })'''

if old_call not in text:
    raise SystemExit("VIDEO_RESULT_CALL_BLOCK_NOT_FOUND")

text = text.replace(old_call, new_call, 1)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "def _ucm_provider_safe_visual_prompt",
    "provider_visual_prompt = _ucm_provider_safe_visual_prompt",
    "provider_visual_prompt_character_count",
    "provider_visual_prompt_limit",
    '"prompt": provider_visual_prompt',
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("UNIVERSAL_RUNWAY_PROMPT_LIMIT_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")