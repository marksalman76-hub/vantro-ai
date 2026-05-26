from __future__ import annotations

from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    is_ai_media_relevant_agent,
)

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

from backend.app.runtime.ai_media_brand_character_memory import enrich_ai_media_payload_with_memory
from backend.app.runtime.ai_media_prompt_template_pack import recommend_ai_media_prompt_template, render_ai_media_prompt_template
from backend.app.runtime.ai_media_creative_model_registry import create_creative_director_plan
from backend.app.runtime.ai_media_quality_gate import score_ai_media_quality
from backend.app.runtime.ai_media_multi_provider_execution_packets import create_ai_media_multi_provider_packet
from backend.app.runtime.ai_media_provider_adapters import prepare_provider_payload

DATA_DIR = Path("data") / "ai_media_end_to_end_pipeline"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE_EVENTS = DATA_DIR / "pipeline_events.jsonl"
PIPELINE_RUNS = DATA_DIR / "pipeline_runs.jsonl"


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


def ai_media_end_to_end_pipeline_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "ai_media_end_to_end_pipeline",
        "pipeline_events_path": str(PIPELINE_EVENTS),
        "pipeline_runs_path": str(PIPELINE_RUNS),
        "chain": [
            "brand_character_memory",
            "prompt_template_pack",
            "creative_director_plan",
            "quality_gate",
            "multi_provider_packet",
            "provider_adapter_payload",
        ],
        "supports_memory_to_template_to_provider_packet": True,
        "supports_quality_gated_execution": True,
        "supports_provider_fallback_packet_creation": True,
        "supports_adapter_ready_payload": True,
        "governance_preserved": True,
        "layout_changes": False,
    }


def run_ai_media_end_to_end_pipeline(
    *,
    tenant_id: str,
    brand_name: str,
    media_type: str,
    objective: str,
    product_or_offer: str = "",
    target_platform: str = "TikTok",
    region: str = "global",
    audience: str = "",
    benefit: str = "",
    cta: str = "Shop now",
    requested_style: str = "",
    preferred_provider: str = "",
    owner_approved: bool = False,
    entitlement_active: bool = True,
    live_keys_available: bool = False,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    run_id = f"media_pipeline_{uuid.uuid4().hex[:16]}"
    context = context or {}

    if not entitlement_active:
        result = {
            "run_id": run_id,
            "status": "blocked",
            "reason": "entitlement_inactive",
            "execution_allowed": False,
            "governance_preserved": True,
            "layout_changes": False,
            "created_at": _now(),
        }
        _append_jsonl(PIPELINE_RUNS, result)
        
    if creative_director_result:
        result["creative_direction"] = creative_director_result


    return result

    base_payload = {
        "brand_name": brand_name,
        "media_type": media_type,
        "objective": objective,
        "product_or_offer": product_or_offer,
        "target_platform": target_platform,
        "region": region,
        "audience": audience,
        "benefit": benefit,
        "cta": cta,
        "requested_style": requested_style,
        **context,
    }

    memory_enrichment = enrich_ai_media_payload_with_memory(
        tenant_id=tenant_id,
        payload=base_payload,
    )
    enriched = memory_enrichment.get("payload", base_payload)

    template_recommendation = recommend_ai_media_prompt_template(
        media_type=media_type,
        target_platform=target_platform,
        objective=objective,
    )
    template_id = template_recommendation.get("recommended_template_id", "ugc_video_ad")

    template_context = {
        **enriched,
        "hook": enriched.get("hook") or "Here is why this product is getting attention",
        "proof": enriched.get("proof") or "clear product proof and real-use demonstration",
        "brand_style": enriched.get("requested_style") or enriched.get("visual_style") or requested_style or "premium realistic commercial style",
        "brand_colours": enriched.get("brand_colours", []),
        "visual_style": enriched.get("requested_style") or requested_style or "premium realistic commercial style",
        "background_direction": enriched.get("background_direction", "clean premium environment"),
        "product_identity": enriched.get("memory_product_identity") or enriched.get("product_identity") or product_or_offer,
        "angle": enriched.get("angle") or objective,
        "scene_goal": enriched.get("scene_goal") or objective,
        "camera_direction": enriched.get("camera_direction", "smooth commercial camera movement"),
        "lighting": enriched.get("lighting", "premium soft commercial lighting"),
        "colour_grade": enriched.get("colour_grade", "brand-consistent cinematic grade"),
        "pacing": enriched.get("pacing", "fast hook, clear demonstration, strong CTA"),
        "tone": enriched.get("tone", "natural, confident, premium"),
        "language": enriched.get("language", "English"),
        "duration": enriched.get("duration", "20-30 seconds"),
        "source_language": enriched.get("source_language", "English"),
        "target_language": enriched.get("target_language", "English"),
        "character_reference": enriched.get("character_reference", ""),
        "script": enriched.get("script", ""),
        "voice_style": enriched.get("voice_style", "natural creator voice"),
    }

    rendered_prompt = render_ai_media_prompt_template(
        tenant_id=tenant_id,
        template_id=template_id,
        context=template_context,
    )

    prompt = rendered_prompt.get("prompt", objective)

    creative_plan = create_creative_director_plan(
        tenant_id=tenant_id,
        brand_name=brand_name,
        media_type=media_type,
        objective=objective,
        product_or_offer=product_or_offer,
        target_platform=target_platform,
        region=region,
        requested_style=requested_style or str(enriched.get("requested_style", "")),
        brand_colours=list(enriched.get("brand_colours", [])) if isinstance(enriched.get("brand_colours", []), list) else [],
        character_reference=str(enriched.get("character_reference", "")),
        owner_approved=owner_approved,
    )

    quality = score_ai_media_quality(
        tenant_id=tenant_id,
        media_type=media_type,
        prompt=prompt,
        payload={
            **enriched,
            "brand_name": brand_name,
            "product_or_offer": product_or_offer,
            "target_platform": target_platform,
            "region": region,
            "objective": objective,
            "media_type": media_type,
        },
        selected_model=preferred_provider,
    )

    packet = create_ai_media_multi_provider_packet(
        tenant_id=tenant_id,
        brand_name=brand_name,
        media_type=media_type,
        prompt=prompt,
        target_platform=target_platform,
        preferred_provider=preferred_provider,
        payload={
            **enriched,
            "brand_colours": enriched.get("brand_colours", []),
            "character_reference": enriched.get("character_reference", ""),
            "style_rules": enriched.get("memory_style_rules", []),
            "same_face_required": bool(enriched.get("character_reference")),
            "lip_sync_required": "video" in media_type.lower() or "avatar" in media_type.lower(),
        },
        owner_approved=owner_approved,
        entitlement_active=entitlement_active,
        quality_score=int(quality.get("score", 0)),
        max_attempts=3,
    )

    adapter_payload = prepare_provider_payload(
        provider=str(packet.get("active_provider", preferred_provider or "")),
        media_type=media_type,
        prompt=prompt,
        payload=packet.get("provider_payload", {}),
    )

    execution_allowed = (
        bool(packet.get("execution_allowed"))
        and bool(quality.get("provider_execution_allowed"))
        and bool(adapter_payload.get("execution_allowed") or not live_keys_available)
    )

    status = "ready_for_provider_execution" if execution_allowed and live_keys_available else "prepared"
    if not quality.get("provider_execution_allowed"):
        status = "blocked_by_quality_gate"
    if packet.get("status") == "pending_owner_approval":
        status = "pending_owner_approval"

    result = {
        "run_id": run_id,
        "tenant_id": tenant_id,
        "status": status,
        "execution_allowed": execution_allowed,
        "live_keys_available": live_keys_available,
        "memory_enrichment": memory_enrichment,
        "template_recommendation": template_recommendation,
        "rendered_prompt": rendered_prompt,
        "creative_director_plan": creative_plan,
        "quality_gate": quality,
        "multi_provider_packet": packet,
        "adapter_payload": adapter_payload,
        "customer_safe_status": "Ready" if status == "ready_for_provider_execution" else "Prepared" if status == "prepared" else "Needs review",
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "internal_config_exposed": False,
        "layout_changes": False,
        "created_at": _now(),
    }

    _append_jsonl(PIPELINE_RUNS, result)
    _append_jsonl(PIPELINE_EVENTS, {
        "event_id": f"pipeline_event_{uuid.uuid4().hex[:16]}",
        "event_type": "ai_media_pipeline_completed",
        "run_id": run_id,
        "tenant_id": tenant_id,
        "status": status,
        "quality_score": quality.get("score"),
        "active_provider": packet.get("active_provider"),
        "created_at": _now(),
        "governance_preserved": True,
    })

    return result


def list_ai_media_pipeline_runs(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(PIPELINE_RUNS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "runs": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }



# SHARED AI MEDIA CREATIVE DIRECTOR INTEGRATION
def attach_shared_creative_direction(agent_id: str, payload: dict):
    if not is_ai_media_relevant_agent(agent_id):
        return None

    return run_shared_ai_media_creative_director({
        "agent_id": agent_id,
        "brand_name": payload.get("brand_name"),
        "product_name": payload.get("product_name"),
        "target_audience": payload.get("target_audience"),
        "objective": payload.get("objective"),
        "platform": payload.get("platform"),
        "media_type": payload.get("media_type"),
        "language": payload.get("language"),
        "region": payload.get("region"),
    })
