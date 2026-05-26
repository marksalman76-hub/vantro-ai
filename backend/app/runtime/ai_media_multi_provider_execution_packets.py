from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

DATA_DIR = Path("data") / "ai_media_multi_provider_packets"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PACKET_EVENTS = DATA_DIR / "packet_events.jsonl"
PACKET_RECORDS = DATA_DIR / "execution_packets.jsonl"


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


PROVIDER_FALLBACKS = {
    "image": ["openai", "google", "flux_kontext", "replicate"],
    "product_image": ["openai", "google", "flux_kontext", "replicate"],
    "video": ["runway", "kling", "veo", "sora", "wan", "replicate"],
    "ugc_video": ["runway", "kling", "heygen", "wan", "replicate"],
    "cinematic_video": ["veo", "sora", "runway", "kling", "wan"],
    "audio": ["elevenlabs", "heygen", "wan"],
    "voiceover": ["elevenlabs", "heygen", "wan"],
    "avatar_video": ["heygen", "wan", "runway"],
}


ASPECT_RATIO_MAP = {
    "tiktok": "9:16",
    "instagram reels": "9:16",
    "reels": "9:16",
    "youtube shorts": "9:16",
    "meta ads": "4:5",
    "facebook": "4:5",
    "instagram feed": "4:5",
    "shopify": "1:1",
    "product page": "1:1",
    "website hero": "16:9",
    "landing page": "16:9",
    "youtube": "16:9",
}


RESOLUTION_TARGETS = {
    "9:16": "1080x1920",
    "4:5": "1080x1350",
    "1:1": "1080x1080",
    "16:9": "1920x1080",
    "3:4": "1080x1440",
}


def ai_media_multi_provider_packets_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "ai_media_multi_provider_execution_packets",
        "fallback_categories": sorted(PROVIDER_FALLBACKS.keys()),
        "supports_provider_fallback_chains": True,
        "supports_generation_retry_strategy": True,
        "supports_cinematic_parameter_normalization": True,
        "supports_aspect_ratio_normalization": True,
        "supports_provider_safe_payload_shaping": True,
        "supports_execution_audit_trails": True,
        "governance_preserved": True,
        "layout_changes": False,
    }


def normalize_media_type(media_type: str) -> str:
    raw = (media_type or "").lower().strip()
    if "avatar" in raw:
        return "avatar_video"
    if "ugc" in raw and "video" in raw:
        return "ugc_video"
    if "cinematic" in raw and "video" in raw:
        return "cinematic_video"
    if "video" in raw:
        return "video"
    if "voice" in raw:
        return "voiceover"
    if "audio" in raw:
        return "audio"
    if "product" in raw and "image" in raw:
        return "product_image"
    if "image" in raw or "photo" in raw:
        return "image"
    return "image"


def normalize_aspect_ratio(target_platform: str = "", requested_aspect_ratio: str = "") -> str:
    if requested_aspect_ratio:
        return requested_aspect_ratio
    raw = (target_platform or "").lower().strip()
    for key, aspect in ASPECT_RATIO_MAP.items():
        if key in raw:
            return aspect
    return "9:16" if "video" in raw else "1:1"


def normalize_cinematic_parameters(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "camera_movement": payload.get("camera_movement") or payload.get("camera_direction") or "smooth commercial motion",
        "lens_style": payload.get("lens_style") or "premium editorial lens, natural depth of field",
        "lighting": payload.get("lighting") or "soft premium commercial lighting",
        "colour_grade": payload.get("colour_grade") or payload.get("color_grade") or "brand-consistent cinematic grade",
        "pacing": payload.get("pacing") or "fast hook, clear demonstration, strong end frame",
        "motion_quality": payload.get("motion_quality") or "realistic, stable, physically believable movement",
        "composition": payload.get("composition") or "mobile-safe framing with clear product/subject focus",
    }


def build_provider_fallback_chain(media_type: str, preferred_provider: str = "") -> list[str]:
    category = normalize_media_type(media_type)
    chain = list(PROVIDER_FALLBACKS.get(category, PROVIDER_FALLBACKS["image"]))
    preferred_provider = (preferred_provider or "").strip().lower()
    if preferred_provider:
        chain = [preferred_provider] + [provider for provider in chain if provider != preferred_provider]
    return chain


def build_retry_strategy(
    *,
    max_attempts: int = 3,
    quality_threshold: int = 75,
    fallback_enabled: bool = True,
) -> Dict[str, Any]:
    return {
        "max_attempts": max(1, min(int(max_attempts or 3), 5)),
        "quality_threshold": max(0, min(int(quality_threshold or 75), 100)),
        "fallback_enabled": bool(fallback_enabled),
        "retry_reasons": [
            "provider_timeout",
            "low_quality_score",
            "policy_safe_rewrite_required",
            "provider_unavailable",
            "motion_or_lip_sync_quality_failed",
        ],
        "owner_review_after_failed_attempts": True,
        "dead_letter_after_exhausted_retries": True,
        "governance_preserved": True,
    }


def create_ai_media_multi_provider_packet(
    *,
    tenant_id: str,
    brand_name: str,
    media_type: str,
    prompt: str,
    target_platform: str = "",
    preferred_provider: str = "",
    payload: Optional[Dict[str, Any]] = None,
    owner_approved: bool = False,
    entitlement_active: bool = True,
    quality_score: int = 0,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    payload = payload or {}
    packet_id = f"multi_provider_packet_{uuid.uuid4().hex[:16]}"

    normalized_type = normalize_media_type(media_type)
    aspect_ratio = normalize_aspect_ratio(target_platform, str(payload.get("aspect_ratio", "")))
    resolution_target = RESOLUTION_TARGETS.get(aspect_ratio, "1080x1080")
    fallback_chain = build_provider_fallback_chain(normalized_type, preferred_provider)
    cinematic = normalize_cinematic_parameters(payload)
    retry_strategy = build_retry_strategy(max_attempts=max_attempts, quality_threshold=75, fallback_enabled=True)

    high_risk_terms = ["increase spend", "scale campaign", "publish paid", "sign contract", "commit budget"]
    risky = any(term in " ".join([prompt, json.dumps(payload, ensure_ascii=False)]).lower() for term in high_risk_terms)

    if not entitlement_active:
        status = "blocked"
        reason = "entitlement_inactive"
        execution_allowed = False
    elif risky and not owner_approved:
        status = "pending_owner_approval"
        reason = "owner_approval_required_for_high_risk_action"
        execution_allowed = False
    elif quality_score and quality_score < retry_strategy["quality_threshold"]:
        status = "blocked_by_quality_gate"
        reason = "quality_score_below_execution_threshold"
        execution_allowed = False
    else:
        status = "prepared"
        reason = "ready_for_provider_selection"
        execution_allowed = True

    provider_payload = {
        "prompt": prompt,
        "brand_name": brand_name,
        "media_type": normalized_type,
        "target_platform": target_platform,
        "aspect_ratio": aspect_ratio,
        "resolution_target": resolution_target,
        "cinematic_parameters": cinematic,
        "brand_colours": payload.get("brand_colours", []),
        "character_reference": payload.get("character_reference", ""),
        "style_rules": payload.get("style_rules", []),
        "audio_requirements": payload.get("audio_requirements", {}),
        "lip_sync_required": bool(payload.get("lip_sync_required", False)),
        "same_face_required": bool(payload.get("same_face_required", False) or payload.get("character_reference")),
        "customer_safe_output_required": True,
        "internal_config_exposed": False,
    }

    packet = {
        "packet_id": packet_id,
        "tenant_id": tenant_id,
        "brand_name": brand_name,
        "media_type": media_type,
        "normalized_media_type": normalized_type,
        "target_platform": target_platform,
        "preferred_provider": preferred_provider,
        "provider_fallback_chain": fallback_chain,
        "active_provider": fallback_chain[0] if fallback_chain else "",
        "retry_strategy": retry_strategy,
        "aspect_ratio": aspect_ratio,
        "resolution_target": resolution_target,
        "cinematic_parameters": cinematic,
        "provider_payload": provider_payload,
        "status": status,
        "reason": reason,
        "execution_allowed": execution_allowed,
        "quality_score": quality_score,
        "owner_approved": owner_approved,
        "entitlement_active": entitlement_active,
        "created_at": _now(),
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "internal_config_exposed": False,
        "layout_changes": False,
    }

    _append_jsonl(PACKET_RECORDS, packet)
    _append_jsonl(PACKET_EVENTS, {
        "event_id": f"packet_event_{uuid.uuid4().hex[:16]}",
        "event_type": "multi_provider_packet_created",
        "packet_id": packet_id,
        "tenant_id": tenant_id,
        "active_provider": packet["active_provider"],
        "status": status,
        "created_at": _now(),
        "governance_preserved": True,
    })

    return packet


def advance_packet_to_next_provider(packet: Dict[str, Any], failure_reason: str = "provider_failed") -> Dict[str, Any]:
    chain = list(packet.get("provider_fallback_chain", []))
    current = packet.get("active_provider")

    if current in chain:
        idx = chain.index(current)
        next_provider = chain[idx + 1] if idx + 1 < len(chain) else ""
    else:
        next_provider = chain[0] if chain else ""

    if not next_provider:
        status = "dead_letter_required"
        reason = "fallback_chain_exhausted"
        execution_allowed = False
    else:
        status = "fallback_provider_selected"
        reason = failure_reason
        execution_allowed = bool(packet.get("execution_allowed"))

    updated = {
        **packet,
        "active_provider": next_provider,
        "status": status,
        "reason": reason,
        "last_failure_reason": failure_reason,
        "fallback_advanced_at": _now(),
        "execution_allowed": execution_allowed,
        "governance_preserved": True,
        "layout_changes": False,
    }

    _append_jsonl(PACKET_RECORDS, updated)
    _append_jsonl(PACKET_EVENTS, {
        "event_id": f"packet_event_{uuid.uuid4().hex[:16]}",
        "event_type": "fallback_provider_advanced",
        "packet_id": updated.get("packet_id"),
        "active_provider": next_provider,
        "status": status,
        "failure_reason": failure_reason,
        "created_at": _now(),
    })

    return updated


def list_ai_media_multi_provider_packets(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(PACKET_RECORDS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "packets": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
