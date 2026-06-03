from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"runway_live_video_quality_adapter_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "runway_live_video_quality_adapter.py"
DOC_FILE = ROOT / "docs" / "runway-live-video-quality-adapter.md"
TEST_FILE = ROOT / "test_runway_live_video_quality_adapter.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import os
import subprocess
import sys


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
RUNWAY_OUTPUT_DIR = ROOT / "runtime_outputs" / "runway_quality_tests"

DEFAULT_MODEL = os.getenv("RUNWAY_MODEL", "gen4.5")
DEFAULT_RATIO = os.getenv("RUNWAY_RATIO", "1280:720")
DEFAULT_DURATION = int(os.getenv("RUNWAY_DURATION", "5"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip().lower())
    return safe[:80] or "runway_quality_test"


def get_runway_live_video_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(
        os.getenv("RUNWAYML_API_SECRET", "").strip()
        or os.getenv("RUNWAY_API_KEY", "").strip()
    )

    return {
        "success": True,
        "provider": "runway",
        "layer": "live_video_quality_adapter",
        "status": "ready",
        "api_key_configured": api_key_present,
        "credential_values_exposed": False,
        "live_execution_requires_explicit_allow": True,
        "default_model": DEFAULT_MODEL,
        "default_ratio": DEFAULT_RATIO,
        "default_duration": DEFAULT_DURATION,
        "video_output_dir": str(RUNWAY_OUTPUT_DIR),
        "external_action_performed": False,
        "live_provider_call_triggered": False,
        "owner_controlled_quality_test": True,
        "verified_at": _now(),
    }


def _ensure_sdk_available() -> Dict[str, Any]:
    try:
        import runwayml  # noqa: F401
        return {
            "available": True,
            "installed_now": False,
            "error": None,
        }
    except Exception:
        install_result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "runwayml"],
            text=True,
            capture_output=True,
        )

        if install_result.returncode != 0:
            return {
                "available": False,
                "installed_now": False,
                "error": (install_result.stderr or install_result.stdout)[-1000:],
            }

        try:
            import runwayml  # noqa: F401
            return {
                "available": True,
                "installed_now": True,
                "error": None,
            }
        except Exception as error:
            return {
                "available": False,
                "installed_now": True,
                "error": str(error),
            }


def run_runway_text_to_video_quality_test(
    prompt_text: str,
    test_label: str = "runway_creative_video_quality_test",
    model: Optional[str] = None,
    ratio: Optional[str] = None,
    duration: Optional[int] = None,
    allow_live_execution: bool = False,
) -> Dict[str, Any]:
    if not allow_live_execution:
        return {
            "success": False,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "blocked_owner_approval_required",
            "reason": "Live Runway execution requires allow_live_execution=True.",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    runway_secret = os.getenv("RUNWAYML_API_SECRET", "").strip() or os.getenv("RUNWAY_API_KEY", "").strip()
    if not runway_secret:
        return {
            "success": False,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "missing_api_key",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    os.environ["RUNWAYML_API_SECRET"] = runway_secret

    if not prompt_text or not prompt_text.strip():
        return {
            "success": False,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "missing_prompt_text",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    sdk_status = _ensure_sdk_available()
    if not sdk_status["available"]:
        return {
            "success": False,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "sdk_unavailable",
            "sdk_error": sdk_status["error"],
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    try:
        from runwayml import RunwayML

        selected_model = model or DEFAULT_MODEL
        selected_ratio = ratio or DEFAULT_RATIO
        selected_duration = duration or DEFAULT_DURATION

        RUNWAY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = f"{stamp}_{_safe_filename(test_label)}"
        metadata_path = RUNWAY_OUTPUT_DIR / f"{base_name}.json"

        client = RunwayML()

        task = client.text_to_video.create(
            model=selected_model,
            prompt_text=prompt_text.strip(),
            ratio=selected_ratio,
            duration=selected_duration,
        )

        output = task.wait_for_task_output()

        metadata = {
            "success": True,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "video_task_completed",
            "test_label": test_label,
            "model": selected_model,
            "ratio": selected_ratio,
            "duration": selected_duration,
            "prompt_character_count": len(prompt_text.strip()),
            "task_id": getattr(task, "id", None),
            "output": output,
            "metadata_path": str(metadata_path),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "sdk_installed_now": sdk_status["installed_now"],
            "generated_at": _now(),
        }

        metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")

        return metadata

    except Exception as error:
        return {
            "success": False,
            "provider": "runway",
            "layer": "live_video_quality_adapter",
            "status": "provider_execution_error",
            "error": str(error),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "verified_at": _now(),
        }
'''

DOC_CONTENT = r'''# Runway Live Video Quality Adapter

## Purpose

This adapter enables controlled live Runway video quality tests for creative agents.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Metadata is saved locally under `runtime_outputs/runway_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.
- The Runway API key must remain server-side only.

## Defaults

- `RUNWAY_MODEL=gen4.5`
- `RUNWAY_RATIO=1280:720`
- `RUNWAY_DURATION=5`

## Status

RUNWAY_LIVE_VIDEO_QUALITY_ADAPTER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "runway_live_video_quality_adapter.py"
doc_file = ROOT / "docs" / "runway-live-video-quality-adapter.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("runway_live_video_quality_adapter", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_runway_live_video_adapter_status()

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential values must not be exposed")

if status.get("live_execution_requires_explicit_allow") is not True:
    raise AssertionError("Live execution must require explicit allow flag")

blocked = module.run_runway_text_to_video_quality_test(
    prompt_text="This blocked test should not call Runway.",
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
    "RUNWAY_LIVE_VIDEO_QUALITY_ADAPTER_READY",
    "run_runway_text_to_video_quality_test",
    "allow_live_execution",
    "RUNWAYML_API_SECRET",
    "credential_values_exposed",
    "runtime_outputs",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("RUNWAY_LIVE_VIDEO_QUALITY_ADAPTER_PASSED")
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

    print("RUNWAY_LIVE_VIDEO_QUALITY_ADAPTER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()