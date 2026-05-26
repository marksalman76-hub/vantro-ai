from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE = RUNTIME_DIR / "ai_media_end_to_end_pipeline.py"
TEST_FILE = ROOT / "test_ai_media_end_to_end_pipeline.py"
IMPORT_TEST = ROOT / "test_ai_media_end_to_end_pipeline_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_ai_media_end_to_end_pipeline_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

PIPELINE.write_text(r'''
from __future__ import annotations

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
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.ai_media_end_to_end_pipeline import ai_media_end_to_end_pipeline_readiness, list_ai_media_pipeline_runs, run_ai_media_end_to_end_pipeline\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/ai-media-pipeline/readiness")
def admin_ai_media_end_to_end_pipeline_readiness():
    return ai_media_end_to_end_pipeline_readiness()


@app.post("/admin/ai-media-pipeline/run")
def admin_run_ai_media_end_to_end_pipeline(payload: dict):
    return run_ai_media_end_to_end_pipeline(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "ugc video")),
        objective=str(payload.get("objective", "Create premium commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "TikTok")),
        region=str(payload.get("region", "global")),
        audience=str(payload.get("audience", "")),
        benefit=str(payload.get("benefit", "")),
        cta=str(payload.get("cta", "Shop now")),
        requested_style=str(payload.get("requested_style", "")),
        preferred_provider=str(payload.get("preferred_provider", "")),
        owner_approved=bool(payload.get("owner_approved", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        context=dict(payload.get("context", {})),
    )


@app.get("/admin/ai-media-pipeline/runs")
def admin_list_ai_media_pipeline_runs(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_pipeline_runs(tenant_id=tenant_id, status=status, limit=limit)
'''

if "/admin/ai-media-pipeline/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.ai_media_brand_character_memory import (
    save_brand_memory,
    save_campaign_style_memory,
    save_character_memory,
)
from backend.app.runtime.ai_media_end_to_end_pipeline import (
    ai_media_end_to_end_pipeline_readiness,
    list_ai_media_pipeline_runs,
    run_ai_media_end_to_end_pipeline,
)


def main():
    readiness = ai_media_end_to_end_pipeline_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_memory_to_template_to_provider_packet"] is True
    assert readiness["layout_changes"] is False

    save_brand_memory(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        brand_colours=["#111827", "#C8A96A"],
        visual_style="cinematic realistic ecommerce studio style",
        product_identity="Premium skincare serum",
    )

    save_character_memory(
        tenant_id="tenant_pipeline",
        character_name="Primary Creator",
        reference_id="creator_reference_pipeline",
        face_consistency_notes="Keep same face across assets.",
        voice_notes="Warm confident creator voice.",
    )

    save_campaign_style_memory(
        tenant_id="tenant_pipeline",
        campaign_name="Serum Launch",
        target_platform="TikTok",
        media_type="ugc video",
        style_rules=["fast hook", "close-up product shot", "natural creator scene"],
        winning_hooks=["My skin looked dull until I tried this"],
        winning_visual_patterns=["texture close-up", "creator proof shot"],
    )

    result = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        media_type="ugc video",
        objective="Create a premium conversion ad for skincare buyers",
        product_or_offer="Hydrating serum",
        target_platform="TikTok",
        region="United States",
        audience="busy skincare buyers",
        benefit="hydrated-looking skin",
        cta="Shop now",
        requested_style="cinematic realistic creator ad",
        preferred_provider="runway",
        owner_approved=True,
        entitlement_active=True,
        live_keys_available=False,
        context={
            "hook": "My skin looked dull until I tried this",
            "proof": "visible glow after application",
        },
    )

    assert result["status"] in {"prepared", "ready_for_provider_execution"}
    assert result["memory_enrichment"]["status"] == "enriched"
    assert result["rendered_prompt"]["status"] == "ready"
    assert result["quality_gate"]["provider_execution_allowed"] is True
    assert result["multi_provider_packet"]["active_provider"] == "runway"
    assert result["adapter_payload"]["status"] == "prepared"
    assert result["layout_changes"] is False

    blocked = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_pipeline",
        brand_name="Pipeline Brand",
        media_type="image",
        objective="Create image",
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_ai_media_pipeline_runs(tenant_id="tenant_pipeline")
    assert listed["count"] >= 1

    print("AI_MEDIA_END_TO_END_PIPELINE_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-pipeline/readiness",
        "/admin/ai-media-pipeline/run",
        "/admin/ai-media-pipeline/runs",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_END_TO_END_PIPELINE_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("AI_MEDIA_END_TO_END_PIPELINE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {PIPELINE}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/ai-media-pipeline/readiness")
print("/admin/ai-media-pipeline/run")
print("/admin/ai-media-pipeline/runs")