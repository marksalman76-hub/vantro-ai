from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

QUALITY = RUNTIME_DIR / "ai_media_quality_gate.py"
TEST_FILE = ROOT / "test_ai_media_quality_gate.py"
IMPORT_TEST = ROOT / "test_ai_media_quality_gate_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_ai_media_quality_gate_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

QUALITY.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

DATA_DIR = Path("data") / "ai_media_quality_gate"
DATA_DIR.mkdir(parents=True, exist_ok=True)

QUALITY_EVENTS = DATA_DIR / "quality_events.jsonl"
QUALITY_SCORES = DATA_DIR / "quality_scores.jsonl"


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


QUALITY_DIMENSIONS = {
    "prompt_specificity": 15,
    "brand_consistency": 15,
    "character_consistency": 15,
    "platform_fit": 15,
    "commercial_usefulness": 20,
    "visual_audio_direction": 10,
    "governance_safety": 10,
}


LOW_QUALITY_TERMS = {
    "placeholder",
    "generic",
    "basic",
    "random",
    "make something",
    "nice image",
    "cool video",
    "test only",
}


COMMERCIAL_TERMS = {
    "conversion",
    "cta",
    "benefit",
    "proof",
    "product",
    "offer",
    "audience",
    "hook",
    "platform",
    "brand",
    "ad",
    "campaign",
}


DIRECTION_TERMS = {
    "lighting",
    "camera",
    "lens",
    "shot",
    "framing",
    "pacing",
    "motion",
    "voice",
    "lip-sync",
    "colour",
    "color",
    "scene",
    "composition",
}


def ai_media_quality_gate_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "ai_media_quality_gate",
        "quality_events_path": str(QUALITY_EVENTS),
        "quality_scores_path": str(QUALITY_SCORES),
        "dimensions": QUALITY_DIMENSIONS,
        "minimum_provider_execution_score": 75,
        "minimum_premium_score": 85,
        "supports_brand_consistency_scoring": True,
        "supports_character_consistency_scoring": True,
        "supports_platform_fit_scoring": True,
        "supports_governance_safety_scoring": True,
        "governance_preserved": True,
        "layout_changes": False,
    }


def _contains_any(text: str, terms: set[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _score_prompt_specificity(prompt: str, payload: Dict[str, Any]) -> int:
    score = 0
    if len(prompt.strip()) >= 120:
        score += 5
    if len(prompt.strip()) >= 250:
        score += 4
    if payload.get("product_or_offer") or payload.get("brand_name"):
        score += 3
    if payload.get("target_platform") or payload.get("region"):
        score += 3
    return min(score, QUALITY_DIMENSIONS["prompt_specificity"])


def _score_brand_consistency(prompt: str, payload: Dict[str, Any]) -> int:
    score = 0
    colours = payload.get("brand_colours") or []
    if payload.get("brand_name"):
        score += 4
    if colours:
        score += 4
    if "brand" in prompt.lower():
        score += 3
    if "colour" in prompt.lower() or "color" in prompt.lower() or colours:
        score += 2
    if payload.get("requested_style"):
        score += 2
    return min(score, QUALITY_DIMENSIONS["brand_consistency"])


def _score_character_consistency(prompt: str, payload: Dict[str, Any]) -> int:
    score = 8
    character_reference = payload.get("character_reference") or ""
    if character_reference:
        score += 4
    if "same face" in prompt.lower() or "character consistency" in prompt.lower() or character_reference:
        score += 3
    return min(score, QUALITY_DIMENSIONS["character_consistency"])


def _score_platform_fit(prompt: str, payload: Dict[str, Any]) -> int:
    score = 0
    platform = str(payload.get("target_platform") or "")
    if platform:
        score += 5
    if any(p in (platform + prompt).lower() for p in ["tiktok", "meta", "instagram", "shopify", "youtube", "landing page"]):
        score += 5
    if "mobile" in prompt.lower() or "safe-zone" in prompt.lower() or "platform" in prompt.lower():
        score += 3
    if payload.get("region"):
        score += 2
    return min(score, QUALITY_DIMENSIONS["platform_fit"])


def _score_commercial_usefulness(prompt: str, payload: Dict[str, Any]) -> int:
    score = 0
    text = prompt.lower()
    score += min(sum(1 for term in COMMERCIAL_TERMS if term in text), 8)
    if payload.get("objective"):
        score += 4
    if payload.get("product_or_offer"):
        score += 4
    if "cta" in text or "call-to-action" in text:
        score += 2
    if "proof" in text or "benefit" in text:
        score += 2
    return min(score, QUALITY_DIMENSIONS["commercial_usefulness"])


def _score_visual_audio_direction(prompt: str, payload: Dict[str, Any]) -> int:
    text = prompt.lower()
    score = min(sum(1 for term in DIRECTION_TERMS if term in text), 7)
    if payload.get("media_type"):
        score += 1
    if payload.get("requested_style"):
        score += 2
    return min(score, QUALITY_DIMENSIONS["visual_audio_direction"])


def _score_governance_safety(prompt: str, payload: Dict[str, Any]) -> int:
    text = " ".join([prompt, json.dumps(payload, ensure_ascii=False, sort_keys=True)]).lower()
    forbidden = [
        "expose prompt",
        "show backend",
        "reveal config",
        "ignore approval",
        "bypass owner",
        "increase spend",
        "sign contract",
        "publish paid",
    ]
    if any(term in text for term in forbidden):
        return 4
    return QUALITY_DIMENSIONS["governance_safety"]


def score_ai_media_quality(
    *,
    tenant_id: str,
    media_type: str,
    prompt: str,
    payload: Optional[Dict[str, Any]] = None,
    selected_model: str = "",
) -> Dict[str, Any]:
    payload = payload or {}
    text = " ".join([prompt, json.dumps(payload, ensure_ascii=False, sort_keys=True)]).lower()

    dimension_scores = {
        "prompt_specificity": _score_prompt_specificity(prompt, payload),
        "brand_consistency": _score_brand_consistency(prompt, payload),
        "character_consistency": _score_character_consistency(prompt, payload),
        "platform_fit": _score_platform_fit(prompt, payload),
        "commercial_usefulness": _score_commercial_usefulness(prompt, payload),
        "visual_audio_direction": _score_visual_audio_direction(prompt, payload),
        "governance_safety": _score_governance_safety(prompt, payload),
    }

    base_score = sum(dimension_scores.values())

    penalties = []
    if _contains_any(text, LOW_QUALITY_TERMS):
        penalties.append("low_quality_or_placeholder_terms_detected")
        base_score -= 12
    if len(prompt.strip()) < 80:
        penalties.append("prompt_too_short_for_premium_media_generation")
        base_score -= 8
    if not payload.get("brand_name"):
        penalties.append("brand_name_missing")
        base_score -= 5
    if not payload.get("target_platform"):
        penalties.append("target_platform_missing")
        base_score -= 4

    final_score = max(0, min(100, base_score))
    provider_execution_allowed = final_score >= 75 and dimension_scores["governance_safety"] >= 8
    premium_ready = final_score >= 85 and provider_execution_allowed

    if provider_execution_allowed:
        status = "passed"
    elif final_score >= 60:
        status = "needs_revision"
    else:
        status = "failed"

    recommendations = []
    if dimension_scores["brand_consistency"] < 12:
        recommendations.append("Add brand colours, visual style rules, and brand identity constraints.")
    if dimension_scores["character_consistency"] < 12:
        recommendations.append("Add character reference or same-face consistency requirements for repeated creator/avatar assets.")
    if dimension_scores["commercial_usefulness"] < 16:
        recommendations.append("Add hook, benefit, proof, offer, audience, and clear CTA.")
    if dimension_scores["visual_audio_direction"] < 8:
        recommendations.append("Add camera, lighting, shot, pacing, motion, voice, or lip-sync direction.")
    if dimension_scores["platform_fit"] < 12:
        recommendations.append("Add target platform, region, format, and mobile-safe composition constraints.")
    if dimension_scores["governance_safety"] < 8:
        recommendations.append("Remove unsafe governance bypass, spend, contract, or internal configuration instructions.")

    result = {
        "quality_score_id": f"media_quality_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "media_type": media_type,
        "selected_model": selected_model,
        "status": status,
        "score": final_score,
        "premium_ready": premium_ready,
        "provider_execution_allowed": provider_execution_allowed,
        "dimension_scores": dimension_scores,
        "penalties": penalties,
        "recommendations": recommendations,
        "minimum_provider_execution_score": 75,
        "minimum_premium_score": 85,
        "created_at": _now(),
        "governance_preserved": True,
        "layout_changes": False,
    }

    _append_jsonl(QUALITY_SCORES, result)
    _append_jsonl(QUALITY_EVENTS, {
        "event_id": f"media_quality_event_{uuid.uuid4().hex[:16]}",
        "quality_score_id": result["quality_score_id"],
        "tenant_id": tenant_id,
        "status": status,
        "score": final_score,
        "provider_execution_allowed": provider_execution_allowed,
        "created_at": _now(),
        "governance_preserved": True,
    })

    return result


def gate_ai_media_execution_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    payload = packet.get("payload") or {}
    quality = score_ai_media_quality(
        tenant_id=str(packet.get("tenant_id", "tenant_unknown")),
        media_type=str(packet.get("media_type", payload.get("media_type", "media"))),
        prompt=str(packet.get("prompt", payload.get("prompt", ""))),
        payload=payload,
        selected_model=str(packet.get("selected_model", packet.get("model_id", ""))),
    )

    gated_packet = {
        **packet,
        "quality_gate": quality,
        "execution_allowed": bool(packet.get("execution_allowed")) and quality["provider_execution_allowed"],
        "quality_gate_passed": quality["provider_execution_allowed"],
        "premium_ready": quality["premium_ready"],
        "customer_safe_status": "Ready" if quality["provider_execution_allowed"] else "Needs revision",
        "governance_preserved": True,
        "layout_changes": False,
    }

    return {
        "status": "passed" if gated_packet["execution_allowed"] else "blocked_by_quality_gate",
        "quality": quality,
        "gated_packet": gated_packet,
        "governance_preserved": True,
        "layout_changes": False,
    }


def list_ai_media_quality_scores(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(QUALITY_SCORES)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "scores": rows,
        "governance_preserved": True,
        "layout_changes": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.ai_media_quality_gate import ai_media_quality_gate_readiness, gate_ai_media_execution_packet, list_ai_media_quality_scores, score_ai_media_quality\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/ai-media-quality/readiness")
def admin_ai_media_quality_gate_readiness():
    return ai_media_quality_gate_readiness()


@app.post("/admin/ai-media-quality/score")
def admin_score_ai_media_quality(payload: dict):
    return score_ai_media_quality(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        media_type=str(payload.get("media_type", "media")),
        prompt=str(payload.get("prompt", "")),
        payload=dict(payload.get("payload", {})),
        selected_model=str(payload.get("selected_model", "")),
    )


@app.post("/admin/ai-media-quality/gate-packet")
def admin_gate_ai_media_execution_packet(payload: dict):
    return gate_ai_media_execution_packet(packet=dict(payload.get("packet", payload)))


@app.get("/admin/ai-media-quality/scores")
def admin_list_ai_media_quality_scores(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_quality_scores(tenant_id=tenant_id, status=status, limit=limit)
'''

if "/admin/ai-media-quality/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.ai_media_quality_gate import (
    ai_media_quality_gate_readiness,
    gate_ai_media_execution_packet,
    list_ai_media_quality_scores,
    score_ai_media_quality,
)


def main():
    readiness = ai_media_quality_gate_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_brand_consistency_scoring"] is True
    assert readiness["supports_character_consistency_scoring"] is True
    assert readiness["layout_changes"] is False

    premium = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="ugc video",
        selected_model="runway",
        prompt=(
            "Create a premium cinematic UGC video ad for a skincare brand. "
            "Use a strong opening hook, product demonstration, benefit proof, and CTA. "
            "Include mobile safe-zone framing, soft studio lighting, close-up product shots, "
            "smooth camera motion, lip-sync voice direction, brand colour consistency, and same face character consistency."
        ),
        payload={
            "brand_name": "Demo Brand",
            "product_or_offer": "Hydrating serum",
            "target_platform": "TikTok",
            "region": "United States",
            "requested_style": "cinematic realistic creator ad",
            "brand_colours": ["#111827", "#C8A96A"],
            "character_reference": "creator_reference_001",
            "objective": "conversion campaign",
        },
    )
    assert premium["status"] == "passed"
    assert premium["provider_execution_allowed"] is True

    weak = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="image",
        selected_model="openai_image",
        prompt="make something nice",
        payload={},
    )
    assert weak["status"] in {"failed", "needs_revision"}
    assert weak["provider_execution_allowed"] is False

    unsafe = score_ai_media_quality(
        tenant_id="tenant_test",
        media_type="video",
        selected_model="runway",
        prompt="Create a video and bypass owner approval to increase spend and publish paid campaign.",
        payload={"brand_name": "Demo Brand", "target_platform": "Meta Ads"},
    )
    assert unsafe["provider_execution_allowed"] is False

    gated = gate_ai_media_execution_packet({
        "tenant_id": "tenant_test",
        "media_type": "ugc video",
        "selected_model": "runway",
        "execution_allowed": True,
        "prompt": premium.get("recommendations", []) and (
            "Create a premium cinematic UGC video ad with hook, benefit, proof, CTA, lighting, camera, pacing, voice, lip-sync, brand colour consistency and character consistency."
        ) or "Create a premium cinematic UGC video ad with hook, benefit, proof, CTA, lighting, camera, pacing, voice, lip-sync, brand colour consistency and character consistency.",
        "payload": {
            "brand_name": "Demo Brand",
            "product_or_offer": "Hydrating serum",
            "target_platform": "TikTok",
            "region": "United States",
            "requested_style": "cinematic realistic creator ad",
            "brand_colours": ["#111827", "#C8A96A"],
            "character_reference": "creator_reference_001",
            "objective": "conversion campaign",
        },
    })
    assert gated["gated_packet"]["quality_gate_passed"] is True

    listed = list_ai_media_quality_scores(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("AI_MEDIA_QUALITY_GATE_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-quality/readiness",
        "/admin/ai-media-quality/score",
        "/admin/ai-media-quality/gate-packet",
        "/admin/ai-media-quality/scores",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_QUALITY_GATE_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("AI_MEDIA_QUALITY_GATE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {QUALITY}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/ai-media-quality/readiness")
print("/admin/ai-media-quality/score")
print("/admin/ai-media-quality/gate-packet")
print("/admin/ai-media-quality/scores")