from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "provider_result_quality_loop.py"
test_file = ROOT / "test_provider_result_quality_loop.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if target.exists():
    backup = BACKUP_DIR / f"provider_result_quality_loop_before_{timestamp}.py"
    backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional


LOW_QUALITY_TERMS = {
    "placeholder",
    "lorem ipsum",
    "generic",
    "sample text",
    "insert here",
    "to be filled",
    "as an ai",
    "i cannot",
    "i'm unable",
    "sorry",
}

PREMIUM_SIGNAL_TERMS = {
    "conversion",
    "audience",
    "offer",
    "positioning",
    "pain point",
    "benefit",
    "cta",
    "campaign",
    "creative",
    "segment",
    "customer",
    "brand",
    "market",
    "retention",
    "upsell",
    "analytics",
    "testing",
    "hook",
    "angle",
    "objection",
}

COMMERCIAL_STRUCTURE_TERMS = {
    "goal",
    "strategy",
    "execution",
    "next step",
    "recommendation",
    "risk",
    "metric",
    "kpi",
    "approval",
    "timeline",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _term_hits(text: str, terms: set[str]) -> list[str]:
    lowered = (text or "").lower()
    return sorted([term for term in terms if term in lowered])


def score_provider_result(
    result: Dict[str, Any],
    task_type: Optional[str] = None,
    minimum_score: int = 72,
) -> Dict[str, Any]:
    text = _normalise_text(
        result.get("output_text")
        or result.get("output")
        or result.get("content")
        or result.get("result")
        or result.get("message")
    )

    words = _word_count(text)
    low_quality_hits = _term_hits(text, LOW_QUALITY_TERMS)
    premium_hits = _term_hits(text, PREMIUM_SIGNAL_TERMS)
    structure_hits = _term_hits(text, COMMERCIAL_STRUCTURE_TERMS)

    score = 40

    if words >= 60:
        score += 15
    elif words >= 30:
        score += 8
    elif words >= 15:
        score += 3
    else:
        score -= 10

    score += min(len(premium_hits) * 4, 24)
    score += min(len(structure_hits) * 3, 18)

    if low_quality_hits:
        score -= min(len(low_quality_hits) * 14, 35)

    if result.get("success") is False:
        score -= 20

    if result.get("provider_execution_attempted") is True:
        score += 5

    if result.get("governance_preserved") is True:
        score += 5

    score = max(0, min(100, score))

    status = "passed_quality_gate"
    recommended_action = "accept_result"

    if score < minimum_score:
        status = "failed_quality_gate"
        recommended_action = "retry_or_regenerate"

    if low_quality_hits:
        recommended_action = "retry_or_escalate_low_quality_output"

    return {
        "success": True,
        "status": status,
        "quality_score": score,
        "minimum_score": minimum_score,
        "recommended_action": recommended_action,
        "task_type": task_type,
        "word_count": words,
        "premium_signal_hits": premium_hits,
        "commercial_structure_hits": structure_hits,
        "low_quality_hits": low_quality_hits,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "generated_at": utc_now_iso(),
    }


def apply_quality_loop_to_provider_result(
    provider_result: Dict[str, Any],
    task_type: Optional[str] = None,
    minimum_score: int = 72,
) -> Dict[str, Any]:
    quality = score_provider_result(
        provider_result,
        task_type=task_type or provider_result.get("action_type"),
        minimum_score=minimum_score,
    )

    accepted = quality["status"] == "passed_quality_gate"

    return {
        **provider_result,
        "quality_loop_applied": True,
        "quality": quality,
        "quality_gate_passed": accepted,
        "execution_status": provider_result.get("execution_status"),
        "finalisation_status": "ready_for_use" if accepted else "requires_retry_or_review",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def decide_retry_from_quality(
    quality_result: Dict[str, Any],
    retry_count: int = 0,
    max_retries: int = 3,
) -> Dict[str, Any]:
    quality = quality_result.get("quality", quality_result)
    score = int(quality.get("quality_score", 0))
    passed = quality.get("status") == "passed_quality_gate"
    retry_available = int(retry_count) < int(max_retries)

    if passed:
        decision = "do_not_retry"
        status = "quality_accepted"
    elif retry_available:
        decision = "retry"
        status = "retry_recommended"
    else:
        decision = "manual_review"
        status = "manual_review_required"

    return {
        "success": True,
        "status": status,
        "decision": decision,
        "quality_score": score,
        "retry_count": int(retry_count),
        "max_retries": int(max_retries),
        "retry_available": retry_available,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "generated_at": utc_now_iso(),
    }


def readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "status": "provider_result_quality_loop_ready",
        "supports_quality_scoring": True,
        "supports_low_quality_detection": True,
        "supports_retry_decisioning": True,
        "supports_manual_review_escalation": True,
        "quality_terms_count": len(PREMIUM_SIGNAL_TERMS),
        "low_quality_terms_count": len(LOW_QUALITY_TERMS),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.provider_result_quality_loop import (
    apply_quality_loop_to_provider_result,
    decide_retry_from_quality,
    readiness,
    score_provider_result,
)


def main():
    ready = readiness()

    strong = {
        "success": True,
        "provider_execution_attempted": True,
        "governance_preserved": True,
        "action_type": "marketing_campaign_execution",
        "output_text": (
            "Goal: increase ecommerce conversion using a clear offer and sharper positioning. "
            "Strategy: create three campaign angles for the target audience, each with a hook, "
            "customer pain point, benefit, CTA, and measurable KPI. Execution: launch creative testing, "
            "track analytics, review retention signals, and recommend next step based on performance. "
            "Risk: do not increase spend without approval."
        ),
    }

    weak = {
        "success": True,
        "provider_execution_attempted": True,
        "governance_preserved": True,
        "action_type": "marketing_campaign_execution",
        "output_text": "Generic placeholder campaign copy. Insert here.",
    }

    strong_score = score_provider_result(strong)
    weak_score = score_provider_result(weak)

    strong_loop = apply_quality_loop_to_provider_result(strong)
    weak_loop = apply_quality_loop_to_provider_result(weak)

    retry_decision = decide_retry_from_quality(weak_loop, retry_count=1, max_retries=3)
    manual_decision = decide_retry_from_quality(weak_loop, retry_count=3, max_retries=3)

    print("PROVIDER_RESULT_QUALITY_LOOP_TEST")
    print("readiness_status", ready["status"])
    print("strong_status", strong_score["status"])
    print("strong_score", strong_score["quality_score"])
    print("weak_status", weak_score["status"])
    print("weak_score", weak_score["quality_score"])
    print("weak_low_quality_hits", weak_score["low_quality_hits"])
    print("strong_finalisation", strong_loop["finalisation_status"])
    print("weak_finalisation", weak_loop["finalisation_status"])
    print("retry_decision", retry_decision["decision"])
    print("manual_decision", manual_decision["decision"])
    print("governance", weak_loop["governance_preserved"])

    assert ready["status"] == "provider_result_quality_loop_ready"
    assert strong_score["status"] == "passed_quality_gate"
    assert strong_score["quality_score"] >= 72
    assert weak_score["status"] == "failed_quality_gate"
    assert weak_score["quality_score"] < 72
    assert "placeholder" in weak_score["low_quality_hits"]
    assert strong_loop["quality_gate_passed"] is True
    assert weak_loop["quality_gate_passed"] is False
    assert weak_loop["finalisation_status"] == "requires_retry_or_review"
    assert retry_decision["decision"] == "retry"
    assert manual_decision["decision"] == "manual_review"
    assert weak_loop["governance_preserved"] is True

    print("PROVIDER_RESULT_QUALITY_LOOP_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("PROVIDER_RESULT_QUALITY_LOOP_INSTALLED")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Quality scoring, retry decisioning, and manual-review escalation foundation installed.")