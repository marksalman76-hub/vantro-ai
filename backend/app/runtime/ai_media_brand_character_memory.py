from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

DATA_DIR = Path("data") / "ai_media_brand_character_memory"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_EVENTS = DATA_DIR / "memory_events.jsonl"
BRAND_MEMORY = DATA_DIR / "brand_memory.jsonl"
CHARACTER_MEMORY = DATA_DIR / "character_memory.jsonl"
CAMPAIGN_STYLE_MEMORY = DATA_DIR / "campaign_style_memory.jsonl"


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


def ai_media_brand_character_memory_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "ai_media_brand_character_memory",
        "brand_memory_path": str(BRAND_MEMORY),
        "character_memory_path": str(CHARACTER_MEMORY),
        "campaign_style_memory_path": str(CAMPAIGN_STYLE_MEMORY),
        "supports_brand_consistency": True,
        "supports_character_consistency": True,
        "supports_campaign_style_reuse": True,
        "supports_platform_preferences": True,
        "governance_preserved": True,
        "internal_prompt_hidden": True,
        "layout_changes": False,
    }


def save_brand_memory(
    *,
    tenant_id: str,
    brand_name: str,
    brand_colours: Optional[list[str]] = None,
    typography_style: str = "",
    visual_style: str = "",
    product_identity: str = "",
    forbidden_styles: Optional[list[str]] = None,
    region_preferences: Optional[Dict[str, Any]] = None,
    platform_preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    record = {
        "memory_id": f"brand_memory_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "brand_name": brand_name,
        "brand_colours": brand_colours or [],
        "typography_style": typography_style,
        "visual_style": visual_style,
        "product_identity": product_identity,
        "forbidden_styles": forbidden_styles or [],
        "region_preferences": region_preferences or {},
        "platform_preferences": platform_preferences or {},
        "created_at": _now(),
        "governance_preserved": True,
        "internal_prompt_hidden": True,
    }
    _append_jsonl(BRAND_MEMORY, record)
    _append_jsonl(MEMORY_EVENTS, {
        "event_id": f"memory_event_{uuid.uuid4().hex[:16]}",
        "event_type": "brand_memory_saved",
        "tenant_id": tenant_id,
        "memory_id": record["memory_id"],
        "created_at": _now(),
    })
    return {"status": "saved", "brand_memory": record, "layout_changes": False}


def save_character_memory(
    *,
    tenant_id: str,
    character_name: str,
    reference_id: str = "",
    face_consistency_notes: str = "",
    voice_notes: str = "",
    age_range: str = "",
    gender_presentation: str = "",
    ethnicity_or_regional_style: str = "",
    accent_or_language_style: str = "",
    usage_rules: Optional[list[str]] = None,
) -> Dict[str, Any]:
    record = {
        "memory_id": f"character_memory_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "character_name": character_name,
        "reference_id": reference_id,
        "face_consistency_notes": face_consistency_notes,
        "voice_notes": voice_notes,
        "age_range": age_range,
        "gender_presentation": gender_presentation,
        "ethnicity_or_regional_style": ethnicity_or_regional_style,
        "accent_or_language_style": accent_or_language_style,
        "usage_rules": usage_rules or [],
        "same_face_required": bool(reference_id or face_consistency_notes),
        "created_at": _now(),
        "governance_preserved": True,
        "internal_prompt_hidden": True,
    }
    _append_jsonl(CHARACTER_MEMORY, record)
    _append_jsonl(MEMORY_EVENTS, {
        "event_id": f"memory_event_{uuid.uuid4().hex[:16]}",
        "event_type": "character_memory_saved",
        "tenant_id": tenant_id,
        "memory_id": record["memory_id"],
        "created_at": _now(),
    })
    return {"status": "saved", "character_memory": record, "layout_changes": False}


def save_campaign_style_memory(
    *,
    tenant_id: str,
    campaign_name: str,
    target_platform: str,
    media_type: str,
    style_rules: Optional[list[str]] = None,
    winning_hooks: Optional[list[str]] = None,
    winning_visual_patterns: Optional[list[str]] = None,
    avoided_patterns: Optional[list[str]] = None,
    performance_notes: str = "",
) -> Dict[str, Any]:
    record = {
        "memory_id": f"campaign_style_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "campaign_name": campaign_name,
        "target_platform": target_platform,
        "media_type": media_type,
        "style_rules": style_rules or [],
        "winning_hooks": winning_hooks or [],
        "winning_visual_patterns": winning_visual_patterns or [],
        "avoided_patterns": avoided_patterns or [],
        "performance_notes": performance_notes,
        "created_at": _now(),
        "governance_preserved": True,
        "internal_prompt_hidden": True,
    }
    _append_jsonl(CAMPAIGN_STYLE_MEMORY, record)
    _append_jsonl(MEMORY_EVENTS, {
        "event_id": f"memory_event_{uuid.uuid4().hex[:16]}",
        "event_type": "campaign_style_memory_saved",
        "tenant_id": tenant_id,
        "memory_id": record["memory_id"],
        "created_at": _now(),
    })
    return {"status": "saved", "campaign_style_memory": record, "layout_changes": False}


def _latest_for_tenant(path: Path, tenant_id: str, limit: int = 10) -> list[Dict[str, Any]]:
    rows = [r for r in _read_jsonl(path) if r.get("tenant_id") == tenant_id]
    return rows[-limit:]


def get_ai_media_memory_context(
    *,
    tenant_id: str,
    brand_name: str = "",
    target_platform: str = "",
    media_type: str = "",
) -> Dict[str, Any]:
    brand_rows = _latest_for_tenant(BRAND_MEMORY, tenant_id, limit=20)
    character_rows = _latest_for_tenant(CHARACTER_MEMORY, tenant_id, limit=20)
    campaign_rows = _latest_for_tenant(CAMPAIGN_STYLE_MEMORY, tenant_id, limit=20)

    if brand_name:
        exact = [r for r in brand_rows if r.get("brand_name", "").lower() == brand_name.lower()]
        if exact:
            brand_rows = exact

    if target_platform:
        matching_campaigns = [r for r in campaign_rows if r.get("target_platform", "").lower() == target_platform.lower()]
        if matching_campaigns:
            campaign_rows = matching_campaigns

    if media_type:
        matching_media = [r for r in campaign_rows if r.get("media_type", "").lower() == media_type.lower()]
        if matching_media:
            campaign_rows = matching_media

    context = {
        "status": "ok",
        "tenant_id": tenant_id,
        "brand_memory": brand_rows[-5:],
        "character_memory": character_rows[-5:],
        "campaign_style_memory": campaign_rows[-5:],
        "memory_context": {
            "brand_colours": brand_rows[-1].get("brand_colours", []) if brand_rows else [],
            "visual_style": brand_rows[-1].get("visual_style", "") if brand_rows else "",
            "product_identity": brand_rows[-1].get("product_identity", "") if brand_rows else "",
            "character_reference": character_rows[-1].get("reference_id", "") if character_rows else "",
            "same_face_required": bool(character_rows[-1].get("same_face_required")) if character_rows else False,
            "platform_style_rules": campaign_rows[-1].get("style_rules", []) if campaign_rows else [],
            "winning_hooks": campaign_rows[-1].get("winning_hooks", []) if campaign_rows else [],
            "winning_visual_patterns": campaign_rows[-1].get("winning_visual_patterns", []) if campaign_rows else [],
            "avoided_patterns": campaign_rows[-1].get("avoided_patterns", []) if campaign_rows else [],
        },
        "governance_preserved": True,
        "internal_prompt_hidden": True,
        "layout_changes": False,
    }
    return context


def enrich_ai_media_payload_with_memory(
    *,
    tenant_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    context = get_ai_media_memory_context(
        tenant_id=tenant_id,
        brand_name=str(payload.get("brand_name", "")),
        target_platform=str(payload.get("target_platform", "")),
        media_type=str(payload.get("media_type", "")),
    )
    memory_context = context["memory_context"]

    enriched_payload = {
        **payload,
        "brand_colours": payload.get("brand_colours") or memory_context.get("brand_colours", []),
        "requested_style": payload.get("requested_style") or memory_context.get("visual_style", ""),
        "character_reference": payload.get("character_reference") or memory_context.get("character_reference", ""),
        "memory_style_rules": memory_context.get("platform_style_rules", []),
        "memory_winning_hooks": memory_context.get("winning_hooks", []),
        "memory_winning_visual_patterns": memory_context.get("winning_visual_patterns", []),
        "memory_avoided_patterns": memory_context.get("avoided_patterns", []),
        "memory_product_identity": memory_context.get("product_identity", ""),
    }

    return {
        "status": "enriched",
        "tenant_id": tenant_id,
        "payload": enriched_payload,
        "memory_context": memory_context,
        "governance_preserved": True,
        "internal_prompt_hidden": True,
        "layout_changes": False,
    }


def list_ai_media_memory(
    *,
    tenant_id: Optional[str] = None,
    memory_type: str = "all",
    limit: int = 50,
) -> Dict[str, Any]:
    rows: list[Dict[str, Any]] = []

    if memory_type in {"all", "brand"}:
        rows.extend([{**r, "memory_type": "brand"} for r in _read_jsonl(BRAND_MEMORY)])
    if memory_type in {"all", "character"}:
        rows.extend([{**r, "memory_type": "character"} for r in _read_jsonl(CHARACTER_MEMORY)])
    if memory_type in {"all", "campaign"}:
        rows.extend([{**r, "memory_type": "campaign"} for r in _read_jsonl(CAMPAIGN_STYLE_MEMORY)])

    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]

    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "memory": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
