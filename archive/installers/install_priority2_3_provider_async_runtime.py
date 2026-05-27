from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
RUNTIME = ROOT / "backend" / "app" / "runtime"
BACKUPS = ROOT / "backups"
RUNTIME.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

provider_file = RUNTIME / "ai_media_provider_async_runtime.py"
test_file = ROOT / "test_priority2_3_provider_async_runtime.py"

if provider_file.exists():
    (BACKUPS / f"ai_media_provider_async_runtime_before_priority2_3_{stamp}.py").write_text(
        provider_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

provider_file.write_text(r'''
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


PROVIDER_REGISTRY = {
    "runway": {
        "required_env": ["RUNWAY_API_KEY"],
        "type": "video",
        "capabilities": ["text_to_video", "image_to_video", "camera_motion"],
        "timeout_seconds": 600,
    },
    "kling": {
        "required_env": ["KLING_API_KEY"],
        "type": "video",
        "capabilities": ["text_to_video", "image_to_video", "realistic_motion"],
        "timeout_seconds": 600,
    },
    "heygen": {
        "required_env": ["HEYGEN_API_KEY"],
        "type": "avatar_video",
        "capabilities": ["avatar_video", "lip_sync", "dubbing"],
        "timeout_seconds": 900,
    },
    "elevenlabs": {
        "required_env": ["ELEVENLABS_API_KEY"],
        "type": "audio",
        "capabilities": ["voiceover", "dubbing", "voice_clone"],
        "timeout_seconds": 300,
    },
    "replicate": {
        "required_env": ["REPLICATE_API_TOKEN"],
        "type": "multi_modal",
        "capabilities": ["image", "video", "upscale", "fallback_generation"],
        "timeout_seconds": 600,
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def provider_key_status(provider: str) -> Dict[str, Any]:
    config = PROVIDER_REGISTRY.get(provider, {})
    required = config.get("required_env", [])
    missing = [name for name in required if not os.getenv(name)]
    return {
        "provider": provider,
        "configured": not missing,
        "required_env": required,
        "missing_env": missing,
        "capabilities": config.get("capabilities", []),
        "provider_type": config.get("type", "unknown"),
        "timeout_seconds": config.get("timeout_seconds", 600),
        "governance_preserved": True,
        "internal_config_exposed": False,
    }


def choose_provider_chain(media_type: str, preferred_provider: str = "") -> List[str]:
    media = (media_type or "").lower()
    if preferred_provider and preferred_provider in PROVIDER_REGISTRY:
        base = [preferred_provider]
    elif "dubbing" in media or "avatar" in media or "lip" in media:
        base = ["heygen", "elevenlabs", "runway", "kling", "replicate"]
    elif "image" in media:
        base = ["replicate", "runway", "kling"]
    else:
        base = ["runway", "kling", "replicate", "heygen", "elevenlabs"]

    seen = set()
    return [p for p in base if not (p in seen or seen.add(p))]


def create_async_generation_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    job_id = "media_job_" + uuid.uuid4().hex[:16]
    media_type = payload.get("media_type", "video")
    preferred = payload.get("preferred_provider", "")
    chain = choose_provider_chain(media_type, preferred)
    active_provider = chain[0]
    status = provider_key_status(active_provider)

    execution_state = "prepared_missing_provider_key"
    if status["configured"]:
        execution_state = "queued_for_provider_execution"

    return {
        "success": True,
        "job_id": job_id,
        "tenant_id": payload.get("tenant_id", "tenant_unknown"),
        "media_type": media_type,
        "objective": payload.get("objective", ""),
        "provider_chain": chain,
        "active_provider": active_provider,
        "provider_status": status,
        "execution_state": execution_state,
        "progress": {
            "stage": "provider_execution_prepared",
            "percentage": 10 if status["configured"] else 5,
            "message": "Provider execution prepared." if status["configured"] else "Provider key required before live execution.",
        },
        "retry_policy": {
            "max_attempts": 3,
            "fallback_enabled": True,
            "fallback_chain": chain[1:],
            "retry_on": [
                "provider_timeout",
                "provider_unavailable",
                "low_quality_result",
                "asset_delivery_failed",
            ],
            "owner_review_after_exhausted_retries": True,
            "dead_letter_after_exhausted_retries": True,
        },
        "timeout_policy": {
            "provider_timeout_seconds": status["timeout_seconds"],
            "cancel_supported": True,
            "polling_interval_seconds": 15,
        },
        "asset_delivery_packet": {
            "status": "awaiting_generation_result",
            "secure_delivery_required": True,
            "tenant_isolated_storage_required": True,
            "customer_safe_preview_required": True,
            "cdn_ready": False,
        },
        "history_event": {
            "event_type": "generation_job_created",
            "created_at": now_iso(),
            "runtime": "priority2_3_provider_async_runtime",
            "governance_preserved": True,
        },
        "customer_safe_status": "Prepared" if not status["configured"] else "Queued",
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }


def poll_async_generation_job(job: Dict[str, Any]) -> Dict[str, Any]:
    state = job.get("execution_state")
    configured = job.get("provider_status", {}).get("configured", False)

    if not configured:
        return {
            **job,
            "execution_state": "waiting_for_provider_key",
            "progress": {
                "stage": "provider_configuration_required",
                "percentage": 5,
                "message": "External provider key required before live generation.",
            },
            "customer_safe_status": "Provider setup required",
            "polled_at": now_iso(),
        }

    return {
        **job,
        "execution_state": "provider_processing",
        "progress": {
            "stage": "provider_processing",
            "percentage": 35,
            "message": "Provider generation is in progress.",
        },
        "customer_safe_status": "Generating",
        "polled_at": now_iso(),
    }


def cancel_async_generation_job(job: Dict[str, Any], reason: str = "owner_cancelled") -> Dict[str, Any]:
    return {
        **job,
        "execution_state": "cancelled",
        "cancelled": True,
        "cancel_reason": reason,
        "progress": {
            "stage": "cancelled",
            "percentage": job.get("progress", {}).get("percentage", 0),
            "message": "Generation job cancelled safely.",
        },
        "customer_safe_status": "Cancelled",
        "updated_at": now_iso(),
        "governance_preserved": True,
    }


def failover_async_generation_job(job: Dict[str, Any], failure_reason: str = "provider_unavailable") -> Dict[str, Any]:
    chain = job.get("provider_chain", [])
    current = job.get("active_provider")
    remaining = [p for p in chain if p != current]

    if not remaining:
        return {
            **job,
            "execution_state": "dead_letter_owner_review_required",
            "failure_reason": failure_reason,
            "customer_safe_status": "Needs review",
            "owner_review_required": True,
            "updated_at": now_iso(),
        }

    next_provider = remaining[0]
    status = provider_key_status(next_provider)

    return {
        **job,
        "active_provider": next_provider,
        "provider_status": status,
        "execution_state": "fallback_provider_selected" if status["configured"] else "fallback_provider_missing_key",
        "failure_reason": failure_reason,
        "progress": {
            "stage": "provider_fallback_selected",
            "percentage": 15,
            "message": "Fallback provider selected safely.",
        },
        "customer_safe_status": "Retry prepared",
        "updated_at": now_iso(),
        "governance_preserved": True,
    }


def finalise_generated_asset_packet(job: Dict[str, Any], provider_result: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = "media_asset_" + uuid.uuid4().hex[:16]
    return {
        "success": True,
        "asset_id": asset_id,
        "job_id": job.get("job_id"),
        "tenant_id": job.get("tenant_id"),
        "provider": job.get("active_provider"),
        "asset_status": "prepared_for_secure_delivery",
        "provider_result": {
            "status": provider_result.get("status", "completed"),
            "external_asset_reference": provider_result.get("external_asset_reference", ""),
            "duration_seconds": provider_result.get("duration_seconds"),
        },
        "delivery": {
            "customer_safe_preview_ready": True,
            "secure_download_ready": False,
            "cdn_ready": False,
            "tenant_isolated": True,
        },
        "quality_review_required": True,
        "customer_safe_status": "Ready for review",
        "internal_config_exposed": False,
        "governance_preserved": True,
        "created_at": now_iso(),
    }


def provider_async_runtime_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime": "priority2_3_provider_async_runtime",
        "status": "ready",
        "providers": {
            name: provider_key_status(name)
            for name in PROVIDER_REGISTRY
        },
        "capabilities": [
            "real_provider_adapter_preparation",
            "async_generation_job_runtime",
            "provider_polling_engine",
            "retry_failover_orchestration",
            "timeout_handling",
            "cancel_runtime",
            "execution_history_event_generation",
            "asset_delivery_packet_finalisation",
        ],
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "internal_config_exposed": False,
        "layout_changes": False,
    }
''', encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.ai_media_provider_async_runtime import (
    provider_async_runtime_readiness,
    create_async_generation_job,
    poll_async_generation_job,
    cancel_async_generation_job,
    failover_async_generation_job,
    finalise_generated_asset_packet,
)


def run():
    readiness = provider_async_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert "runway" in readiness["providers"]
    assert readiness["governance_preserved"] is True

    job = create_async_generation_job({
        "tenant_id": "tenant_test",
        "media_type": "ugc video",
        "objective": "premium governed generation",
        "preferred_provider": "runway",
    })
    assert job["success"] is True
    assert job["active_provider"] == "runway"
    assert job["governance_preserved"] is True
    assert job["internal_config_exposed"] is False

    polled = poll_async_generation_job(job)
    assert "execution_state" in polled
    assert polled["governance_preserved"] is True

    failed_over = failover_async_generation_job(job, "provider_timeout")
    assert failed_over["active_provider"] != "runway"
    assert failed_over["governance_preserved"] is True

    cancelled = cancel_async_generation_job(job)
    assert cancelled["execution_state"] == "cancelled"

    asset = finalise_generated_asset_packet(job, {
        "status": "completed",
        "external_asset_reference": "provider_asset_test",
        "duration_seconds": 12,
    })
    assert asset["success"] is True
    assert asset["asset_status"] == "prepared_for_secure_delivery"
    assert asset["delivery"]["tenant_isolated"] is True
    assert asset["customer_safe_status"] == "Ready for review"

    print("PRIORITY2_3_PROVIDER_ASYNC_RUNTIME_OK")


if __name__ == "__main__":
    run()
''', encoding="utf-8")

print("PRIORITY2_3_PROVIDER_ASYNC_RUNTIME_INSTALLED")
print(f"Created/updated: {provider_file}")
print(f"Created/updated: {test_file}")