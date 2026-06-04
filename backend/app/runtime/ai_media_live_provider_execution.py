from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


AI_MEDIA_PROVIDER_ENV_MAP = {
    "openai_image": {
        "env_keys": ["OPENAI_API_KEY"],
        "category": "image",
        "capabilities": ["image_generation", "image_variation", "product_visual"],
        "live_execution_supported": True,
    },
    "runway": {
        "env_keys": ["RUNWAYML_API_SECRET"],
        "category": "video",
        "capabilities": ["video_generation", "cinematic_generation", "image_to_video"],
        "live_execution_supported": True,
    },
    "kling": {
        "env_keys": ["KLING_ACCESS_KEY", "KLING_SECRET_KEY"],
        "category": "video",
        "capabilities": ["video_generation", "character_motion", "cinematic_video"],
        "live_execution_supported": True,
    },
    "heygen": {
        "env_keys": ["HEYGEN_API_KEY"],
        "category": "avatar_video",
        "capabilities": ["avatar_video", "presenter_video", "lipsync_video"],
        "live_execution_supported": True,
    },
    "elevenlabs": {
        "env_keys": ["ELEVENLABS_API_KEY"],
        "category": "audio",
        "capabilities": ["voice_generation", "dubbing", "multilingual_audio"],
        "live_execution_supported": True,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _env_enabled(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in TRUE_VALUES


def _env_present(keys: List[str], *, require_all: bool = False) -> bool:
    checks = [bool(os.getenv(key, "").strip()) for key in keys]
    return all(checks) if require_all else any(checks)


def _live_dispatch_enabled() -> bool:
    return all(
        [
            _env_enabled("LIVE_EXTERNAL_CALLS_ENABLED"),
            _env_enabled("OWNER_APPROVED_LIVE_ACTIVATION"),
            _env_enabled("REAL_PROVIDER_HTTP_DISPATCH_ENABLED"),
        ]
    )


def _credential_configured(provider_id: str) -> bool:
    config = AI_MEDIA_PROVIDER_ENV_MAP.get(provider_id, {})
    keys = list(config.get("env_keys") or [])
    if provider_id == "kling":
        return _env_present(keys, require_all=True)
    return _env_present(keys)


def _request_json(
    *,
    url: str,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers or {},
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read()
            response_text = response_body.decode("utf-8", errors="replace")
            try:
                parsed = json.loads(response_text)
            except Exception:
                parsed = {"raw_response": response_text[:5000]}

            return {
                "success": 200 <= int(response.status) < 300,
                "status_code": int(response.status),
                "response": parsed,
                "credential_values_exposed": False,
                "customer_safe": True,
            }

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        return {
            "success": False,
            "status_code": int(error.code),
            "response": {"error_body": error_body[:5000]},
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    except Exception as exc:
        return {
            "success": False,
            "status_code": 0,
            "response": {"error": str(exc)[:1500]},
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def _extract_first_url(value: Any) -> str:
    if isinstance(value, str):
        clean = value.strip()
        if clean.startswith(("http://", "https://", "data:")):
            return clean
        return ""

    if isinstance(value, list):
        for item in value:
            found = _extract_first_url(item)
            if found:
                return found

    if isinstance(value, dict):
        for key in [
            "url",
            "asset_url",
            "media_url",
            "video_url",
            "audio_url",
            "image_url",
            "download_url",
            "preview_url",
            "output_url",
        ]:
            found = _extract_first_url(value.get(key))
            if found:
                return found

        for nested in value.values():
            found = _extract_first_url(nested)
            if found:
                return found

    return ""


def _provider_parameters(packet: Dict[str, Any]) -> Dict[str, Any]:
    params = packet.get("provider_parameters")
    if isinstance(params, dict):
        return params
    return {}


def _packet_prompt(packet: Dict[str, Any]) -> str:
    params = _provider_parameters(packet)
    return (
        _safe_text(params.get("prompt"))
        or _safe_text(params.get("script"))
        or _safe_text(packet.get("prompt"))
        or _safe_text(packet.get("task"))
        or "Create a premium, customer-safe creative media asset."
    )


def _packet_script(packet: Dict[str, Any]) -> str:
    params = _provider_parameters(packet)
    return (
        _safe_text(params.get("script"))
        or _safe_text(params.get("prompt"))
        or _safe_text(packet.get("script"))
        or _packet_prompt(packet)
    )


def _media_type(packet: Dict[str, Any]) -> str:
    params = _provider_parameters(packet)
    return (
        _safe_text(params.get("media_type"))
        or _safe_text(packet.get("media_type"))
        or "media"
    ).lower()


def _make_data_url(content_type: str, binary: bytes) -> str:
    return f"data:{content_type};base64,{base64.b64encode(binary).decode('utf-8')}"


def _post_binary(
    *,
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    content_type: str,
    timeout: int = 90,
) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),