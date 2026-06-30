from __future__ import annotations

from typing import Any, Dict


VIDEO_PROVIDER = "higgsfield"
IMAGE_PROVIDER = "nano_banana"

VIDEO_MODELS = {
    "Kling 3.0 Turbo": {
        "provider": VIDEO_PROVIDER,
        "model": "Kling 3.0 Turbo",
        "quality": "720p",
        "capability": "video_generation",
    },
    "Kling 3.0": {
        "provider": VIDEO_PROVIDER,
        "model": "Kling 3.0",
        "quality": "1080p",
        "capability": "video_generation",
    },
    "Cinema Studio 4K": {
        "provider": VIDEO_PROVIDER,
        "model": "Cinema Studio 4K",
        "quality": "4K",
        "capability": "video_generation",
    },
}

IMAGE_MODELS = {
    "Nano Banana 2": {
        "provider": IMAGE_PROVIDER,
        "model": "Nano Banana 2",
        "tier": "standard",
        "capability": "image_generation",
    },
    "Nano Banana Pro": {
        "provider": IMAGE_PROVIDER,
        "model": "Nano Banana Pro",
        "tier": "pro",
        "capability": "image_generation",
    },
}

AGENT_CREATIVE_MODEL_ACCESS: dict[str, dict[str, list[str]]] = {
    "ugc_media_agent": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0"],
        "image": ["Nano Banana 2"],
    },
    "ugc_creative_agent": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
    "product_image_agent": {
        "video": [],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
    "ad_creative_agent": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0"],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
    "creative_rotation_agent": {
        "video": ["Kling 3.0 Turbo"],
        "image": ["Nano Banana 2"],
    },
    "social_media_content_agent": {
        "video": ["Kling 3.0 Turbo"],
        "image": ["Nano Banana 2"],
    },
    "ads_optimisation_agent": {
        "video": [],
        "image": ["Nano Banana 2"],
    },
}

PACKAGE_CREATIVE_MODEL_ACCESS: dict[str, dict[str, list[str]]] = {
    "starter": {
        "video": ["Kling 3.0 Turbo"],
        "image": ["Nano Banana 2"],
    },
    "growth": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0"],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
    "business": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
    "enterprise": {
        "video": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
        "image": ["Nano Banana 2", "Nano Banana Pro"],
    },
}


def normalize_package_tier(package_tier: Any) -> str:
    tier = str(package_tier or "enterprise").strip().lower()
    return tier if tier in PACKAGE_CREATIVE_MODEL_ACCESS else "starter"


def allowed_models_for_agent(agent_id: str) -> dict[str, list[str]]:
    policy = AGENT_CREATIVE_MODEL_ACCESS.get(str(agent_id or "").strip(), {})
    return {
        "video": list(policy.get("video", [])),
        "image": list(policy.get("image", [])),
    }


def allowed_models_for_package(package_tier: Any, *, admin_override: bool = False) -> dict[str, list[str]]:
    tier = "enterprise" if admin_override else normalize_package_tier(package_tier)
    policy = PACKAGE_CREATIVE_MODEL_ACCESS[tier]
    return {
        "video": list(policy.get("video", [])),
        "image": list(policy.get("image", [])),
    }


def effective_allowed_models(
    agent_id: str,
    package_tier: Any = "enterprise",
    *,
    admin_override: bool = False,
) -> dict[str, Any]:
    agent_allowed = allowed_models_for_agent(agent_id)
    package_allowed = allowed_models_for_package(package_tier, admin_override=admin_override)
    effective = {
        media_type: [model for model in agent_allowed[media_type] if model in package_allowed[media_type]]
        for media_type in ("video", "image")
    }
    return {
        "agent_allowed": agent_allowed,
        "package_allowed": package_allowed,
        "effective": effective,
        "package_tier": "enterprise" if admin_override else normalize_package_tier(package_tier),
        "admin_override": bool(admin_override),
        "credential_values_exposed": False,
    }


def creative_capability_policy_status() -> Dict[str, Any]:
    return {
        "success": True,
        "agent_model_access": {
            agent_id: allowed_models_for_agent(agent_id)
            for agent_id in sorted(AGENT_CREATIVE_MODEL_ACCESS)
        },
        "package_model_access": {
            tier: {
                "video": list(policy["video"]),
                "image": list(policy["image"]),
            }
            for tier, policy in PACKAGE_CREATIVE_MODEL_ACCESS.items()
        },
        "credential_values_exposed": False,
    }
