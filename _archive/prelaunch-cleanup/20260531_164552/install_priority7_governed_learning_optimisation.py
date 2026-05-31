from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
DATA = ROOT / "data" / "learning"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

LEARNING_FILE = CORE / "governed_learning_optimisation_runtime.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_text = MAIN.read_text(encoding="utf-8")

backup = BACKUPS / f"main_before_priority7_learning_optimisation_{timestamp}.py"
backup.write_text(main_text, encoding="utf-8")

learning_code = r'''
from __future__ import annotations

import json
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


LEARNING_OPTIMISATION_PROFILE = "priority7_governed_learning_optimisation_v1"

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "learning"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTCOME_LOG = DATA_DIR / "governed_outcome_scores.jsonl"
PATTERN_LOG = DATA_DIR / "learning_pattern_memory.jsonl"
COACHING_LOG = DATA_DIR / "agent_coaching_recommendations.jsonl"


OWNER_ONLY_TERMS = [
    "increase spend",
    "increase budget",
    "scale campaign",
    "commit budget",
    "sign contract",
    "purchase",
    "paid collaboration",
    "launch paid ads",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _score_output_quality(payload: Dict[str, Any]) -> int:
    output = str(payload.get("output") or payload.get("result_summary") or payload.get("content") or "")
    score = 70

    if len(output) >= 500:
        score += 10
    if any(term in output.lower() for term in ["specific", "action", "next step", "recommendation", "metric"]):
        score += 8
    if any(term in output.lower() for term in ["region", "currency", "audience", "competitor", "offer"]):
        score += 7
    if any(term in output.lower() for term in ["generic", "placeholder", "todo", "lorem"]):
        score -= 25

    return max(0, min(100, score))


def _confidence_score(payload: Dict[str, Any], quality_score: int) -> int:
    confidence = quality_score

    evidence = payload.get("evidence") or payload.get("supporting_data") or []
    if isinstance(evidence, list) and evidence:
        confidence += 5

    if payload.get("client_context_used") is True:
        confidence += 5

    if payload.get("competitor_context_used") is True:
        confidence += 5

    if payload.get("uncertainty_flag") is True:
        confidence -= 15

    return max(0, min(100, confidence))


def _consequence_score(payload: Dict[str, Any]) -> int:
    text = json.dumps(payload, ensure_ascii=False).lower()
    score = 20

    if any(term in text for term in OWNER_ONLY_TERMS):
        score += 55
    if "publish" in text or "send email" in text or "contact customer" in text:
        score += 25
    if "delete" in text or "refund" in text or "cancel subscription" in text:
        score += 35

    return max(0, min(100, score))


def score_learning_outcome(payload: Dict[str, Any]) -> Dict[str, Any]:
    quality_score = _score_output_quality(payload)
    confidence_score = _confidence_score(payload, quality_score)
    consequence_score = _consequence_score(payload)

    owner_review_required = consequence_score >= 70 or payload.get("owner_review_required") is True

    outcome = {
        "outcome_id": f"outcome_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "profile": LEARNING_OPTIMISATION_PROFILE,
        "tenant_id": str(payload.get("tenant_id") or "unknown"),
        "project_id": str(payload.get("project_id") or payload.get("plan_id") or "unknown"),
        "agent_id": str(payload.get("agent_id") or "unknown"),
        "task_type": str(payload.get("task_type") or payload.get("action_type") or "unknown"),
        "quality_score": quality_score,
        "confidence_score": confidence_score,
        "consequence_score": consequence_score,
        "owner_review_required": owner_review_required,
        "approved_for_autonomous_learning": not owner_review_required,
        "learning_mode": "governed_feedback_optimisation",
        "core_model_retraining_allowed": False,
        "protected_governance_rules_mutable": False,
        "recommendation": (
            "owner_review_required_before_action"
            if owner_review_required else "safe_for_pattern_learning"
        ),
        "signals": {
            "client_context_used": bool(payload.get("client_context_used")),
            "competitor_context_used": bool(payload.get("competitor_context_used")),
            "uncertainty_flag": bool(payload.get("uncertainty_flag")),
        },
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    _append_jsonl(OUTCOME_LOG, outcome)

    return {
        "success": True,
        "learning_profile": LEARNING_OPTIMISATION_PROFILE,
        "outcome": outcome,
        "outcome_persisted": True,
    }


def aggregate_learning_patterns(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    events = _read_jsonl(OUTCOME_LOG, limit=1000)

    agent_scores = defaultdict(list)
    recommendations = Counter()
    high_consequence_agents = Counter()

    for event in events:
        agent_id = str(event.get("agent_id") or "unknown")
        agent_scores[agent_id].append({
            "quality": int(event.get("quality_score") or 0),
            "confidence": int(event.get("confidence_score") or 0),
            "consequence": int(event.get("consequence_score") or 0),
        })
        recommendations[str(event.get("recommendation") or "unknown")] += 1
        if int(event.get("consequence_score") or 0) >= 70:
            high_consequence_agents[agent_id] += 1

    performance = []
    for agent_id, rows in agent_scores.items():
        count = len(rows)
        performance.append({
            "agent_id": agent_id,
            "event_count": count,
            "average_quality_score": round(sum(r["quality"] for r in rows) / count, 2),
            "average_confidence_score": round(sum(r["confidence"] for r in rows) / count, 2),
            "average_consequence_score": round(sum(r["consequence"] for r in rows) / count, 2),
            "high_consequence_count": high_consequence_agents.get(agent_id, 0),
        })

    performance.sort(key=lambda x: (x["average_quality_score"], x["average_confidence_score"]), reverse=True)

    pattern = {
        "pattern_id": f"pattern_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "profile": LEARNING_OPTIMISATION_PROFILE,
        "tenant_id": str(payload.get("tenant_id") or "global"),
        "outcome_event_count": len(events),
        "agent_performance": performance,
        "recommendation_counts": dict(recommendations),
        "top_agents": performance[:5],
        "risk_agents": [p for p in performance if p["high_consequence_count"] > 0],
        "pattern_detection_enabled": True,
        "adaptive_optimisation_enabled": True,
        "governed_learning_only": True,
        "core_model_retraining_allowed": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    _append_jsonl(PATTERN_LOG, pattern)

    return {
        "success": True,
        "learning_profile": LEARNING_OPTIMISATION_PROFILE,
        "pattern": pattern,
        "pattern_persisted": True,
    }


def generate_agent_coaching_recommendations(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    patterns = _read_jsonl(PATTERN_LOG, limit=100)
    latest = patterns[-1] if patterns else aggregate_learning_patterns(payload).get("pattern", {})

    coaching = []

    for agent in latest.get("agent_performance", []):
        agent_id = agent.get("agent_id")
        quality = float(agent.get("average_quality_score") or 0)
        confidence = float(agent.get("average_confidence_score") or 0)
        consequence = float(agent.get("average_consequence_score") or 0)

        recommendations = []

        if quality < 80:
            recommendations.append("Increase business-specific detail, action steps, and measurable outcome framing.")
        if confidence < 80:
            recommendations.append("Use stronger client context, competitor context, and evidence-backed reasoning.")
        if consequence >= 70:
            recommendations.append("Keep high-consequence recommendations behind owner approval and avoid autonomous execution.")

        if recommendations:
            coaching.append({
                "agent_id": agent_id,
                "recommendations": recommendations,
                "safe_to_apply_automatically": consequence < 70,
                "owner_review_required": consequence >= 70,
            })

    record = {
        "coaching_id": f"coach_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "profile": LEARNING_OPTIMISATION_PROFILE,
        "tenant_id": str(payload.get("tenant_id") or "global"),
        "coaching_recommendations": coaching,
        "governed_coaching_enabled": True,
        "internal_only": True,
        "client_visible": False,
        "core_model_retraining_allowed": False,
        "protected_governance_rules_mutable": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    _append_jsonl(COACHING_LOG, record)

    return {
        "success": True,
        "learning_profile": LEARNING_OPTIMISATION_PROFILE,
        "coaching": record,
        "coaching_persisted": True,
    }


def governed_learning_readiness() -> Dict[str, Any]:
    outcomes = _read_jsonl(OUTCOME_LOG, limit=1000)
    patterns = _read_jsonl(PATTERN_LOG, limit=1000)
    coaching = _read_jsonl(COACHING_LOG, limit=1000)

    return {
        "success": True,
        "learning_profile": LEARNING_OPTIMISATION_PROFILE,
        "outcome_scoring_enabled": True,
        "confidence_scoring_enabled": True,
        "consequence_scoring_enabled": True,
        "orchestration_outcome_learning_enabled": True,
        "pattern_aggregation_enabled": True,
        "agent_performance_ranking_enabled": True,
        "governed_coaching_recommendations_enabled": True,
        "adaptive_optimisation_telemetry_enabled": True,
        "replay_safe_optimisation_memory_enabled": True,
        "core_model_retraining_allowed": False,
        "autonomous_governance_mutation_allowed": False,
        "owner_approval_controls_preserved": True,
        "internal_learning_not_client_visible": True,
        "outcome_log_exists": OUTCOME_LOG.exists(),
        "pattern_log_exists": PATTERN_LOG.exists(),
        "coaching_log_exists": COACHING_LOG.exists(),
        "outcome_count": len(outcomes),
        "pattern_count": len(patterns),
        "coaching_count": len(coaching),
        "customer_safe_response_mode": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }
'''

LEARNING_FILE.write_text(learning_code.strip() + "\n", encoding="utf-8")

import_line = "from backend.app.core.governed_learning_optimisation_runtime import governed_learning_readiness, score_learning_outcome, aggregate_learning_patterns, generate_agent_coaching_recommendations\n"

if import_line not in main_text:
    marker = "\napp = FastAPI"
    idx = main_text.find(marker)
    if idx == -1:
        marker = "\napp=FastAPI"
        idx = main_text.find(marker)
    if idx == -1:
        raise RuntimeError("Could not find FastAPI app marker.")
    main_text = main_text[:idx] + "\n" + import_line + main_text[idx:]

routes = '''
@app.get("/admin/learning/governed-readiness")
async def admin_learning_governed_readiness():
    return governed_learning_readiness()


@app.post("/admin/learning/score-outcome")
async def admin_learning_score_outcome(payload: dict):
    return score_learning_outcome(payload)


@app.post("/admin/learning/aggregate-patterns")
async def admin_learning_aggregate_patterns(payload: dict = None):
    return aggregate_learning_patterns(payload or {})


@app.post("/admin/learning/generate-coaching")
async def admin_learning_generate_coaching(payload: dict = None):
    return generate_agent_coaching_recommendations(payload or {})
'''

if "/admin/learning/governed-readiness" not in main_text:
    main_text = main_text.rstrip() + "\n\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("PRIORITY7_GOVERNED_LEARNING_OPTIMISATION_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {LEARNING_FILE}")
print("Routes:")
print("/admin/learning/governed-readiness")
print("/admin/learning/score-outcome")
print("/admin/learning/aggregate-patterns")
print("/admin/learning/generate-coaching")