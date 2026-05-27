from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.app.runtime.async_provider_orchestration_runtime import prepare_provider_selection_packet
from backend.app.runtime.provider_outcome_learning_runtime import summarise_provider_outcome_learning
from backend.app.runtime.provider_result_quality_review_runtime import score_provider_result_quality
from backend.app.runtime.live_provider_adapters import calculate_provider_health_score


def _now_ms() -> int:
    return int(time.time() * 1000)


def build_provider_health_profile(
    *,
    provider_key: str,
    success_count: int = 0,
    failure_count: int = 0,
    timeout_count: int = 0,
    average_latency_ms: Optional[int] = None,
    average_quality_score: Optional[int] = None,
    retry_rate: float = 0.0,
    learning_score: Optional[int] = None,
) -> Dict[str, Any]:
    base_health = calculate_provider_health_score(
        success_count=success_count,
        failure_count=failure_count,
        timeout_count=timeout_count,
        average_latency_ms=average_latency_ms,
    )

    score = int(base_health["health_score"])
    reasons = list(base_health.get("reasons", []))

    if average_quality_score is not None:
        if average_quality_score >= 90:
            score += 8
            reasons.append("excellent_quality_score")
        elif average_quality_score < 60:
            score -= 18
            reasons.append("low_quality_score")

    if learning_score is not None:
        if learning_score >= 85:
            score += 7
            reasons.append("strong_learning_signal")
        elif learning_score < 60:
            score -= 15
            reasons.append("weak_learning_signal")

    if retry_rate > 0.4:
        score -= 12
        reasons.append("high_retry_rate")

    score = max(0, min(100, score))

    return {
        "provider_key": provider_key,
        "health_score": score,
        "base_health_score": base_health["health_score"],
        "failover_recommended": score < 65,
        "success_count": success_count,
        "failure_count": failure_count,
        "timeout_count": timeout_count,
        "average_latency_ms": average_latency_ms,
        "average_quality_score": average_quality_score,
        "retry_rate": retry_rate,
        "learning_score": learning_score,
        "reasons": reasons,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def rank_provider_failover_candidates(
    *,
    requested_provider: str,
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    safe_candidates = [dict(c) for c in candidates]
    ranked = sorted(
        safe_candidates,
        key=lambda c: (
            int(c.get("health_score", 0)),
            int(c.get("average_quality_score") or 0),
            -int(c.get("average_latency_ms") or 999999),
        ),
        reverse=True,
    )

    selected = ranked[0] if ranked else None
    requested = next((c for c in ranked if c.get("provider_key") == requested_provider), None)

    failover_required = False
    failover_reason = "none"

    if requested is None:
        failover_required = bool(selected)
        failover_reason = "requested_provider_not_available"
    elif requested.get("health_score", 0) < 65 and selected and selected.get("provider_key") != requested_provider:
        failover_required = True
        failover_reason = "requested_provider_health_below_threshold"

    return {
        "requested_provider": requested_provider,
        "selected_provider": selected.get("provider_key") if selected else None,
        "failover_required": failover_required,
        "failover_reason": failover_reason,
        "ranked_candidates": ranked,
        "owner_review_required_before_strategy_change": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def automate_provider_selection(
    *,
    requested_provider: str,
    available_providers: List[str],
    provider_health_inputs: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    provider_health_inputs = provider_health_inputs or {}

    profiles = []
    for provider in available_providers:
        raw = provider_health_inputs.get(provider, {})
        learning_summary = summarise_provider_outcome_learning(provider_key=provider)

        learning_score = None
        quality_score = raw.get("average_quality_score")

        if learning_summary.get("record_count", 0) > 0:
            learning_score = int(learning_summary.get("average_learning_score") or 0)
            quality_score = int(learning_summary.get("average_quality_score") or quality_score or 0)

        profiles.append(build_provider_health_profile(
            provider_key=provider,
            success_count=int(raw.get("success_count", 0) or 0),
            failure_count=int(raw.get("failure_count", 0) or 0),
            timeout_count=int(raw.get("timeout_count", 0) or 0),
            average_latency_ms=raw.get("average_latency_ms"),
            average_quality_score=quality_score,
            retry_rate=float(raw.get("retry_rate", learning_summary.get("retry_rate") or 0) or 0),
            learning_score=learning_score,
        ))

    ranked = rank_provider_failover_candidates(
        requested_provider=requested_provider,
        candidates=profiles,
    )

    orchestration_selection = prepare_provider_selection_packet(
        requested_provider=requested_provider,
        available_providers=available_providers,
        provider_health=provider_health_inputs,
    )

    return {
        "status": "selected",
        "requested_provider": requested_provider,
        "selected_provider": ranked["selected_provider"],
        "failover_required": ranked["failover_required"],
        "failover_reason": ranked["failover_reason"],
        "profiles": profiles,
        "ranked_candidates": ranked["ranked_candidates"],
        "orchestration_selection": orchestration_selection,
        "owner_review_required_before_strategy_change": True,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def recommend_provider_after_result(
    *,
    provider_key: str,
    task_type: str,
    result_payload: Dict[str, Any],
    latency_ms: int = 0,
    retry_count: int = 0,
) -> Dict[str, Any]:
    quality = score_provider_result_quality(
        provider_key=provider_key,
        task_type=task_type,
        result_payload=result_payload,
        latency_ms=latency_ms,
        retry_count=retry_count,
    )

    if quality["quality_score"] >= 85 and retry_count == 0:
        recommendation = "keep_or_increase_provider_priority"
    elif quality["quality_score"] >= 65:
        recommendation = "keep_provider_with_monitoring"
    elif retry_count < 2:
        recommendation = "retry_before_failover"
    else:
        recommendation = "failover_or_manual_review"

    return {
        "provider_key": provider_key,
        "task_type": task_type,
        "quality": quality,
        "recommendation": recommendation,
        "owner_review_required_before_strategy_change": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def provider_health_failover_automation_status() -> Dict[str, Any]:
    return {
        "provider_health_failover_automation_ready": True,
        "provider_health_profiles_enabled": True,
        "failover_candidate_ranking_enabled": True,
        "automated_provider_selection_enabled": True,
        "post_result_recommendations_enabled": True,
        "owner_review_required_before_strategy_change": True,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
