from __future__ import annotations

import base64
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


def _credential_configured(provider_id: str) -> bool:
    config = AI_MEDIA_PROVIDER_ENV_MAP.get(provider_id, {})
    keys = list(config.get("env_keys") or [])
    if provider_id == "kling":
        return _env_present(keys, require_all=True)
    return _env_present(keys)


def _live_dispatch_enabled() -> bool:
    return all(
        [
            _env_enabled("LIVE_EXTERNAL_CALLS_ENABLED"),
            _env_enabled("OWNER_APPROVED_LIVE_ACTIVATION"),
            _env_enabled("REAL_PROVIDER_HTTP_DISPATCH_ENABLED"),
        ]
    )


def _dispatch_diagnostics() -> Dict[str, Any]:
    live_external_calls_enabled = _env_enabled("LIVE_EXTERNAL_CALLS_ENABLED")
    owner_approved_live_activation = _env_enabled("OWNER_APPROVED_LIVE_ACTIVATION")
    real_provider_http_dispatch_enabled = _env_enabled("REAL_PROVIDER_HTTP_DISPATCH_ENABLED")
    return {
        "provider_dispatch_enabled": bool(
            live_external_calls_enabled
            and owner_approved_live_activation
            and real_provider_http_dispatch_enabled
        ),
        "live_external_calls_enabled": live_external_calls_enabled,
        "owner_approved_live_activation": owner_approved_live_activation,
        "real_provider_http_dispatch_enabled": real_provider_http_dispatch_enabled,
    }


def _request_json(
    *,
    url: str,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 90,
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
            raw = response.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {"raw_response": raw[:5000]}

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


def _first_string_field(value: Any, keys: List[str]) -> str:
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        for nested in value.values():
            found = _first_string_field(nested, keys)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _first_string_field(item, keys)
            if found:
                return found
    return ""


def _response_shape(value: Any) -> str:
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return "list"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "empty"
    return type(value).__name__.lower()


def _extract_embedded_media_data_url(value: Any, media_type: str = "") -> str:
    if isinstance(value, dict):
        for key in ["b64_json", "base64", "audio_base64", "video_base64", "image_base64"]:
            encoded = value.get(key)
            if isinstance(encoded, str) and encoded.strip():
                lowered_key = key.lower()
                lowered_media = str(media_type or "").lower()
                content_type = "application/octet-stream"
                if "audio" in lowered_key or "audio" in lowered_media:
                    content_type = "audio/mpeg"
                elif "video" in lowered_key or "video" in lowered_media:
                    content_type = "video/mp4"
                elif "image" in lowered_key or "image" in lowered_media or key == "b64_json":
                    content_type = "image/png"
                return f"data:{content_type};base64,{encoded.strip()}"
        for nested in value.values():
            found = _extract_embedded_media_data_url(nested, media_type)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _extract_embedded_media_data_url(item, media_type)
            if found:
                return found
    return ""


def _provider_error_code(response: Dict[str, Any], execution_status: str) -> str:
    return (
        _safe_text(response.get("error_code"))
        or _safe_text(response.get("code"))
        or (execution_status if "error" in execution_status or "failed" in execution_status else "")
    )


def _provider_error_safe_message(response: Dict[str, Any], error: Optional[str], execution_status: str) -> str:
    if "http_error" in execution_status:
        return "Provider HTTP request failed safely. No credentials or provider secrets were exposed."
    if "failed" in execution_status or error:
        return "Provider execution failed safely. No credentials or provider secrets were exposed."
    if execution_status in {"polling_provider", "processing"}:
        return "Provider execution is still processing. No playable media asset is available yet."
    return ""


def _has_explicit_output_reference(response: Dict[str, Any]) -> bool:
    return bool(
        _first_string_field(
            response,
            [
                "asset_url",
                "media_url",
                "video_url",
                "audio_url",
                "image_url",
                "download_url",
                "preview_url",
                "output_url",
                "url",
            ],
        )
    )


def _provider_parameters(packet: Dict[str, Any]) -> Dict[str, Any]:
    params = packet.get("provider_parameters")
    return params if isinstance(params, dict) else {}


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


def detect_ai_media_provider_readiness() -> Dict[str, Any]:
    providers = {}

    for provider_id, config in AI_MEDIA_PROVIDER_ENV_MAP.items():
        env_keys = list(config.get("env_keys", []))
        configured = _credential_configured(provider_id)
        providers[provider_id] = {
            "provider_id": provider_id,
            "configured": configured,
            "env_keys_checked": env_keys,
            "category": config.get("category"),
            "capabilities": config.get("capabilities", []),
            "live_execution_supported": bool(config.get("live_execution_supported")),
            "live_execution_enabled": bool(configured and _live_dispatch_enabled()),
            "credential_values_exposed": False,
        }

    configured_providers = [
        provider_id
        for provider_id, provider in providers.items()
        if provider.get("configured")
    ]

    live_supported_configured = [
        provider_id
        for provider_id, provider in providers.items()
        if provider.get("configured") and provider.get("live_execution_supported")
    ]

    return {
        "success": True,
        "runtime": "ai_media_live_provider_execution",
        "status": "ready",
        "provider_detection_enabled": True,
        "configured_provider_count": len(configured_providers),
        "configured_providers": configured_providers,
        "live_supported_configured_providers": live_supported_configured,
        "live_dispatch_enabled": _live_dispatch_enabled(),
        "providers": providers,
        "governance_preserved": True,
        "secret_exposure": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "layout_changes": False,
    }


def select_provider_route(provider_ready_packet: Dict[str, Any]) -> Dict[str, Any]:
    readiness = detect_ai_media_provider_readiness()
    providers = readiness.get("providers", {})

    params = _provider_parameters(provider_ready_packet)
    primary_slot = _safe_text(
        provider_ready_packet.get("primary_provider_slot") or params.get("provider"),
        "multi_modal_generation_provider",
    ).lower()
    fallback_slots = provider_ready_packet.get("fallback_provider_slots", []) or []
    media_type = _media_type(provider_ready_packet)

    if primary_slot in providers and providers.get(primary_slot, {}).get("configured"):
        preferred = [primary_slot]
    elif "voice" in media_type or "audio" in media_type or "dub" in media_type:
        preferred = ["elevenlabs"]
    elif "avatar" in media_type or "presenter" in media_type or "lipsync" in media_type:
        preferred = ["heygen"]
    elif "image" in media_type or "product" in media_type:
        preferred = ["openai_image"]
    elif "video" in media_type or "ugc" in media_type:
        preferred = ["runway", "kling", "openai_image"]
    else:
        preferred = ["openai_image", "runway", "kling", "heygen", "elevenlabs"]

    available = [
        provider_id
        for provider_id in preferred
        if providers.get(provider_id, {}).get("configured")
    ]

    selected_provider = available[0] if available else None

    return {
        "success": True,
        "routing_mode": "best_available_provider_for_media_type",
        "primary_provider_slot": primary_slot,
        "fallback_provider_slots": fallback_slots,
        "preferred_provider_order": preferred,
        "available_provider_order": available,
        "selected_provider": selected_provider,
        "provider_available": bool(selected_provider),
        "live_execution_supported": bool(
            selected_provider
            and providers.get(selected_provider, {}).get("live_execution_supported")
        ),
        "live_dispatch_enabled": _live_dispatch_enabled(),
        "manual_review_required": not bool(selected_provider),
        "fallback_to_adapter_stub": not bool(selected_provider),
        "secret_exposure": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _standard_result(
    *,
    success: bool,
    provider_id: Optional[str],
    execution_status: str,
    provider_ready_packet: Dict[str, Any],
    provider_response: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    asset_url: str = "",
    media_type: str = "",
) -> Dict[str, Any]:
    response = provider_response or {}
    resolved_asset_url = asset_url or _extract_first_url(response) or _extract_embedded_media_data_url(response, media_type or _media_type(provider_ready_packet))
    provider_job_id = _first_string_field(response, ["provider_job_id", "job_id", "task_id", "prediction_id", "id"])
    provider_polling_url = _first_string_field(response, ["status_url", "polling_url", "poll_url", "task_url", "retrieve_url"])
    if resolved_asset_url and provider_polling_url and resolved_asset_url == provider_polling_url and not _has_explicit_output_reference(response):
        resolved_asset_url = ""
    provider_http_status = response.get("status_code") or response.get("http_status")
    provider_output_url_present = bool(resolved_asset_url and not str(resolved_asset_url).startswith("data:"))
    provider_output_base64_present = bool(str(resolved_asset_url).startswith("data:"))
    provider_output_bytes_present = bool(
        response.get("audio_bytes") or response.get("video_bytes") or response.get("image_bytes") or response.get("bytes")
    )

    return {
        "success": bool(success),
        "runtime": "ai_media_live_provider_execution",
        "execution_status": execution_status,
        "status": execution_status,
        "provider_id": provider_id,
        "provider": provider_id,
        "media_type": media_type or _media_type(provider_ready_packet),
        "provider_response": response,
        "error": error,
        "asset_url": resolved_asset_url,
        "media_url": resolved_asset_url,
        "preview_url": resolved_asset_url,
        "download_url": resolved_asset_url,
        "real_media_asset_created": bool(resolved_asset_url),
        "live_provider_execution_attempted": True,
        "packet_type": provider_ready_packet.get("packet_type"),
        "governance_controls": provider_ready_packet.get("governance_controls", {}),
        "quality_controls": provider_ready_packet.get("quality_controls", {}),
        "generated_at": _now(),
        "provider_request_attempted": True,
        "provider_http_status": provider_http_status,
        "provider_response_shape": _response_shape(response),
        "provider_job_id": provider_job_id,
        "provider_job_id_present": bool(provider_job_id),
        "provider_polling_required": bool(
            not resolved_asset_url and execution_status in {"polling_provider", "processing"}
        ),
        "provider_polling_url": provider_polling_url,
        "provider_polling_url_present": bool(provider_polling_url),
        "provider_output_url_present": provider_output_url_present,
        "provider_output_bytes_present": provider_output_bytes_present,
        "provider_output_base64_present": provider_output_base64_present,
        "provider_error_code": _provider_error_code(response, execution_status),
        "provider_error_safe_message": _provider_error_safe_message(response, error, execution_status),
        "secret_exposure": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "layout_changes": False,
    }


def build_standard_ai_media_provider_result(
    *,
    success: bool,
    provider_id: Optional[str],
    execution_status: str,
    provider_ready_packet: Dict[str, Any],
    provider_response: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    return _standard_result(
        success=success,
        provider_id=provider_id,
        execution_status=execution_status,
        provider_ready_packet=provider_ready_packet,
        provider_response=provider_response,
        error=error,
    )


def _execute_openai_image(packet: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    prompt = _packet_prompt(packet)

    if not api_key:
        return _standard_result(
            success=False,
            provider_id="openai_image",
            execution_status="provider_key_missing",
            provider_ready_packet=packet,
            error="OPENAI_API_KEY missing",
            media_type="image",
        )

    result = _request_json(
        url="https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload={
            "model": os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            "prompt": prompt[:32000],
            "size": os.getenv("OPENAI_IMAGE_SIZE", "1024x1536"),
        },
        timeout=120,
    )

    response = result.get("response", {})
    asset_url = _extract_first_url(response)

    if not asset_url and isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, list) and data:
            b64 = data[0].get("b64_json") if isinstance(data[0], dict) else None
            if b64:
                try:
                    asset_url = _make_data_url("image/png", base64.b64decode(b64))
                except Exception:
                    asset_url = ""

    return _standard_result(
        success=bool(result.get("success") and asset_url),
        provider_id="openai_image",
        execution_status="completed" if asset_url else "provider_execution_attempted_no_asset_url",
        provider_ready_packet=packet,
        provider_response=response,
        asset_url=asset_url,
        media_type="image",
    )


def _execute_elevenlabs(packet: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()
    script = _packet_script(packet)

    if not api_key:
        return _standard_result(
            success=False,
            provider_id="elevenlabs",
            execution_status="provider_key_missing",
            provider_ready_packet=packet,
            error="ELEVENLABS_API_KEY missing",
            media_type="audio",
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    request = urllib.request.Request(
        url,
        data=json.dumps(
            {
                "text": script[:4500],
                "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
                "voice_settings": {
                    "stability": 0.48,
                    "similarity_boost": 0.75,
                },
            }
        ).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            audio = response.read()
            asset_url = _make_data_url("audio/mpeg", audio)
            return _standard_result(
                success=True,
                provider_id="elevenlabs",
                execution_status="completed",
                provider_ready_packet=packet,
                provider_response={
                    "status_code": int(response.status),
                    "audio_bytes": len(audio),
                    "provider_job_id": f"elevenlabs_audio_{int(time.time())}",
                },
                asset_url=asset_url,
                media_type="audio",
            )
    except urllib.error.HTTPError as error:
        return _standard_result(
            success=False,
            provider_id="elevenlabs",
            execution_status="provider_http_error",
            provider_ready_packet=packet,
            provider_response={
                "status_code": int(error.code),
                "error_body": error.read().decode("utf-8", errors="replace")[:2000],
            },
            media_type="audio",
        )
    except Exception as exc:
        return _standard_result(
            success=False,
            provider_id="elevenlabs",
            execution_status="provider_execution_failed",
            provider_ready_packet=packet,
            error=str(exc)[:1200],
            media_type="audio",
        )


def _execute_configured_job_provider(packet: Dict[str, Any], provider_id: str) -> Dict[str, Any]:
    """
    Runway, Kling, and HeyGen APIs vary by account/product version.
    This uses explicit endpoint env vars when configured, otherwise records a governed
    live-ready provider job instead of pretending that a file was generated.
    """
    params = _provider_parameters(packet)
    prompt = _packet_prompt(packet)

    endpoint_env = {
        "runway": "RUNWAY_CREATE_JOB_URL",
        "kling": "KLING_CREATE_JOB_URL",
        "heygen": "HEYGEN_CREATE_JOB_URL",
    }.get(provider_id)

    endpoint = os.getenv(endpoint_env or "", "").strip()

    if not endpoint:
        return _standard_result(
            success=True,
            provider_id=provider_id,
            execution_status="live_provider_ready_endpoint_missing",
            provider_ready_packet=packet,
            provider_response={
                "provider_job_prepared": True,
                "endpoint_env_required": endpoint_env,
                "prompt": prompt,
                "provider_parameters": {
                    key: value
                    for key, value in params.items()
                    if "key" not in str(key).lower() and "secret" not in str(key).lower() and "token" not in str(key).lower()
                },
            },
            media_type=_media_type(packet),
        )

    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "script": _packet_script(packet),
        "aspect_ratio": params.get("aspect_ratio", "9:16"),
        "duration": params.get("duration", 10),
        "format": params.get("format", "mp4"),
    }

    if provider_id == "runway":
        headers["Authorization"] = f"Bearer {os.getenv('RUNWAYML_API_SECRET', '').strip()}"
    elif provider_id == "kling":
        headers["X-Kling-Access-Key"] = os.getenv("KLING_ACCESS_KEY", "").strip()
        headers["X-Kling-Secret-Key"] = os.getenv("KLING_SECRET_KEY", "").strip()
    elif provider_id == "heygen":
        headers["X-Api-Key"] = os.getenv("HEYGEN_API_KEY", "").strip()

    result = _request_json(
        url=endpoint,
        headers=headers,
        payload=payload,
        timeout=120,
    )

    response = dict(result.get("response", {}) or {})
    response.setdefault("status_code", result.get("status_code"))
    asset_url = _extract_first_url(response) or _extract_embedded_media_data_url(response, _media_type(packet))
    provider_job_id = _first_string_field(response, ["provider_job_id", "job_id", "task_id", "prediction_id", "id"])
    provider_polling_url = _first_string_field(response, ["status_url", "polling_url", "poll_url", "task_url", "retrieve_url"])
    if asset_url and provider_polling_url and asset_url == provider_polling_url and not _has_explicit_output_reference(response):
        asset_url = ""
    if result.get("success") and asset_url:
        execution_status = "completed"
    elif result.get("success") and (provider_job_id or provider_polling_url):
        execution_status = "polling_provider"
    elif result.get("success"):
        execution_status = "provider_job_created_or_attempted"
    else:
        execution_status = "provider_http_error"

    return _standard_result(
        success=bool(result.get("success")),
        provider_id=provider_id,
        execution_status=execution_status,
        provider_ready_packet=packet,
        provider_response=response,
        asset_url=asset_url,
        media_type=_media_type(packet),
    )


def execute_ai_media_provider_ready_packet(provider_ready_packet: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(provider_ready_packet, dict):
        return build_standard_ai_media_provider_result(
            success=False,
            provider_id=None,
            execution_status="invalid_provider_packet",
            provider_ready_packet={},
            error="provider_ready_packet_required",
        )

    if provider_ready_packet.get("execution_allowed") is False:
        return build_standard_ai_media_provider_result(
            success=False,
            provider_id=None,
            execution_status="blocked_by_orchestration",
            provider_ready_packet=provider_ready_packet,
            error="provider_execution_not_allowed_by_orchestration",
        )

    route = select_provider_route(provider_ready_packet)
    selected_provider = route.get("selected_provider")
    dispatch = _dispatch_diagnostics()

    route["provider_available"] = bool(route.get("provider_available"))
    route["provider_configured"] = bool(selected_provider and _credential_configured(str(selected_provider)))
    route["provider_dispatch_enabled"] = bool(dispatch.get("provider_dispatch_enabled"))
    route["live_external_calls_enabled"] = bool(dispatch.get("live_external_calls_enabled"))
    route["owner_approved_live_activation"] = bool(dispatch.get("owner_approved_live_activation"))
    route["real_provider_http_dispatch_enabled"] = bool(dispatch.get("real_provider_http_dispatch_enabled"))

    if not selected_provider:
        result = build_standard_ai_media_provider_result(
            success=True,
            provider_id=None,
            execution_status="prepared_no_live_provider_configured",
            provider_ready_packet=provider_ready_packet,
            provider_response={
                "route": route,
                "adapter_stub_ready": False,
                "live_generation_attempted": False,
                "reason": "no_configured_ai_media_provider",
            },
        )
        result["route"] = route
        result["provider_configured"] = False
        result["provider_available"] = False
        result["provider_dispatch_enabled"] = bool(dispatch.get("provider_dispatch_enabled"))
        result["live_external_calls_enabled"] = bool(dispatch.get("live_external_calls_enabled"))
        result["owner_approved_live_activation"] = bool(dispatch.get("owner_approved_live_activation"))
        result["real_provider_http_dispatch_enabled"] = bool(dispatch.get("real_provider_http_dispatch_enabled"))
        result["provider_unavailable_reason"] = "provider_key_missing_or_not_configured_on_runtime"
        result["playable_asset_created"] = False
        result["signed_delivery_created"] = False
        result["metadata_only"] = True
        result["credential_values_exposed"] = False
        return result

    if not route.get("live_dispatch_enabled"):
        result = build_standard_ai_media_provider_result(
            success=True,
            provider_id=selected_provider,
            execution_status="blocked_live_dispatch_not_enabled",
            provider_ready_packet=provider_ready_packet,
            provider_response={
                "route": route,
                "live_generation_attempted": False,
                "reason": "LIVE_EXTERNAL_CALLS_ENABLED, OWNER_APPROVED_LIVE_ACTIVATION, and REAL_PROVIDER_HTTP_DISPATCH_ENABLED must be true.",
            },
        )
        result["route"] = route
        result["provider_configured"] = bool(route.get("provider_configured"))
        result["provider_available"] = bool(route.get("provider_available"))
        result["provider_dispatch_enabled"] = bool(dispatch.get("provider_dispatch_enabled"))
        result["live_external_calls_enabled"] = bool(dispatch.get("live_external_calls_enabled"))
        result["owner_approved_live_activation"] = bool(dispatch.get("owner_approved_live_activation"))
        result["real_provider_http_dispatch_enabled"] = bool(dispatch.get("real_provider_http_dispatch_enabled"))
        result["provider_unavailable_reason"] = "blocked_live_dispatch_not_enabled"
        result["playable_asset_created"] = False
        result["signed_delivery_created"] = False
        result["metadata_only"] = True
        result["credential_values_exposed"] = False
        return result

    if selected_provider == "openai_image":
        result = _execute_openai_image(provider_ready_packet)
    elif selected_provider == "elevenlabs":
        result = _execute_elevenlabs(provider_ready_packet)
    elif selected_provider in {"runway", "kling", "heygen"}:
        result = _execute_configured_job_provider(provider_ready_packet, selected_provider)
    else:
        result = build_standard_ai_media_provider_result(
            success=False,
            provider_id=selected_provider,
            execution_status="unsupported_provider",
            provider_ready_packet=provider_ready_packet,
            error=f"Unsupported provider: {selected_provider}",
        )

    result["route"] = route
    result["provider_configured"] = bool(route.get("provider_configured"))
    result["provider_available"] = bool(route.get("provider_available"))
    result["provider_dispatch_enabled"] = bool(dispatch.get("provider_dispatch_enabled"))
    result["live_external_calls_enabled"] = bool(dispatch.get("live_external_calls_enabled"))
    result["owner_approved_live_activation"] = bool(dispatch.get("owner_approved_live_activation"))
    result["real_provider_http_dispatch_enabled"] = bool(dispatch.get("real_provider_http_dispatch_enabled"))
    result["provider_unavailable_reason"] = (
        ""
        if result.get("real_media_asset_created")
        else str(result.get("execution_status") or "provider_unavailable")
    )
    result["playable_asset_created"] = bool(result.get("real_media_asset_created"))
    result["signed_delivery_created"] = bool(result.get("real_media_asset_created"))
    result["metadata_only"] = not bool(result.get("real_media_asset_created"))
    result["live_generation_attempted"] = True
    result["live_provider_execution_attempted"] = True
    result["credential_values_exposed"] = False
    result["customer_safe"] = True
    return result