from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import os
import uuid

DATA_DIR = Path("data") / "ai_media_provider_adapters"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ADAPTER_EVENTS = DATA_DIR / "adapter_events.jsonl"
ADAPTER_RESULTS = DATA_DIR / "adapter_results.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"record_type": "corrupt_jsonl_line", "raw": line, "loaded_at": _now()})
    return rows


ADAPTER_ENV_REQUIREMENTS: Dict[str, list[str]] = {
    "openai": ["OPENAI_API_KEY"],
    "google": ["GOOGLE_API_KEY"],
    "runway": ["RUNWAY_API_KEY"],
    "kling": ["KLING_API_KEY"],
    "veo": ["GOOGLE_API_KEY"],
    "sora": ["OPENAI_API_KEY"],
    "wan": ["WAN_API_KEY"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
    "heygen": ["HEYGEN_API_KEY"],
    "replicate": ["REPLICATE_API_TOKEN"],
    "flux_kontext": ["FLUX_API_KEY"],
}


PROVIDER_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "openai": {
        "provider_type": "image_text",
        "capabilities": ["image_generation", "image_editing", "creative_prompting"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "google": {
        "provider_type": "image_video",
        "capabilities": ["image_generation", "video_generation", "creative_prompting"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "runway": {
        "provider_type": "video",
        "capabilities": ["image_to_video", "text_to_video", "camera_motion"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "kling": {
        "provider_type": "video",
        "capabilities": ["realistic_motion", "text_to_video", "image_to_video"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "veo": {
        "provider_type": "video",
        "capabilities": ["cinematic_video", "text_to_video", "storytelling"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "sora": {
        "provider_type": "video",
        "capabilities": ["cinematic_video", "world_consistency", "story_video"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "wan": {
        "provider_type": "video_audio",
        "capabilities": ["text_to_video", "image_to_video", "synchronised_audio", "lip_sync"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "elevenlabs": {
        "provider_type": "audio",
        "capabilities": ["tts", "voice_clone", "dubbing", "voice_replacement"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "heygen": {
        "provider_type": "avatar_video",
        "capabilities": ["avatar_video", "lip_sync", "multilingual_presenter", "voice_translation"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "replicate": {
        "provider_type": "model_marketplace",
        "capabilities": ["image_generation", "video_generation", "specialist_models"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
    "flux_kontext": {
        "provider_type": "image_editing",
        "capabilities": ["context_image_editing", "style_transfer", "brand_consistency"],
        "safe_modes": ["prepare", "draft", "execute_if_key_present"],
    },
}


def ai_media_provider_adapters_readiness() -> Dict[str, Any]:
    providers = []
    for provider, required_env in ADAPTER_ENV_REQUIREMENTS.items():
        missing = [name for name in required_env if not os.getenv(name)]
        providers.append({
            "provider": provider,
            "configured": not missing,
            "missing_env": missing,
            "capabilities": PROVIDER_CAPABILITIES.get(provider, {}).get("capabilities", []),
            "provider_type": PROVIDER_CAPABILITIES.get(provider, {}).get("provider_type", "unknown"),
        })

    return {
        "status": "ready",
        "runtime": "ai_media_provider_adapters",
        "provider_count": len(providers),
        "providers": providers,
        "supports_safe_prepare_without_keys": True,
        "supports_key_presence_detection": True,
        "external_execution_guarded": True,
        "owner_approval_required_for_paid_scaling": True,
        "governance_preserved": True,
        "layout_changes": False,
    }


def get_provider_adapter_status(provider: str) -> Dict[str, Any]:
    provider = str(provider or "").strip().lower()
    required_env = ADAPTER_ENV_REQUIREMENTS.get(provider)
    capabilities = PROVIDER_CAPABILITIES.get(provider)

    if not required_env or not capabilities:
        return {
            "status": "unsupported",
            "provider": provider,
            "configured": False,
            "missing_env": [],
            "reason": "provider_adapter_not_registered",
            "governance_preserved": True,
        }

    missing = [name for name in required_env if not os.getenv(name)]
    return {
        "status": "configured" if not missing else "missing_keys",
        "provider": provider,
        "configured": not missing,
        "missing_env": missing,
        "required_env": required_env,
        "capabilities": capabilities,
        "governance_preserved": True,
        "layout_changes": False,
    }


def prepare_provider_payload(
    *,
    provider: str,
    media_type: str,
    prompt: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = payload or {}
    provider = str(provider or "").strip().lower()
    status = get_provider_adapter_status(provider)
    capabilities = PROVIDER_CAPABILITIES.get(provider, {})

    prepared = {
        "adapter_payload_id": f"adapter_payload_{uuid.uuid4().hex[:16]}",
        "provider": provider,
        "media_type": media_type,
        "prompt": prompt,
        "provider_type": capabilities.get("provider_type", "unknown"),
        "capabilities": capabilities.get("capabilities", []),
        "input_payload": payload,
        "safe_mode": "prepare",
        "created_at": _now(),
        "customer_safe_status": "Prepared",
        "internal_config_exposed": False,
        "governance_preserved": True,
    }

    return {
        "status": "prepared",
        "provider_status": status,
        "prepared_payload": prepared,
        "execution_allowed": bool(status.get("configured")),
        "reason": "ready_for_external_execution" if status.get("configured") else "provider_key_required_before_external_execution",
        "governance_preserved": True,
    }


def execute_ai_media_provider_adapter(
    *,
    provider: str,
    media_type: str,
    prompt: str,
    payload: Optional[Dict[str, Any]] = None,
    owner_approved: bool = False,
    allow_external_execution: bool = False,
) -> Dict[str, Any]:
    provider = str(provider or "").strip().lower()
    execution_id = f"adapter_exec_{uuid.uuid4().hex[:16]}"
    prepared = prepare_provider_payload(provider=provider, media_type=media_type, prompt=prompt, payload=payload)

    high_risk_terms = ["increase spend", "scale campaign", "publish paid", "contract", "budget increase"]
    risky = any(term in (prompt or "").lower() for term in high_risk_terms)

    if risky and not owner_approved:
        status = "pending_owner_approval"
        execution_state = "blocked_before_external_execution"
        external_execution_performed = False
    elif not allow_external_execution:
        status = "prepared"
        execution_state = "safe_prepare_only"
        external_execution_performed = False
    elif not prepared["execution_allowed"]:
        status = "prepared"
        execution_state = "provider_key_required"
        external_execution_performed = False
    else:
        status = "ready_for_external_execution"
        execution_state = "adapter_ready_provider_call_not_invoked_by_stub"
        external_execution_performed = False

    result = {
        "execution_id": execution_id,
        "provider": provider,
        "media_type": media_type,
        "status": status,
        "execution_state": execution_state,
        "external_execution_performed": external_execution_performed,
        "prepared": prepared,
        "owner_approved": owner_approved,
        "allow_external_execution": allow_external_execution,
        "created_at": _now(),
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "internal_config_exposed": False,
        "layout_changes": False,
    }

    _append_jsonl(ADAPTER_RESULTS, result)
    _append_jsonl(ADAPTER_EVENTS, {
        "event_id": f"adapter_event_{uuid.uuid4().hex[:16]}",
        "execution_id": execution_id,
        "provider": provider,
        "media_type": media_type,
        "status": status,
        "created_at": _now(),
        "governance_preserved": True,
    })

    return result


def list_ai_media_provider_adapter_results(
    *,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(ADAPTER_RESULTS)
    if provider:
        rows = [r for r in rows if r.get("provider") == provider]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "results": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
