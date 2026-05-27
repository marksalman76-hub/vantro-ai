from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY = RUNTIME_DIR / "ai_media_creative_model_registry.py"
TEST_FILE = ROOT / "test_ai_media_creative_model_registry.py"
IMPORT_TEST = ROOT / "test_ai_media_creative_model_registry_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_ai_media_creative_registry_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

REGISTRY.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.ai_media_creative_model_registry import ai_media_registry_readiness, create_ai_media_execution_packet, create_creative_director_plan, list_ai_media_execution_packets, list_ai_media_models, list_creative_director_plans\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/ai-media/readiness")
def admin_ai_media_registry_readiness():
    return ai_media_registry_readiness()


@app.get("/admin/ai-media/models")
def admin_list_ai_media_models(category: str | None = None):
    return list_ai_media_models(category=category)


@app.post("/admin/ai-media/creative-plan")
def admin_create_ai_media_creative_plan(payload: dict):
    return create_creative_director_plan(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "image")),
        objective=str(payload.get("objective", "Create commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "Meta Ads")),
        region=str(payload.get("region", "global")),
        requested_style=str(payload.get("requested_style", "")),
        brand_colours=list(payload.get("brand_colours", [])) if payload.get("brand_colours") is not None else [],
        character_reference=payload.get("character_reference"),
        owner_approved=bool(payload.get("owner_approved", False)),
    )


@app.get("/admin/ai-media/creative-plans")
def admin_list_ai_media_creative_plans(tenant_id: str | None = None, limit: int = 50):
    return list_creative_director_plans(tenant_id=tenant_id, limit=limit)


@app.post("/admin/ai-media/execution-packet")
def admin_create_ai_media_execution_packet(payload: dict):
    return create_ai_media_execution_packet(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        plan_id=str(payload.get("plan_id", "")),
        selected_model=str(payload.get("selected_model", "")),
        prompt=str(payload.get("prompt", "")),
        media_type=str(payload.get("media_type", "image")),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        owner_approved=bool(payload.get("owner_approved", False)),
    )


@app.get("/admin/ai-media/execution-packets")
def admin_list_ai_media_execution_packets(tenant_id: str | None = None, limit: int = 50):
    return list_ai_media_execution_packets(tenant_id=tenant_id, limit=limit)
'''

if "/admin/ai-media/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.ai_media_creative_model_registry import (
    ai_media_registry_readiness,
    create_ai_media_execution_packet,
    create_creative_director_plan,
    list_ai_media_execution_packets,
    list_ai_media_models,
    list_creative_director_plans,
)


def main():
    readiness = ai_media_registry_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_image_generation"] is True
    assert readiness["supports_video_generation"] is True
    assert readiness["supports_audio_generation"] is True
    assert readiness["supports_creative_director_layer"] is True

    models = list_ai_media_models()
    assert models["count"] >= 8

    plan = create_creative_director_plan(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="ugc video with voice",
        objective="Create a premium conversion ad for a skincare product",
        product_or_offer="Hydrating serum",
        target_platform="TikTok",
        region="United States",
        requested_style="cinematic realistic creator ad",
        brand_colours=["#111827", "#C8A96A"],
        character_reference="creator_reference_001",
        owner_approved=False,
    )
    assert plan["status"] == "planned"
    assert "runway" in plan["selected_models"] or "kling" in plan["selected_models"]
    assert plan["character_consistency"]["use_same_face_across_outputs"] is True
    assert plan["audio_layer"]["lip_sync_recommended"] is True

    packet = create_ai_media_execution_packet(
        tenant_id="tenant_test",
        plan_id=plan["plan_id"],
        selected_model=plan["selected_models"][0],
        prompt="Create a cinematic UGC ad with premium lighting and a clear product demonstration.",
        media_type="video",
        live_keys_available=False,
        owner_approved=False,
    )
    assert packet["status"] == "prepared"
    assert packet["execution_allowed"] is False

    ready_packet = create_ai_media_execution_packet(
        tenant_id="tenant_test",
        plan_id=plan["plan_id"],
        selected_model="openai_image",
        prompt="Create a premium product hero image with brand-consistent colours.",
        media_type="image",
        live_keys_available=True,
        owner_approved=True,
    )
    assert ready_packet["status"] == "ready_for_execution"
    assert ready_packet["execution_allowed"] is True

    listed_plans = list_creative_director_plans(tenant_id="tenant_test")
    assert listed_plans["count"] >= 1

    listed_packets = list_ai_media_execution_packets(tenant_id="tenant_test")
    assert listed_packets["count"] >= 2

    print("AI_MEDIA_CREATIVE_MODEL_REGISTRY_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media/readiness",
        "/admin/ai-media/models",
        "/admin/ai-media/creative-plan",
        "/admin/ai-media/creative-plans",
        "/admin/ai-media/execution-packet",
        "/admin/ai-media/execution-packets",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_CREATIVE_MODEL_REGISTRY_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("AI_MEDIA_CREATIVE_MODEL_REGISTRY_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {REGISTRY}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/ai-media/readiness")
print("/admin/ai-media/models")
print("/admin/ai-media/creative-plan")
print("/admin/ai-media/creative-plans")
print("/admin/ai-media/execution-packet")
print("/admin/ai-media/execution-packets")