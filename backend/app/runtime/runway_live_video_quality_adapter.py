from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import os
import re
import subprocess
import sys
import urllib.request


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


def _extract_output_urls(output: Any) -> List[str]:
    urls: List[str] = []

    if isinstance(output, dict):
        for key in ("output", "outputs", "video", "videos", "url", "urls"):
            value = output.get(key)
            urls.extend(_extract_output_urls(value))

    elif isinstance(output, (list, tuple)):
        for item in output:
            urls.extend(_extract_output_urls(item))

    elif isinstance(output, str):
        urls.extend(re.findall(r"https://[^\s'\"\]]+", output))

    else:
        urls.extend(re.findall(r"https://[^\s'\"\]]+", str(output)))

    cleaned: List[str] = []
    for url in urls:
        cleaned_url = url.rstrip("',)]}")
        if cleaned_url not in cleaned:
            cleaned.append(cleaned_url)

    return cleaned


def _download_first_video_url(output: Any, video_path: Path) -> Dict[str, Any]:
    urls = _extract_output_urls(output)
    mp4_urls = [url for url in urls if ".mp4" in url.lower()]

    if not mp4_urls:
        return {
            "download_attempted": False,
            "video_saved": False,
            "video_url_found": False,
            "video_url_preview": None,
            "video_path": None,
            "video_size_bytes": 0,
            "download_error": None,
        }

    selected_url = mp4_urls[0]

    try:
        request = urllib.request.Request(
            selected_url,
            headers={
                "User-Agent": "Mozilla/5.0 governed-runway-quality-adapter",
            },
        )
        with urllib.request.urlopen(request, timeout=120) as response:
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


def get_runway_live_video_adapter_status() -> Dict[str, Any]:
    api_key_present = bool(
        os.getenv("RUNWAYML_API_SECRET", "").strip()
        or os.getenv("RUNWAY_API_KEY", "").strip()
        or os.getenv("RUNWAYML_API_KEY", "").strip()
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
        "local_mp4_download_enabled": True,
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

    runway_secret = (
        os.getenv("RUNWAYML_API_SECRET", "").strip()
        or os.getenv("RUNWAY_API_KEY", "").strip()
        or os.getenv("RUNWAYML_API_KEY", "").strip()
    )
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
        video_path = RUNWAY_OUTPUT_DIR / f"{base_name}.mp4"

        client = RunwayML()

        task = client.text_to_video.create(
            model=selected_model,
            prompt_text=prompt_text.strip(),
            ratio=selected_ratio,
            duration=selected_duration,
        )

        output = task.wait_for_task_output()

        download_result = _download_first_video_url(output, video_path)

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
            "output": str(output),
            "metadata_path": str(metadata_path),
            "credential_values_exposed": False,
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "sdk_installed_now": sdk_status["installed_now"],
            "generated_at": _now(),
            **download_result,
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
