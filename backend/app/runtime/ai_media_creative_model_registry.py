from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid

DATA_DIR = Path("data") / "ai_media_creative"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CREATIVE_REQUESTS = DATA_DIR / "creative_model_requests.jsonl"
CREATIVE_DIRECTOR_PLANS = DATA_DIR / "creative_director_plans.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({
                "record_type": "corrupt_jsonl_line",
                "raw": line,
                "loaded_at": _now(),
            })
    return rows


MEDIA_MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "openai_image": {
        "category": "image",
        "capabilities": ["product_image", "ad_creative", "brand_visual", "lifestyle_scene"],
        "strength": "premium image generation and prompt-following",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
    "google_image": {
        "category": "image",
        "capabilities": ["product_image", "brand_visual", "fast_variations"],
        "strength": "fast visual generation and editing",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
    "flux_kontext": {
        "category": "image",
        "capabilities": ["image_editing", "style_transfer", "brand_consistency"],
        "strength": "context-aware image editing and consistency",
        "requires_key": True,
        "live_execution_mode": "adapter_or_partner_required",
    },
    "replicate": {
        "category": "image_video",
        "capabilities": ["model_marketplace", "image", "video", "specialist_models"],
        "strength": "broad model access and fallback coverage",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
    "runway": {
        "category": "video",
        "capabilities": ["cinematic_video", "image_to_video", "camera_motion"],
        "strength": "commercial video generation workflow",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
    "kling": {
        "category": "video",
        "capabilities": ["realistic_motion", "image_to_video", "text_to_video"],
        "strength": "high-motion realism and creator video",
        "requires_key": True,
        "live_execution_mode": "partner_or_api_required",
    },
    "veo": {
        "category": "video",
        "capabilities": ["cinematic_video", "text_to_video", "visual_storytelling"],
        "strength": "cinematic video generation",
        "requires_key": True,
        "live_execution_mode": "google_access_required",
    },
    "sora": {
        "category": "video",
        "capabilities": ["cinematic_video", "story_video", "world_simulation_style_generation"],
        "strength": "high-end video generation",
        "requires_key": True,
        "live_execution_mode": "openai_access_required",
    },
    "wan": {
        "category": "video_audio",
        "capabilities": ["text_to_video", "image_to_video", "synchronised_audio", "lip_sync"],
        "strength": "video with audio/lip-sync style workflow",
        "requires_key": True,
        "live_execution_mode": "partner_or_api_required",
    },
    "elevenlabs": {
        "category": "audio",
        "capabilities": ["tts", "voice_clone", "dubbing", "voice_replacement"],
        "strength": "high-quality synthetic voice and multilingual audio",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
    "heygen": {
        "category": "avatar_video",
        "capabilities": ["avatar_video", "lip_sync", "multilingual_ugc", "voice_translation"],
        "strength": "avatar and presenter video workflows",
        "requires_key": True,
        "live_execution_mode": "provider_key_required",
    },
}


def ai_media_registry_readiness() -> Dict[str, Any]:
    categories = sorted({item["category"] for item in MEDIA_MODEL_REGISTRY.values()})
    return {
        "status": "ready",
        "runtime": "ai_media_creative_model_registry",
        "model_count": len(MEDIA_MODEL_REGISTRY),
        "categories": categories,
        "supports_image_generation": True,
        "supports_video_generation": True,
        "supports_audio_generation": True,
        "supports_avatar_lip_sync": True,
        "supports_creative_director_layer": True,
        "supports_brand_consistency_layer": True,
        "supports_character_consistency_layer": True,
        "live_provider_keys_required": True,
        "governance_preserved": True,
        "owner_approval_required_for_paid_scaling": True,
        "white_label_ready": True,
    }


def list_ai_media_models(category: Optional[str] = None) -> Dict[str, Any]:
    models = []
    for model_id, config in MEDIA_MODEL_REGISTRY.items():
        if category and config.get("category") != category:
            continue
        models.append({"model_id": model_id, **config})
    return {
        "status": "ok",
        "count": len(models),
        "models": models,
        "governance_preserved": True,
    }


def _select_models_for_request(media_type: str, objective: str, requested_style: str = "") -> List[str]:
    raw = " ".join([media_type, objective, requested_style]).lower()
    selected: List[str] = []

    if "image" in raw or "photo" in raw or "product" in raw or "fashion" in raw:
        selected.extend(["openai_image", "google_image", "flux_kontext", "replicate"])

    if "video" in raw or "ugc" in raw or "cinematic" in raw or "ad" in raw:
        selected.extend(["runway", "kling", "veo", "sora", "wan", "replicate"])

    if "voice" in raw or "audio" in raw or "dub" in raw or "lip" in raw:
        selected.extend(["elevenlabs", "heygen", "wan"])

    if not selected:
        selected.extend(["openai_image", "replicate"])

    unique = []
    for item in selected:
        if item not in unique and item in MEDIA_MODEL_REGISTRY:
            unique.append(item)
    return unique


def create_creative_director_plan(
    *,
    tenant_id: str,
    brand_name: str,
    media_type: str,
    objective: str,
    product_or_offer: str = "",
    target_platform: str = "Meta Ads",
    region: str = "global",
    requested_style: str = "",
    brand_colours: Optional[List[str]] = None,
    character_reference: Optional[str] = None,
    owner_approved: bool = False,
) -> Dict[str, Any]:
    selected_models = _select_models_for_request(media_type, objective, requested_style)
    brand_colours = brand_colours or []

    plan_id = f"creative_plan_{uuid.uuid4().hex[:16]}"

    risk_requires_owner = any(term in objective.lower() for term in [
        "increase spend",
        "scale campaign",
        "publish paid",
        "commit budget",
        "contract",
    ])

    status = "pending_owner_approval" if risk_requires_owner and not owner_approved else "planned"

    plan = {
        "plan_id": plan_id,
        "tenant_id": tenant_id,
        "brand_name": brand_name,
        "media_type": media_type,
        "objective": objective,
        "product_or_offer": product_or_offer,
        "target_platform": target_platform,
        "region": region,
        "requested_style": requested_style,
        "selected_models": selected_models,
        "status": status,
        "creative_director": {
            "narrative_arc": [
                "Hook the viewer with a clear product or pain-point moment.",
                "Show the product/service solving the problem in a believable context.",
                "End with a conversion-focused call-to-action suitable for the platform.",
            ],
            "shot_list": [
                "Opening attention frame",
                "Product/service proof frame",
                "Benefit demonstration frame",
                "Social proof or credibility frame",
                "CTA/end card frame",
            ],
            "camera_direction": {
                "lens_style": "commercial editorial / cinematic social ad",
                "movement": "smooth push-in, controlled handheld, or product orbit depending on platform",
                "framing": "mobile-first safe-zone composition",
                "lighting": "premium soft key light with brand-consistent contrast",
            },
            "pacing": "fast hook, clear mid-section, decisive CTA",
            "visual_emphasis": "product clarity, human believability, brand consistency, conversion intent",
        },
        "brand_consistency": {
            "brand_colours": brand_colours,
            "colour_control_required": bool(brand_colours),
            "style_memory_recommended": True,
            "safe_claims_required": True,
        },
        "character_consistency": {
            "reference_supplied": bool(character_reference),
            "character_reference": character_reference or "",
            "consistency_required": bool(character_reference),
            "use_same_face_across_outputs": bool(character_reference),
        },
        "audio_layer": {
            "tts_recommended": "voice" in media_type.lower() or "video" in media_type.lower(),
            "dubbing_recommended": region.lower() not in {"global", "australia", "us", "usa", "uk"},
            "lip_sync_recommended": "video" in media_type.lower() or "ugc" in media_type.lower(),
        },
        "governance": {
            "owner_approval_required": risk_requires_owner,
            "no_autonomous_spend_or_scaling": True,
            "customer_safe_output_required": True,
            "internal_prompt_hidden": True,
        },
        "created_at": _now(),
    }

    _append_jsonl(CREATIVE_DIRECTOR_PLANS, plan)
    return plan


def create_ai_media_execution_packet(
    *,
    tenant_id: str,
    plan_id: str,
    selected_model: str,
    prompt: str,
    media_type: str,
    live_keys_available: bool = False,
    owner_approved: bool = False,
) -> Dict[str, Any]:
    model = MEDIA_MODEL_REGISTRY.get(selected_model)
    if not model:
        status = "manual_review_required"
        reason = "unsupported_media_model"
        execution_allowed = False
    elif model.get("requires_key") and not live_keys_available:
        status = "prepared"
        reason = "live_provider_key_required_before_external_execution"
        execution_allowed = False
    else:
        status = "ready_for_execution"
        reason = "provider_ready"
        execution_allowed = True

    packet = {
        "packet_id": f"media_packet_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "plan_id": plan_id,
        "selected_model": selected_model,
        "model_config": model,
        "prompt": prompt,
        "media_type": media_type,
        "status": status,
        "reason": reason,
        "execution_allowed": execution_allowed,
        "live_keys_available": live_keys_available,
        "owner_approved": owner_approved,
        "governance_preserved": True,
        "customer_safe_status": "Prepared" if status == "prepared" else "Ready" if execution_allowed else "Needs review",
        "created_at": _now(),
    }

    _append_jsonl(CREATIVE_REQUESTS, packet)
    return packet


def list_creative_director_plans(tenant_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    rows = _read_jsonl(CREATIVE_DIRECTOR_PLANS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    return {
        "status": "ok",
        "count": len(rows[-limit:]),
        "plans": rows[-limit:],
        "governance_preserved": True,
    }


def list_ai_media_execution_packets(tenant_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    rows = _read_jsonl(CREATIVE_REQUESTS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    return {
        "status": "ok",
        "count": len(rows[-limit:]),
        "packets": rows[-limit:],
        "governance_preserved": True,
    }
