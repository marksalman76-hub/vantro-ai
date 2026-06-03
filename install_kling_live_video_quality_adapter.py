from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"kling_live_video_quality_adapter_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "kling_live_video_quality_adapter.py"
DOC_FILE = ROOT / "docs" / "kling-live-video-quality-adapter.md"
TEST_FILE = ROOT / "test_kling_live_video_quality_adapter.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import os
import re
import subprocess
import sys
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
KLING_OUTPUT_DIR = ROOT / "runtime_outputs" / "kling_quality_tests"

KLING_API_BASE = os.getenv("KLING_API_BASE", "https://api.klingai.com")
KLING_MODEL = os.getenv("KLING_MODEL", "kling-v1")
KLING_MODE = os.getenv("KLING_MODE", "std")
KLING_ASPECT_RATIO = os.getenv("KLING_ASPECT_RATIO", "16:9")
KLING_DURATION = os.getenv("KLING_DURATION", "5")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip().lower())
    return safe[:80] or "kling_quality_test"


def _ensure_pyjwt_available() -> Dict[str, Any]:
    try:
        import jwt  # noqa: F401
        return {"available": True, "installed_now": False, "error": None}
    except Exception:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "PyJWT"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            return {"available": False, "installed_now": False, "error": (result.stderr or result.stdout)[-1000:]}

        try:
            import jwt  # noqa: F401
            return {"available": True, "installed_now": True, "error": None}
        except Exception as error:
            return {"available": False, "installed_now": True, "error": str(error)}


def _create_kling_jwt(access_key: str, secret_key: str) -> str:
    import jwt
    now = int(time.time())
    payload = {
        "iss": access_key,
        "exp": now + 1800,
        "nbf": now - 5,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def _extract_urls(value: Any) -> List[str]:
    urls: List[str] = []

    if isinstance(value, dict):
        for item in value.values():
            urls.extend(_extract_urls(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            urls.extend(_extract_urls(item))
    elif isinstance(value, str):
        urls.extend(re.findall(r"https://[^\s'\"\]]+", value))
    else:
        urls.extend(re.findall(r"https://[^\s'\"\]]+", str(value)))

    cleaned: List[str] = []
    for url in urls:
        cleaned_url = url.rstrip("',)]}")
        if cleaned_url not in cleaned:
            cleaned.append(cleaned_url)
    return cleaned


def _download_first_video(result: Any, video_path: Path) -> Dict[str, Any]:
    urls = _extract_urls(result)
    video_urls = [url for url in urls if ".mp4" in url.lower() or "video" in url.lower()]

    if not video_urls:
        return {
            "download_attempted": False,
            "video_saved": False,
            "video_url_found": False,
            "video_url_preview": None,
            "video_path": None,
            "video_size_bytes": 0,
            "download_error": None,
        }

    selected_url = video_urls[0]

    try:
        request = urllib.request.Request(selected_url, headers={"User-Agent": "Mozilla/5.0 governed-kling-quality-adapter"})
        with urllib.request.urlopen(request, timeout=180) as response:
            video_bytes = response.read()

        video_path.write_bytes(video_bytes)

        return {
            "download_attempted": True,
            "video_saved": True,
            "video_url_found": True,
            "video_url_preview": selected_url.split("?")[0],
            "video_path": str(video_path),
            "video_size_bytes": len(video_bytes),
            "download_error": None,
        }

    except Exception as error:
        return {
            "download_attempted": True,
            "video_saved": False,
            "video_url_found": True,
            "video_url_preview": selected_url.split("?")[0],
            "video_path": str(video_path),
            "video_size_bytes": 0,
            "download_error": str(error),
        }


def get_kling_live_video_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(os.getenv("KLING_API_KEY", "").strip())
    secret_key_present = bool(os.getenv("KLING_SECRET_KEY", "").strip())

    return {
        "success": True,
        "provider": "kling",
        "layer": "live_video_quality_adapter",
        "status": "ready",
        "api_key_configured": api_key_present,
        "secret_key_configured": secret_key_present,
        "credential_values_exposed": False,
        "live_execution_requires_explicit_allow": True,
        "default_model": KLING_MODEL,
        "default_mode": KLING_MODE,
        "default_aspect_ratio": KLING_ASPECT_RATIO,
        "default_duration": KLING_DURATION,
        "video_output_dir": str(KLING_OUTPUT_DIR),
        "local_video_download_enabled": True,
        "external_action_performed": False,
        "live_provider_call_triggered": False,
        "owner_controlled_quality_test": True,
        "verified_at": _now(),
    }


def _post_json(url: str, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str, token: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _find_task_id(result: Dict[str, Any]) -> Optional[str]:
    candidates = [
        result.get("task_id"),
        result.get("id"),
        (result.get("data") or {}).get("task_id") if isinstance(result.get("data"), dict) else None,
        (result.get("data") or {}).get("id") if isinstance(result.get("data"), dict) else None,
    ]
    return next((str(value) for value in candidates if value), None)


def run_kling_text_to_video_quality_test(
    prompt_text: str,
    test_label: str = "kling_video_quality_test",
    model_name: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    duration: Optional[str] = None,
    mode: Optional[str] = None,
    allow_live_execution: bool = False,
    poll_for_completion: bool = True,
    poll_attempts: int = 30,
    poll_seconds: int = 10,
) -> Dict[str, Any]:
    if not allow_live_execution:
        return {
            "success": False,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "blocked_owner_approval_required",
            "reason": "Live Kling execution requires allow_live_execution=True.",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    access_key = os.getenv("KLING_API_KEY", "").strip()
    secret_key = os.getenv("KLING_SECRET_KEY", "").strip()

    if not access_key or not secret_key:
        return {
            "success": False,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "missing_api_credentials",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    if not prompt_text or not prompt_text.strip():
        return {
            "success": False,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "missing_prompt_text",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    jwt_status = _ensure_pyjwt_available()
    if not jwt_status["available"]:
        return {
            "success": False,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "jwt_dependency_unavailable",
            "dependency_error": jwt_status["error"],
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    KLING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"{stamp}_{_safe_filename(test_label)}"
    metadata_path = KLING_OUTPUT_DIR / f"{base_name}.json"
    video_path = KLING_OUTPUT_DIR / f"{base_name}.mp4"

    selected_model = model_name or KLING_MODEL
    selected_aspect_ratio = aspect_ratio or KLING_ASPECT_RATIO
    selected_duration = str(duration or KLING_DURATION)
    selected_mode = mode or KLING_MODE

    token = _create_kling_jwt(access_key=access_key, secret_key=secret_key)

    create_payload = {
        "model_name": selected_model,
        "prompt": prompt_text.strip(),
        "mode": selected_mode,
        "aspect_ratio": selected_aspect_ratio,
        "duration": selected_duration,
    }

    try:
        create_url = f"{KLING_API_BASE.rstrip('/')}/v1/videos/text2video"
        create_result = _post_json(create_url, token, create_payload)
        task_id = _find_task_id(create_result)

        poll_results: List[Dict[str, Any]] = []
        final_result: Any = create_result
        final_status = None

        if poll_for_completion and task_id:
            query_url = f"{KLING_API_BASE.rstrip('/')}/v1/videos/text2video/{task_id}"
            for _ in range(max(1, poll_attempts)):
                time.sleep(max(1, poll_seconds))
                poll_result = _get_json(query_url, token)
                poll_results.append(poll_result)
                final_result = poll_result

                data = poll_result.get("data") if isinstance(poll_result, dict) else {}
                if isinstance(data, dict):
                    final_status = data.get("task_status") or data.get("status")
                final_status = final_status or poll_result.get("task_status") or poll_result.get("status")

                if str(final_status).lower() in {"succeed", "succeeded", "success", "complete", "completed", "done", "failed", "fail"}:
                    break

        download_result = _download_first_video(final_result, video_path)

        metadata = {
            "success": True,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "video_task_created_or_completed",
            "test_label": test_label,
            "model_name": selected_model,
            "mode": selected_mode,
            "aspect_ratio": selected_aspect_ratio,
            "duration": selected_duration,
            "prompt_character_count": len(prompt_text.strip()),
            "task_id": task_id,
            "create_result": create_result,
            "poll_for_completion": poll_for_completion,
            "final_status": final_status,
            "poll_results": poll_results,
            "metadata_path": str(metadata_path),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "jwt_dependency_installed_now": jwt_status["installed_now"],
            "generated_at": _now(),
            **download_result,
        }

        metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
        return metadata

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "provider": "kling",
            "layer": "live_video_quality_adapter",
            "status": "provider_http_error",
            "http_status": error.code,
            "provider_error_preview": error_body[:1000],
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "verified_at": _now(),
        }

    except Exception as error:
        return {
            "success": False,
            "provider": "kling",
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

DOC_CONTENT = r'''# Kling Live Video Quality Adapter

## Purpose

This adapter enables controlled live Kling text-to-video quality tests for creative agents.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Access Key and Secret Key values are never returned.
- Metadata is saved locally under `runtime_outputs/kling_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Defaults

- `KLING_API_BASE=https://api.klingai.com`
- `KLING_MODEL=kling-v1`
- `KLING_MODE=std`
- `KLING_ASPECT_RATIO=16:9`
- `KLING_DURATION=5`

## Status

KLING_LIVE_VIDEO_QUALITY_ADAPTER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "kling_live_video_quality_adapter.py"
doc_file = ROOT / "docs" / "kling-live-video-quality-adapter.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("kling_live_video_quality_adapter", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_kling_live_video_adapter_status()

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential values must not be exposed")

if status.get("live_execution_requires_explicit_allow") is not True:
    raise AssertionError("Live execution must require explicit allow flag")

blocked = module.run_kling_text_to_video_quality_test(
    prompt_text="This blocked test should not call Kling.",
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
    "KLING_LIVE_VIDEO_QUALITY_ADAPTER_READY",
    "run_kling_text_to_video_quality_test",
    "allow_live_execution",
    "KLING_SECRET_KEY",
    "credential_values_exposed",
    "runtime_outputs",
    "/v1/videos/text2video",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("KLING_LIVE_VIDEO_QUALITY_ADAPTER_PASSED")
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

    print("KLING_LIVE_VIDEO_QUALITY_ADAPTER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()