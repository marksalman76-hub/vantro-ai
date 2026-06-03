from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"elevenlabs_live_tts_quality_adapter_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "elevenlabs_live_tts_quality_adapter.py"
DOC_FILE = ROOT / "docs" / "elevenlabs-live-tts-quality-adapter.md"
TEST_FILE = ROOT / "test_elevenlabs_live_tts_quality_adapter.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import os
import urllib.request
import urllib.error


def _load_env_local() -> None:
    root = Path(__file__).resolve().parents[3]
    env_file = root / ".env.local"

    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and value and key not in os.environ:
            os.environ[key] = value


_load_env_local()


ROOT = Path(__file__).resolve().parents[3]
AUDIO_OUTPUT_DIR = ROOT / "runtime_outputs" / "elevenlabs_quality_tests"

DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
DEFAULT_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip().lower())
    return safe[:80] or "elevenlabs_quality_test"


def get_elevenlabs_live_tts_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(os.getenv("ELEVENLABS_API_KEY", "").strip())

    return {
        "success": True,
        "provider": "elevenlabs",
        "layer": "live_tts_quality_adapter",
        "status": "ready",
        "api_key_configured": api_key_present,
        "credential_values_exposed": False,
        "live_execution_requires_explicit_allow": True,
        "default_voice_id_configured": bool(DEFAULT_VOICE_ID),
        "default_model_id": DEFAULT_MODEL_ID,
        "audio_output_dir": str(AUDIO_OUTPUT_DIR),
        "external_action_performed": False,
        "live_provider_call_triggered": False,
        "owner_controlled_quality_test": True,
        "verified_at": _now(),
    }


def run_elevenlabs_tts_quality_test(
    text: str,
    voice_id: Optional[str] = None,
    model_id: Optional[str] = None,
    test_label: str = "creative_agent_quality_test",
    allow_live_execution: bool = False,
) -> Dict[str, Any]:
    if not allow_live_execution:
        return {
            "success": False,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "blocked_owner_approval_required",
            "reason": "Live ElevenLabs execution requires allow_live_execution=True.",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "audio_saved": False,
            "verified_at": _now(),
        }

    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        return {
            "success": False,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "missing_api_key",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "audio_saved": False,
            "verified_at": _now(),
        }

    if not text or not text.strip():
        return {
            "success": False,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "missing_text",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "audio_saved": False,
            "verified_at": _now(),
        }

    selected_voice_id = voice_id or DEFAULT_VOICE_ID
    selected_model_id = model_id or DEFAULT_MODEL_ID

    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"{stamp}_{_safe_filename(test_label)}"
    audio_path = AUDIO_OUTPUT_DIR / f"{base_name}.mp3"
    metadata_path = AUDIO_OUTPUT_DIR / f"{base_name}.json"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice_id}?output_format=mp3_44100_128"

    payload = {
        "text": text.strip(),
        "model_id": selected_model_id,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            audio_bytes = response.read()

        audio_path.write_bytes(audio_bytes)

        metadata = {
            "success": True,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "audio_generated",
            "test_label": test_label,
            "voice_id": selected_voice_id,
            "model_id": selected_model_id,
            "text_character_count": len(text.strip()),
            "audio_path": str(audio_path),
            "metadata_path": str(metadata_path),
            "audio_size_bytes": len(audio_bytes),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "audio_saved": True,
            "generated_at": _now(),
        }

        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return metadata

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "provider_http_error",
            "http_status": error.code,
            "provider_error_preview": error_body[:500],
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "audio_saved": False,
            "verified_at": _now(),
        }

    except Exception as error:
        return {
            "success": False,
            "provider": "elevenlabs",
            "layer": "live_tts_quality_adapter",
            "status": "provider_execution_error",
            "error": str(error),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "audio_saved": False,
            "verified_at": _now(),
        }
'''

DOC_CONTENT = r'''# ElevenLabs Live TTS Quality Adapter

## Purpose

This adapter enables controlled live ElevenLabs text-to-speech quality tests.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Generated audio is saved locally under `runtime_outputs/elevenlabs_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Default Provider Settings

- Default voice ID can be overridden with `ELEVENLABS_DEFAULT_VOICE_ID`.
- Default model ID can be overridden with `ELEVENLABS_MODEL_ID`.
- Default model fallback: `eleven_multilingual_v2`.

## Status

ELEVENLABS_LIVE_TTS_QUALITY_ADAPTER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "elevenlabs_live_tts_quality_adapter.py"
doc_file = ROOT / "docs" / "elevenlabs-live-tts-quality-adapter.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("elevenlabs_live_tts_quality_adapter", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_elevenlabs_live_tts_adapter_status()

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential values must not be exposed")

if status.get("live_execution_requires_explicit_allow") is not True:
    raise AssertionError("Live execution must require explicit allow flag")

blocked = module.run_elevenlabs_tts_quality_test(
    text="This blocked test should not call ElevenLabs.",
    allow_live_execution=False,
)

if blocked.get("status") != "blocked_owner_approval_required":
    raise AssertionError("Adapter must block live execution unless explicitly allowed")

if blocked.get("live_provider_call_triggered") is not False:
    raise AssertionError("Blocked test must not trigger provider calls")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "ELEVENLABS_LIVE_TTS_QUALITY_ADAPTER_READY",
    "run_elevenlabs_tts_quality_test",
    "allow_live_execution",
    "xi-api-key",
    "credential_values_exposed",
    "runtime_outputs",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("ELEVENLABS_LIVE_TTS_QUALITY_ADAPTER_PASSED")
'''
def backup_path(path: Path) -> None:
    if path.exists():
        destination = BACKUP / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)

def write_file(path: Path, content: str) -> None:
    backup_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)

    print("ELEVENLABS_LIVE_TTS_QUALITY_ADAPTER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()