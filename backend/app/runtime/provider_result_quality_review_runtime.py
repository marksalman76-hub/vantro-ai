from __future__ import annotations

import time
from typing import Any, Dict, Optional

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_worker_event_bridge,
    persist_latency_metric_bridge,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


LOW_QUALITY_TERMS = [
    "placeholder",
    "lorem ipsum",
    "generic",
    "sample text",
    "todo",
    "test output",
    "dummy",
    "n/a",
]


def score_provider_result_quality(
    *,
    provider_key: str,
    task_type: str,
    result_payload: Optional[Dict[str, Any]] = None,
    latency_ms: int = 0,
    retry_count: int = 0,
) -> Dict[str, Any]:
    payload = dict(result_payload or {})
    text = str(payload.get("text") or payload.get("output_text") or payload.get("summary") or "").strip()
    asset_url_present = bool(payload.get("asset_url") or payload.get("output_url") or payload.get("asset_id"))

    score = 100
    reasons = []

    if not text and not asset_url_present:
        score -= 45
        reasons.append("missing_text_or_asset")

    if text and len(text) < 30 and task_type not in {"short_text", "classification"}:
        score -= 20
        reasons.append("output_too_short")

    lowered = text.lower()
    flagged_terms = [term for term in LOW_QUALITY_TERMS if term in lowered]
    if flagged_terms:
        score -= 35
        reasons.append("low_quality_terms_detected")

    if latency_ms > 120000:
        score -= 12
        reasons.append("very_high_latency")
    elif latency_ms > 60000:
        score -= 6
        reasons.append("high_latency")

    if retry_count >= 2:
        score -= 10
        reasons.append("multiple_retries")

    if payload.get("provider_status") in {"failed", "error", "timeout"}:
        score -= 50
        reasons.append("provider_failed_status")

    score = max(0, min(100, score))

    return {
        "provider_key": provider_key,
        "task_type": task_type,
        "quality_score": score,
        "quality_band": "excellent" if score >= 90 else "good" if score >= 75 else "review" if score >= 55 else "poor",
        "reasons": reasons,
        "asset_url_present": asset_url_present,
        "text_present": bool(text),
        "flagged_terms": flagged_terms,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def classify_provider_result_review_action(
    *,
    quality_score: int,
    consequence_level: str = "medium",
    retry_count: int = 0,
    owner_review_required: bool = False,
) -> Dict[str, Any]:
    consequence = (consequence_level or "medium").lower()

    if owner_review_required:
        action = "owner_review_required"
        reason = "owner_review_required_by_policy"
    elif quality_score >= 85 and consequence in {"low", "medium"}:
        action = "ready_for_customer_preview"
        reason = "quality_passed"
    elif quality_score >= 75 and consequence == "low":
        action = "ready_for_customer_preview"
        reason = "quality_passed_low_consequence"
    elif quality_score >= 55 and retry_count < 2:
        action = "queue_retry"
        reason = "quality_needs_improvement"
    else:
        action = "manual_review_required"
        reason = "quality_or_consequence_threshold_not_met"

    return {
        "review_action": action,
        "reason": reason,
        "quality_score": quality_score,
        "consequence_level": consequence,
        "retry_count": retry_count,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def evaluate_provider_result_for_delivery(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    task_type: str,
    result_payload: Optional[Dict[str, Any]] = None,
    latency_ms: int = 0,
    retry_count: int = 0,
    consequence_level: str = "medium",
    owner_review_required: bool = False,
) -> Dict[str, Any]:
    quality = score_provider_result_quality(
        provider_key=provider_key,
        task_type=task_type,
        result_payload=result_payload or {},
        latency_ms=latency_ms,
        retry_count=retry_count,
    )

    classification = classify_provider_result_review_action(
        quality_score=quality["quality_score"],
        consequence_level=consequence_level,
        retry_count=retry_count,
        owner_review_required=owner_review_required,
    )

    event = persist_worker_event_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=execution_id,
        provider_key=provider_key,
        event_type="provider_result_quality_reviewed",
        status=classification["review_action"],
        details={
            "quality_score": quality["quality_score"],
            "quality_band": quality["quality_band"],
            "review_action": classification["review_action"],
            "reason": classification["reason"],
        },
    )

    latency = persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key=provider_key,
        latency_ms=int(latency_ms or 0),
        operation="provider_result_quality_review",
    )

    return {
        "status": "evaluated",
        "quality": quality,
        "classification": classification,
        "event_bridge": event,
        "latency_bridge": latency,
        "ready_for_customer_preview": classification["review_action"] == "ready_for_customer_preview",
        "retry_recommended": classification["review_action"] == "queue_retry",
        "manual_or_owner_review_required": classification["review_action"] in {"manual_review_required", "owner_review_required"},
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def provider_result_quality_review_status() -> Dict[str, Any]:
    return {
        "provider_result_quality_review_ready": True,
        "quality_scoring_enabled": True,
        "automatic_review_classification_enabled": True,
        "retry_recommendation_enabled": True,
        "owner_review_escalation_enabled": True,
        "ledger_event_enabled": True,
        "latency_metric_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
