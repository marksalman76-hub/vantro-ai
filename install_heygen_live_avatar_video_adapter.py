from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"heygen_live_avatar_video_adapter_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "heygen_live_avatar_video_adapter.py"
DOC_FILE = ROOT / "docs" / "heygen-live-avatar-video-adapter.md"
TEST_FILE = ROOT / "test_heygen_live_avatar_video_adapter.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import os
import time
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
HEYGEN_OUTPUT_DIR = ROOT / "runtime_outputs" / "heygen_quality_tests"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip().lower())
    return safe[:80] or "heygen_quality_test"


def get_heygen_live_avatar_video_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(os.getenv("HEYGEN_API_KEY", "").strip())

    return {
        "success": True,
        "provider": "heygen",
        "layer": "live_avatar_video_quality_adapter",
        "status": "ready",
        "api_key_configured": api_key_present,
        "credential_values_exposed": False,
        "live_execution_requires_explicit_allow": True,
        "video_output_dir": str(HEYGEN_OUTPUT_DIR),
        "external_action_performed": False,
        "live_provider_call_triggered": False,
        "owner_controlled_quality_test": True,
        "verified_at": _now(),
    }


def _post_video_agent(api_key: str, prompt: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url="https://api.heygen.com/v3/video-agents",
        data=json.dumps({"prompt": prompt}).encode("utf-8"),
        headers={
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_video(api_key: str, video_id: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers={
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        },
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def run_heygen_avatar_video_quality_test(
    prompt_text: str,
    test_label: str = "heygen_avatar_video_quality_test",
    allow_live_execution: bool = False,
    poll_for_completion: bool = False,
    poll_attempts: int = 12,
    poll_seconds: int = 10,
) -> Dict[str, Any]:
    if not allow_live_execution:
        return {
            "success": False,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "blocked_owner_approval_required",
            "reason": "Live HeyGen execution requires allow_live_execution=True.",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    api_key = os.getenv("HEYGEN_API_KEY", "").strip()
    if not api_key:
        return {
            "success": False,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "missing_api_key",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    if not prompt_text or not prompt_text.strip():
        return {
            "success": False,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "missing_prompt_text",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    HEYGEN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"{stamp}_{_safe_filename(test_label)}"
    metadata_path = HEYGEN_OUTPUT_DIR / f"{base_name}.json"

    try:
        create_result = _post_video_agent(api_key=api_key, prompt=prompt_text.strip())

        data = create_result.get("data") or {}
        video_id = data.get("video_id") or data.get("id") or create_result.get("video_id") or create_result.get("id")

        poll_results = []
        final_video_status = None

        if poll_for_completion and video_id:
            for _ in range(max(1, poll_attempts)):
                time.sleep(max(1, poll_seconds))
                status_result = _get_video(api_key=api_key, video_id=video_id)
                poll_results.append(status_result)
                status_data = status_result.get("data") or {}
                final_video_status = status_data.get("status") or status_result.get("status")
                if str(final_video_status).lower() in {"completed", "complete", "done", "success", "succeeded", "failed"}:
                    break

        metadata = {
            "success": True,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "video_agent_task_created",
            "test_label": test_label,
            "video_id": video_id,
            "prompt_character_count": len(prompt_text.strip()),
            "create_result": create_result,
            "poll_for_completion": poll_for_completion,
            "final_video_status": final_video_status,
            "poll_results": poll_results,
            "metadata_path": str(metadata_path),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "generated_at": _now(),
        }

        metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")

        return metadata

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "provider_http_error",
            "http_status": error.code,
            "provider_error_preview": error_body[:700],
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "verified_at": _now(),
        }

    except Exception as error:
        return {
            "success": False,
            "provider": "heygen",
            "layer": "live_avatar_video_quality_adapter",
            "status": "provider_execution_error",
            "error": str(error),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "verified_at": _now(),
        }
'''

DOC_CONTENT = r'''# HeyGen Live Avatar Video Quality Adapter

## Purpose

This adapter enables controlled live HeyGen Video Agent / avatar-video quality tests.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Metadata is saved locally under `runtime_outputs/heygen_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Default API Path

- Create Video Agent task: `POST https://api.heygen.com/v3/video-agents`
- Authentication header: `X-Api-Key`

## Status

HEYGEN_LIVE_AVATAR_VIDEO_ADAPTER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "heygen_live_avatar_video_adapter.py"
doc_file = ROOT / "docs" / "heygen-live-avatar-video-adapter.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("heygen_live_avatar_video_adapter", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_heygen_live_avatar_video_adapter_status()

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential values must not be exposed")

if status.get("live_execution_requires_explicit_allow") is not True:
    raise AssertionError("Live execution must require explicit allow flag")

blocked = module.run_heygen_avatar_video_quality_test(
    prompt_text="This blocked test should not call HeyGen.",
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
    "HEYGEN_LIVE_AVATAR_VIDEO_ADAPTER_READY",
    "run_heygen_avatar_video_quality_test",
    "allow_live_execution",
    "X-Api-Key",
    "credential_values_exposed",
    "runtime_outputs",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("HEYGEN_LIVE_AVATAR_VIDEO_ADAPTER_PASSED")
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

    print("HEYGEN_LIVE_AVATAR_VIDEO_ADAPTER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()