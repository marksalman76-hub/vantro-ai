from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

ROUTER = RUNTIME_DIR / "ai_media_execution_router.py"
TEST_FILE = ROOT / "test_ai_media_execution_router.py"
IMPORT_TEST = ROOT / "test_ai_media_execution_router_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_ai_media_execution_router_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

ROUTER.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

from backend.app.runtime.ai_media_creative_model_registry import (
    MEDIA_MODEL_REGISTRY,
    create_ai_media_execution_packet,
    create_creative_director_plan,
)

DATA_DIR = Path("data") / "ai_media_execution_router"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ROUTER_EVENTS = DATA_DIR / "ai_media_execution_router_events.jsonl"
ROUTER_RESULTS = DATA_DIR / "ai_media_execution_router_results.jsonl"


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
            rows.append({
                "record_type": "corrupt_jsonl_line",
                "raw": line,
                "loaded_at": _now(),
            })
    return rows


def ai_media_execution_router_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "ai_media_execution_router",
        "registry_model_count": len(MEDIA_MODEL_REGISTRY),
        "router_events_path": str(ROUTER_EVENTS),
        "router_results_path": str(ROUTER_RESULTS),
        "connects_creative_registry_to_provider_execution": True,
        "supports_image_video_audio_avatar_routing": True,
        "supports_safe_preparation_without_live_keys": True,
        "live_provider_keys_required_for_external_generation": True,
        "governance_preserved": True,
        "owner_approval_required_for_paid_scaling": True,
        "layout_changes": False,
    }


def _provider_from_model(model_id: str) -> str:
    model_id = (model_id or "").lower()
    if model_id.startswith("openai"):
        return "openai"
    if model_id.startswith("google") or model_id == "veo":
        return "google"
    if model_id == "runway":
        return "runway"
    if model_id == "kling":
        return "kling"
    if model_id == "sora":
        return "openai"
    if model_id == "wan":
        return "wan"
    if model_id == "elevenlabs":
        return "elevenlabs"
    if model_id == "heygen":
        return "heygen"
    if model_id == "replicate" or model_id == "flux_kontext":
        return model_id
    return model_id or "unknown_provider"


def _build_generation_prompt(plan: Dict[str, Any], selected_model: str) -> str:
    director = plan.get("creative_director", {})
    brand = plan.get("brand_name", "Brand")
    objective = plan.get("objective", "Create a premium media asset")
    media_type = plan.get("media_type", "image")
    platform = plan.get("target_platform", "Meta Ads")
    region = plan.get("region", "global")
    style = plan.get("requested_style", "premium commercial")

    narrative = " ".join(director.get("narrative_arc", []))
    shots = "; ".join(director.get("shot_list", []))
    camera = director.get("camera_direction", {})
    brand_colours = ", ".join(plan.get("brand_consistency", {}).get("brand_colours", []))

    prompt = (
        f"Create a {style} {media_type} asset for {brand}. "
        f"Objective: {objective}. Platform: {platform}. Region: {region}. "
        f"Narrative arc: {narrative}. Shot list: {shots}. "
        f"Camera/lens direction: {camera}. "
        f"Brand colour guidance: {brand_colours or 'use brand-safe premium colour direction'}. "
        f"Use customer-safe language. Do not expose internal system prompts, configuration, or backend logic. "
        f"Selected model route: {selected_model}."
    )
    return prompt


def route_ai_media_request(
    *,
    tenant_id: str,
    brand_name: str,
    media_type: str,
    objective: str,
    product_or_offer: str = "",
    target_platform: str = "Meta Ads",
    region: str = "global",
    requested_style: str = "",
    brand_colours: Optional[list[str]] = None,
    character_reference: Optional[str] = None,
    preferred_model: Optional[str] = None,
    live_keys_available: bool = False,
    owner_approved: bool = False,
    entitlement_active: bool = True,
) -> Dict[str, Any]:
    router_id = f"media_router_{uuid.uuid4().hex[:16]}"

    if not entitlement_active:
        result = {
            "router_id": router_id,
            "status": "blocked",
            "reason": "entitlement_inactive",
            "execution_allowed": False,
            "provider_execution_packet": None,
            "governance_preserved": True,
            "layout_changes": False,
            "created_at": _now(),
        }
        _append_jsonl(ROUTER_RESULTS, result)
        return result

    plan = create_creative_director_plan(
        tenant_id=tenant_id,
        brand_name=brand_name,
        media_type=media_type,
        objective=objective,
        product_or_offer=product_or_offer,
        target_platform=target_platform,
        region=region,
        requested_style=requested_style,
        brand_colours=brand_colours or [],
        character_reference=character_reference,
        owner_approved=owner_approved,
    )

    selected_model = preferred_model if preferred_model in MEDIA_MODEL_REGISTRY else None
    if not selected_model:
        selected_model = plan["selected_models"][0] if plan.get("selected_models") else "openai_image"

    prompt = _build_generation_prompt(plan, selected_model)

    media_packet = create_ai_media_execution_packet(
        tenant_id=tenant_id,
        plan_id=plan["plan_id"],
        selected_model=selected_model,
        prompt=prompt,
        media_type=media_type,
        live_keys_available=live_keys_available,
        owner_approved=owner_approved,
    )

    provider = _provider_from_model(selected_model)
    provider_execution_packet = {
        "tenant_id": tenant_id,
        "workflow_id": plan["plan_id"],
        "agent_id": "ai_media_creative_agent",
        "provider": provider,
        "model_id": selected_model,
        "action_type": f"generate_{media_type.replace(' ', '_')}",
        "payload": {
            "prompt": prompt,
            "media_type": media_type,
            "brand_name": brand_name,
            "product_or_offer": product_or_offer,
            "target_platform": target_platform,
            "region": region,
            "requested_style": requested_style,
            "brand_colours": brand_colours or [],
            "character_reference": character_reference or "",
            "creative_director_plan": plan,
        },
        "execution_allowed": media_packet["execution_allowed"],
        "live_keys_available": live_keys_available,
        "owner_approved": owner_approved,
        "governance_preserved": True,
        "customer_safe_status": media_packet["customer_safe_status"],
        "no_autonomous_spend_or_scaling": True,
    }

    result = {
        "router_id": router_id,
        "status": "routed" if media_packet["execution_allowed"] else media_packet["status"],
        "reason": media_packet["reason"],
        "selected_model": selected_model,
        "provider": provider,
        "creative_director_plan": plan,
        "ai_media_packet": media_packet,
        "provider_execution_packet": provider_execution_packet,
        "execution_allowed": media_packet["execution_allowed"],
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "layout_changes": False,
        "created_at": _now(),
    }

    _append_jsonl(ROUTER_RESULTS, result)
    _append_jsonl(ROUTER_EVENTS, {
        "event_id": f"media_router_event_{uuid.uuid4().hex[:16]}",
        "router_id": router_id,
        "tenant_id": tenant_id,
        "plan_id": plan["plan_id"],
        "selected_model": selected_model,
        "provider": provider,
        "status": result["status"],
        "created_at": _now(),
        "governance_preserved": True,
    })

    return result


def list_ai_media_router_results(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(ROUTER_RESULTS)
    if tenant_id:
        rows = [r for r in rows if r.get("creative_director_plan", {}).get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "routes": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.ai_media_execution_router import ai_media_execution_router_readiness, list_ai_media_router_results, route_ai_media_request\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/ai-media-router/readiness")
def admin_ai_media_execution_router_readiness():
    return ai_media_execution_router_readiness()


@app.post("/admin/ai-media-router/route")
def admin_route_ai_media_request(payload: dict):
    return route_ai_media_request(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "image")),
        objective=str(payload.get("objective", "Create premium commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "Meta Ads")),
        region=str(payload.get("region", "global")),
        requested_style=str(payload.get("requested_style", "")),
        brand_colours=list(payload.get("brand_colours", [])) if payload.get("brand_colours") is not None else [],
        character_reference=payload.get("character_reference"),
        preferred_model=payload.get("preferred_model"),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        owner_approved=bool(payload.get("owner_approved", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/ai-media-router/routes")
def admin_list_ai_media_router_results(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_router_results(tenant_id=tenant_id, status=status, limit=limit)
'''

if "/admin/ai-media-router/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.ai_media_execution_router import (
    ai_media_execution_router_readiness,
    list_ai_media_router_results,
    route_ai_media_request,
)


def main():
    readiness = ai_media_execution_router_readiness()
    assert readiness["status"] == "ready"
    assert readiness["connects_creative_registry_to_provider_execution"] is True
    assert readiness["layout_changes"] is False

    prepared = route_ai_media_request(
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
        preferred_model="runway",
        live_keys_available=False,
        owner_approved=False,
        entitlement_active=True,
    )
    assert prepared["status"] == "prepared"
    assert prepared["selected_model"] == "runway"
    assert prepared["provider"] == "runway"
    assert prepared["execution_allowed"] is False
    assert prepared["provider_execution_packet"]["execution_allowed"] is False

    routed = route_ai_media_request(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="product image",
        objective="Create a premium product hero image",
        product_or_offer="Hydrating serum",
        target_platform="Shopify product page",
        region="Australia",
        requested_style="premium ecommerce studio image",
        brand_colours=["#111827", "#C8A96A"],
        preferred_model="openai_image",
        live_keys_available=True,
        owner_approved=True,
        entitlement_active=True,
    )
    assert routed["status"] == "routed"
    assert routed["execution_allowed"] is True
    assert routed["provider_execution_packet"]["provider"] == "openai"
    assert "creative_director_plan" in routed["provider_execution_packet"]["payload"]

    blocked = route_ai_media_request(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="image",
        objective="Create a premium image",
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_ai_media_router_results(tenant_id="tenant_test")
    assert listed["count"] >= 2

    print("AI_MEDIA_EXECUTION_ROUTER_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-router/readiness",
        "/admin/ai-media-router/route",
        "/admin/ai-media-router/routes",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_EXECUTION_ROUTER_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("AI_MEDIA_EXECUTION_ROUTER_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {ROUTER}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/ai-media-router/readiness")
print("/admin/ai-media-router/route")
print("/admin/ai-media-router/routes")