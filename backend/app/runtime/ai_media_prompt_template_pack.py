from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

DATA_DIR = Path("data") / "ai_media_prompt_templates"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_EVENTS = DATA_DIR / "template_events.jsonl"
RENDERED_PROMPTS = DATA_DIR / "rendered_prompts.jsonl"


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


AI_MEDIA_PROMPT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "ugc_video_ad": {
        "category": "video",
        "best_for": ["TikTok", "Instagram Reels", "Meta Ads", "YouTube Shorts"],
        "required_fields": ["brand_name", "product_or_offer", "target_platform", "audience", "benefit", "cta"],
        "template": (
            "Create a premium realistic UGC video ad for {brand_name}. "
            "Product/offer: {product_or_offer}. Target audience: {audience}. Platform: {target_platform}. "
            "Open with a 2-second scroll-stopping hook: {hook}. Show a believable creator using or explaining the product. "
            "Demonstrate the key benefit: {benefit}. Include proof or credibility: {proof}. "
            "Use natural creator pacing, mobile-safe framing, realistic expressions, smooth motion, and clean lighting. "
            "End with the call-to-action: {cta}. Keep claims safe and customer-facing. "
            "Brand style: {brand_style}. Brand colours: {brand_colours}. Region/language: {region}."
        ),
    },
    "product_hero_image": {
        "category": "image",
        "best_for": ["Shopify", "Landing Page", "Meta Ads", "Website Hero"],
        "required_fields": ["brand_name", "product_or_offer", "brand_colours", "visual_style"],
        "template": (
            "Create a premium commercial product hero image for {brand_name}. "
            "Product: {product_or_offer}. Visual style: {visual_style}. "
            "Use brand colours: {brand_colours}. Lighting: premium soft studio lighting with crisp product detail. "
            "Composition: clean ecommerce hero layout, high perceived value, conversion-focused product clarity, no clutter. "
            "Background: {background_direction}. Include subtle lifestyle cues if appropriate. "
            "Avoid cheap stock-photo styling, distorted packaging, unreadable labels, and off-brand colours."
        ),
    },
    "shopify_product_media": {
        "category": "image",
        "best_for": ["Shopify PDP", "Collection Page", "Product Gallery"],
        "required_fields": ["brand_name", "product_or_offer", "product_identity"],
        "template": (
            "Create Shopify-ready product media for {brand_name}. Product: {product_or_offer}. "
            "Product identity: {product_identity}. Generate a clean product gallery direction with: "
            "1) main hero product shot, 2) lifestyle use-case shot, 3) close-up texture/detail shot, "
            "4) benefit-led visual proof shot. Keep images consistent in lighting, colour, composition, and brand quality. "
            "Use ecommerce-safe framing, avoid misleading claims, and preserve accurate product appearance."
        ),
    },
    "meta_ad_creative": {
        "category": "image_video",
        "best_for": ["Meta Ads", "Instagram", "Facebook"],
        "required_fields": ["brand_name", "product_or_offer", "audience", "hook", "benefit", "cta"],
        "template": (
            "Create a high-converting Meta ad creative for {brand_name}. Product/offer: {product_or_offer}. "
            "Audience: {audience}. Creative angle: {angle}. Hook: {hook}. Key benefit: {benefit}. "
            "Visual direction: mobile-first, clear focal point, strong contrast, brand-safe colours {brand_colours}. "
            "Use a conversion-focused structure: hook, problem, solution, proof, CTA. CTA: {cta}. "
            "Keep text minimal and readable, and avoid exaggerated or non-compliant claims."
        ),
    },
    "cinematic_video_scene": {
        "category": "video",
        "best_for": ["Runway", "Kling", "Veo", "Sora", "WAN"],
        "required_fields": ["brand_name", "scene_goal", "visual_style", "camera_direction"],
        "template": (
            "Create a cinematic video scene for {brand_name}. Scene goal: {scene_goal}. "
            "Visual style: {visual_style}. Camera direction: {camera_direction}. "
            "Shot design: opening establishing frame, product/subject emphasis, movement beat, emotional payoff, end frame. "
            "Lighting: {lighting}. Motion: smooth, realistic, physically believable. "
            "Colour grade: {colour_grade}. Pacing: {pacing}. Keep the result premium, realistic, and commercially usable."
        ),
    },
    "voiceover_audio_script": {
        "category": "audio",
        "best_for": ["ElevenLabs", "HeyGen", "WAN", "Dubbing"],
        "required_fields": ["brand_name", "product_or_offer", "tone", "language", "cta"],
        "template": (
            "Write a studio-quality voiceover script for {brand_name}. Product/offer: {product_or_offer}. "
            "Language/accent: {language}. Tone: {tone}. Duration: {duration}. "
            "Structure: hook, relatable problem, product benefit, proof, CTA. CTA: {cta}. "
            "Keep the script natural, conversational, and suitable for lip-sync or dubbing. "
            "Avoid robotic phrasing and unsupported claims."
        ),
    },
    "multilingual_dubbing": {
        "category": "audio_video",
        "best_for": ["HeyGen", "ElevenLabs", "WAN"],
        "required_fields": ["source_language", "target_language", "brand_name", "tone"],
        "template": (
            "Create a multilingual dubbing direction for {brand_name}. Source language: {source_language}. "
            "Target language: {target_language}. Tone: {tone}. Region: {region}. "
            "Preserve meaning, emotional pacing, speaker intent, and conversion intent. "
            "Adapt idioms for the target market. Maintain natural mouth timing and lip-sync suitability. "
            "Do not expose internal translation notes in the customer-facing output."
        ),
    },
    "avatar_lip_sync": {
        "category": "avatar_video",
        "best_for": ["HeyGen", "WAN", "Avatar Video"],
        "required_fields": ["brand_name", "character_reference", "script", "voice_style"],
        "template": (
            "Create an avatar/lip-sync video direction for {brand_name}. Character reference: {character_reference}. "
            "Voice style: {voice_style}. Script: {script}. "
            "Maintain same-face consistency, realistic expression timing, natural blinking, accurate lip-sync, and premium lighting. "
            "Use platform-safe framing and brand-consistent wardrobe/background. Avoid uncanny movement and distorted facial features."
        ),
    },
}


def ai_media_prompt_template_pack_readiness() -> Dict[str, Any]:
    categories = sorted({v["category"] for v in AI_MEDIA_PROMPT_TEMPLATES.values()})
    return {
        "status": "ready",
        "runtime": "ai_media_prompt_template_pack",
        "template_count": len(AI_MEDIA_PROMPT_TEMPLATES),
        "categories": categories,
        "supports_ugc_video_ads": True,
        "supports_product_hero_images": True,
        "supports_shopify_media": True,
        "supports_meta_tiktok_ads": True,
        "supports_cinematic_video": True,
        "supports_audio_voiceover": True,
        "supports_multilingual_dubbing": True,
        "supports_avatar_lip_sync": True,
        "governance_preserved": True,
        "layout_changes": False,
    }


def list_ai_media_prompt_templates(category: Optional[str] = None) -> Dict[str, Any]:
    templates = []
    for template_id, config in AI_MEDIA_PROMPT_TEMPLATES.items():
        if category and config["category"] != category:
            continue
        templates.append({"template_id": template_id, **config})
    return {
        "status": "ok",
        "count": len(templates),
        "templates": templates,
        "governance_preserved": True,
        "layout_changes": False,
    }


def _safe_context_value(context: Dict[str, Any], key: str) -> str:
    value = context.get(key, "")
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def render_ai_media_prompt_template(
    *,
    tenant_id: str,
    template_id: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    template = AI_MEDIA_PROMPT_TEMPLATES.get(template_id)
    if not template:
        return {
            "status": "not_found",
            "reason": "template_not_registered",
            "template_id": template_id,
            "governance_preserved": True,
            "layout_changes": False,
        }

    missing = [field for field in template["required_fields"] if not context.get(field)]

    safe_context = {
        "brand_name": _safe_context_value(context, "brand_name") or "the brand",
        "product_or_offer": _safe_context_value(context, "product_or_offer") or "the product",
        "target_platform": _safe_context_value(context, "target_platform") or "the target platform",
        "audience": _safe_context_value(context, "audience") or "the target audience",
        "benefit": _safe_context_value(context, "benefit") or "the main benefit",
        "cta": _safe_context_value(context, "cta") or "Shop now",
        "hook": _safe_context_value(context, "hook") or "Here is why people are paying attention",
        "proof": _safe_context_value(context, "proof") or "clear product proof",
        "brand_style": _safe_context_value(context, "brand_style") or _safe_context_value(context, "visual_style") or "premium ecommerce style",
        "brand_colours": _safe_context_value(context, "brand_colours") or "brand-safe premium colours",
        "region": _safe_context_value(context, "region") or "global",
        "visual_style": _safe_context_value(context, "visual_style") or "premium commercial style",
        "background_direction": _safe_context_value(context, "background_direction") or "clean premium studio background",
        "product_identity": _safe_context_value(context, "product_identity") or "accurate product identity",
        "angle": _safe_context_value(context, "angle") or "conversion-focused product benefit",
        "scene_goal": _safe_context_value(context, "scene_goal") or "create a premium commercial scene",
        "camera_direction": _safe_context_value(context, "camera_direction") or "smooth cinematic camera movement",
        "lighting": _safe_context_value(context, "lighting") or "soft premium lighting",
        "colour_grade": _safe_context_value(context, "colour_grade") or "brand-consistent cinematic grade",
        "pacing": _safe_context_value(context, "pacing") or "fast hook with clear conversion pacing",
        "tone": _safe_context_value(context, "tone") or "natural, confident, premium",
        "language": _safe_context_value(context, "language") or "English",
        "duration": _safe_context_value(context, "duration") or "20-30 seconds",
        "source_language": _safe_context_value(context, "source_language") or "English",
        "target_language": _safe_context_value(context, "target_language") or "English",
        "character_reference": _safe_context_value(context, "character_reference") or "provided creator/avatar reference",
        "script": _safe_context_value(context, "script") or "Use the approved customer-facing script.",
        "voice_style": _safe_context_value(context, "voice_style") or "natural creator voice",
    }

    prompt = template["template"].format(**safe_context)

    rendered = {
        "render_id": f"rendered_prompt_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "template_id": template_id,
        "category": template["category"],
        "best_for": template["best_for"],
        "required_fields": template["required_fields"],
        "missing_fields": missing,
        "prompt": prompt,
        "status": "ready" if not missing else "needs_context",
        "created_at": _now(),
        "governance_preserved": True,
        "internal_prompt_hidden": True,
        "layout_changes": False,
    }

    _append_jsonl(RENDERED_PROMPTS, rendered)
    _append_jsonl(TEMPLATE_EVENTS, {
        "event_id": f"template_event_{uuid.uuid4().hex[:16]}",
        "event_type": "prompt_template_rendered",
        "tenant_id": tenant_id,
        "template_id": template_id,
        "status": rendered["status"],
        "created_at": _now(),
    })

    return rendered


def recommend_ai_media_prompt_template(
    *,
    media_type: str,
    target_platform: str = "",
    objective: str = "",
) -> Dict[str, Any]:
    raw = " ".join([media_type, target_platform, objective]).lower()

    if "avatar" in raw or "lip" in raw:
        recommended = "avatar_lip_sync"
    elif "dub" in raw or "translate" in raw or "multilingual" in raw:
        recommended = "multilingual_dubbing"
    elif "voice" in raw or "audio" in raw:
        recommended = "voiceover_audio_script"
    elif "cinematic" in raw or "scene" in raw or "film" in raw:
        recommended = "cinematic_video_scene"
    elif "shopify" in raw or "product page" in raw or "gallery" in raw:
        recommended = "shopify_product_media"
    elif "hero" in raw or "product image" in raw:
        recommended = "product_hero_image"
    elif "meta" in raw or "facebook" in raw or "instagram" in raw:
        recommended = "meta_ad_creative"
    elif "ugc" in raw or "tiktok" in raw or "reels" in raw:
        recommended = "ugc_video_ad"
    else:
        recommended = "ugc_video_ad" if "video" in raw else "product_hero_image"

    return {
        "status": "ok",
        "recommended_template_id": recommended,
        "template": AI_MEDIA_PROMPT_TEMPLATES[recommended],
        "governance_preserved": True,
        "layout_changes": False,
    }


def list_rendered_ai_media_prompts(
    *,
    tenant_id: Optional[str] = None,
    template_id: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(RENDERED_PROMPTS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if template_id:
        rows = [r for r in rows if r.get("template_id") == template_id]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "rendered_prompts": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
