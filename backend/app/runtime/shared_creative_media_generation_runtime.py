
from __future__ import annotations

from datetime import datetime
import os
import uuid
from typing import Any, Dict, List

from dotenv import load_dotenv

from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset
from backend.app.runtime.audio_visual_provider_stack import recommended_stack_for_task

load_dotenv(".env.local")


CREATIVE_MEDIA_AGENTS = {
    "ugc_creative_agent",
    "paid_ads_agent",
    "product_image_agent",
    "social_media_manager_content_creator_agent",
    "brand_strategy_agent",
    "marketing_specialist_agent",
    "website_landing_apps_agent",
    "influencer_collaboration_agent",
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _provider_env_present(names: List[str]) -> bool:
    return any(bool(os.getenv(name, "").strip()) for name in names)


def _voiceover_script(task: str, agent_id: str) -> str:
    return f"""Premium voiceover script for {agent_id}

Hook:
Stop scrolling — this is the premium creative your brand has been missing.

Body:
Designed for a polished, conversion-focused campaign, this asset introduces the product with clear visual proof, emotional relevance, and a premium brand feel.

CTA:
Tap to discover the full offer today.
"""


def _video_prompt(task: str, agent_id: str) -> str:
    return f"""Premium short-form video generation prompt for {agent_id}

Create a cinematic 9:16 social ad with premium lighting, clean camera motion, realistic product/creator framing, polished commercial pacing, and conversion-focused scene progression.

Task context:
{task}

Required sequence:
1. Hook frame within first 2 seconds.
2. Product or offer reveal.
3. Lifestyle/benefit demonstration.
4. Proof or transformation moment.
5. Strong CTA end frame.

Style:
Premium, realistic, agency-grade, brand-safe, high-conversion.
"""


def _avatar_prompt(task: str, agent_id: str) -> str:
    return f"""Avatar/presenter video prompt for {agent_id}

Create a premium presenter-led script with natural delivery, strong lip-sync suitability, clear brand-safe claims, and a confident expert tone.

Task context:
{task}

Presenter style:
Polished, natural, trustworthy, commercially credible.
"""


def generate_creative_media_pack(
    *,
    task: str,
    agent_id: str,
    tenant_id: str = "owner_admin",
    include_image: bool = True,
    include_audio: bool = True,
    include_video: bool = True,
    include_avatar: bool = True,
) -> Dict[str, Any]:
    agent_id = str(agent_id or "").strip() or "creative_agent"
    task = str(task or "").strip()

    pack_id = f"creative_media_pack_{uuid.uuid4().hex[:12]}"

    image_asset = None
    if include_image:
        image_asset = generate_creative_visual_asset(
            prompt=task,
            agent_id=agent_id,
            tenant_id=tenant_id,
            asset_kind=f"{agent_id}_image_asset",
        )

    audio_script = _voiceover_script(task, agent_id) if include_audio else ""
    video_prompt = _video_prompt(task, agent_id) if include_video else ""
    avatar_prompt = _avatar_prompt(task, agent_id) if include_avatar else ""

    provider_stack = recommended_stack_for_task(agent_id, task)

    audio_configured = _provider_env_present(["ELEVENLABS_API_KEY", "HEYGEN_API_KEY"])
    video_configured = _provider_env_present(["RUNWAY_API_KEY", "KLING_API_KEY", "REPLICATE_API_TOKEN"])
    avatar_configured = _provider_env_present(["HEYGEN_API_KEY"])

    generation_jobs = []

    if include_audio:
        generation_jobs.append({
            "job_id": f"audio_job_{uuid.uuid4().hex[:10]}",
            "media_type": "voiceover_audio",
            "status": "ready_for_provider" if audio_configured else "provider_key_missing",
            "preferred_providers": ["elevenlabs", "heygen"],
            "live_generation_available": audio_configured,
            "script": audio_script,
        })

    if include_video:
        generation_jobs.append({
            "job_id": f"video_job_{uuid.uuid4().hex[:10]}",
            "media_type": "short_form_video",
            "status": "ready_for_provider" if video_configured else "provider_key_missing",
            "preferred_providers": ["runway", "kling", "replicate"],
            "live_generation_available": video_configured,
            "prompt": video_prompt,
        })

    if include_avatar:
        generation_jobs.append({
            "job_id": f"avatar_job_{uuid.uuid4().hex[:10]}",
            "media_type": "avatar_video",
            "status": "ready_for_provider" if avatar_configured else "provider_key_missing",
            "preferred_providers": ["heygen"],
            "live_generation_available": avatar_configured,
            "prompt": avatar_prompt,
        })

    return {
        "success": True,
        "media_pack_id": pack_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "supports_image": include_image,
        "supports_audio": include_audio,
        "supports_video": include_video,
        "supports_avatar_video": include_avatar,
        "image_assets": [image_asset] if image_asset else [],
        "audio_assets": [],
        "video_assets": [],
        "avatar_assets": [],
        "audio_url": "",
        "video_url": "",
        "avatar_video_url": "",
        "voiceover_script": audio_script,
        "video_prompt": video_prompt,
        "avatar_prompt": avatar_prompt,
        "generation_jobs": generation_jobs,
        "provider_stack": provider_stack,
        "provider_chain": provider_stack.get("preferred_providers", []) if isinstance(provider_stack, dict) else [],
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }
