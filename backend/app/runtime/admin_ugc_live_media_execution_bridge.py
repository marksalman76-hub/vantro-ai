from datetime import datetime, timezone
from typing import Any, Dict

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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def should_route_to_ugc_live_media(task: str, agent_key: str = "") -> bool:
    text = f"{task or ''} {agent_key or ''}".lower()

    ugc_agent_match = (
        "ugc" in text
        or "ugc_creative" in text
        or "ugc creative" in text
    )

    media_intent_match = any(
        marker in text
        for marker in [
            "video",
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
        ]
    )

    return bool(ugc_agent_match and media_intent_match)


def run_admin_ugc_live_media_execution(
    task: str,
    agent_key: str = "ugc_creative_agent",
    owner_approved_live_execution: bool = False,
    test_label: str = "admin_ugc_live_media_execution",
) -> Dict[str, Any]:
    if not owner_approved_live_execution:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "blocked_owner_approval_required",
            "reason": "Live UGC media execution requires owner_approved_live_execution=True.",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "media_assets_created": False,
            "created_at": _now(),
        }

    if create_runtime_creative_execution_plan is None:
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "runtime_creative_execution_integration_unavailable",
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

    media_assets_created = bool(
        voice_result.get("audio_saved") or video_result.get("video_saved")
    )

    persisted_asset_records = []

    if persist_creative_asset is not None:
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

    return {
        "success": True,
        "provider_runtime": "admin_ugc_live_media_execution_bridge",
        "status": "ugc_live_media_execution_completed",
        "agent_key": agent_key,
        "task": task,
        "execution_plan": execution_plan,
        "voice_result": voice_result,
        "video_result": video_result,
        "media_assets_created": media_assets_created,
        "audio_saved": bool(voice_result.get("audio_saved")),
        "video_saved": bool(video_result.get("video_saved")),
        "audio_path": voice_result.get("audio_path"),
        "video_path": video_result.get("video_path"),
        "video_url_preview": video_result.get("video_url_preview"),
        "persisted_asset_records": persisted_asset_records,
        "persisted_asset_count": len(persisted_asset_records),
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
            "title": "UGC media execution completed",
            "description": "Generated live premium creative media assets through governed provider execution.",
            "audio_created": bool(voice_result.get("audio_saved")),
            "video_created": bool(video_result.get("video_saved")),
        },
        "created_at": _now(),
    }


def get_admin_ugc_live_media_execution_bridge_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_runtime": "admin_ugc_live_media_execution_bridge",
        "status": "ready",
        "ugc_media_routing_enabled": True,
        "runtime_creative_execution_connected": create_runtime_creative_execution_plan is not None,
        "elevenlabs_adapter_connected": run_elevenlabs_tts_quality_test is not None,
        "runway_adapter_connected": run_runway_text_to_video_quality_test is not None,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "verified_at": _now(),
    }
