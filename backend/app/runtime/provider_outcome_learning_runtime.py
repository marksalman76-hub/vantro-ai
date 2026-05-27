from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_latency_metric_bridge,
    persist_worker_event_bridge,
)

_OUTCOME_LEARNING_MEMORY: List[Dict[str, Any]] = []


def _now_ms() -> int:
    return int(time.time() * 1000)


def reset_provider_outcome_learning_for_tests() -> Dict[str, Any]:
    _OUTCOME_LEARNING_MEMORY.clear()
    return {
        "reset": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def record_provider_outcome_learning(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    task_type: str,
    quality_score: int,
    review_action: str,
    final_outcome: str,
    retry_count: int = 0,
    latency_ms: int = 0,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    success = final_outcome in {"approved", "delivered", "completed", "customer_accepted"}
    failure = final_outcome in {"rejected", "failed", "manual_review_failed", "customer_rejected"}

    learning_score = quality_score
    if success:
        learning_score += 5
    if failure:
        learning_score -= 20
    if retry_count >= 2:
        learning_score -= 8
    if latency_ms > 60000:
        learning_score -= 5

    learning_score = max(0, min(100, learning_score))

    signal = {
        "learning_id": f"provider_learning_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "quality_score": int(quality_score),
        "learning_score": learning_score,
        "review_action": review_action,
        "final_outcome": final_outcome,
        "retry_count": int(retry_count),
        "latency_ms": int(latency_ms),
        "success": success,
        "failure": failure,
        "notes_present": bool(notes),
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _OUTCOME_LEARNING_MEMORY.append(signal)

    persist_worker_event_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=execution_id,
        provider_key=provider_key,
        event_type="provider_outcome_learning_recorded",
        status=final_outcome,
        details={
            "learning_score": learning_score,
            "quality_score": quality_score,
            "review_action": review_action,
            "retry_count": retry_count,
        },
    )

    persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key=provider_key,
        latency_ms=int(latency_ms or 0),
        operation="provider_outcome_learning",
    )

    return signal


def list_provider_outcome_learning(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    items = list(_OUTCOME_LEARNING_MEMORY)

    if tenant_id:
        items = [i for i in items if i.get("tenant_id") == tenant_id]
    if provider_key:
        items = [i for i in items if i.get("provider_key") == provider_key]
    if task_type:
        items = [i for i in items if i.get("task_type") == task_type]

    items = sorted(items, key=lambda i: i.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "records": items,
        "count": len(items),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def summarise_provider_outcome_learning(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    task_type: Optional[str] = None,
) -> Dict[str, Any]:
    records = list_provider_outcome_learning(
        tenant_id=tenant_id,
        provider_key=provider_key,
        task_type=task_type,
        limit=1000,
    )["records"]

    if not records:
        return {
            "record_count": 0,
            "average_learning_score": None,
            "average_quality_score": None,
            "success_rate": None,
            "retry_rate": None,
            "recommended_action": "collect_more_outcomes",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    avg_learning = round(sum(r["learning_score"] for r in records) / len(records), 2)
    avg_quality = round(sum(r["quality_score"] for r in records) / len(records), 2)
    success_rate = round(sum(1 for r in records if r["success"]) / len(records), 4)
    retry_rate = round(sum(1 for r in records if r["retry_count"] > 0) / len(records), 4)

    if avg_learning >= 85 and success_rate >= 0.8:
        recommended_action = "prefer_provider_for_similar_tasks"
    elif avg_learning >= 70:
        recommended_action = "use_provider_with_monitoring"
    elif retry_rate > 0.4:
        recommended_action = "reduce_provider_priority_and_tune_prompts"
    else:
        recommended_action = "manual_review_provider_performance"

    return {
        "record_count": len(records),
        "average_learning_score": avg_learning,
        "average_quality_score": avg_quality,
        "success_rate": success_rate,
        "retry_rate": retry_rate,
        "recommended_action": recommended_action,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def generate_provider_improvement_recommendation(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    task_type: Optional[str] = None,
) -> Dict[str, Any]:
    summary = summarise_provider_outcome_learning(
        tenant_id=tenant_id,
        provider_key=provider_key,
        task_type=task_type,
    )

    action = summary["recommended_action"]

    if action == "prefer_provider_for_similar_tasks":
        recommendation = "Increase provider priority for similar tasks while keeping governance gates active."
    elif action == "use_provider_with_monitoring":
        recommendation = "Keep provider active, monitor quality, and continue collecting outcome signals."
    elif action == "reduce_provider_priority_and_tune_prompts":
        recommendation = "Reduce provider priority, improve prompts, and route lower-quality outputs through retry/manual review."
    elif action == "manual_review_provider_performance":
        recommendation = "Review provider quality patterns before scaling usage."
    else:
        recommendation = "Collect more outcome data before changing routing behaviour."

    return {
        "summary": summary,
        "recommendation": recommendation,
        "owner_review_required_before_strategy_change": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def provider_outcome_learning_status() -> Dict[str, Any]:
    return {
        "provider_outcome_learning_ready": True,
        "learning_memory_count": len(_OUTCOME_LEARNING_MEMORY),
        "outcome_recording_enabled": True,
        "learning_summary_enabled": True,
        "improvement_recommendations_enabled": True,
        "owner_review_required_before_strategy_change": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
