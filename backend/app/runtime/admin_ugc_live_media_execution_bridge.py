from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
from typing import Any, Dict, Optional

try:
    from backend.app.runtime.creative_product_asset_library import build_creative_execution_asset_context
except Exception:
    build_creative_execution_asset_context = None

try:
    from backend.app.runtime.runtime_creative_execution_integration import create_runtime_creative_execution_plan
except Exception:
    create_runtime_creative_execution_plan = None

try:
    from backend.app.runtime.elevenlabs_live_tts_quality_adapter import run_elevenlabs_tts_quality_test
except Exception:
    run_elevenlabs_tts_quality_test = None

try:
    from backend.app.runtime.runway_live_video_quality_adapter import run_runway_text_to_video_quality_test
except Exception:
    run_runway_text_to_video_quality_test = None

try:
    from backend.app.runtime.creative_asset_persistence_bridge import persist_creative_asset
except Exception:
    persist_creative_asset = None


ROOT = Path(__file__).resolve().parents[3]
COMPOSED_OUTPUT_DIR = ROOT / "runtime_outputs" / "creative_composed_media"
COMPOSED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_label(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(value or "asset"))
    return cleaned[:120] or "asset"


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _file_exists(path: Optional[str]) -> bool:
    return bool(path and Path(path).exists() and Path(path).is_file())


def compose_audio_video_asset(
    *,
    video_path: Optional[str],
    audio_path: Optional[str],
    test_label: str,
) -> Dict[str, Any]:
    if not _file_exists(video_path) or not _file_exists(audio_path):
        return {
            "success": False,
            "status": "composition_skipped_missing_audio_or_video",
            "video_path_present": bool(video_path),
            "audio_path_present": bool(audio_path),
            "video_file_exists": _file_exists(video_path),
            "audio_file_exists": _file_exists(audio_path),
            "composed_video_saved": False,
            "credential_values_exposed": False,
        }

    if not _ffmpeg_available():
        return {
            "success": False,
            "status": "composition_skipped_ffmpeg_unavailable",
            "composed_video_saved": False,
            "credential_values_exposed": False,
        }

    safe_label = _safe_label(test_label)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = COMPOSED_OUTPUT_DIR / f"{stamp}_{safe_label}_final_synced_video.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if completed.returncode != 0:
            return {
                "success": False,
                "status": "composition_failed",
                "return_code": completed.returncode,
                "stderr": (completed.stderr or "")[-2000:],
                "composed_video_saved": False,
                "credential_values_exposed": False,
            }

        return {
            "success": True,
            "status": "composed_synced_video_created",
            "provider": "internal_ffmpeg",
            "asset_type": "combined_video",
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "composed_video_path": str(output_path),
            "composed_video_saved": output_path.exists(),
            "composed_video_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "ffmpeg_available": True,
            "credential_values_exposed": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "created_at": _now(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "composition_exception",
            "error": str(exc),
            "composed_video_saved": False,
            "credential_values_exposed": False,
        }


def should_route_to_ugc_live_media(task: str, agent_key: str = "") -> bool:
    text = f"{task or ''} {agent_key or ''}".lower()

    creative_agent_match = any(
        marker in text
        for marker in [
            "ugc",
            "ugc_creative",
            "ugc creative",
            "paid_ads",
            "paid ads",
            "product_image",
            "product image",
            "social_media",
            "social media",
            "marketing",
            "influencer",
            "creative",
        ]
    )

    media_intent_match = any(
        marker in text
        for marker in [
            "video",
            "audio",
            "ad",
            "advertisement",
            "reel",
            "tiktok",
            "instagram",
            "voiceover",
            "creative",
            "campaign",
            "product demo",
            "social media",
            "visual",
            "image",
        ]
    )

    return bool(creative_agent_match and media_intent_match)


def _run_direct_live_media_execution(
    *,
    task: str,
    agent_key: str,
    test_label: str,
) -> Dict[str, Any]:
    if create_runtime_creative_execution_plan is None:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "runtime_creative_execution_integration_unavailable",
            "fallback_runtime": "direct_live_media",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "media_assets_created": False,
            "created_at": _now(),
        }

    execution_plan = create_runtime_creative_execution_plan(
        creative_goal=task,
        content_type="ugc video ad",
        target_platform="TikTok / Instagram Reels / Meta Ads",
        language="English",
        quality_priority="high",
        budget_priority="balanced",
        requires_avatar=False,
        requires_lipsync=False,
        requires_dubbing=False,
        requires_cinematic=False,
        requires_ugc_realism=True,
        requires_voiceover=True,
        owner_approved_live_execution=True,
    )

    voice_result: Dict[str, Any] = {
        "success": False,
        "status": "elevenlabs_adapter_unavailable",
        "audio_saved": False,
    }

    video_result: Dict[str, Any] = {
        "success": False,
        "status": "runway_adapter_unavailable",
        "video_saved": False,
    }

    if run_elevenlabs_tts_quality_test is not None:
        voice_script = (
            "This lymphatic massager has become my favourite part of my evening wellness routine. "
            "It feels relaxing, easy to use, and gives me that spa-like self-care feeling at home. "
            "If you want a simple way to level up your recovery and body-care routine, this is worth trying."
        )

        voice_result = run_elevenlabs_tts_quality_test(
            text=voice_script,
            voice_id="pNInz6obpgDQGcFmaJgB",
            test_label=f"{test_label}_voiceover",
            allow_live_execution=True,
        )

    if run_runway_text_to_video_quality_test is not None:
        video_prompt = (
            "A premium realistic UGC-style ecommerce advertisement for a lymphatic drainage massager. "
            "A wellness-focused female creator demonstrates the device in a clean luxury bathroom and spa-like home setting. "
            "Soft natural lighting, calming self-care routine, close-up product shots, realistic human movement, "
            "premium TikTok and Instagram Reel style, luxury wellness brand aesthetic, smooth camera motion, high-converting social ad."
        )

        video_result = run_runway_text_to_video_quality_test(
            prompt_text=video_prompt,
            test_label=f"{test_label}_runway_video",
            allow_live_execution=True,
        )

    audio_path = voice_result.get("audio_path")
    video_path = video_result.get("video_path")

    creative_asset_context = (
        build_creative_execution_asset_context(tenant_id="owner_admin", limit=25)
        if build_creative_execution_asset_context is not None
        else {"success": False, "asset_count": 0, "assets_by_type": {}}
    )

    composition_result = compose_audio_video_asset(
        video_path=video_path,
        audio_path=audio_path,
        test_label=test_label,
    )

    media_assets_created = bool(
        voice_result.get("audio_saved")
        or video_result.get("video_saved")
        or composition_result.get("composed_video_saved")
    )

    persisted_asset_records = []

    if persist_creative_asset is not None:
        if composition_result.get("composed_video_saved"):
            persisted_asset_records.append(
                persist_creative_asset(
                    {
                        "provider": "internal_ffmpeg",
                        "asset_type": "combined_video",
                        "test_label": f"{test_label}_final_synced_video",
                        "provider_asset_id": composition_result.get("composed_video_path"),
                        "provider_asset_url": composition_result.get("composed_video_path"),
                        "preview_url": composition_result.get("composed_video_path"),
                        "download_url": composition_result.get("composed_video_path"),
                        "status": "final_synced_video_persisted",
                        "summary": "Final synced MP4 combining generated Runway video with ElevenLabs voiceover.",
                    }
                )
            )

        if voice_result.get("audio_saved"):
            persisted_asset_records.append(
                persist_creative_asset(
                    {
                        "provider": "elevenlabs",
                        "asset_type": "audio",
                        "test_label": voice_result.get("test_label") or f"{test_label}_voiceover",
                        "provider_asset_id": voice_result.get("generation_id") or voice_result.get("task_id"),
                        "provider_asset_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                        "preview_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                        "download_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                    }
                )
            )

        if video_result.get("video_saved") or video_result.get("video_url_preview") or video_result.get("video_url"):
            persisted_asset_records.append(
                persist_creative_asset(
                    {
                        "provider": "runway",
                        "asset_type": "video",
                        "test_label": video_result.get("test_label") or f"{test_label}_runway_video",
                        "provider_asset_id": video_result.get("task_id") or video_result.get("video_id") or video_result.get("generation_id"),
                        "provider_asset_url": video_result.get("video_url") or video_result.get("video_url_preview") or video_result.get("video_path"),
                        "preview_url": video_result.get("video_url_preview") or video_result.get("video_url") or video_result.get("video_path"),
                        "download_url": video_result.get("video_url") or video_result.get("video_path"),
                    }
                )
            )

    playable_records = [
        record
        for record in persisted_asset_records
        if isinstance(record, dict) and bool(record.get("playable"))
    ]

    return {
        "success": True,
        "provider_runtime": "admin_ugc_live_media_execution_bridge",
        "fallback_runtime": "direct_live_media",
        "status": "ugc_live_media_execution_completed" if playable_records else "ugc_live_media_execution_no_playable_output",
        "agent_key": agent_key,
        "task": task,
        "execution_plan": execution_plan,
        "creative_asset_context": creative_asset_context,
        "voice_result": voice_result,
        "video_result": video_result,
        "composition_result": composition_result,
        "media_assets_created": media_assets_created,
        "audio_saved": bool(voice_result.get("audio_saved")),
        "video_saved": bool(video_result.get("video_saved")),
        "final_synced_video_saved": bool(composition_result.get("composed_video_saved")),
        "audio_path": audio_path,
        "video_path": video_path,
        "final_synced_video_path": composition_result.get("composed_video_path"),
        "video_url_preview": video_result.get("video_url_preview"),
        "persisted_asset_records": persisted_asset_records,
        "persisted_asset_count": len(persisted_asset_records),
        "playable_asset_count": len(playable_records),
        "primary_deliverable_type": "combined_video" if composition_result.get("composed_video_saved") else "separate_audio_video",
        "credential_values_exposed": False,
        "external_actions_performed": bool(
            voice_result.get("external_action_performed")
            or video_result.get("external_action_performed")
        ),
        "live_provider_calls_triggered": bool(
            voice_result.get("live_provider_call_triggered")
            or video_result.get("live_provider_call_triggered")
        ),
        "customer_safe_summary": {
            "title": "Creative media execution completed",
            "description": "Generated live premium creative media assets through governed provider execution.",
            "audio_created": bool(voice_result.get("audio_saved")),
            "video_created": bool(video_result.get("video_saved")),
            "final_synced_video_created": bool(composition_result.get("composed_video_saved")),
        },
        "created_at": _now(),
    }


def run_admin_ugc_live_media_execution(
    task: str,
    agent_key: str = "ugc_creative_agent",
    owner_approved_live_execution: bool = False,
    test_label: str = "admin_ugc_live_media_execution",
    force_direct_fallback: bool = False,
) -> Dict[str, Any]:
    if not owner_approved_live_execution:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "blocked_owner_approval_required",
            "reason": "Live creative media execution requires owner_approved_live_execution=True.",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "media_assets_created": False,
            "created_at": _now(),
        }

    if force_direct_fallback:
        return _run_direct_live_media_execution(
            task=task,
            agent_key=agent_key,
            test_label=test_label,
        )

    try:
        from backend.app.runtime.async_media_job_foundation import enqueue_media_job

        media_job = enqueue_media_job(
            task=task or "Create a premium UGC creative media asset.",
            agent_id=agent_key or "ugc_creative_agent",
            tenant_id="owner_admin",
            include_image=True,
            include_audio=True,
            include_video=True,
            include_avatar=False,
        )

        execution_plan = (
            create_runtime_creative_execution_plan(
                creative_goal=task,
                content_type="ugc video ad",
                target_platform="TikTok / Instagram Reels / Meta Ads",
                language="English",
                quality_priority="high",
                budget_priority="balanced",
                requires_avatar=False,
                requires_lipsync=False,
                requires_dubbing=False,
                requires_cinematic=False,
                requires_ugc_realism=True,
                requires_voiceover=True,
                owner_approved_live_execution=True,
            )
            if create_runtime_creative_execution_plan is not None
            else {"success": True, "status": "media_job_queued_without_runtime_plan"}
        )

        return {
            "success": True,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "media_job_queued",
            "execution_status": "media_job_queued",
            "agent_key": agent_key,
            "task": task,
            "execution_plan": execution_plan,
            "media_job_created": True,
            "media_job_id": media_job.get("job_id"),
            "media_job_status": media_job.get("status"),
            "media_assets_created": False,
            "preview_ready": False,
            "download_ready": False,
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_summary": {
                "title": "Creative media job queued",
                "description": "Live provider execution will run through the governed media job worker.",
                "audio_created": False,
                "video_created": False,
                "final_synced_video_created": False,
            },
            "created_at": _now(),
        }
    except Exception as exc:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "media_job_queue_failed",
            "error": str(exc)[:800],
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "media_assets_created": False,
            "created_at": _now(),
        }


def run_admin_ugc_live_media_execution_fallback(
    task: str,
    agent_key: str = "ugc_creative_agent",
    owner_approved_live_execution: bool = False,
    test_label: str = "admin_ugc_live_media_execution_fallback",
) -> Dict[str, Any]:
    if not owner_approved_live_execution:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "blocked_owner_approval_required",
            "reason": "Live creative media fallback requires owner_approved_live_execution=True.",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "media_assets_created": False,
            "created_at": _now(),
        }

    return _run_direct_live_media_execution(
        task=task,
        agent_key=agent_key,
        test_label=test_label,
    )


def get_admin_ugc_live_media_execution_bridge_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_runtime": "admin_ugc_live_media_execution_bridge",
        "status": "ready",
        "ugc_media_routing_enabled": True,
        "creative_team_media_routing_enabled": True,
        "runtime_creative_execution_connected": create_runtime_creative_execution_plan is not None,
        "elevenlabs_adapter_connected": run_elevenlabs_tts_quality_test is not None,
        "runway_adapter_connected": run_runway_text_to_video_quality_test is not None,
        "media_composition_enabled": True,
        "ffmpeg_available": _ffmpeg_available(),
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "verified_at": _now(),
    }
