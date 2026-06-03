from datetime import datetime, timezone
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
