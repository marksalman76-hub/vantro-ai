from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import os
import re
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
SYNC_OUTPUT_DIR = ROOT / "runtime_outputs" / "sync_lipsync_quality_tests"

SYNC_API_BASE = os.getenv("SYNC_API_BASE", "https://api.sync.so")
SYNC_MODEL = os.getenv("SYNC_MODEL", "sync-3")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip().lower())
    return safe[:80] or "sync_lipsync_quality_test"


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

    cleaned = []
    for url in urls:
        clean = url.rstrip("',)]}")
        if clean not in cleaned:
            cleaned.append(clean)
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
        request = urllib.request.Request(
            selected_url,
            headers={"User-Agent": "Mozilla/5.0 governed-sync-lipsync-adapter"},
        )
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


def get_sync_live_lipsync_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(os.getenv("SYNC_API_KEY", "").strip() or os.getenv("LIPSYNC_API_KEY", "").strip())

    return {
        "success": True,
        "provider": "sync",
        "layer": "live_lipsync_dubbing_quality_adapter",
        "status": "ready",
        "api_key_configured": api_key_present,
        "credential_values_exposed": False,
        "live_execution_requires_explicit_allow": True,
        "default_model": SYNC_MODEL,
        "video_output_dir": str(SYNC_OUTPUT_DIR),
        "local_video_download_enabled": True,
        "external_action_performed": False,
        "live_provider_call_triggered": False,
        "owner_controlled_quality_test": True,
        "verified_at": _now(),
    }


def _post_json(url: str, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str, api_key: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _find_generation_id(result: Dict[str, Any]) -> Optional[str]:
    candidates = [
        result.get("id"),
        result.get("generation_id"),
        (result.get("data") or {}).get("id") if isinstance(result.get("data"), dict) else None,
        (result.get("data") or {}).get("generation_id") if isinstance(result.get("data"), dict) else None,
    ]
    return next((str(value) for value in candidates if value), None)


def run_sync_lipsync_quality_test(
    video_url: str,
    audio_url: str,
    test_label: str = "sync_lipsync_quality_test",
    model: Optional[str] = None,
    allow_live_execution: bool = False,
    poll_for_completion: bool = True,
    poll_attempts: int = 30,
    poll_seconds: int = 10,
) -> Dict[str, Any]:
    if not allow_live_execution:
        return {
            "success": False,
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
            "status": "blocked_owner_approval_required",
            "reason": "Live Sync execution requires allow_live_execution=True.",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    api_key = os.getenv("SYNC_API_KEY", "").strip() or os.getenv("LIPSYNC_API_KEY", "").strip()
    if not api_key:
        return {
            "success": False,
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
            "status": "missing_api_key",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    if not video_url or not audio_url:
        return {
            "success": False,
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
            "status": "missing_video_or_audio_url",
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "video_saved": False,
            "verified_at": _now(),
        }

    SYNC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"{stamp}_{_safe_filename(test_label)}"
    metadata_path = SYNC_OUTPUT_DIR / f"{base_name}.json"
    video_path = SYNC_OUTPUT_DIR / f"{base_name}.mp4"

    selected_model = model or SYNC_MODEL

    payload = {
        "model": selected_model,
        "input": [
            {"type": "video", "url": video_url},
            {"type": "audio", "url": audio_url},
        ],
    }

    try:
        create_url = f"{SYNC_API_BASE.rstrip('/')}/v2/generate"
        create_result = _post_json(create_url, api_key, payload)
        generation_id = _find_generation_id(create_result)

        poll_results = []
        final_result = create_result
        final_status = create_result.get("status")

        if poll_for_completion and generation_id:
            query_url = f"{SYNC_API_BASE.rstrip('/')}/v2/generate/{generation_id}"
            for _ in range(max(1, poll_attempts)):
                time.sleep(max(1, poll_seconds))
                poll_result = _get_json(query_url, api_key)
                poll_results.append(poll_result)
                final_result = poll_result
                final_status = poll_result.get("status") or (poll_result.get("data") or {}).get("status")

                if str(final_status).upper() in {"COMPLETED", "SUCCEEDED", "SUCCESS", "FAILED", "ERROR"}:
                    break

        download_result = _download_first_video(final_result, video_path)

        metadata = {
            "success": True,
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
            "status": "lipsync_task_created_or_completed",
            "test_label": test_label,
            "model": selected_model,
            "generation_id": generation_id,
            "final_status": final_status,
            "create_result": create_result,
            "poll_for_completion": poll_for_completion,
            "poll_results": poll_results,
            "metadata_path": str(metadata_path),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "generated_at": _now(),
            **download_result,
        }

        metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
        return metadata

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
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
            "provider": "sync",
            "layer": "live_lipsync_dubbing_quality_adapter",
            "status": "provider_execution_error",
            "error": str(error),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "video_saved": False,
            "verified_at": _now(),
        }
