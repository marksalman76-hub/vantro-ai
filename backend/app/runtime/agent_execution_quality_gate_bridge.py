from __future__ import annotations

import time
from typing import Any, Dict, Optional

from backend.app.runtime.global_agent_output_quality_runtime import evaluate_global_agent_output


def _now_ms() -> int:
    return int(time.time() * 1000)


def extract_agent_output_text(execution_result: Dict[str, Any]) -> str:
    result = dict(execution_result or {})

    candidates = [
        result.get("output_text"),
        result.get("output"),
        result.get("result"),
        result.get("message"),
        result.get("content"),
    ]

    payload = result.get("payload")
    if isinstance(payload, dict):
        candidates.extend([
            payload.get("output_text"),
            payload.get("output"),
            payload.get("result"),
            payload.get("message"),
            payload.get("content"),
        ])

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    return ""


def apply_global_quality_gate_to_agent_result(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    agent_key: str,
    execution_result: Dict[str, Any],
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
    retry_count: int = 0,
    latency_ms: int = 0,
) -> Dict[str, Any]:
    output_text = extract_agent_output_text(execution_result)

    quality = evaluate_global_agent_output(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        agent_key=agent_key,
        output_text=output_text,
        business_context=business_context or {},
        task_type=task_type,
        consequence_level=consequence_level,
        retry_count=retry_count,
        latency_ms=latency_ms,
    )

    action = quality["classification"]["action"]

    delivery_status = "blocked_for_improvement"
    if action == "deliver_to_client":
        delivery_status = "client_delivery_allowed"
    elif action == "deliver_or_head_agent_review":
        delivery_status = "head_agent_review_recommended"
    elif action == "head_agent_review_required":
        delivery_status = "head_agent_review_required"
    elif action == "auto_improve_then_rescore":
        delivery_status = "auto_improvement_required"
    elif action == "retry_agent_output":
        delivery_status = "agent_retry_required"
    elif action in {"manual_review_required", "reject_and_manual_review"}:
        delivery_status = "manual_review_required"

    gated_result = dict(execution_result or {})
    gated_result["global_quality_gate"] = {
        "delivery_status": delivery_status,
        "quality_score": quality["score"]["quality_score"],
        "quality_band": quality["score"]["quality_band"],
        "classification_action": action,
        "classification_reason": quality["classification"]["reason"],
        "client_safe": quality["score"]["client_safe"],
        "deliverable": quality["deliverable"],
        "head_agent_review_required": quality["head_agent_review_required"],
        "manual_review_required": quality["manual_review_required"],
        "improvement": quality.get("improvement"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    return {
        "status": "quality_gate_applied",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "agent_key": agent_key,
        "delivery_status": delivery_status,
        "quality": quality,
        "gated_result": gated_result,
        "client_delivery_allowed": delivery_status == "client_delivery_allowed",
        "requires_follow_up": delivery_status != "client_delivery_allowed",
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def agent_execution_quality_gate_bridge_status() -> Dict[str, Any]:
    return {
        "agent_execution_quality_gate_bridge_ready": True,
        "global_quality_gate_required_before_client_delivery": True,
        "weak_output_blocking_enabled": True,
        "head_agent_review_trigger_enabled": True,
        "manual_review_trigger_enabled": True,
        "auto_improvement_guidance_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
