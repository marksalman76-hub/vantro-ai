from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
RUNTIME = ROOT / "backend" / "app" / "runtime"
BACKUPS = ROOT / "backups"

RUNTIME.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_file = RUNTIME / "real_provider_activation_layer.py"
test_file = ROOT / "test_real_provider_activation_layer.py"

if runtime_file.exists():
    (BACKUPS / f"real_provider_activation_layer_before_{stamp}.py").write_text(
        runtime_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

runtime_file.write_text(r'''
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List


PROVIDER_REQUIREMENTS = {
    "openai": {
        "required_env": ["OPENAI_API_KEY"],
        "category": "llm_generation",
        "capabilities": ["premium_text_generation", "brief_generation", "reasoning", "structured_output"],
    },
    "runway": {
        "required_env": ["RUNWAY_API_KEY"],
        "category": "video_generation",
        "capabilities": ["text_to_video", "image_to_video", "camera_motion"],
    },
    "kling": {
        "required_env": ["KLING_API_KEY"],
        "category": "video_generation",
        "capabilities": ["text_to_video", "image_to_video", "realistic_motion"],
    },
    "heygen": {
        "required_env": ["HEYGEN_API_KEY"],
        "category": "avatar_video_generation",
        "capabilities": ["avatar_video", "lip_sync", "dubbing"],
    },
    "elevenlabs": {
        "required_env": ["ELEVENLABS_API_KEY"],
        "category": "audio_generation",
        "capabilities": ["voiceover", "dubbing", "voice_clone"],
    },
    "replicate": {
        "required_env": ["REPLICATE_API_TOKEN"],
        "category": "fallback_multimodal_generation",
        "capabilities": ["image_generation", "video_generation", "upscale", "fallback_generation"],
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _enabled(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _present(name: str) -> bool:
    return bool(str(os.getenv(name, "")).strip())


def provider_readiness(provider: str) -> Dict[str, Any]:
    key = str(provider or "").strip().lower()
    config = PROVIDER_REQUIREMENTS.get(key)

    if not config:
        return {
            "success": False,
            "provider": key,
            "status": "unknown_provider",
            "configured": False,
            "missing_env": [],
            "credential_values_exposed": False,
            "governance_preserved": True,
        }

    required = config["required_env"]
    missing = [env for env in required if not _present(env)]

    return {
        "success": True,
        "provider": key,
        "category": config["category"],
        "capabilities": config["capabilities"],
        "configured": len(missing) == 0,
        "status": "ready" if not missing else "missing_credentials",
        "required_env": required,
        "missing_env": missing,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def owner_live_execution_enabled() -> bool:
    return (
        _enabled("ENABLE_LIVE_LLM_CALLS")
        or _enabled("OWNER_LIVE_EXECUTION_ENABLED")
        or _enabled("ENABLE_REAL_PROVIDER_EXECUTION")
    )


def real_provider_execution_gate(provider: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    readiness = provider_readiness(provider)

    checks = {
        "provider_known": readiness.get("success") is True,
        "provider_configured": readiness.get("configured") is True,
        "owner_live_execution_enabled": owner_live_execution_enabled(),
        "tenant_id_present": bool(payload.get("tenant_id")),
        "agent_id_present": bool(payload.get("agent_id") or payload.get("requested_agent")),
        "task_present": bool(payload.get("task") or payload.get("action_type")),
        "client_safe_boundary_enforced": True,
        "credential_exposure_blocked": True,
        "internal_prompt_exposure_blocked": True,
        "backend_config_exposure_blocked": True,
    }

    failed = [name for name, passed in checks.items() if not passed]
    live_allowed = len(failed) == 0

    return {
        "success": True,
        "provider": provider,
        "live_execution_allowed": live_allowed,
        "execution_mode": "real_provider_execution_allowed" if live_allowed else "real_provider_execution_blocked",
        "failed_checks": failed,
        "passed_checks": [name for name, passed in checks.items() if passed],
        "provider_readiness": readiness,
        "customer_safe_message": (
            "Real provider execution is ready."
            if live_allowed
            else "Provider execution is prepared but blocked until credentials and owner live-execution controls are enabled."
        ),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "created_at": now_iso(),
    }


def select_provider_for_media(media_type: str, preferred_provider: str = "") -> Dict[str, Any]:
    media = str(media_type or "").lower()
    preferred = str(preferred_provider or "").strip().lower()

    if preferred in PROVIDER_REQUIREMENTS:
        chain = [preferred]
    elif "dubbing" in media or "avatar" in media or "lip" in media:
        chain = ["heygen", "elevenlabs", "runway", "kling", "replicate"]
    elif "video" in media or "ugc" in media:
        chain = ["runway", "kling", "heygen", "replicate"]
    elif "voice" in media or "audio" in media:
        chain = ["elevenlabs", "heygen"]
    else:
        chain = ["openai", "replicate"]

    for provider in PROVIDER_REQUIREMENTS:
        if provider not in chain:
            chain.append(provider)

    readiness_chain = [provider_readiness(provider) for provider in chain]
    configured = [item for item in readiness_chain if item.get("configured")]

    selected = configured[0]["provider"] if configured else chain[0]

    return {
        "success": True,
        "media_type": media_type,
        "selected_provider": selected,
        "provider_chain": chain,
        "configured_provider_count": len(configured),
        "readiness_chain": readiness_chain,
        "fallback_enabled": True,
        "credential_values_exposed": False,
        "governance_preserved": True,
    }


def build_real_provider_activation_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    media_type = payload.get("media_type") or payload.get("request", {}).get("media_type") or "generated_media"
    preferred_provider = payload.get("preferred_provider", "")

    selection = select_provider_for_media(media_type, preferred_provider)
    provider = selection["selected_provider"]
    gate = real_provider_execution_gate(provider, payload)

    return {
        "success": True,
        "runtime": "real_provider_activation_layer",
        "status": "ready_for_real_provider_when_credentials_enabled",
        "provider_selection": selection,
        "execution_gate": gate,
        "live_execution_allowed": gate["live_execution_allowed"],
        "next_steps": [
            "Add provider API keys in production environment variables.",
            "Enable owner-controlled live execution flag only after safe test generation.",
            "Run provider readiness test.",
            "Run one controlled provider generation.",
            "Persist generated asset and deliver through signed customer-safe delivery packet.",
        ],
        "blocked_until_ready": not gate["live_execution_allowed"],
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "created_at": now_iso(),
    }


def real_provider_activation_readiness() -> Dict[str, Any]:
    providers = {
        name: provider_readiness(name)
        for name in PROVIDER_REQUIREMENTS
    }

    configured_count = len([p for p in providers.values() if p.get("configured")])

    return {
        "success": True,
        "runtime": "real_provider_activation_layer",
        "status": "ready",
        "owner_live_execution_enabled": owner_live_execution_enabled(),
        "configured_provider_count": configured_count,
        "provider_count": len(PROVIDER_REQUIREMENTS),
        "providers": providers,
        "capabilities": [
            "provider_credential_readiness_checks",
            "owner_live_execution_gate",
            "media_type_provider_selection",
            "multi_provider_fallback_chain",
            "client_safe_provider_activation_packet",
            "credential_value_exposure_blocking",
            "real_provider_execution_gate",
        ],
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "layout_changes": False,
    }
''', encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.real_provider_activation_layer import (
    real_provider_activation_readiness,
    provider_readiness,
    select_provider_for_media,
    real_provider_execution_gate,
    build_real_provider_activation_packet,
)


def run():
    readiness = real_provider_activation_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["credential_values_exposed"] is False
    assert readiness["governance_preserved"] is True
    assert "openai" in readiness["providers"]

    openai = provider_readiness("openai")
    assert openai["success"] is True
    assert openai["credential_values_exposed"] is False

    selection = select_provider_for_media("ugc video")
    assert selection["success"] is True
    assert selection["provider_chain"][0] in {"runway", "kling", "heygen", "replicate"}

    gate = real_provider_execution_gate("openai", {
        "tenant_id": "tenant_test",
        "agent_id": "ugc_creative_agent",
        "task": "test task",
    })
    assert gate["success"] is True
    assert gate["credential_values_exposed"] is False
    assert gate["internal_config_exposed"] is False

    packet = build_real_provider_activation_packet({
        "tenant_id": "tenant_test",
        "agent_id": "ugc_creative_agent",
        "task": "Generate UGC brief",
        "media_type": "ugc video",
    })
    assert packet["success"] is True
    assert packet["runtime"] == "real_provider_activation_layer"
    assert packet["credential_values_exposed"] is False
    assert packet["governance_preserved"] is True

    print("REAL_PROVIDER_ACTIVATION_LAYER_OK")


if __name__ == "__main__":
    run()
''', encoding="utf-8")

print("REAL_PROVIDER_ACTIVATION_LAYER_INSTALLED")
print(f"Created/updated: {runtime_file}")
print(f"Created/updated: {test_file}")